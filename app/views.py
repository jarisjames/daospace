from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.db.models import Q, Sum, Count
from .models import DAO, ForumLinks, ForumPosts, TopicSummaries
from django.core.paginator import Paginator
import ast  # Safely evaluate string representation of a Python expression
import re
from django.http import JsonResponse, HttpResponseForbidden
from web3 import Web3
import json
from django.views.decorators.csrf import csrf_protect
from eth_account.messages import encode_defunct
import random
import string
import requests
from bs4 import BeautifulSoup
import ast  # Safely evaluate string representation of a Python expression
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.db.models import F, Sum, IntegerField, Value as V
from django.db.models.functions import Coalesce
from django.db.models import F, ExpressionWrapper, fields, IntegerField
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from .utils import parse_boolean_query, parse_emoji_reactions, emoji_mapping
from decimal import Decimal
from django.conf import settings
from django.templatetags.static import static
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string



def parse_emoji_reactions(emoji_reactions_str):
    # Adjusted regex pattern to match negative numbers as well
    pattern = re.compile(r'([+-]?\w+)-(\d+) reactions \((.*?)\)')
    emoji_reactions = {}
    
    for match in pattern.finditer(emoji_reactions_str):
        emoji, count, users_str = match.groups()
        users = users_str.split(', ')
        emoji_reactions[emoji] = {'count': int(count), 'users': users}
    
    return emoji_reactions

# Emoji mapping from identifier to Unicode
emoji_mapping = {
    "+1": "👍",
    "-1": "👎",
    "0": "0️⃣",
    "1": "👍",
    "100": "💯",
    "clap": "👏",
    "confetti_ball": "🎊",
    "confused": "😕",
    "exclamation": "❗",
    "eyes": "👀",
    "fire": "🔥",
    "heart": "❤️",
    "hugs": "🤗",
    "ice_cube": "🧊",
    "laughing": "😆",
    "no_entry": "⛔",
    "open_mouth": "😮",
    "pray": "🙏",
    "rocket": "🚀",
    "tada": "🎉",
}

def simple_view(request):
    query = request.GET.get('q', '')

    dao_results = None
    forum_link_results = None
    forum_post_results = None
    active_page = 'home'

    # Fetch the logged-in user's wallet address from the session
    user_wallet_address = request.session.get('wallet_address')

    # Debugging logged-in wallet address
    print(f"Logged in wallet address: {user_wallet_address}")

    # Ensure the wallet address is not None
    if user_wallet_address:
        linked_forum_links = ForumLinks.objects.filter(wallet_address=user_wallet_address)
        linked_forum_posts = ForumPosts.objects.filter(wallet_address=user_wallet_address)

        # Debugging associated authors
        linked_authors = set()
        for link in linked_forum_links:
            linked_authors.add(link.OriginalPoster)
        for post in linked_forum_posts:
            linked_authors.add(post.author)
        print("Linked Authors:", linked_authors)
    else:
        print("No wallet address found for the logged-in user.")

    if query:
        dao_results = DAO.objects.filter(
            Q(name__icontains=query) |
            Q(categories__icontains=query) |
            Q(forum_link__icontains=query)
        )
        forum_link_results = ForumLinks.objects.filter(
            Q(name__icontains=query) |
            Q(title__icontains=query) |
            Q(OriginalPoster__icontains=query) |
            Q(Category__icontains=query) |
            Q(link__icontains=query)
        )
        forum_post_results = ForumPosts.objects.filter(
            Q(content__icontains=query) |
            Q(author__icontains=query) |
            Q(Role__icontains=query) |
            Q(dao_name__icontains=query) |
            Q(post_time__icontains=query) |
            Q(post_links__icontains=query) |
            Q(link_clicks__icontains=query) |
            Q(Links__icontains=query) |
            Q(title__icontains=query)
        )
    else:
        active_page = 'home'

    if forum_post_results:
        for post in forum_post_results:
            post.likes_list = post.likes.split(',') if post.likes else []
            try:
                replies_tuples = ast.literal_eval(post.replies)
                post.replies_list = [f"{reply[0]}: {reply[1]}" for reply in replies_tuples]
            except (ValueError, SyntaxError):
                post.replies_list = []

            if post.dao_name == "ENS" and post.emoji_reactions:
                raw_reactions = parse_emoji_reactions(post.emoji_reactions)
                post.emoji_reactions_display = {}
                for key, reaction_info in raw_reactions.items():
                    emoji_unicode = emoji_mapping.get(key, key)
                    post.emoji_reactions_display[emoji_unicode] = reaction_info['users']

    # Add the dao_feed logic
    dao = None
    topics = TopicSummaries.objects.all().order_by('-Created')

    return render(request, 'app/home.html', {
        'dao_results': dao_results,
        'forum_link_results': forum_link_results,
        'forum_post_results': forum_post_results,
        'active_page': active_page,
        'dao': dao,
        'topics': topics,  # Include topics for the feed
    })






