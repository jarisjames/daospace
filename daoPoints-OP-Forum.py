import sqlite3
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def ensure_author_entry(author, points_dict):
    if author not in points_dict:
        points_dict[author] = {
            'total_points': 0,
            'topic_likes': 0,
            'regular_post_likes': 0,
            'aligned_topic_replies': 0,
            'aligned_post_replies': 0
        }


# Initialize VADER SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def calculate_alignment_score(original_compound, reply_compound):
    """Calculate alignment based on sentiment compound scores."""
    alignment_score = 100 - (abs(original_compound - reply_compound) / 2) * 100
    return alignment_score >= 50  # True if alignment score is 50% or higher

def calculate_likes_and_points_verbose(dao_name):
    conn = sqlite3.connect("path_to_your_database.db")
    cursor = conn.cursor()
    points_dict = {}  # Example format: { 'username': {'total_points': 0, 'topic_likes': 0, 'regular_post_likes': 0, 'aligned_topic_replies': 0, 'aligned_post_replies': 0} }
    # To track titles and authors of processed topic creations for avoiding double-counting
    topic_creation_posts = set()


    # Processing topic creation likes
    print("\nProcessing topic creation likes:")
    cursor.execute("""
        SELECT FL.title, FL.OriginalPoster, FP.likes, FP.post_identifier
        FROM ForumLinks FL
        JOIN ForumPosts FP ON FL.title = FP.title AND FL.OriginalPoster = FP.author
        WHERE FL.name = ?
        GROUP BY FL.title, FL.OriginalPoster
        ORDER BY FP.post_time ASC
    """, (dao_name,))
    for title, author, likes, post_identifier in cursor.fetchall():
        like_count = len(likes.split(',')) if likes else 0
        ensure_author_entry(author, points_dict)  # Ensure author entry is initialized
        points_dict[author]['topic_likes'] += like_count
        points = like_count * 10  # Assuming 10 points per like for topic creation posts
        points_dict[author]['total_points'] += points
        topic_creation_posts.add(post_identifier)
        print(f"Topic: '{title}' by {author}, Likes: {like_count}, Points from this topic: {points}")
    
