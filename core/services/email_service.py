from django.core.mail import send_mail
from django.conf import settings 

class EmailNotificationService:

    @staticmethod
    def notificar_novo_envio(email_destino, nome_aluno, nome_documento):
        assunto = f"Ibmec - Novo documento recebido: {nome_documento}"
        mensagem = f"Olá,\n\nO aluno {nome_aluno} enviou um novo documento: {nome_documento}.\n\nPor favor, acesse o painel da Secretaria para revisar o documento e tomar as ações necessárias.\n\nAtenciosamente,\nEquipe Ibmec."

        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            fail_silently=False,
        )

    @staticmethod
    def notificar_avaliacao(email_destino, nome_aluno, status, observacoes=""):
        assunto = f"Ibmec - Atualizacao do seu processo: {status}"

        if status.upper() == "APROVADO":
            mensagem = f"Olá {nome_aluno},\n\nParabéns! Seu processo foi aprovado.\n\nAtenciosamente,\nEquipe Ibmec."
        else:
            mensagem = f"Olá {nome_aluno},\n\nInfelizmente, seu processo foi reprovado.\n\nObservações do avaliador: {observacoes}\n\nAtenciosamente,\nEquipe Ibmec."
        
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            fail_silently=False,
        )
