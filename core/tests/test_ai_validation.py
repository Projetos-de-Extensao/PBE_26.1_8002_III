import pytest
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Relatorio, Curso, Area, Coordenador
from core.enums import StatusRelatorio, Veredito
from core.services.AI.lerRelatorio import carregar_ementa_curso, avaliarRelatorio
from core.tasks import avaliarRelatorioComIa

@pytest.mark.django_db
class TestAIValidation:

    def test_carregar_ementa_curso_sucesso(self):
        """Testa que carregar_ementa_curso localiza e lê a ementa de Engenharia de Software."""
        ementa_texto = carregar_ementa_curso("Engenharia de Software")
        assert "Ementa do Curso" in ementa_texto
        assert "Engenharia de Software" in ementa_texto

    def test_carregar_ementa_curso_inexistente_lanca_excecao(self):
        """Testa que carregar_ementa_curso lança FileNotFoundError para curso inexistente."""
        with pytest.raises(FileNotFoundError):
            carregar_ementa_curso("Curso de Pintura Artistica")

    @patch("core.services.AI.lerRelatorio.client.models.generate_content")
    def test_avaliar_relatorio_aprovado(self, mock_generate_content):
        """Testa a avaliação de relatório com veredito APROVADO."""
        mock_response = MagicMock()
        mock_response.text = '{"status": "APROVADO", "justificativa": "As atividades de desenvolvimento backend estão alinhadas com as disciplinas de banco de dados e engenharia de software."}'
        mock_generate_content.return_value = mock_response

        resultado = avaliarRelatorio(
            corpo_relatorio="Fiz banco de dados postgresql e django",
            ementa_curso="Banco de Dados e Programação Web"
        )
        assert resultado["status"] == "APROVADO"
        assert resultado["compativel"] is True
        assert "justificativa" in resultado

    @patch("core.services.AI.lerRelatorio.client.models.generate_content")
    def test_avaliar_relatorio_reprovado(self, mock_generate_content):
        """Testa a avaliação de relatório com veredito REPROVADO."""
        mock_response = MagicMock()
        mock_response.text = '{"status": "REPROVADO", "justificativa": "Atividades de culinária e gastronomia não possuem aderência à ementa do curso."}'
        mock_generate_content.return_value = mock_response

        resultado = avaliarRelatorio(
            corpo_relatorio="Fiz bolo de cenoura e torta de limão",
            ementa_curso="Banco de Dados e Programação Web"
        )
        assert resultado["status"] == "REPROVADO"
        assert resultado["compativel"] is False
        assert "justificativa" in resultado

    @patch("core.services.AI.lerRelatorio.client.models.generate_content")
    @patch("core.services.email_service.EmailNotificationService.notificar_avaliacao")
    def test_task_avaliar_relatorio_com_ia(self, mock_notificar, mock_generate_content, relatorio, coordenador):
        """Testa se a tarefa avaliarRelatorioComIa atualiza corretamente o status do relatório baseado na IA."""
        mock_response = MagicMock()
        mock_response.text = '{"status": "APROVADO", "justificativa": "Atividades perfeitamente aderentes."}'
        mock_generate_content.return_value = mock_response

        # Garantir que o curso associado tem o nome correto
        aluno = relatorio.processo_id.aluno
        curso = aluno.curso
        curso.nome = "Engenharia de Software"
        curso.save()

        # Executa a tarefa diretamente
        avaliarRelatorioComIa(relatorio.id)

        relatorio.refresh_from_db()
        assert relatorio.status == StatusRelatorio.APROVADO
        mock_notificar.assert_called_once()