def parse_boolean_query(query, fields):
    tokens = re.findall(r'\".*?\"|\S+', query)
    query_obj = Q()

    current_op = None

    for token in tokens:
        if token.upper() == 'AND':
            current_op = 'AND'
        elif token.upper() == 'OR':
            current_op = 'OR'
        elif token.upper() == 'NOT':
            current_op = 'NOT'
        else:
            token = token.strip('"')
            sub_query = Q()

            for field in fields:
                if current_op == 'NOT':
                    sub_query |= ~Q(**{f"{field}__icontains": token})
                else:
                    sub_query |= Q(**{f"{field}__icontains": token})

            if current_op == 'OR':
                query_obj |= sub_query
            else:
                query_obj &= sub_query

            current_op = None

    return query_obj



import ast

def search_view(request):
    query = request.GET.get('q', '')
    date_field = request.GET.get('date_field')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    view = request.GET.get('view', 'topics')  # Default view is 'topics'
    sort = request.GET.get('sort', 'latest')  # Default sort is 'latest'

    dao_results = None
    page_obj_post = None
    page_obj_link = None
    total_post_results = 0
    total_link_results = 0

    # Map for sorting keys
    sort_mapping = {
        'latest': '-post_time',
        'top': '-total_likes',
    }

    # Resolve date field
    if date_field and date_field.lower() == 'last_activity':
        date_field = 'LastActivityDate'
    elif date_field and date_field.lower() == 'created':
        date_field = 'Created'

    # DAO Results
    if query:
        dao_results = DAO.objects.filter(
            parse_boolean_query(query, ['name', 'categories', 'forum_link'])
        ).only('name', 'categories', 'forum_link')

    # Date filter
    date_filter = {}
    if date_field and start_date and end_date:
        date_filter[f'{date_field}__range'] = [start_date, end_date]

    # ForumPosts Query
    if query or date_filter:
        forum_post_results = ForumPosts.objects.filter(
            parse_boolean_query(query, [
                'content', 'author', 'Role', 'dao_name', 'post_time',
                'post_links', 'link_clicks', 'Links', 'title'
            ]),
            **date_filter
        ).only('content', 'author', 'dao_name', 'post_time', 'total_likes', 'replies', 'likes', 'title')  # Fetch relevant fields

        # Sorting
        sort_field = sort_mapping.get(sort, '-post_time')
        forum_post_results = forum_post_results.order_by(sort_field)

        # Pagination
        paginator_post = Paginator(forum_post_results, 10)
        page_number_post = request.GET.get('page_post')
        page_obj_post = paginator_post.get_page(page_number_post)
        total_post_results = paginator_post.count

        # Add hyperlinks and parse likers/repliers
        for post in page_obj_post:
            # Hyperlink logic for likers and repliers
            post.likes_list = post.likes.split(',') if post.likes else []
            try:
                replies_tuples = ast.literal_eval(post.replies)
                post.replies_list = [(reply[0], reply[1]) for reply in replies_tuples]  # Store as tuples (replier, reply_content)
            except (ValueError, SyntaxError):
                post.replies_list = []

            # Add link_id for hyperlinking posts
            link = ForumLinks.objects.filter(title=post.title, name=post.dao_name).first()
            post.link_id = link.id if link else None

    # ForumLinks Query
    if query or date_filter:
        forum_link_results = ForumLinks.objects.filter(
            parse_boolean_query(query, ['title', 'name', 'OriginalPoster']),
            **date_filter
        ).only('title', 'name', 'OriginalPoster', 'views', 'replies', 'Created')

        # Sorting
        if sort == 'top':
            forum_link_results = forum_link_results.annotate(
                engagement=F('views') + F('replies')
            ).order_by('-engagement')
        else:
            forum_link_results = forum_link_results.order_by('-Created')

        # Pagination
        paginator_link = Paginator(forum_link_results, 10)
        page_number_link = request.GET.get('page_link')
        page_obj_link = paginator_link.get_page(page_number_link)
        total_link_results = paginator_link.count

    # Determine the default view
    if not page_obj_link and page_obj_post:
        view = 'posts'
    elif page_obj_link and not page_obj_post:
        view = 'topics'

    return render(request, 'app/search_results.html', {
        'dao_results': dao_results,
        'page_obj_post': page_obj_post,
        'page_obj_link': page_obj_link,
        'current_view': view,
        'total_post_results': total_post_results,
        'total_link_results': total_link_results,
        'current_sort': sort,
    })














