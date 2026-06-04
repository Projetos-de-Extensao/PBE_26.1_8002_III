import pytest
from django.test import override_settings
from django.core import mail

from core.services.email_service import EmailNotificationService


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_notificar_novo_envio_sends_email():
    EmailNotificationService.notificar_novo_envio(
        email_destino='destino@test.com',
        nome_aluno='João Silva',
        nome_documento='Contrato de Estágio'
    )

    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert 'Contrato de Estágio' in sent.subject
    assert 'João Silva' in sent.body
    assert sent.to == ['destino@test.com']


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_notificar_avaliacao_aprovado_and_reprovado():
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
    assert 'Parabéns' in sent.body
    assert sent.to == ['aluno@test.com']

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
    assert 'REPROVADO' in sent.subject.upper() or 'REPROVADO' in sent.body.upper()
    assert 'Motivo: documento incompleto' in sent.body
    assert sent.to == ['aluno2@test.com']
