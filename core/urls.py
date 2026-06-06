from .views import DownloadDocumentoAPIView

from django.urls import path
from . import views
from .views import UploadContrato, AvaliarContratoAPIView, AvaliarRelatorioAPIView, UploadRelatorio

urlpatterns = [
    path('documentos/<int:id>/download/', DownloadDocumentoAPIView.as_view(), name='documento-download'),
    path('aluno/', views.AlunoAPIView.as_view()),
    path('processo/', views.ProcessoAPIView.as_view()),
    path('processo/<int:id>/', views.ProcessoDetailAPIView.as_view()),
    path('processo/<int:id>/contrato/', UploadContrato.as_view(), name='upload_contrato'),
    path('contrato/avaliar/', AvaliarContratoAPIView.as_view(), name='avaliar_contrato'),
    path('processo/<int:id>/relatorio/', UploadRelatorio.as_view(), name='upload_relatorio'),
    path('relatorio/avaliar/', AvaliarRelatorioAPIView.as_view(), name='avaliar_relatorio'),
]