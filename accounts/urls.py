from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),  # This handles both GET and PUT
    path('users/<str:username>/reviews/', views.user_reviews, name='user-reviews'),
    path('users/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('users/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('users/<str:username>/followers/', views.get_followers, name='get_followers'),
    path('users/<str:username>/following/', views.get_following, name='get_following'),
    path('feed/', views.user_feed, name='user-feed'),
    path('users/search/', views.search_users, name='search-users'),
]