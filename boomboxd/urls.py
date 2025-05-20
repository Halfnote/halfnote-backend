from django.urls import path
from accounts import views as account_views
from music import views as music_views
from reviews import views as review_views

urlpatterns = [
    # Auth endpoints
    path('api/register/', account_views.register),
    path('api/login/', account_views.login),
    path('api/profile/', account_views.profile),
    
    # Album endpoints
    path('api/albums/search/', music_views.search),
    path('api/albums/import/<int:discogs_id>/', music_views.import_album),
    path('api/albums/<uuid:album_id>/', music_views.album_detail),
    
    # Review endpoints
    path('api/albums/<uuid:album_id>/reviews/', review_views.album_reviews),
    path('api/albums/<uuid:album_id>/review/', review_views.create_review),
    path('api/users/<str:username>/reviews/', review_views.user_reviews),
] 