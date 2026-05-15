from django.urls import path
from .views import AlunoListView

urlpatterns = [
    path('alunos/', AlunoListView.as_view(), name='listar-alunos'),
]