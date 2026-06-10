# Local de armazenamento dos enums do projeto
#                             ass: doutor bazinga (lucas jesus)

from django.db import models
import datetime


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
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    REPROVADO ='reprovado','Reprovado'
    CONCLUIDO = 'concluido','Concluido'
    CANCELADO ='cancelado','Cancelado'


class StatusContrato(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANALISE_SECRETARIA = 'analise_sec', 'Análise Secretaria'
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado'

class StatusRelatorio(models.TextChoices):
    AGUARDANDO_VALIDACAO = 'aguardando_validacao', 'Aguardando Validação'
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


class DiasDaSemana(models.TextChoices):
    SEGUNDA = 'segunda', 'Segunda-Feira'
    TERCA = 'terca', 'Terça-Feira'
    QUARTA = 'quarta', 'Quarta-Feira'
    QUINTA = 'quinta', 'Quinta-Feira'
    SEXTA = 'sexta', 'Sexta-Feira'
    SABADO = 'sabado', 'Sábado'

class Turno(models.TextChoices):
    MANHA = 'manha','Manhã'
    TARDE = 'tarde','Tarde'
    NOITE = 'noite','Noite'

    @property
    def inicio(self) -> datetime.time:
        horarios = {
            Turno.MANHA:datetime.time(7,30),
            Turno.TARDE:datetime.time(13,30),
            Turno.NOITE:datetime.time(18,30)
        }
        return horarios[self]

    @property
    def fim(self) -> datetime.time:
        horarios = {
            Turno.MANHA:datetime.time(11,40),
            Turno.TARDE:datetime.time(17,40),
            Turno.NOITE:datetime.time(22,30)
        }
        return horarios[self]


