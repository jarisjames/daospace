# app/urls.py

from django.urls import path, re_path
from . import views
from .views import verify_signature, simple_view, search_view, daos_view, dao_detail_view, dao_forum_view, forum_topic_detail, dao_members_view, member_detail, profile_view, link_forum_data, custom_view_dispatcher

urlpatterns = [
    path('', simple_view, name='home'),  # Changed name to 'home' for clarity
    path('login/', views.login_view, name='login'),
    path('search/', search_view, name='search'),
    path('daos/', daos_view, name='daos'),  # New URL pattern for the DAOs page
    path('verify_signature/', verify_signature, name='verify_signature'),
    path('<str:account>/link_forum_data/', link_forum_data, name='link_forum_data'),  # Adjusted pattern for linking forum data
    re_path(r'^(?P<identifier>0x[a-fA-F0-9]{40}|[^/]+)/$', custom_view_dispatcher, name='custom_dispatcher'),  # Custom dispatcher
    path('<str:dao_name>/', dao_detail_view, name='dao_detail'),  # URL with dynamic DAO Profiles
    path('<str:dao_name>/forum/', dao_forum_view, name='dao_forum'),
    path('forum-topic/<int:link_id>/posts/', forum_topic_detail, name='forum_topic_detail'),  # Updated pattern using ID
    path('<str:dao_name>/members/', dao_members_view, name='dao_members'),
    path('<str:dao_name>/members/<str:member_name>/', member_detail, name='member_detail'),
]
