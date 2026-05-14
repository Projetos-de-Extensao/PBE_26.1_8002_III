from django.urls import path
from .views import AlunoCreateView

urlpatterns = [
    path('alunos/', AlunoCreateView.as_view(), name='criar-aluno'),
]