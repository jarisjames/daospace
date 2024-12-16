from django.db import models

class DAO(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    categories = models.TextField(blank=True, null=True)
    forum_link = models.CharField(max_length=255)

    class Meta:
        db_table = 'DAOs'

class ForumLinks(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True, default="Default Name", blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(max_length=500)
    views = models.IntegerField(default=0, blank=True, null=True)
    replies = models.IntegerField(default=0, blank=True, null=True)
    LastActivityDate = models.DateField(blank=True, null=True)
    OriginalPoster = models.CharField(max_length=255, blank=True, null=True)
    Category = models.CharField(max_length=255, blank=True, null=True)
    Created = models.DateTimeField(blank=True, null=True)
    wallet_address = models.CharField(max_length=42, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ForumLinks'

class ForumPosts(models.Model):
    PostID = models.AutoField(primary_key=True)
    dao_name = models.CharField(max_length=255, blank=True, null=True)
    author = models.TextField()
    Role = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    post_time = models.DateTimeField(blank=True, null=True)
    total_likes = models.IntegerField(default=0)
    likes = models.TextField(blank=True, null=True)
    TotalEmojiReactions = models.IntegerField(default=0)
    emoji_reactions = models.TextField(blank=True, null=True)
    replies = models.TextField()
    repliers = models.TextField(blank=True, null=True)
    TotalReplies = models.IntegerField(default=0)
    post_links = models.TextField(blank=True, null=True)
    link_clicks = models.TextField(blank=True, null=True)
    Links = models.TextField(blank=True, null=True)
    Images = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    post_identifier = models.CharField(max_length=64, blank=True, null=True)
    wallet_address = models.CharField(max_length=42, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "Forum Post"

    class Meta:
        db_table = 'ForumPosts'

class TopicSummaries(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(max_length=500)
    views = models.IntegerField(default=0, blank=True, null=True)
    replies = models.IntegerField(default=0, blank=True, null=True)
    LastActivityDate = models.DateField(blank=True, null=True)
    OriginalPoster = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    Category = models.CharField(max_length=255, blank=True, null=True)
    Created = models.DateTimeField(blank=True, null=True)
    wallet_address = models.CharField(max_length=42, blank=True, null=True)
    post_identifier = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "Topic Summary"

    class Meta:
        db_table = 'TopicSummaries'
