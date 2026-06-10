from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import re


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

def validar_cpf(value):
    """
    Valida um CPF utilizando o algoritmo da Receita Federal.
    """
    # Remove qualquer caractere que não seja número (pontos, traços)
    cpf = re.sub(r'[^0-9]', '', str(value))
    
    if len(cpf) != 11:
        raise ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.", code='cpf_invalido_tamanho')
        
    # Rejeita CPFs com todos os números iguais (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.", code='cpf_invalido_sequencia')
        
    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        raise ValidationError("CPF inválido.", code='cpf_invalido_digito')
        
    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        raise ValidationError("CPF inválido.", code='cpf_invalido_digito')





