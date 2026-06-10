"""
Serviço de notificação por email.

Delega o envio real para tasks Celery assíncronas,
garantindo que as views retornem imediatamente sem bloqueio.
"""


class EmailNotificationService:

    @staticmethod
    def notificar_novo_envio(email_destino, nome_aluno, nome_documento):
        """
        Notifica a secretaria/coordenação sobre um novo documento recebido.
        O envio é assíncrono via Celery.

        Args:
            email_destino: Email do destinatário (secretaria/coordenação).
            nome_aluno: Nome do aluno que enviou o documento.
            nome_documento: Tipo do documento (ex: 'Contrato de Estágio').
        """
        from core.email_tasks import enviar_email_novo_envio
        enviar_email_novo_envio.delay(email_destino, nome_aluno, nome_documento)

    @staticmethod
    def notificar_avaliacao(email_destino, nome_aluno, status, observacoes=""):
        """
        Notifica o aluno sobre o resultado da avaliação do processo.
        O envio é assíncrono via Celery.

        Args:
            email_destino: Email do aluno.
            nome_aluno: Nome do aluno.
            status: Veredito da avaliação ('aprovado' ou 'reprovado').
            observacoes: Observações do avaliador (opcional).
        """
        from core.email_tasks import enviar_email_avaliacao
        enviar_email_avaliacao.delay(
            email_destino, nome_aluno, str(status), observacoes
        )
