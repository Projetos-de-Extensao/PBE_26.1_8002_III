from django.urls import path, include
from . import views

urlpatterns = [
    path('aluno/', views.aluno),
    path('processo/', views.processo)
]

