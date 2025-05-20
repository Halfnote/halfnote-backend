from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from music import views as music_views
from reviews import views as review_views
from . import views as root_views

urlpatterns = [
    # Root endpoint
    path('', root_views.api_root, name='api-root'),
    
    # Auth endpoints
    path('api/register/', account_views.register, name='register'),
    path('api/login/', account_views.login, name='login'),
    path('api/profile/', account_views.profile, name='profile'),
    
    # Album endpoints
    path('api/albums/search/', music_views.search, name='album-search'),
    path('api/albums/import/<int:discogs_id>/', music_views.import_album, name='album-import'),
    path('api/albums/<uuid:album_id>/', music_views.album_detail, name='album-detail'),
    
    # Review endpoints
    path('api/albums/<uuid:album_id>/reviews/', review_views.album_reviews, name='album-reviews'),
    path('api/albums/<uuid:album_id>/review/', review_views.create_review, name='create-review'),
    path('api/users/<str:username>/reviews/', review_views.user_reviews, name='user-reviews'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 