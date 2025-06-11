from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as root_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', root_views.api_root, name='api-root'),  # Move JSON API info to /api/
    path('search/', root_views.search_results, name='search_results'),  # Dedicated search results page
    path('activity/', root_views.activity_page, name='activity_page'),  # Activity feed page
    path('users/<str:username>/', root_views.user_profile, name='user_profile'),  # User profile page
    path('users/<str:username>/followers/', root_views.followers_page, name='followers_page'),  # Followers page
    path('users/<str:username>/following/', root_views.following_page, name='following_page'),  # Following page
    path('', root_views.frontend, name='frontend'),       # HTML landing page at root
    path('api/accounts/', include('accounts.urls')),
    path('api/music/', include('music.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 