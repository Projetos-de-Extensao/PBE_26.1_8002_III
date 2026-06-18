"""
Tasks Celery para envio assíncrono de emails.

Arquitetura de Resiliência:
Cada task registra um EmailLog no banco com status PENDENTE ANTES de chamar o SMTP.
Utilizamos 'acks_late=True' para garantir que, se o Celery worker cair no meio do envio,
a mensagem retorne para a fila do RabbitMQ/Redis e não seja perdida.
O 'autoretry_for' aplica backoff exponencial (30s, 60s, 120s) em caso de falha de rede.
"""
import logging
from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _get_ano_atual():
    """Retorna o ano atual para uso nos templates."""
    return timezone.now().year


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, OSError),
    retry_backoff=30,
    retry_backoff_max=300,
    retry_kwargs={'max_retries': 3},
    acks_late=True,
    name='core.enviar_email_novo_envio',
)
def enviar_email_novo_envio(self, email_destino, nome_aluno, nome_documento):
    """
    Envia notificação de novo documento enviado (para secretaria/coordenação).

    Args:
        email_destino: Email do destinatário.
        nome_aluno: Nome do aluno que enviou o documento.
        nome_documento: Tipo do documento (ex: 'Contrato de Estágio').
    """
    from core.models import EmailLog
    from core.enums import StatusEmail

    assunto = f"Ibmec - Novo documento recebido: {nome_documento}"

    contexto = {
        'nome_aluno': nome_aluno,
        'nome_documento': nome_documento,
        'ano_atual': _get_ano_atual(),
    }

    corpo_html = render_to_string('emails/novo_envio.html', contexto)
    corpo_texto = strip_tags(corpo_html)

    # Cria o log antes de enviar
    email_log = EmailLog.objects.create(
        destinatario=email_destino,
        assunto=assunto,
        corpo_texto=corpo_texto,
        corpo_html=corpo_html,
        status=StatusEmail.PENDENTE,
        celery_task_id=self.request.id or '',
    )

    try:
        email_log.tentativas += 1
        email_log.save(update_fields=['tentativas'])

        msg = EmailMultiAlternatives(
            subject=assunto,
            body=corpo_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        msg.attach_alternative(corpo_html, "text/html")
        msg.send(fail_silently=False)

        email_log.status = StatusEmail.ENVIADO
        email_log.enviado_em = timezone.now()
        email_log.save(update_fields=['status', 'enviado_em'])

        logger.info(
            "Email enviado com sucesso [log_id=%s] para %s — %s",
            email_log.id, email_destino, assunto,
        )

    except (SMTPException, ConnectionError, OSError) as exc:
        email_log.status = StatusEmail.FALHOU
        email_log.erro = str(exc)
        email_log.save(update_fields=['status', 'erro'])

        logger.error(
            "Falha ao enviar email [log_id=%s] para %s — Tentativa %d: %s",
            email_log.id, email_destino, email_log.tentativas, exc,
        )
        raise  # Re-raise para o autoretry do Celery


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, OSError),
    retry_backoff=30,
    retry_backoff_max=300,
    retry_kwargs={'max_retries': 3},
    acks_late=True,
    name='core.enviar_email_avaliacao',
)
def enviar_email_avaliacao(self, email_destino, nome_aluno, status_avaliacao, observacoes=""):
    """
    Envia notificação de resultado de avaliação (para aluno).

    Args:
        email_destino: Email do aluno.
        nome_aluno: Nome do aluno.
        status_avaliacao: Status da avaliação ('aprovado' ou 'reprovado').
        observacoes: Observações do avaliador (opcional).
    """
    from core.models import EmailLog
    from core.enums import StatusEmail

    assunto = f"Ibmec - Atualização do seu processo: {status_avaliacao}"

    contexto = {
        'nome_aluno': nome_aluno,
        'status_avaliacao': str(status_avaliacao).lower(),
        'observacoes': observacoes,
        'ano_atual': _get_ano_atual(),
    }

    corpo_html = render_to_string('emails/avaliacao.html', contexto)
    corpo_texto = strip_tags(corpo_html)

    # Cria o log antes de enviar
    email_log = EmailLog.objects.create(
        destinatario=email_destino,
        assunto=assunto,
        corpo_texto=corpo_texto,
        corpo_html=corpo_html,
        status=StatusEmail.PENDENTE,
        celery_task_id=self.request.id or '',
    )

    try:
        email_log.tentativas += 1
        email_log.save(update_fields=['tentativas'])

        msg = EmailMultiAlternatives(
            subject=assunto,
            body=corpo_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        msg.attach_alternative(corpo_html, "text/html")
        msg.send(fail_silently=False)

        email_log.status = StatusEmail.ENVIADO
        email_log.enviado_em = timezone.now()
        email_log.save(update_fields=['status', 'enviado_em'])

        logger.info(
            "Email enviado com sucesso [log_id=%s] para %s — %s",
            email_log.id, email_destino, assunto,
        )

    except (SMTPException, ConnectionError, OSError) as exc:
        email_log.status = StatusEmail.FALHOU
        email_log.erro = str(exc)
        email_log.save(update_fields=['status', 'erro'])

        logger.error(
            "Falha ao enviar email [log_id=%s] para %s — Tentativa %d: %s",
            email_log.id, email_destino, email_log.tentativas, exc,
        )
        raise  # Re-raise para o autoretry do Celery


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, OSError),
    retry_backoff=30,
    retry_backoff_max=300,
    retry_kwargs={'max_retries': 3},
    acks_late=True,
    name='core.enviar_email_grade_atualizada',
)
def enviar_email_grade_atualizada(self, email_destino, nome_aluno, matricula_aluno, grade_slots):
    """
    Envia notificação de atualização de grade horária (para secretaria).
    """
    from core.models import EmailLog
    from core.enums import StatusEmail

    assunto = f"Ibmec - Grade Horária Atualizada: {nome_aluno}"

    contexto = {
        'nome_aluno': nome_aluno,
        'matricula_aluno': matricula_aluno,
        'grade_slots': grade_slots,
        'ano_atual': _get_ano_atual(),
    }

    corpo_html = render_to_string('emails/grade_atualizada.html', contexto)
    corpo_texto = strip_tags(corpo_html)

    # Cria o log antes de enviar
    email_log = EmailLog.objects.create(
        destinatario=email_destino,
        assunto=assunto,
        corpo_texto=corpo_texto,
        corpo_html=corpo_html,
        status=StatusEmail.PENDENTE,
        celery_task_id=self.request.id or '',
    )

    try:
        email_log.tentativas += 1
        email_log.save(update_fields=['tentativas'])

        msg = EmailMultiAlternatives(
            subject=assunto,
            body=corpo_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        msg.attach_alternative(corpo_html, "text/html")
        msg.send(fail_silently=False)

        email_log.status = StatusEmail.ENVIADO
        email_log.enviado_em = timezone.now()
        email_log.save(update_fields=['status', 'enviado_em'])

        logger.info(
            "Email enviado com sucesso [log_id=%s] para %s — %s",
            email_log.id, email_destino, assunto,
        )

    except (SMTPException, ConnectionError, OSError) as exc:
        email_log.status = StatusEmail.FALHOU
        email_log.erro = str(exc)
        email_log.save(update_fields=['status', 'erro'])

        logger.error(
            "Falha ao enviar email [log_id=%s] para %s — Tentativa %d: %s",
            email_log.id, email_destino, email_log.tentativas, exc,
        )
        raise  # Re-raise para o autoretry do Celery
