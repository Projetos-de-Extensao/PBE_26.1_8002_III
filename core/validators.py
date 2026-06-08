from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from datetime import date
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



def valida_periodo_relatorio(relatorio, contrato):
        data_inicio_prevista = contrato.data_inicio
        data_termino_prevista = contrato.data_termino
        
        data_inicio_relatorio = relatorio.data_inicio
        data_termino_relatorio = relatorio.data_termino

        if data_inicio_prevista is None or data_termino_prevista is None:
            return False
        if data_inicio_relatorio is None or data_termino_relatorio is None:
            return False
        
        comecou_antes = data_inicio_relatorio < data_inicio_prevista
        terminou_depois = data_termino_relatorio > data_termino_prevista
      
        

        if comecou_antes or terminou_depois:
            return False
        else:
            return True


def valida_carga_horaria(contrato):
        horas_diarias = contrato.horas_diarias
        horas_semanais = contrato.horas_semanais

        if horas_diarias is None or horas_semanais is None:
            return True

        if horas_diarias > 6 or horas_semanais > 30:
            return False
        
        return True


def valida_limite_formatura(contrato, aluno):
        data_termino = contrato.data_termino
        data_previsao_formatura = aluno.data_previsao_formatura

        if data_termino is None or data_previsao_formatura is None:
            return True

        if data_termino > data_previsao_formatura:
            return False
        
        return True


def valida_retroatividade(contrato):
        data_inicio = contrato.data_inicio

        if data_inicio is None:
            return True

        diferenca = (date.today() - data_inicio).days

        if diferenca > 30:
            return False
        
        return True
