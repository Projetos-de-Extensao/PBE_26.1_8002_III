from django.urls import path, include
from . import views

urlpatterns = [
    path('aluno/', views.AlunoAPIView.as_view()),
    path('processo/', views.ProcessoAPIView.as_view())
]

