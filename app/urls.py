# app/urls.py

from django.urls import path, re_path
from . import views
from .views import (
    verify_signature,
    simple_view,
    search_view,
    daos_view,
    dao_detail_view,
    dao_forum_view,
    forum_topic_detail,
    dao_members_view,
    member_detail,
    profile_view,
    link_forum_data,
    custom_view_dispatcher,
    claim_contributor_card,
    dao_feed,  # Ensure dao_feed is imported
)

urlpatterns = [
    path('', simple_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('search/', search_view, name='search'),
    path('daos/', daos_view, name='daos'),
    path('verify_signature/', verify_signature, name='verify_signature'),
    path('claim-1st-edition-contributor-card/', claim_contributor_card, name='claim_contributor_card'),
    path('feed/', dao_feed, name='dao_feed'),  # General feed without dao_name
    path('<str:dao_name>/feed/', dao_feed, name='dao_feed_by_dao'),  # DAO-specific feed
    path('<str:account>/link_forum_data/', link_forum_data, name='link_forum_data'),
    re_path(r'^(?P<identifier>0x[a-fA-F0-9]{40}|[^/]+)/$', custom_view_dispatcher, name='custom_dispatcher'),
    path('<str:dao_name>/forum/', dao_forum_view, name='dao_forum'),
    path('forum-topic/<int:link_id>/posts/', forum_topic_detail, name='forum_topic_detail'),
    path('<str:dao_name>/members/', dao_members_view, name='dao_members'),
    path('<str:dao_name>/members/<str:member_name>/', member_detail, name='member_detail'),
    path('<str:dao_name>/', dao_detail_view, name='dao_detail'),  # Keep this after more specific patterns
]
