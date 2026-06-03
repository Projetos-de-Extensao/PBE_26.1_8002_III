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


class StatusProcesso(models.TextChoices):
    ABERTO = 'aberto', 'Aberto'
    PENDENTE = 'pendente', 'Pendente'
    REPROVADO ='reprovado','Reprovado'
    CONCLUIDO = 'concluido','Concluido'
    CANCELADO ='cancelado','Cancelado'


class StatusContrato(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANALISE_SECRETARIA = 'analise_sec', 'Análise Secretaria'
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado'

class StatusRelatorio(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANALISE_COORDENACAO = 'analise_coord', 'Análise Coordenação'
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado'
    

class Unidade(models.TextChoices):
    BARRA = 'barra', 'Barra'
    BOTAFOGO = 'botafogo', 'Botafogo'   

class Periodo(models.IntegerChoices):
    PRIMEIRO = 1, "Primeiro"
    SEGUNDO = 2, "Segundo"
    TERCEIRO = 3, "Terceiro"
    QUARTO = 4, "Quarto"
    QUINTO = 5, "Quinto"
    SEXTO = 6, "Sexto"
    SETIMO = 7, "Setimo"
    OITAVO = 8, "Oitavo"
    NONO = 9, "Nono"
    DECIMO = 10, "Decimo"

class Veredito(models.TextChoices):
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado'
