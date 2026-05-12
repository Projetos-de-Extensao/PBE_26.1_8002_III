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
