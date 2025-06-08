from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/<str:username>/', views.get_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('feed/', views.user_feed, name='user-feed'),
    path('users/<str:username>/reviews/', views.user_reviews, name='user-reviews'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('followers/<str:username>/', views.get_followers, name='get_followers'),
    path('following/<str:username>/', views.get_following, name='get_following'),
]