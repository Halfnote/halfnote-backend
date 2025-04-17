from django.contrib import admin
from django.urls import path, include
# Temporarily commented out to fix deployment
# from rest_framework.routers import DefaultRouter
# from music.views import AlbumViewSet
# from reviews.views import ReviewViewSet
# from rest_framework_simplejwt.views import TokenRefreshView
# from accounts.views import RegisterView, LoginView, UserProfileViewSet, RefreshTokenView, LogoutView
from .views import health_check

# Temporarily simplified for deployment
# Create a router for our API
# router = DefaultRouter()
# router.register(r'albums', AlbumViewSet)
# router.register(r'reviews', ReviewViewSet)
# router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    # path('', include(router.urls)),  # Root URL now shows DRF API root
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls')),
    # path('api/auth/register/', RegisterView.as_view(), name='register'),
    # path('api/auth/login/', LoginView.as_view(), name='login'),
    # path('api/auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    # path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('health/', health_check, name='health_check'),
    path('', health_check, name='root'),  # Add root path to health check
] 