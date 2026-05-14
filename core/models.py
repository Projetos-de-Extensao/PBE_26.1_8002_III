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


class Contrato(models.Model):
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_termino = models.DateField(verbose_name="Data de Término")
    cnpj_empresa = models.CharField(max_length=18, verbose_name="CNPJ da Empresa")
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    apolice_seguro = models.CharField(max_length=255, verbose_name="Apólice de Seguro")
    plano_atividade = models.TextField(verbose_name="Plano de Atividades")
    
    # Assinaturas como booleanos (Verdadeiro/Falso)
    assinatura_aluno = models.BooleanField(default=False, verbose_name="Assinatura do Aluno")
    assinatura_empresa = models.BooleanField(default=False, verbose_name="Assinatura da Empresa")
    assinatura_faculdade = models.BooleanField(default=False, verbose_name="Assinatura da Faculdade")
    
    arquivo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL do Arquivo")
    versao = models.IntegerField(default=1, verbose_name="Versão")

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"Contrato {self.nome_empresa} - Versão {self.versao}"