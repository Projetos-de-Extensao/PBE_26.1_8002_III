from django.db import models

class Aluno(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=30, unique=True, verbose_name="Matrícula")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    is_ativo = models.BooleanField(default=True, verbose_name="Status Ativo")ß

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self): ##
        # Isso define como o aluno vai aparecer no painel da Secretaria (ex: "dr. bazinga - 20236769420")
        return f"{self.nome} - {self.matricula}"


class StatusProcesso(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANALISE = 'em_analise', 'Em Análise'
    APROVADO = 'aprovado', 'Aprovado'
    REPROVADO = 'reprovado', 'Reprovado'

class Processo(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='processos', verbose_name="Aluno")
    status = models.CharField(max_length=20, choices=StatusProcesso.choices, default=StatusProcesso.PENDENTE, verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"

    def __str__(self):
        return f"Processo {self.id} - {self.aluno.nome} ({self.get_status_display()})"