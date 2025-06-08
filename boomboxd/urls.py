from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as root_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', root_views.api_root, name='api-root'),  # Move JSON API info to /api/
    path('', root_views.frontend, name='frontend'),       # HTML landing page at root
    path('api/accounts/', include('accounts.urls')),
    path('api/music/', include('music.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 