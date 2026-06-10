"""
Testes para Upload e Avaliação de Contratos.

Cobre os cenários:
- Upload de contrato válido (PDF)
- Upload de arquivo inválido (não-PDF)
- Avaliação: aprovação de contrato
- Avaliação: reprovação de contrato
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from core.models import Contrato, HistoricoAvaliacaoContrato
from core.enums import StatusContrato, Veredito


# ── Helpers ──────────────────────────────────────────────────────────

def _make_pdf_bytes():
    """Retorna bytes com magic bytes de PDF válido."""
    return b"%PDF-1.4 fake content for test"


def _make_non_pdf_bytes():
    """Retorna bytes que NÃO são PDF."""
    return b"this is not a pdf file at all"


# ── Upload de Contrato ───────────────────────────────────────────────

@pytest.mark.django_db
class TestUploadContrato:

    def test_upload_contrato_valido(self, api_client, processo):
        """Upload de PDF válido retorna 201."""
        arquivo = SimpleUploadedFile(
            "contrato.pdf",
            _make_pdf_bytes(),
            content_type="application/pdf"
        )
        response = api_client.post(
            f"/processo/{processo.id}/contrato/",
            {"arquivo": arquivo},
            format="multipart"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Contrato.objects.filter(processoId=processo).exists()

    def test_upload_contrato_sem_arquivo(self, api_client, processo):
        """Upload sem arquivo retorna 400."""
        response = api_client.post(
            f"/processo/{processo.id}/contrato/",
            {},
            format="multipart"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_contrato_processo_inexistente(self, api_client):
        """Upload para processo inexistente retorna 404."""
        arquivo = SimpleUploadedFile(
            "contrato.pdf",
            _make_pdf_bytes(),
            content_type="application/pdf"
        )
        response = api_client.post(
            "/processo/99999/contrato/",
            {"arquivo": arquivo},
            format="multipart"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ── Avaliação de Contrato ────────────────────────────────────────────

@pytest.mark.django_db
class TestAvaliarContrato:

    def test_aprovar_contrato(self, api_client, contrato, secretaria):
        """Avaliação com veredito APROVADO atualiza status do contrato."""
        payload = {
            "observacoes": "Contrato está em conformidade.",
            "veredito": Veredito.APROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

        contrato.refresh_from_db()
        assert contrato.status == StatusContrato.APROVADO

    def test_reprovar_contrato(self, api_client, contrato, secretaria):
        """Avaliação com veredito REPROVADO atualiza status do contrato."""
        payload = {
            "observacoes": "Faltam assinaturas.",
            "veredito": Veredito.REPROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

        contrato.refresh_from_db()
        assert contrato.status == StatusContrato.REPROVADO

    def test_avaliar_contrato_sem_dados(self, api_client):
        """Avaliação sem dados obrigatórios retorna 400."""
        response = api_client.post("/contrato/avaliar/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
