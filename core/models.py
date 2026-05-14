from django.db import models

class Aluno(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=30, unique=True, verbose_name="Matrícula")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    is_ativo = models.BooleanField(default=True, verbose_name="Status Ativo")

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self): ##
        # Isso define como o aluno vai aparecer no painel da Secretaria (ex: "dr. bazinga - 20236769420")
        return f"{self.nome} - {self.matricula}"


class Area(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Área")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self):
        return self.nome

class Curso(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Curso")
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, related_name='cursos', verbose_name="Área")
    is_ativo = models.BooleanField(default=True, verbose_name="Status Ativo")

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.nome