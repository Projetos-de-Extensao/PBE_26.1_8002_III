from django.urls import path
from . import views
from .views import UploadContrato, AvaliarContratoAPIView, AvaliarRelatorioAPIView, UploadRelatorio, ReprovarContratoAPIView, DownloadContratoAPIView, AtualizarContratoAPIView, AtualizarRelatorioAPIView, HorariosAPIView

urlpatterns = [
    path('aluno/', views.AlunoAPIView.as_view()),
    path('coordenador/me/', views.CoordenadorMeAPIView.as_view(), name='coordenador_me'),
    path('secretaria/me/', views.SecretariaMeAPIView.as_view(), name='secretaria_me'),
    path('processo/', views.ProcessoAPIView.as_view()),
    path('processo/<int:id>/', views.ProcessoDetailAPIView.as_view()),
    path('processo/<int:id>/contrato/', UploadContrato.as_view(), name='upload_contrato'),
    path('processo/<int:id>/contrato/atualizar/', AtualizarContratoAPIView.as_view(), name='atualizar_contrato'),
    path('contrato/avaliar/', AvaliarContratoAPIView.as_view(), name='avaliar_contrato'),
    path('contrato/<int:id>/download/', DownloadContratoAPIView.as_view(), name='download_contrato'),
    path('processo/<int:id>/reprovar/', ReprovarContratoAPIView.as_view(), name='reprovar_contrato'),
    path('processo/<int:id>/relatorio/', UploadRelatorio.as_view(), name='upload_relatorio'),
    path('processo/<int:id>/relatorio/atualizar/', AtualizarRelatorioAPIView.as_view(), name='atualizar_relatorio'),
    path('relatorio/avaliar/', AvaliarRelatorioAPIView.as_view(), name='avaliar_relatorio'),
    path('relatorio/<int:id>/download/', views.DownloadRelatorioAPIView.as_view(), name='download_relatorio'),
    path('horarios/', HorariosAPIView.as_view(), name='listar_horarios'),
]