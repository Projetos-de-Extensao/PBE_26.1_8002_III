"""
Testes para Upload e Avaliação de Relatórios.

Cobre os cenários:
- Upload de relatório válido
- Avaliação: aprovação de relatório
- Avaliação: reprovação de relatório
- Fluxo completo: upload → avaliação
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from core.models import Relatorio, HistoricoAvaliacaoRelatorio
from core.enums import StatusRelatorio, StatusContrato, Veredito, StatusProcesso


# ── Upload de Relatório ──────────────────────────────────────────────

@pytest.mark.django_db
class TestUploadRelatorio:

    def test_upload_relatorio_valido(self, api_client, processo, contrato):
        """Upload de relatório com contrato aprovado retorna 201."""
        # Aprovar contrato para que o relatório seja aceito
        contrato.status = StatusContrato.APROVADO
        contrato.save()
        
        processo.status = StatusProcesso.EM_ANDAMENTO
        processo.save()

        arquivo = SimpleUploadedFile(
            "relatorio.pdf",
            b"%PDF-1.4 fake relatorio content",
            content_type="application/pdf"
        )
        response = api_client.post(
            f"/processo/{processo.id}/relatorio/",
            {
                "arquivo": arquivo,
                "titulo": "Meu Relatório Final",
            },
            format="multipart"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Relatorio.objects.filter(processo_id=processo).exists()

    def test_upload_relatorio_processo_inexistente(self, api_client):
        """Upload para processo inexistente retorna 404."""
        arquivo = SimpleUploadedFile(
            "relatorio.pdf",
            b"%PDF-1.4 fake content",
            content_type="application/pdf"
        )
        response = api_client.post(
            "/processo/99999/relatorio/",
            {"arquivo": arquivo},
            format="multipart"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_relatorio_processo_inativo(self, api_client, processo, contrato):
        """Upload de relatório para processo com status inativo (ex: REPROVADO) deve falhar (HTTP 400)."""
        from core.enums import StatusProcesso
        processo.status = StatusProcesso.REPROVADO
        processo.save()

        arquivo = SimpleUploadedFile(
            "relatorio.pdf",
            b"%PDF-1.4 fake relatorio content",
            content_type="application/pdf"
        )
        response = api_client.post(
            f"/processo/{processo.id}/relatorio/",
            {
                "arquivo": arquivo,
                "titulo": "Meu Relatório Final",
            },
            format="multipart"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Avaliação de Relatório ───────────────────────────────────────────

@pytest.mark.django_db
class TestAvaliarRelatorio:

    def test_aprovar_relatorio(self, api_client, relatorio, coordenador):
        """Avaliação com veredito APROVADO atualiza status do relatório."""
        api_client.force_authenticate(user=coordenador)
        payload = {
            "observacoes": "Relatório completo e adequado.",
            "veredito": Veredito.APROVADO.value,
            "avaliador": coordenador.id,
            "relatorio_id": relatorio.id,
        }
        response = api_client.post("/relatorio/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

        relatorio.refresh_from_db()
        assert relatorio.status == StatusRelatorio.APROVADO

    def test_reprovar_relatorio(self, api_client, relatorio, coordenador):
        """Avaliação com veredito REPROVADO atualiza status do relatório."""
        api_client.force_authenticate(user=coordenador)
        payload = {
            "observacoes": "Horas insuficientes.",
            "justificativa": "Falta de requisitos",
            "veredito": Veredito.REPROVADO.value,
            "avaliador": coordenador.id,
            "relatorio_id": relatorio.id,
        }
        response = api_client.post("/relatorio/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

        relatorio.refresh_from_db()
        assert relatorio.status == StatusRelatorio.REPROVADO

    def test_avaliar_relatorio_sem_dados(self, api_client, coordenador):
        """Avaliação sem dados obrigatórios retorna 400."""
        api_client.force_authenticate(user=coordenador)
        response = api_client.post("/relatorio/avaliar/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
