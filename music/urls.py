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
] 