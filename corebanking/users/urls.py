from django.urls import path
from .views import RegisterView, LoginView, ProfileView, RefreshTokenView, LogoutView
# from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
]
