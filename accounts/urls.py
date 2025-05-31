from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('feed/', views.user_feed, name='user-feed'),
    path('users/<str:username>/reviews/', views.user_reviews, name='user-reviews'),
    path('users/<str:username>/follow/', views.follow_user, name='follow-user'),
    path('users/<str:username>/unfollow/', views.unfollow_user, name='unfollow-user'),
    path('users/<str:username>/is-following/', views.check_following, name='check-following'),
    path('users/<str:username>/followers/', views.user_followers, name='user-followers'),
    path('users/<str:username>/following/', views.user_following, name='user-following'),
]