from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from music.views import AlbumViewSet, SingleViewSet
from reviews.views import ReviewViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import RegisterView, LoginView, UserProfileViewSet, RefreshTokenView, LogoutView
from .views import health_check
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'singles', SingleViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('health/', health_check, name='health_check'),
    path('api/docs/', include_docs_urls(title='Boomboxd API')),
] 