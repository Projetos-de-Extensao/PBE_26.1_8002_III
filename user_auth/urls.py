from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('login/', obtain_auth_token),
    path('primeiro-acesso/', views.PrimeiroAcessoAPIView.as_view(), name='primeiro-acesso'),
]