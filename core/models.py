from django.db.models import ProtectedError
from core.enums import StatusRelatorio
from django.template.defaultfilters import default
from core.services.upload_contrato import upload_contrato_path
from core.services.validacao_arquivos import validar_pdf_e_tamanho_seguro
from django.utils import choices, timezone
from core.enums import StatusProcesso
from django.db.models import CASCADE
from django.db.models import ForeignKey
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from .enums import *
from core.services.upload_relatorio import upload_relatorio_path
from .validators import validar_email_institucional, validar_cpf

class Usuario(models.Model):
    """
    Entidade base abstrata para todos os tipos de usuários.
    Centraliza os campos de autenticação e informações gerais, garantindo que
    as subclasses (Aluno, Coordenador, Secretaria) compartilhem a mesma estrutura base.
    """
    matricula = models.CharField(max_length=30, unique=True, db_index=True, verbose_name="Matrícula")    
    nome = models.CharField(max_length=255, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail", validators=[validar_email_institucional])
    senha = models.CharField(max_length=255, verbose_name="Senha")
    unidade = models.CharField(max_length=15, choices=Unidade)
    precisa_redefinir_senha = models.BooleanField(default=True, verbose_name="Precisa redefinir senha?")
    aceite_lgpd = models.BooleanField(default=False, verbose_name="Aceite dos Termos de Uso e LGPD")

    class Meta:
        abstract = True 

class Aluno(Usuario):
    """
    Representa o estudante que participa de processos de estágio.
    A grade horária do aluno (ManyToMany com Horarios) é crucial para a regra de negócio
    que impede a assinatura de contratos cujas atividades conflitem com o horário de aulas.
    """
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF", validators=[validar_cpf])
    is_ativo = models.BooleanField(default=True, verbose_name="Status Ativo")
    periodo = models.IntegerField(choices=Periodo, default=Periodo.PRIMEIRO)
    curso = models.ForeignKey("Curso", on_delete=models.CASCADE)
    unidade = models.CharField(max_length=15, choices=Unidade)
    grade = models.ManyToManyField('Horarios',db_table='grade_horaria')
    is_pcd = models.BooleanField(default=False, verbose_name="PCD")

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['id']

    def __str__(self):
        return f"{self.nome} - {self.matricula}"

class Area(models.Model):
    nome = models.CharField(max_length=20, verbose_name="Nome")
    coordenador = models.OneToOneField('Coordenador', on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self):
        return self.nome

class Coordenador(Usuario):
    class Meta:
        verbose_name = "Coordenador"
        verbose_name_plural = "Coordenadores"

    def __str__(self):
        return self.nome

class Secretaria(Usuario):
    class Meta:
        verbose_name = "Secretária"
        verbose_name_plural = "Secretárias"

    def __str__(self):
        return self.nome

class Curso(models.Model):
    nome = models.CharField(max_length=40, verbose_name="Nome")
    areaId = models.ForeignKey(Area, on_delete=models.CASCADE)
    ementa_md = models.FileField(upload_to="ementas/", verbose_name="Ementa do Curso (MD)", null=True, blank=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
    
    def __str__(self):
        return self.nome

class Processo(models.Model):
    """
    Agrupador lógico de um estágio. Um Processo vincula um Aluno à empresa,
    e atua como "pasta" que conterá todos os Documentos do estágio (Contrato e Relatórios).
    Regra: Um aluno geralmente não deve possuir múltiplos processos "ABERTOS" simultaneamente.
    """
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da empresa")
    data_criacao = models.DateField(verbose_name="Data de Criação", default=timezone.now)
    status = models.CharField(max_length=20, choices=StatusProcesso, default=StatusProcesso.ABERTO)
    aluno = models.ForeignKey(Aluno, to_field='matricula', related_name="aluno", on_delete=models.CASCADE, max_length=30)
    coordenacao = models.ForeignKey(Coordenador, to_field='matricula', related_name="coordenacao", on_delete=models.PROTECT)
    secretaria = models.ForeignKey(Secretaria, to_field='matricula', related_name="secretaria", on_delete=models.PROTECT)
    criado_por = models.CharField(max_length=100, verbose_name="Criado por", null=True)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ['status']

    @property
    def nome_processo(self):
        return self.nome_empresa + " - " + self.data_criacao.strftime("%d/%m/%Y")
    
    def __str__(self):
        return self.nome_processo

class Contrato(models.Model):
    """
    Termo legal e formal do estágio.
    Regras Críticas:
    1. A duração não pode exceder 24 meses (validado no Serializer), exceto para alunos PCD.
    2. Possui um campo flag 'conflito_grade' preenchido automaticamente por um Signal 
       para alertar os avaliadores se o horário bate com as aulas do aluno.
    """
    arquivo = models.FileField(upload_to=upload_contrato_path, verbose_name="Arquivo", validators=[validar_pdf_e_tamanho_seguro])
    data_upload = models.DateField(verbose_name="Data de Upload", default=timezone.now)
    cnpj_empresa = models.CharField(max_length=14, verbose_name="CNPJ da empresa", null=True, blank=True)
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da empresa", null=True, blank=True)
    data_inicio = models.DateField(verbose_name="Data de Início", null=True, blank=True)   
    data_termino = models.DateField(verbose_name="Data de Término", null=True, blank=True)
    apolice_seguro = models.CharField(max_length=100, verbose_name="Apólice de Seguro", null=True, blank=True)
    plano_atividade = models.BooleanField(default=False, verbose_name="Plano de Atividade", null=True, blank=True)
    horarios_atividade = models.ManyToManyField('Horarios', db_table='horarios_contrato')
    assinatura_aluno = models.BooleanField(default=False, verbose_name="Assinatura do Aluno", null=True, blank=True)
    assinatura_empresa = models.BooleanField(default=False, verbose_name="Assinatura da Empresa", null=True, blank=True)
    assinatura_faculdade = models.BooleanField(default=False, verbose_name="Assinatura da Faculdade", null=True, blank=True)
    processoId = models.ForeignKey(Processo, on_delete=models.CASCADE, verbose_name="Processo")
    status = models.CharField(max_length = 15, choices=StatusContrato, default = StatusContrato.PENDENTE )
    conflito_grade = models.BooleanField(default=False, verbose_name="Conflito de Grade")

    @property
    def nome_contrato(self):
        return f"{self.nome_empresa} {self.id}"

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
    
    def __str__(self):
        return self.nome_contrato

class Relatorio(models.Model):
    processo_id = models.ForeignKey(Processo, on_delete=models.CASCADE)
    arquivo = models.FileField(upload_to=upload_relatorio_path, verbose_name="url do arquivo", null=True, blank=True)
    data_upload = models.DateField(verbose_name="Data de upload", default=timezone.now)
    titulo = models.CharField(max_length=255, verbose_name="Título", null=True, blank=True)
    corpo = models.TextField(verbose_name="Corpo", null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusRelatorio, default=StatusRelatorio.AGUARDANDO_VALIDACAO)
    fora_do_prazo = models.BooleanField(default=False, verbose_name="Fora do Prazo")

class HistoricoAvaliacao(models.Model):
    observacoes = models.TextField(verbose_name="Observações")
    data_avaliacao = models.DateTimeField(verbose_name="Data de avaliação",default=timezone.now)
    veredito = models.CharField(max_length=20,choices=Veredito,verbose_name="Veredito")

    class Meta:
        abstract = True
        
class HistoricoAvaliacaoRelatorio(HistoricoAvaliacao):
    """
    Auditoria inalterável da decisão do Coordenador sobre um relatório.
    Caso seja reprovado, a justificativa é obrigatória para informar o aluno.
    """
    avaliador = models.ForeignKey(Coordenador, on_delete=models.PROTECT)
    relatorio_id = models.OneToOneField(Relatorio, on_delete=models.CASCADE)
    justificativa = models.CharField(max_length=200, verbose_name="Justificativa", blank=True, default="")

    def delete(self, *args, **kwargs):
        raise ProtectedError("Histórico de Justificativas não pode ser alterado ou deletado.")

class HistoricoAvaliacaoContrato(HistoricoAvaliacao):
    """
    Auditoria inalterável da avaliação de contratos pela Secretaria.
    Semelhante ao Relatório, impede exclusões para manter histórico legal das decisões.
    """
    avaliador = models.ForeignKey(Secretaria, on_delete=models.PROTECT)
    contrato_id = models.OneToOneField(Contrato, on_delete=models.CASCADE)
    justificativa = models.CharField(max_length=200,verbose_name="Justificativa", blank=True, default="")

    def delete(self, *args, **kwargs):
        raise ProtectedError("Histórico de Justificativas não pode ser alterado ou deletado.")

class Horarios(models.Model):
    turno = models.CharField(max_length=12, choices=Turno)
    dia = models.CharField(max_length=20, choices=DiasDaSemana)

    class Meta:
        verbose_name = "Grade Horária"
        verbose_name_plural = "Grades Horárias"
    
    def __str__(self):
        return f"{self.aluno} - {self.dia} - {self.periodo}"


# Sinais para regras de negócio automatizadas
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed, sender=Contrato.horarios_atividade.through)
def verificar_conflito_grade(sender, instance, action, **kwargs):
    """
    Signal disparado sempre que os horários de um contrato são alterados.
    Se cruzar com a grade de estudos do aluno atrelado, sinaliza `conflito_grade=True`.
    Isso exime o backend de fazer validações custosas nas views de inserção.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        aluno = instance.processoId.aluno
        horarios_contrato = instance.horarios_atividade.all()
        grade_aluno = aluno.grade.all()
        
        conflito = False
        for horario in horarios_contrato:
            if horario in grade_aluno:
                conflito = True
                break
        
        if instance.conflito_grade != conflito:
            instance.conflito_grade = conflito
            Contrato.objects.filter(id=instance.id).update(conflito_grade=conflito)


class FeatureFlagManager(models.Manager):
    """
    Manager customizado para o model FeatureFlag.
    """
    def is_active(self, flag_name: str) -> bool:
        """
        Retorna se a feature flag informada está ativa.
        """
        return self.model.is_active(flag_name)


class FeatureFlag(models.Model):
    """
    Representa uma Feature Flag do sistema, gerenciada pelo Django Admin
    e cacheada no Redis para alta performance.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message="O nome da feature flag deve conter apenas letras minúsculas, números e sublinhados (underscores)."
            )
        ],
        help_text="Nome identificador único da feature flag usado no código (ex: 'async_contract_ai')."
    )
    is_enabled = models.BooleanField(default=False, verbose_name="Habilitado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Atualizado por",
        related_name="updated_feature_flags"
    )

    objects = FeatureFlagManager()

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self) -> str:
        return f"{self.name} ({'Ativa' if self.is_enabled else 'Inativa'})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.set(f"feature_flag:{self.name}", self.is_enabled, timeout=None)

    @classmethod
    def is_active(cls, flag_name: str) -> bool:
        """
        Implementação do Cache-Aside:
        1. Tenta ler do Redis (Django Cache).
        2. Se der cache miss, busca no banco de dados.
        3. Se encontrar no banco, salva no cache por 24h e retorna o valor.
        4. Se não encontrar, retorna False.
        """
        from django.core.cache import cache
        cache_key = f"feature_flag:{flag_name}"
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            return bool(cached_val)

        try:
            flag = cls.objects.get(name=flag_name)
            # Salva no Redis (Django Cache) por 24 horas (86400 segundos)
            cache.set(cache_key, flag.is_enabled, timeout=86400)
            return flag.is_enabled
        except cls.DoesNotExist:
            return False


class EmailLog(models.Model):
    """
    Registro de todos os emails enviados pelo sistema.
    Permite auditoria e rastreamento de entregas e falhas.
    """
    destinatario = models.EmailField(verbose_name="Destinatário")
    assunto = models.CharField(max_length=255, verbose_name="Assunto")
    corpo_texto = models.TextField(verbose_name="Corpo (texto)", blank=True, default="")
    corpo_html = models.TextField(verbose_name="Corpo (HTML)", blank=True, default="")
    status = models.CharField(
        max_length=15,
        choices=StatusEmail,
        default=StatusEmail.PENDENTE,
        verbose_name="Status"
    )
    tentativas = models.PositiveIntegerField(default=0, verbose_name="Tentativas")
    erro = models.TextField(verbose_name="Mensagem de Erro", blank=True, default="")
    celery_task_id = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Celery Task ID"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    enviado_em = models.DateTimeField(null=True, blank=True, verbose_name="Enviado em")

    class Meta:
        verbose_name = "Log de Email"
        verbose_name_plural = "Logs de Email"
        ordering = ['-criado_em']

    def __str__(self):
        return f"[{self.status}] {self.assunto} → {self.destinatario}"
