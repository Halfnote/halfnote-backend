from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),  # This handles both GET and PUT
    path('update-profile/', views.update_profile, name='update-profile'),
    path('favorite-albums/', views.favorite_albums, name='favorite-albums'),
    path('followers/<str:username>/', views.get_followers, name='get-followers'),
    path('following/<str:username>/', views.get_following, name='get-following'),
    path('users/search/', views.search_users, name='users-search'),
    path('users/<str:username>/', views.get_profile, name='get-profile'),
    path('users/<str:username>/reviews/', views.user_reviews, name='user-reviews'),
    path('users/<str:username>/activity/', views.user_activity_feed, name='user-activity-feed'),
    path('users/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('users/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('users/<str:username>/followers/', views.get_followers, name='get_followers'),
    path('users/<str:username>/following/', views.get_following, name='get-following'),
    path('users/<str:username>/genre-stats/', views.user_genre_stats, name='user-genre-stats'),
    path('feed/', views.user_feed, name='user-feed'),
    path('search/', views.search_users, name='search-users'),
    path('debug-cloudinary/', views.debug_cloudinary, name='debug-cloudinary'),
    path('debug-storage/', views.debug_storage, name='debug-storage'),
    path('remove-avatar/', views.remove_avatar, name='remove-avatar'),
    path('debug/<str:username>/', views.debug_profile, name='debug-profile'),
]