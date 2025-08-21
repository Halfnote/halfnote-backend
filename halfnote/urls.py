"""
Halfnote URL Configuration
Clean and simple routing for music review platform
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', views.api_root, name='api-root'),
    path('api/accounts/', include('accounts.urls')),
    path('api/music/', include('music.urls')),
    
    # React Frontend (catch-all for SPA)
    re_path(r'^.*$', views.frontend, name='react-frontend'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)