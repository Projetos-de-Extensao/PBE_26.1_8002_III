# Local de armazenamento dos enums do projeto
#                             ass: doutor bazinga (lucas jesus)

from django.db import models

class StatusContrato(models.TextChoices):
    """
    Enumeração que define os estados possíveis de um contrato de estágio no sistema.
    """

    #  nome no BD -v           v- texto que vai aparecer no front (acho????)
    ANALISE = 'analise', 'Em análise'
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado com justificativa'

class TipoUsuario(models.TextChoices):
    """
    Enumeração que define os papéis dos atores do sistema.
    """
    ALUNO = 'aluno', 'Aluno'
    SECRETARIA = 'secretaria', 'Secretaria'
    COORDENACAO = 'coordenacao', 'Coordenação'
    CARREIRAS = 'carreiras', 'Carreiras'