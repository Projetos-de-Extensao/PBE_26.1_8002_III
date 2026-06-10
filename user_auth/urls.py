from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginAPIView, PrimeiroAcessoAPIView, LogoutAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("primeiro-acesso/", PrimeiroAcessoAPIView.as_view(), name="primeiro-acesso"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]