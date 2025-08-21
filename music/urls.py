"""
Halfnote Music URL Configuration
Simplified URL patterns for music discovery and reviews
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
    path('reviews/<int:review_id>/', views.review_detail, name='review-detail'),
    path('reviews/<int:review_id>/like/', views.toggle_review_like, name='toggle-review-like'),
    path('reviews/<int:review_id>/comments/', views.review_comments, name='review-comments'),
    
    # Activity and social
    path('activity/', views.activity_feed, name='activity-feed'),
    
    # Lists
    path('lists/', views.lists_view, name='lists'),
    path('users/<str:username>/lists/', views.user_lists, name='user-lists'),
]