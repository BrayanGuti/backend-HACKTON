from django.urls import path
from . import views

urlpatterns = [
    path('oauth/init/', views.gmail_auth_init, name='gmail_auth_init'),
    path('oauth/callback', views.gmail_auth_callback, name='gmail_auth_callback'),
    path('auth-url/', views.auth_url, name='auth_url'),
]

