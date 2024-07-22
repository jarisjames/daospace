from django.contrib import admin
from .models import DAO, ForumLinks, ForumPosts
from django.utils.html import format_html

class ForumPostsAdmin(admin.ModelAdmin):
    list_display = ('PostID', 'title', 'author', 'Role', 'formatted_post_time', 'formatted_replies')

    fields = ('dao_name', 'author', 'Role', 'content', 'post_time', 'total_likes', 
              'likes', 'TotalEmojiReactions', 'emoji_reactions', 'replies', 
              'repliers', 'TotalReplies', 'post_links', 'link_clicks', 
              'Links', 'Images', 'title', 'post_identifier')

    def formatted_post_time(self, obj):
        if obj.post_time:
            return obj.post_time.strftime('%Y-%m-%d %H:%M:%S UTC')
        return None

    def formatted_replies(self, obj):
        if obj.replies:
            # Here you can format the replies as you see fit
            # For example, you can return a truncated version or a nicely formatted HTML
            return format_html("<div>{}</div>", obj.replies[:100] + "..." if len(obj.replies) > 100 else obj.replies)
        return "No Replies"

    formatted_post_time.short_description = 'Post Time'
    formatted_replies.short_description = 'Formatted Replies'

admin.site.register(DAO)
admin.site.register(ForumLinks)
admin.site.register(ForumPosts, ForumPostsAdmin)
