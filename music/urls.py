from django.urls import path
from . import views

urlpatterns = [
    # Search endpoint - searches Discogs
    path('search/', views.search, name='album-search'),
    

    
    # Unified album view - handles both database and Discogs preview
    path('albums/<str:discogs_id>/', views.unified_album_view, name='album-detail'),
    
    # Create review endpoint - imports album if needed
    path('albums/<str:discogs_id>/review/', views.create_review, name='create-review'),
    
    # Edit/delete review endpoint
    path('reviews/<int:review_id>/', views.edit_review, name='edit-review'),
    
    # Pin/unpin review endpoint
    path('reviews/<int:review_id>/pin/', views.pin_review, name='pin-review'),
    
    # Like/unlike review endpoint
    path('reviews/<int:review_id>/like/', views.like_review, name='like-review'),
    
    # Get review likes endpoint (with optional pagination and review details)
    path('reviews/<int:review_id>/likes/', views.review_likes, name='review-likes'),
    
    # Activity feed endpoint
    path('activity/', views.activity_feed, name='activity-feed'),
    path('activity/<int:activity_id>/delete/', views.delete_activity, name='delete-activity'),
    
    # Comment endpoints
    path('reviews/<int:review_id>/comments/', views.review_comments, name='review-comments'),
    path('comments/<int:comment_id>/', views.edit_comment, name='edit-comment'),
    
    # Genre endpoints
    path('genres/', views.genre_list, name='genre-list'),
    
    # List endpoints
    path('lists/', views.lists_view, name='lists'),
    path('lists/<int:list_id>/', views.list_detail, name='list-detail'),
    path('lists/<int:list_id>/albums/', views.list_albums, name='list-albums'),
    path('lists/<int:list_id>/like/', views.like_list, name='like-list'),
    path('lists/<int:list_id>/likes/', views.list_likes, name='list-likes'),
    path('users/<str:username>/lists/', views.user_lists, name='user-lists'),
] 