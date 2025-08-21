"""
Halfnote Music URL Configuration
URL patterns that match the frontend API expectations
"""

from django.urls import path
from . import views

urlpatterns = [
    # Search and discovery
    path('search/', views.search, name='search'),
    path('genres/', views.genres, name='genres'),
    
    # Albums and reviews
    path('albums/<str:discogs_id>/', views.album_detail, name='album-detail'),
    path('albums/<str:discogs_id>/review/', views.create_review, name='create-review'),
    
    # Review management
    path('reviews/<int:review_id>/', views.review_detail, name='review-detail'),
    path('reviews/<int:review_id>/like/', views.toggle_review_like, name='toggle-review-like'),
    path('reviews/<int:review_id>/likes/', views.review_likes, name='review-likes'),
    path('reviews/<int:review_id>/pin/', views.pin_review, name='pin-review'),
    path('reviews/<int:review_id>/comments/', views.review_comments, name='review-comments'),
    
    # Comments
    path('comments/<int:comment_id>/', views.comment_detail, name='comment-detail'),
    
    # Activity and social
    path('activity/', views.activity_feed, name='activity-feed'),
    path('activity/<int:activity_id>/delete/', views.delete_activity, name='delete-activity'),
    
    # Lists
    path('lists/', views.lists_view, name='lists'),
    path('users/<str:username>/lists/', views.user_lists, name='user-lists'),
]