# Processing regular post likes with optimized query
    print("\nProcessing regular post likes:")
    cursor.execute("""
        SELECT FP.title, FP.author, FP.likes, FP.post_identifier
        FROM ForumPosts FP
        WHERE FP.dao_name = ? AND FP.post_identifier NOT IN (
            SELECT post_identifier FROM ForumPosts WHERE dao_name = ? AND post_identifier IN (
                SELECT post_identifier FROM ForumPosts WHERE dao_name = ? GROUP BY title HAVING MIN(post_time)
            )
        )
    """, (dao_name, dao_name, dao_name))
    for title, author, likes, post_identifier in cursor.fetchall():
        if post_identifier in topic_creation_posts:
            continue  # Skip if this post was a topic creation post
        like_count = len(likes.split(',')) if likes else 0
        ensure_author_entry(author, points_dict)  # Ensure author entry is initialized
        points_dict[author]['regular_post_likes'] += like_count
        points = like_count * 1  # Assuming 1 point per like for regular posts
        points_dict[author]['total_points'] += points
        print(f"Post in topic '{title}' by {author}, Likes: {like_count}, Points from this post: {points}")



    
    # Processing aligned replies
    print("\nProcessing aligned replies:")
    cursor.execute("""
        SELECT FL.title, FL.OriginalPoster
        FROM ForumLinks FL
        WHERE FL.name = ?
    """, (dao_name,))  # Make sure to provide a tuple with a single element (dao_name,)

    topics = cursor.fetchall()

    for title, original_poster in topics:
        cursor.execute("""
            SELECT content
            FROM ForumPosts
            WHERE title = ? AND author = ? AND dao_name = ?
            ORDER BY post_time ASC
            LIMIT 1
        """, (title, original_poster, dao_name))  # Ensure all placeholders are matched with parameters

        original_post_content_row = cursor.fetchone()
        if original_post_content_row:
            original_post_content = original_post_content_row[0]
            original_post_sentiment = sia.polarity_scores(original_post_content)['compound']

            cursor.execute("""
                SELECT author, content
                FROM ForumPosts
                WHERE dao_name = ? AND title = ? AND author != ?
            """, (dao_name, title, original_poster))  # Again, ensure parameter count matches

            for reply_author, reply_content in cursor.fetchall():
                reply_sentiment = sia.polarity_scores(reply_content)['compound']
                if calculate_alignment_score(original_post_sentiment, reply_sentiment):
                    ensure_author_entry(original_poster, points_dict)  # Ensure original poster's entry is initialized
                    points_dict[original_poster]['aligned_topic_replies'] += 1  # Increment aligned topic replies count
                    points = 20  # Assuming 20 points are awarded for aligned topic replies
                    points_dict[original_poster]['total_points'] += points  # Increment total points
                    print(f"Aligned Reply in '{title}' by {reply_author}, Alignment Score: >= 50%, Points awarded to OP: {original_poster}, 20 points")

    
    
    
    # Initialize a set to track Topic Creation Posts identifiers
    topic_creation_posts = set()

    # Populate the set with identifiers of Topic Creation Posts
    cursor.execute("""
        SELECT FP.post_identifier
        FROM ForumPosts FP
        JOIN ForumLinks FL ON FP.title = FL.title AND FP.author = FL.OriginalPoster
        WHERE FP.dao_name = ?
    """, (dao_name,))
    topic_creation_posts = {row[0] for row in cursor.fetchall()}
    
   
    # Processing aligned replies to regular posts (excluding Topic Created posts and self-replies)
    print("\nProcessing aligned replies to regular posts:")
    # Fetch titles for all topics within the DAO
    cursor.execute("SELECT title FROM ForumLinks WHERE name = ?", (dao_name,))
    topics = cursor.fetchall()

    for (title,) in topics:
        # Fetch regular posts within each topic, excluding the first post (topic creation post)
        cursor.execute("""
            SELECT FP.post_identifier, FP.author, FP.content, FP.replies
            FROM ForumPosts FP
            WHERE FP.dao_name = ? AND FP.title = ? AND FP.replies IS NOT NULL AND FP.replies != '()' AND TRIM(FP.replies) != ''
            AND FP.post_time > (SELECT MIN(FP2.post_time) FROM ForumPosts FP2 WHERE FP2.title = FP.title AND FP2.dao_name = FP.dao_name)
        """, (dao_name, title))

        for post_identifier, post_author, post_content, replies_text in cursor.fetchall():
            if post_identifier in topic_creation_posts:
                continue  # Skip if this post was a topic creation post
            try:
                replies = eval(replies_text)
            except SyntaxError:
                continue  # If replies_text is not safely evaluable, skip to the next post

            for reply_author, reply_content in replies:
                if reply_author == post_author:
                    continue  # Skip self-replies
                post_sentiment = sia.polarity_scores(post_content)['compound']
                reply_sentiment = sia.polarity_scores(reply_content)['compound']
                if calculate_alignment_score(post_sentiment, reply_sentiment):
                    ensure_author_entry(post_author, points_dict)  # Ensure the post author's entry exists
                    points_dict[post_author]['aligned_post_replies'] += 1  # Increment aligned regular post replies count
                    points = 2  # Assuming 2 points are awarded for aligned regular post replies
                    points_dict[post_author]['total_points'] += points  # Increment total points
                    print(f"Aligned Reply in '{title}' by {reply_author} to post by {post_author}, Alignment Score: >= 50%, Points awarded to OP (for regular post): {post_author}, 2 points")


    # Print total points for each author after all processing
    print("\nTotal Points for each author after processing topics and posts:")
    for author, details in sorted(points_dict.items(), key=lambda item: item[1]['total_points'], reverse=True):
        print(f"{author}: {details['total_points']} points")
        print(f"  (Total Topic Likes): {details['topic_likes']}")
        print(f"  (Total Regular Post Likes): {details['regular_post_likes']}")
        print(f"  (Total Aligned Topic Replies): {details['aligned_topic_replies']}")
        print(f"  (Total Aligned Regular Post Replies): {details['aligned_post_replies']}")

    conn.close()

calculate_likes_and_points_verbose("Optimism")
