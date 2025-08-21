"""
Halfnote Accounts URL Configuration
Simplified URL patterns for authentication and user management
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    
    # User profiles and social features
    path('users/<str:username>/', views.user_profile, name='user-profile'),
    path('users/<str:username>/reviews/', views.user_reviews, name='user-reviews'),
    path('users/<str:username>/follow/', views.follow_user, name='follow-user'),
    path('users/<str:username>/followers/', views.user_followers, name='user-followers'),
    path('users/<str:username>/following/', views.user_following, name='user-following'),
]