def daos_view(request):
    cache_key = "dao_leaderboard"
    leaderboard = cache.get(cache_key)

    if not leaderboard:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, COUNT(*) AS total_topics
                FROM ForumLinks
                GROUP BY name
            """)
            topics_data = cursor.fetchall()

            cursor.execute("""
                SELECT dao_name, COUNT(*) AS total_posts
                FROM ForumPosts
                GROUP BY dao_name
            """)
            posts_data = cursor.fetchall()

            cursor.execute("""
                SELECT dao_name, COUNT(DISTINCT author) AS total_members
                FROM ForumPosts
                GROUP BY dao_name
            """)
            members_data = cursor.fetchall()

        topics_dict = {item[0]: item[1] for item in topics_data}
        posts_dict = {item[0]: item[1] for item in posts_data}
        members_dict = {item[0]: item[1] for item in members_data}

        dao_list = DAO.objects.all()
        leaderboard = []

        for dao in dao_list:
            dao_name = dao.name
            logo_file = f'{dao_name.replace(" ", "")}.webp'
            logo_static_path = f'Images/dao-logos/{logo_file}'

            total_members = members_dict.get(dao_name, 0)
            total_topics = topics_dict.get(dao_name, 0)
            total_posts = posts_dict.get(dao_name, 0)
            total_score = total_topics + total_posts

            leaderboard.append({
                'dao': dao,
                'logo_static_path': logo_static_path,
                'total_members': total_members,
                'total_topics': total_topics,
                'total_posts': total_posts,
                'total_score': total_score,
            })

        leaderboard = sorted(leaderboard, key=lambda x: x['total_score'], reverse=True)
        cache.set(cache_key, leaderboard, 300)

    return render(request, 'app/daos.html', {'leaderboard': leaderboard})




def dao_detail_view(request, dao_name):
    dao = get_object_or_404(DAO, name__iexact=dao_name)  # Using iexact to ignore case sensitivity
    return render(request, 'app/dao_detail.html', {'dao': dao})

def dao_forum_view(request, dao_name):
    # Fetching the specific DAO
    dao = get_object_or_404(DAO, name__iexact=dao_name)
    
    # Filtering ForumLinks entries that match the DAO name.
    # Assuming the 'name' field in ForumLinks is used to store corresponding DAO names.
    forum_links = ForumLinks.objects.filter(name__iexact=dao_name).order_by('-Created')

    return render(request, 'app/dao_forum.html', {
        'dao': dao,
        'forum_links': forum_links
    })


def forum_topic_detail(request, link_id):
    import ast  # Ensure this is imported at the top if not already
    
    link = get_object_or_404(ForumLinks, id=link_id)
    
    # Order the posts by 'post_time' in ascending order (earliest to latest)
    forum_posts = ForumPosts.objects.filter(title=link.title, dao_name=link.name).order_by('post_time')
    
    # Fetch the summary content from TopicSummaries
    try:
        topic_summary = TopicSummaries.objects.get(post_identifier=link_id)
        summary_content = topic_summary.content
    except TopicSummaries.DoesNotExist:
        summary_content = None  # Handle the case where there is no summary

    for post in forum_posts:
        post.likes_list = post.likes.split(',') if post.likes else []
        try:
            replies_tuples = ast.literal_eval(post.replies)
            post.replies_list = replies_tuples  # Store as tuples (replier, reply_content)
        except (ValueError, SyntaxError):
            post.replies_list = []

    return render(request, 'app/forum_topic_detail.html', {
        'forum_posts': forum_posts,
        'link': link,
        'summary_content': summary_content
    })





def dao_members_view(request, dao_name):
    dao = DAO.objects.get(name=dao_name)
    
    cache_key = f"dao_members_leaderboard_{dao_name}"
    leaderboard = cache.get(cache_key)

    if not leaderboard:
        with connection.cursor() as cursor:
            # Query to get total topics created by each member
            cursor.execute("""
                SELECT OriginalPoster, COUNT(*) AS total_topics, SUM(views) AS total_views
                FROM ForumLinks
                WHERE name = %s
                GROUP BY OriginalPoster
            """, [dao_name])
            topics_data = cursor.fetchall()

            # Query to get total posts made by each member
            cursor.execute("""
                SELECT author, COUNT(*) AS total_posts, SUM(total_likes) AS total_likes, SUM(TotalReplies) AS total_replies
                FROM ForumPosts
                WHERE dao_name = %s
                GROUP BY author
            """, [dao_name])
            posts_data = cursor.fetchall()

        # Convert the data into dictionaries for easier access
        topics_dict = {item[0]: {'total_topics': item[1], 'total_views': item[2]} for item in topics_data}
        posts_dict = {item[0]: {'total_posts': item[1], 'total_likes': item[2], 'total_replies': item[3]} for item in posts_data}

        # Combine the data
        combined_data = {}
        for member, data in topics_dict.items():
            combined_data[member] = data
        for member, data in posts_dict.items():
            if member in combined_data:
                combined_data[member].update(data)
            else:
                combined_data[member] = data

        # Prepare the leaderboard data
        leaderboard = []
        for member, data in combined_data.items():
            total_topics = Decimal(data.get('total_topics', 0))
            total_posts = Decimal(data.get('total_posts', 0))
            total_likes = Decimal(data.get('total_likes', 0))
            total_replies = Decimal(data.get('total_replies', 0))
            total_views = Decimal(data.get('total_views', 0))
            
            # Calculate the total score
            total_score = total_topics + total_posts + total_likes + total_replies + (total_views / Decimal('10000'))
            
            leaderboard.append({
                'member': member,
                'total_topics': total_topics,
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_replies': total_replies,
                'total_views': total_views,
                'total_score': total_score,
            })

        # Sort leaderboard by total score in descending order
        leaderboard = sorted(leaderboard, key=lambda x: x['total_score'], reverse=True)
        
        # Cache the leaderboard data for 10 minutes (600 seconds)
        cache.set(cache_key, leaderboard, 600)

    return render(request, 'app/dao_members.html', {'dao': dao, 'leaderboard': leaderboard})





def member_detail(request, dao_name, member_name):
    dao = get_object_or_404(DAO, name=dao_name)

    # Retrieve all posts for this member, ordered by most recent
    post_list = ForumPosts.objects.filter(dao_name=dao_name, author=member_name).order_by('-post_time')

    # Set up pagination: 10 posts per page
    paginator = Paginator(post_list, 10)

    # Get the page number from the query string (?page=2, etc.)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Process each post in the current page for likes, replies, and link_id
    for post in page_obj:
        post.likes_list = post.likes.split(',') if post.likes else []
        try:
            replies_tuples = ast.literal_eval(post.replies)
            post.replies_list = replies_tuples  # Store as tuples (replier, reply_content)
        except (ValueError, SyntaxError):
            post.replies_list = []

        # Assign link_id for each post
        try:
            link = ForumLinks.objects.get(title=post.title, name=post.dao_name)
            post.link_id = link.id
        except ForumLinks.DoesNotExist:
            post.link_id = None
        except ForumLinks.MultipleObjectsReturned:
            links = ForumLinks.objects.filter(title=post.title, name=post.dao_name)
            post.link_id = links.first().id if links.exists() else None

        # Handle emoji reactions for ENS DAO posts if needed
        if post.dao_name == "ENS" and post.emoji_reactions:
            raw_reactions = parse_emoji_reactions(post.emoji_reactions)
            post.emoji_reactions_display = {}
            for key, reaction_info in raw_reactions.items():
                emoji_unicode = emoji_mapping.get(key, key)
                post.emoji_reactions_display[emoji_unicode] = reaction_info['users']

    return render(request, 'app/member_detail.html', {
        'dao': dao,
        'member': member_name,
        'page_obj': page_obj,
    })




@csrf_protect
def verify_signature(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        signature = data['signature']
        account = data['account']
        message = data['message']
        print("Received data:", data)  # Debugging information

        # Initialize Web3
        w3 = Web3()

        # Encode the message
        encoded_message = encode_defunct(text=message)
        
        # Verify the signature correctly
        try:
            signer = w3.eth.account.recover_message(encoded_message, signature=signature)
            print("Recovered signer:", signer)  # Debugging information
            if signer.lower() == account.lower():
                print("Signature verified successfully")  # Debugging information
                # Store wallet address in session
                request.session['wallet_address'] = account.lower()
                print("Wallet address stored in session:", request.session['wallet_address'])
                return JsonResponse({'success': True, 'message': 'Logged in successfully'})
            else:
                print("Invalid signature")  # Debugging information
                return JsonResponse({'success': False, 'message': 'Invalid signature'})
        except Exception as e:
            print("Error during verification:", str(e))  # Debugging information
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def generate_unique_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))




@csrf_protect
def profile_view(request, account):
    daos = DAO.objects.all()  # Fetch all DAOs from the database

    forum_posts = ForumPosts.objects.filter(wallet_address=account)
    forum_links = ForumLinks.objects.filter(wallet_address=account)

    # Process posts to get likes and replies
    for post in forum_posts:
        post.likes_list = post.likes.split(',') if post.likes else []
        try:
            replies_tuples = ast.literal_eval(post.replies)
            post.replies_list = [(reply[0], reply[1]) for reply in replies_tuples]  # Store as tuples (replier, reply_content)
        except (ValueError, SyntaxError):
            post.replies_list = []

        # Assign link_id for each post
        try:
            link = ForumLinks.objects.get(title=post.title, name=post.dao_name)
            post.link_id = link.id
        except ForumLinks.DoesNotExist:
            post.link_id = None
        except ForumLinks.MultipleObjectsReturned:
            # Handle case where multiple links exist for the same title and dao_name
            links = ForumLinks.objects.filter(title=post.title, name=post.dao_name)
            post.link_id = links.first().id if links.exists() else None

    if request.method == 'POST':
        forum_username = request.POST['forumUsername']
        dao_name = request.POST['daoName']
        unique_code = generate_unique_code()
        
        # Save the unique code in the session for later verification
        request.session['unique_code'] = unique_code
        
        # Return the unique code as JSON response
        return JsonResponse({'unique_code': unique_code})
    
    return render(request, 'app/profile.html', {
        'account': account,
        'daos': daos,
        'forum_posts': forum_posts,
        'forum_links': forum_links
    })

# Function to suppress output (if necessary)
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

# Function to scrape the bio from the user's profile page
def scrape_bio(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    with SuppressOutput():
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    bio_text = None

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bio div.ember-view p')))
        bio_div = driver.find_element(By.CSS_SELECTOR, 'div.bio div.ember-view p')
        bio_text = bio_div.text
        print(f'Bio: {bio_text}')
    except Exception as e:
        print(f'Error: {e}')
    driver.quit()

    return bio_text

# Updated link_forum_data view
@csrf_protect
def link_forum_data(request, account):
    if request.method == 'POST':
        data = json.loads(request.body)
        forum_username = data['forumUsername']
        dao_name = data['daoName']
        unique_code = data['uniqueCode']

        print(f"Incoming data: {data}")  # Debugging information
        print(f"Account: {account}")  # Debugging information

        # Verify the unique code
        stored_unique_code = request.session.get('unique_code', '')

        if unique_code == stored_unique_code:
            dao = DAO.objects.get(name=dao_name)
            forum_link = dao.forum_link
            profile_url = forum_link.replace('/categories', f'/u/{forum_username}')

            print(f"Visiting profile URL: {profile_url}")  # Debugging information

            bio_text = scrape_bio(profile_url)

            if bio_text:
                print(f"Scraped bio content: {bio_text}")  # Debugging information

                if unique_code in bio_text:
                    # Update the ForumPosts and ForumLinks with the wallet address
                    forum_posts = ForumPosts.objects.filter(dao_name=dao_name, author=forum_username)
                    forum_links = ForumLinks.objects.filter(name=dao_name, OriginalPoster=forum_username)

                    forum_posts.update(wallet_address=account)
                    forum_links.update(wallet_address=account)

                    return JsonResponse({'success': True, 'message': 'Forum data linked successfully'})
                else:
                    return JsonResponse({'success': False, 'message': 'Verification code not found in bio'})
            else:
                print("Bio element not found")  # Debugging information
                return JsonResponse({'success': False, 'message': 'Bio element not found'})
        else:
            print("Invalid verification code")  # Debugging information
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})

    print("Invalid request method")  # Debugging information
    return JsonResponse({'success': False, 'message': 'Invalid request'})




def custom_view_dispatcher(request, identifier):
    # Check if the identifier is a valid Ethereum address
    if re.match(r'^0x[a-fA-F0-9]{40}$', identifier):
        return profile_view(request, identifier)
    else:
        return dao_detail_view(request, identifier)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        signature = data.get('signature')
        wallet_address = data.get('account')
        message = data.get('message')

        # Verify the signature and wallet address (assuming verification is done here)
        # If verification is successful:
        request.session['wallet_address'] = wallet_address
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)




from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.conf import settings
import os

# Whitelist mapping: wallet addresses to GLB file paths
WALLET_TO_GLB = {
    "0xb04e6891e584f2884ad2ee90b6545ba44f843c4a": "models/CCs/jarisjames.glb",
    "0xc2971fe806ce4438da09e21fc7be7fb121cf7e13": "models/CCs/sixty.glb",
    "0xca85c622d4c61047f96e352cb919695486a193e6": "models/CCs/Jaf.glb",
    "0xe50c860db2ddc5e9c901aa3b3dc497b3e6ea4ad5": "models/CCs/addie.glb",
    "0xa439a408a8e4f1d07757a21ad0858f62ece0a77a": "models/CCs/janaBe.glb",
    "0xd8936e602e38dfee5d6466865068b94b1943debf": "models/CCs/forexus.glb",
    "0x53eaa0d7f5e43d47b0b0e30b283e923601eaa80b": "models/CCs/dzonson.glb",
    "0xbe3f82034778fbf474060f7d4a032f592559ab4d": "models/CCs/firefly808.glb",
    "0x3bc71d21dc7b07a70e01159593d8f954eb065644": "models/CCs/coffee-crusher.glb",
    "0x4d32d90d6535bd4e7eabaa27ee72932cb214bbfa": "models/CCs/bitblondy.glb",
    "0xafd4aa1eecefb409e627674f023b235c3b06203d": "models/CCs/sohobiit.glb",
    "0xc04d122c91bbcd4c15f0ebb73fc3fcdaee687fd4": "models/CCs/winverse.glb",
    "0x326301483aaa7366960877fa18b019e9c2d53e5d": "models/CCs/lionmsee.glb",
    "0xb4ca913e2b6efb7cf3798b41cd68c72a5d1cac23": "models/CCs/KAF.glb",
    "0xfa773d02eb76ad8c7585d36c87707b9fe13d766d": "models/CCs/cr1st0f.glb",
    "0xf31df2dcd4083ee57f0d33d386656cfbd1e859a1": "models/CCs/jengajojo.glb",
    "0x1d671d1b191323a38490972d58354971e5c1cd2a": "models/CCs/andreitr.glb",
    "0x6f9bb7e454f5b3eb2310343f0e99269dc2bb8a1d": "models/CCs/alexq.glb",
    "0x7f953f11343408ebccaecd04eb0d1e6bacdef87f": "models/CCs/coolhorsegirl.glb",

    


    # Add the rest of your wallet address and GLB file mappings here
    # For example:
    # "0x123...abc": "models/CCs/addie.glb",
    # "0x456...def": "models/CCs/akihiru.glb",
    # "0x789...ghi": "models/CCs/alexq.glb",
    # ...
}

def claim_contributor_card(request):
    # Fetch the connected wallet address from the session
    wallet_address = request.session.get('wallet_address')

    if not wallet_address:
        # Wallet not connected: Display the Contributor Card Template
        glb_file = "models/ContributorCardTemplate.glb"
        return render(request, 'app/claim_contributor_card.html', {'glb_file': glb_file})

    # Convert wallet_address to lowercase to ensure case-insensitive matching
    wallet_address = wallet_address.lower()

    # Find the corresponding .glb file using the whitelist dictionary
    glb_file = WALLET_TO_GLB.get(wallet_address)

    if not glb_file:
        # Wallet is connected but not whitelisted: Display the Contributor Card Template
        glb_file = "models/ContributorCardTemplate.glb"
        return render(request, 'app/claim_contributor_card.html', {'glb_file': glb_file})

    # Wallet is connected and whitelisted: Display the custom Contributor Card
    return render(request, 'app/claim_contributor_card.html', {'glb_file': glb_file})








def dao_feed(request, dao_name=None):
    if dao_name:
        dao = DAO.objects.get(name=dao_name)
        topics = TopicSummaries.objects.filter(name=dao_name).order_by('-Created')
    else:
        dao = None
        topics = TopicSummaries.objects.all().order_by('-Created')
    return render(request, 'app/dao_feed.html', {'dao': dao, 'topics': topics})

