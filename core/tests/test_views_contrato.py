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
        """Avaliação com veredito REPROVADO e justificativa atualiza status do contrato."""
        payload = {
            "observacoes": "Faltam assinaturas.",
            "veredito": Veredito.REPROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
            "justificativa": "Documento não assinado.",
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

        contrato.refresh_from_db()
        assert contrato.status == StatusContrato.REPROVADO

    def test_reprovar_contrato_sem_justificativa(self, api_client, contrato, secretaria):
        """Avaliação com veredito REPROVADO sem justificativa deve falhar (HTTP 400)."""
        payload = {
            "observacoes": "Faltam assinaturas.",
            "veredito": Veredito.REPROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
            "justificativa": "   ", # em branco
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_aprovar_contrato_duracao_superior_24_meses_nao_pcd(self, api_client, contrato, secretaria):
        """Aprovação de contrato com duração superior a 24 meses para aluno não-PCD deve falhar."""
        from datetime import date
        contrato.data_inicio = date(2026, 1, 1)
        contrato.data_termino = date(2028, 1, 2) # 24 meses e 1 dia
        contrato.processoId.aluno.is_pcd = False
        contrato.processoId.aluno.save()
        contrato.save()

        payload = {
            "observacoes": "Aprovando contrato longo.",
            "veredito": Veredito.APROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_aprovar_contrato_duracao_superior_24_meses_pcd(self, api_client, contrato, secretaria):
        """Aprovação de contrato com duração superior a 24 meses para aluno PCD deve passar."""
        from datetime import date
        contrato.data_inicio = date(2026, 1, 1)
        contrato.data_termino = date(2028, 1, 2) # 24 meses e 1 dia
        contrato.processoId.aluno.is_pcd = True
        contrato.processoId.aluno.save()
        contrato.save()

        payload = {
            "observacoes": "Aprovando contrato longo PCD.",
            "veredito": Veredito.APROVADO.value,
            "avaliador": secretaria.id,
            "contrato_id": contrato.id,
        }
        response = api_client.post("/contrato/avaliar/", payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_conflito_grade_sinalizacao(self, api_client, contrato, aluno, horario_segunda_manha):
        """Verifica se a flag conflito_grade é setada ao associar horário conflitante com a grade do aluno."""
        # Configura aluno com a segunda de manhã na grade
        aluno.grade.add(horario_segunda_manha)
        
        # O contrato inicialmente não deve ter conflito
        assert not contrato.conflito_grade
        
        # Associa o mesmo horário ao contrato
        contrato.horarios_atividade.add(horario_segunda_manha)
        
        # Deve detectar o conflito através do sinal m2m_changed
        contrato.refresh_from_db()
        assert contrato.conflito_grade

    def test_avaliar_contrato_sem_dados(self, api_client):
        """Avaliação sem dados obrigatórios retorna 400."""
        response = api_client.post("/contrato/avaliar/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDownloadContrato:
    def test_download_contrato_arquivo_nao_encontrado(self, api_client, contrato):
        """Tentativa de download de um contrato cujo arquivo não existe no disco deve retornar 404."""
        contrato.arquivo.name = "caminho/inexistente.pdf"
        contrato.save()

        response = api_client.get(f"/contrato/{contrato.id}/download/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
