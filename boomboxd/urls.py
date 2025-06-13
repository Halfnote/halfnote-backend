from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views as root_views
import os

urlpatterns = [
    # Admin and API routes first
    path('admin/', admin.site.urls),
    path('api/', root_views.api_root, name='api-root'),
    path('api/accounts/', include('accounts.urls')),
    path('api/music/', include('music.urls')),
    
    # Legacy Django template routes (for comparison/testing)
    path('legacy/', root_views.legacy_frontend, name='legacy-frontend'),
    path('legacy/search/', root_views.search_results, name='legacy-search_results'),
    path('legacy/activity/', root_views.activity_page, name='legacy-activity_page'),
    path('legacy/users/<str:username>/', root_views.user_profile, name='legacy-user_profile'),
    path('legacy/users/<str:username>/followers/', root_views.followers_page, name='legacy-followers_page'),
    path('legacy/users/<str:username>/following/', root_views.following_page, name='legacy-following_page'),
    path('legacy/review/<int:review_id>/', root_views.review_detail, name='legacy-review_detail'),
    
    # Static files serving
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'staticfiles')}),
    
    # React frontend routes (catch-all for SPA)
    re_path(r'^(?!api|admin|legacy|static|media).*$', root_views.frontend, name='react-frontend'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 