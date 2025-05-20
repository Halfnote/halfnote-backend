from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from . import views as root_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_views.api_root, name='api-root'),
    
    # Auth endpoints
    path('api/register/', account_views.register, name='register'),
    path('api/login/', account_views.login, name='login'),
    path('api/profile/', account_views.profile, name='profile'),
    
    # Include music URLs
    path('api/', include('music.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 