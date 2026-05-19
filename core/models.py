
from core.services import upload_contrato_path
from django.utils import choices,timezone
from core.enums import StatusProcesso
from django.db.models import CASCADE
from django.db.models import ForeignKey
from enum import unique
from django.db.models import functions
from django.db import models
from .enums import *
from .services import *


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
    nome = models.CharField(max_length=20, verbose_name="Nome")

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self):
        return self.nome


class Curso(models.Model):
    nome = models.CharField(max_length=20, verbose_name="Nome")
    areaId = models.ForeignKey(Area, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
    
    def __str__(self):
        return self.nome

class Processo(models.Model):
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da empresa")
    data_criacao = models.DateField(verbose_name="Data de Criação",default=timezone.now)
    status = models.CharField(max_length = 15, choices=StatusProcesso, default = StatusProcesso.ABERTO )
    matricula_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    # matricula_coordenacao = models.ForeignKey(Coordenacao, on_delete=models.SET_NULL)
    # matricula_secretaria = models.ForeignKey(Secretaria, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"

    @property
    def nome_processo(self):
        """Cria nome automatico para o processo"""
        return self.nome_empresa + " - " + self.data_criacao.strftime("%d/%m/%Y")
    
    def __str__(self):
        return self.nome_processo



class Contrato(models.Model):
    arquivo = models.FileField(upload_to=upload_contrato_path,verbose_name="url do arquivo")
    data_upload = models.DateField(verbose_name="Data de Upload")
    cnpj_empresa = models.CharField(max_length=14, verbose_name="CNPJ da empresa")
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da empresa")
    data_inicio = models.DateField(verbose_name="Data de Início")   
    data_termino = models.DateField(verbose_name="Data de Término")
    apolice_seguro = models.CharField(max_length=100, verbose_name="Apólice de Seguro")
    plano_atividade = models.BooleanField(default=False, verbose_name="Plano de Atividade")
    assinatura_aluno = models.BooleanField(default=False, verbose_name="Assinatura do Aluno")
    assinatura_empresa = models.BooleanField(default=False, verbose_name="Assinatura da Empresa")
    assinatura_faculdade = models.BooleanField(default=False, verbose_name="Assinatura da Faculdade")
    processoId = models.ForeignKey(Processo, on_delete=models.CASCADE, verbose_name="Processo")

    @property
    def nome_contrato(self):
        """Calcula o nome do contrato automaticamente"""
        return f"{self.nome_empresa} {self.id}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
    
    def __str__(self):
        return self.nome_contrato