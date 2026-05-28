from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


# Domínios institucionais aceitos pelo sistema
DOMINIOS_PERMITIDOS = [
    "ibmec.edu.br",
]


def validar_email_institucional(value):
    """
    Valida que o email possui formato válido e pertence
    a um domínio institucional autorizado.

    Raises:
        ValidationError: Se o email não for válido ou não pertencer
        a um domínio institucional autorizado.
    """
    # Primeiro valida o formato geral do email
    email_validator = EmailValidator(
        message="Informe um endereço de e-mail válido."
    )
    email_validator(value)

    # Depois valida o domínio institucional
    dominio = value.strip().lower().rsplit("@", 1)[-1]

    if dominio not in DOMINIOS_PERMITIDOS:
        dominios_formatados = ", ".join(
            f"@{d}" for d in DOMINIOS_PERMITIDOS
        )
        raise ValidationError(
            f"Apenas e-mails institucionais são aceitos ({dominios_formatados}).",
            code="dominio_nao_permitido",
        )
