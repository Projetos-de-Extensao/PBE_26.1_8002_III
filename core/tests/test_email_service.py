"""
Testes de integração do EmailNotificationService com Celery em modo eager.

Em modo CELERY_TASK_ALWAYS_EAGER, as tasks executam sincronamente,
permitindo verificar o fluxo completo: Service → Task → EmailLog + email.
"""
import pytest
from django.test import override_settings
from django.core import mail

from core.services.email_service import EmailNotificationService
from core.models import EmailLog
from core.enums import StatusEmail


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
def test_notificar_novo_envio_sends_email():
    """Fluxo completo: Service → Celery task (eager) → email enviado + EmailLog criado."""
    mail.outbox.clear()

    EmailNotificationService.notificar_novo_envio(
        email_destino='destino@test.com',
        nome_aluno='João Silva',
        nome_documento='Contrato de Estágio'
    )

    # Verifica email enviado
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert 'Contrato de Estágio' in sent.subject
    assert sent.to == ['destino@test.com']

    # Verifica EmailLog no banco
    log = EmailLog.objects.last()
    assert log is not None
    assert log.status == StatusEmail.ENVIADO
    assert log.destinatario == 'destino@test.com'
    assert 'João Silva' in log.corpo_html


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
def test_notificar_avaliacao_aprovado_and_reprovado():
    """Fluxo completo de avaliação aprovada e reprovada via Celery eager."""
    # Aprovado
    mail.outbox.clear()
    EmailNotificationService.notificar_avaliacao(
        email_destino='aluno@test.com',
        nome_aluno='Aluno Teste',
        status='APROVADO',
        observacoes=''
    )
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert 'APROVADO' in sent.subject.upper()
    assert sent.to == ['aluno@test.com']

    log = EmailLog.objects.last()
    assert log.status == StatusEmail.ENVIADO

    # Reprovado
    mail.outbox.clear()
    EmailNotificationService.notificar_avaliacao(
        email_destino='aluno2@test.com',
        nome_aluno='Aluno Teste',
        status='REPROVADO',
        observacoes='Motivo: documento incompleto'
    )
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert 'REPROVADO' in sent.subject.upper()
    assert sent.to == ['aluno2@test.com']

    log = EmailLog.objects.filter(destinatario='aluno2@test.com').first()
    assert log.status == StatusEmail.ENVIADO
    assert 'Motivo: documento incompleto' in log.corpo_html
