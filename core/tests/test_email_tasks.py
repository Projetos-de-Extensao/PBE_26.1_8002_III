"""
Testes para as tasks Celery de envio de email e para o EmailNotificationService.
"""
import pytest
from smtplib import SMTPException
from unittest.mock import patch, MagicMock

from core.email_tasks import enviar_email_novo_envio, enviar_email_avaliacao
from core.models import EmailLog
from core.enums import StatusEmail
from core.services.email_service import EmailNotificationService


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def email_destino():
    return "aluno@ibmec.edu.br"


@pytest.fixture
def nome_aluno():
    return "João Santos"


# ── Testes: enviar_email_novo_envio ──────────────────────────────────

@pytest.mark.django_db
class TestEnviarEmailNovoEnvio:

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_envio_bem_sucedido_cria_email_log(self, mock_email_cls, email_destino, nome_aluno):
        """Deve criar um EmailLog com status ENVIADO após envio com sucesso."""
        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        enviar_email_novo_envio(email_destino, nome_aluno, "Contrato de Estágio")

        assert EmailLog.objects.count() == 1
        log = EmailLog.objects.first()
        assert log.destinatario == email_destino
        assert log.status == StatusEmail.ENVIADO
        assert log.tentativas == 1
        assert log.enviado_em is not None
        assert "Novo documento recebido" in log.assunto
        assert log.corpo_html != ""

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_envio_usa_template_html(self, mock_email_cls, email_destino, nome_aluno):
        """Deve renderizar o template HTML e anexar como alternativa."""
        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        enviar_email_novo_envio(email_destino, nome_aluno, "Contrato de Estágio")

        mock_msg.attach_alternative.assert_called_once()
        args = mock_msg.attach_alternative.call_args[0]
        assert "text/html" in args
        assert nome_aluno in args[0]  # Nome do aluno no HTML

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_envio_chama_send(self, mock_email_cls, email_destino, nome_aluno):
        """Deve chamar send() no objeto EmailMultiAlternatives."""
        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        enviar_email_novo_envio(email_destino, nome_aluno, "Relatório de Estágio")

        mock_msg.send.assert_called_once_with(fail_silently=False)

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_falha_smtp_registra_erro_no_log(self, mock_email_cls, email_destino, nome_aluno):
        """Deve registrar erro no EmailLog e re-raise para retry do Celery."""
        mock_msg = MagicMock()
        mock_msg.send.side_effect = SMTPException("Connection refused")
        mock_email_cls.return_value = mock_msg

        with pytest.raises(SMTPException):
            enviar_email_novo_envio(email_destino, nome_aluno, "Contrato de Estágio")

        log = EmailLog.objects.first()
        assert log.status == StatusEmail.FALHOU
        assert "Connection refused" in log.erro
        assert log.tentativas == 1


# ── Testes: enviar_email_avaliacao ───────────────────────────────────

@pytest.mark.django_db
class TestEnviarEmailAvaliacao:

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_avaliacao_aprovada_envia_com_sucesso(self, mock_email_cls, email_destino, nome_aluno):
        """Deve enviar email de aprovação e registrar como ENVIADO."""
        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        enviar_email_avaliacao(email_destino, nome_aluno, "aprovado")

        log = EmailLog.objects.first()
        assert log.status == StatusEmail.ENVIADO
        assert "aprovado" in log.assunto.lower()

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_avaliacao_reprovada_inclui_observacoes(self, mock_email_cls, email_destino, nome_aluno):
        """Deve incluir observações no template quando reprovado."""
        mock_msg = MagicMock()
        mock_email_cls.return_value = mock_msg

        observacoes = "Documento sem assinatura do orientador"
        enviar_email_avaliacao(email_destino, nome_aluno, "reprovado", observacoes)

        log = EmailLog.objects.first()
        assert log.status == StatusEmail.ENVIADO
        assert observacoes in log.corpo_html

    @patch("core.email_tasks.EmailMultiAlternatives")
    def test_falha_conexao_registra_erro(self, mock_email_cls, email_destino, nome_aluno):
        """Deve registrar ConnectionError no log e re-raise."""
        mock_msg = MagicMock()
        mock_msg.send.side_effect = ConnectionError("Host unreachable")
        mock_email_cls.return_value = mock_msg

        with pytest.raises(ConnectionError):
            enviar_email_avaliacao(email_destino, nome_aluno, "aprovado")

        log = EmailLog.objects.first()
        assert log.status == StatusEmail.FALHOU
        assert "Host unreachable" in log.erro


# ── Testes: EmailNotificationService (integração com delay) ──────────

@pytest.mark.django_db
class TestEmailNotificationServiceAsync:

    @patch("core.email_tasks.enviar_email_novo_envio.delay")
    def test_notificar_novo_envio_chama_delay(self, mock_delay):
        """Deve chamar .delay() na task Celery ao notificar novo envio."""
        EmailNotificationService.notificar_novo_envio(
            "secretaria@ibmec.edu.br", "João Santos", "Contrato de Estágio"
        )
        mock_delay.assert_called_once_with(
            "secretaria@ibmec.edu.br", "João Santos", "Contrato de Estágio"
        )

    @patch("core.email_tasks.enviar_email_avaliacao.delay")
    def test_notificar_avaliacao_chama_delay(self, mock_delay):
        """Deve chamar .delay() na task Celery ao notificar avaliação."""
        EmailNotificationService.notificar_avaliacao(
            "aluno@ibmec.edu.br", "João Santos", "aprovado", "Parabéns"
        )
        mock_delay.assert_called_once_with(
            "aluno@ibmec.edu.br", "João Santos", "aprovado", "Parabéns"
        )

    @patch("core.email_tasks.enviar_email_avaliacao.delay")
    def test_notificar_avaliacao_converte_status_para_string(self, mock_delay):
        """Deve converter o status para string antes de chamar delay."""
        from core.enums import Veredito
        EmailNotificationService.notificar_avaliacao(
            "aluno@ibmec.edu.br", "João Santos", Veredito.REPROVADO, ""
        )
        # Verifica que o status foi convertido para string
        call_args = mock_delay.call_args[0]
        assert isinstance(call_args[2], str)


# ── Testes: Modelo EmailLog ──────────────────────────────────────────

@pytest.mark.django_db
class TestEmailLogModel:

    def test_criacao_email_log(self):
        """Deve criar EmailLog com valores padrão corretos."""
        log = EmailLog.objects.create(
            destinatario="test@ibmec.edu.br",
            assunto="Teste",
        )
        assert log.status == StatusEmail.PENDENTE
        assert log.tentativas == 0
        assert log.erro == ""
        assert log.celery_task_id == ""
        assert log.criado_em is not None
        assert log.enviado_em is None

    def test_str_representation(self):
        """Deve retornar representação legível."""
        log = EmailLog.objects.create(
            destinatario="test@ibmec.edu.br",
            assunto="Teste de Email",
            status=StatusEmail.ENVIADO,
        )
        assert "[enviado]" in str(log)
        assert "test@ibmec.edu.br" in str(log)

    def test_ordering_por_data(self):
        """Deve ter ordering definido como '-criado_em'."""
        assert EmailLog._meta.ordering == ['-criado_em']
