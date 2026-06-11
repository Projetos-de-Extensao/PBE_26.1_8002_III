from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from .enums import *
from .validators import validar_email_institucional
from .enums import StatusProcesso
from .services.ler_extrair_infos_pdf import ler_pdf_modo_layout

from datetime import datetime
from django.shortcuts import get_object_or_404


import os

class NestedContratoSerializer(serializers.ModelSerializer):
    observacoes = serializers.SerializerMethodField()
    nome_arquivo = serializers.SerializerMethodField()
    data_envio = serializers.SerializerMethodField()

    class Meta:
        model = Contrato
        fields = [
            'id', 'nome_empresa', 'data_upload', 'status', 'conflito_grade', 
            'arquivo', 'observacoes', 'nome_arquivo', 'data_envio', 
            'data_inicio', 'apolice_seguro'
        ]

    def get_observacoes(self, obj):
        if hasattr(obj, 'historicoavaliacaocontrato'):
            return obj.historicoavaliacaocontrato.observacoes or obj.historicoavaliacaocontrato.justificativa
        return None

    def get_nome_arquivo(self, obj):
        if obj.arquivo:
            return os.path.basename(obj.arquivo.name)
        return ""

    def get_data_envio(self, obj):
        if obj.data_upload:
            return obj.data_upload.strftime("%Y-%m-%d")
        return ""

class NestedRelatorioSerializer(serializers.ModelSerializer):
    nome_arquivo = serializers.SerializerMethodField()
    data_envio = serializers.SerializerMethodField()
    atraso = serializers.SerializerMethodField()

    class Meta:
        model = Relatorio
        fields = ['id', 'titulo', 'corpo', 'data_upload', 'status', 'arquivo', 'nome_arquivo', 'data_envio', 'atraso']

    def get_nome_arquivo(self, obj):
        if obj.arquivo:
            return os.path.basename(obj.arquivo.name)
        return ""

    def get_data_envio(self, obj):
        if obj.data_upload:
            return obj.data_upload.strftime("%Y-%m-%d")
        return ""

    def get_atraso(self, obj):
        return obj.fora_do_prazo

class NestedProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ["id", "nome_empresa", "status"]

class NestedAlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ["nome", "matricula"]

class NestedCoordenacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = ["nome", "matricula", "area", "unidade"]

class NestedSecretariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secretaria
        fields = ["nome", "matricula", "unidade"]

class AlunoSerializer(serializers.ModelSerializer):
    """
    Serializer responsável pela leitura e escrita de dados de Alunos.
    Transforma senhas em hash (make_password) e garante que o campo 'senha'
    nunca seja retornado nas respostas (write_only=True).
    Sincroniza automaticamente a criação/edição do Aluno com o model `User` nativo do Django
    para manter a compatibilidade com a autenticação JWT.
    """
    senha = serializers.CharField(write_only=True, required=False)
    processos = NestedProcessoSerializer(source="aluno", many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade', 'periodo', 'curso', 'processos', 'aceite_lgpd']
        read_only_fields = ['id']
        extra_kwargs = {
            'senha': {'write_only': True},
            # UC-04: Mensagem customizada para unicidade
            'matricula': {'error_messages': {'unique': "A matrícula ou CPF informados já estão em uso por outro aluno."}},
            'cpf': {'error_messages': {'unique': "A matrícula ou CPF informados já estão em uso por outro aluno."}}
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'cpf' in data and data['cpf']:
            cpf_original = data['cpf']
            if len(cpf_original) >= 11:
                data['cpf'] = f"***.***.{cpf_original[-5:]}"
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('senha'))
        validated_data['nome'] = validated_data['nome'].title().strip()
        aluno = Aluno.objects.create(**validated_data)
        return aluno

    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            validated_data['password'] = make_password(validated_data.pop('senha'))
        if 'nome' in validated_data:
            validated_data['nome'] = validated_data['nome'].lower().capitalize().strip()

        instance.nome = validated_data.get("nome", instance.nome)
        instance.email = validated_data.get("email", instance.email)
        instance.matricula = validated_data.get("matricula", instance.matricula)
        if 'password' in validated_data:
            instance.password = validated_data['password']
        instance.cpf = validated_data.get("cpf", instance.cpf)
        instance.is_ativo = validated_data.get("is_ativo", instance.is_ativo)
        instance.unidade = validated_data.get("unidade", instance.unidade)
        instance.aceite_lgpd = validated_data.get("aceite_lgpd", instance.aceite_lgpd)
        instance.save()

        return instance

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome"]
        read_only_fields = ["id"]

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["nome"]
        read_only_fields = ["id"]

class ProcessoSerializer(serializers.ModelSerializer):
    matricula_aluno = serializers.SlugRelatedField(slug_field='matricula', queryset=Aluno.objects.all(), source='aluno', required=False)
    matricula_secretaria = serializers.SlugRelatedField(slug_field='matricula', queryset=Secretaria.objects.all(), source='secretaria', required=False)
    matricula_coordenacao = serializers.SlugRelatedField(slug_field='matricula', queryset=Coordenador.objects.all(), source='coordenacao', required=False)

    aluno_id = serializers.CharField(source='aluno.id', read_only=True)
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    matricula = serializers.CharField(source='aluno.matricula', read_only=True)
    curso = serializers.CharField(source='aluno.curso.nome', read_only=True)
    empresa = serializers.CharField(source='nome_empresa', read_only=True)
    criado_em = serializers.SerializerMethodField()
    contrato = serializers.SerializerMethodField()
    relatorios = NestedRelatorioSerializer(source='relatorio_set', many=True, read_only=True)
    historico = serializers.SerializerMethodField()

    class Meta:
        model = Processo
        fields = [
            "id", "nome_empresa", "empresa", "status", "matricula_aluno", 
            "matricula_secretaria", "matricula_coordenacao", "aluno_id", 
            "aluno_nome", "matricula", "curso", "criado_em", "contrato", 
            "relatorios", "historico"
        ]
        read_only_fields = ["id", "criado_em"]

    def get_criado_em(self, obj):
        if obj.data_criacao:
            return obj.data_criacao.strftime("%Y-%m-%d")
        return ""

    def get_contrato(self, obj):
        c = obj.contrato_set.last()
        if c:
            return NestedContratoSerializer(c).data
        return None

    def get_historico(self, obj):
        eventos = []
        if obj.data_criacao:
            eventos.append({"data": obj.data_criacao.strftime("%Y-%m-%d"), "evento": "Processo iniciado"})
        
        for c in obj.contrato_set.all():
            if c.data_upload:
                eventos.append({"data": c.data_upload.strftime("%Y-%m-%d"), "evento": "Contrato enviado para análise"})
            if hasattr(c, 'historicoavaliacaocontrato'):
                h = c.historicoavaliacaocontrato
                evento_nome = "Contrato aprovado" if h.veredito == Veredito.APROVADO else f"Contrato reprovado: {h.justificativa or 'sem justificativa'}"
                if h.data_avaliacao:
                    eventos.append({"data": h.data_avaliacao.strftime("%Y-%m-%d"), "evento": evento_nome})

        for r in obj.relatorio_set.all():
            if r.data_upload:
                eventos.append({"data": r.data_upload.strftime("%Y-%m-%d"), "evento": f"Relatório '{r.titulo or 'Sem Título'}' enviado"})
            if hasattr(r, 'historicoavaliacaorelatorio'):
                h = r.historicoavaliacaorelatorio
                evento_nome = f"Relatório avaliado: {h.veredito} — {h.justificativa}" if h.justificativa else f"Relatório avaliado: {h.veredito}"
                if h.data_avaliacao:
                    eventos.append({"data": h.data_avaliacao.strftime("%Y-%m-%d"), "evento": evento_nome})
        
        eventos.sort(key=lambda x: x["data"])
        return eventos

    def validate(self, attrs):
        aluno = attrs.get('aluno') or (self.instance.aluno if self.instance else None)
        status_atual = attrs.get('status') or (self.instance.status if self.instance else None)
        if status_atual == StatusProcesso.ABERTO:
            query = Processo.objects.filter(aluno=aluno, status=StatusProcesso.ABERTO)
            if self.instance:
                query = query.exclude(id=self.instance.id)
            if query.exists():
                raise serializers.ValidationError({"status": "O aluno já tem processos em aberto"})
        return attrs

    def create(self, validated_data):
        return Processo.objects.create(**validated_data)

class ProcessoDetailSerializer(serializers.ModelSerializer):
    aluno = NestedAlunoSerializer(read_only=True)
    secretaria = NestedSecretariaSerializer(read_only=True)
    coordenacao = NestedCoordenacaoSerializer(read_only=True)
    contrato = NestedContratoSerializer(source='contrato_set', many=True, read_only=True)
    relatorio = NestedRelatorioSerializer(source='relatorio_set', many=True, read_only=True)
    historico = serializers.SerializerMethodField()

    class Meta:
        model = Processo
        fields = ["nome_empresa", "status", "aluno", "secretaria", "coordenacao", "contrato", "relatorio", "historico"]

    def get_historico(self, obj):
        eventos = []
        if obj.data_criacao:
            eventos.append({"data": obj.data_criacao.strftime("%Y-%m-%d"), "evento": "Processo iniciado"})
        
        for c in obj.contrato_set.all():
            if c.data_upload:
                eventos.append({"data": c.data_upload.strftime("%Y-%m-%d"), "evento": "Contrato enviado para análise"})
            if hasattr(c, 'historicoavaliacaocontrato'):
                h = c.historicoavaliacaocontrato
                evento_nome = "Contrato aprovado" if h.veredito == Veredito.APROVADO else f"Contrato reprovado: {h.justificativa or 'sem justificativa'}"
                if h.data_avaliacao:
                    eventos.append({"data": h.data_avaliacao.strftime("%Y-%m-%d"), "evento": evento_nome})

        for r in obj.relatorio_set.all():
            if r.data_upload:
                eventos.append({"data": r.data_upload.strftime("%Y-%m-%d"), "evento": f"Relatório '{r.titulo or 'Sem Título'}' enviado"})
            if hasattr(r, 'historicoavaliacaorelatorio'):
                h = r.historicoavaliacaorelatorio
                evento_nome = f"Relatório avaliado: {h.veredito} — {h.justificativa}" if h.justificativa else f"Relatório avaliado: {h.veredito}"
                if h.data_avaliacao:
                    eventos.append({"data": h.data_avaliacao.strftime("%Y-%m-%d"), "evento": evento_nome})
        
        eventos.sort(key=lambda x: x["data"])
        return eventos

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and hasattr(request.user, 'coordenador') and not hasattr(request.user, 'secretaria'):
            data.pop('contrato', None)
        return data

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            "id", "arquivo", 'status', 'conflito_grade'
        ]
        read_only_fields = ["id", "data_upload", "cnpj_empresa", "nome_empresa",
            "data_inicio", "data_termino", "apolice_seguro", "plano_atividade",
            "assinatura_aluno", "assinatura_empresa", "assinatura_faculdade",
            "processoId", "conflito_grade"]

    def create(self, validated_data):
        return Contrato.objects.create(**validated_data)

class CoordenadorSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Coordenador
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade', 'areaId']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('senha'))
        coordenador = Coordenador.objects.create(**validated_data)
        return coordenador

class SecretariaSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Secretaria
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('senha'))
        secretaria = Secretaria.objects.create(**validated_data)
        return secretaria

class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = [
            'processo_id', 'arquivo', 'data_upload',
            'status', 'fora_do_prazo'
        ]
        read_only_fields = ['id', 'data_upload', 'processo_id', 'fora_do_prazo']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        validated_data['status'] = StatusRelatorio.AGUARDANDO_VALIDACAO
        return Relatorio.objects.create(**validated_data) 

class AtualizarContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            'cnpj_empresa', 'nome_empresa', 'data_inicio', 'data_termino',
            'apolice_seguro', 'plano_atividade', 'assinatura_aluno',
            'assinatura_empresa', 'assinatura_faculdade'
        ]

class AtualizarRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ['titulo', 'corpo']

class HistoricoAvaliacaoRelatorioSerializer(serializers.ModelSerializer):
    justificativa = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = HistoricoAvaliacaoRelatorio
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'relatorio_id', 'justificativa']
        read_only_fields = ['id', 'data_avaliacao']

    def validate(self, attrs):
        """
        Garante as regras de auditoria: se o coordenador decidir por 'REPROVADO',
        é estritamente necessário fornecer a justificativa para dar transparência ao aluno.
        """
        veredito = attrs.get('veredito')
        justificativa = attrs.get('justificativa', '')
        if veredito == Veredito.REPROVADO:
            if not justificativa or not str(justificativa).strip():
                raise serializers.ValidationError(
                    {"justificativa": "A justificativa é obrigatória em caso de reprovação."}
                )
        return attrs

class HistoricoAvaliacaoContratoSerializer(serializers.ModelSerializer):
    justificativa = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = HistoricoAvaliacaoContrato
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'contrato_id', 'justificativa']
        read_only_fields = ['id', 'data_avaliacao']

    def validate(self, attrs):
        """
        Validações de auditoria de Contrato:
        1. Reprovações exigem justificativa.
        2. Aprovações são vetadas se a duração for maior que 24 meses (para não-PCD),
           atendendo à Lei do Estágio.
        """
        veredito = attrs.get('veredito')
        justificativa = attrs.get('justificativa', '')
        contrato = attrs.get('contrato_id')
        
        # Validar justificativa obrigatória se veredito for REPROVADO (Issue 168)
        if veredito == Veredito.REPROVADO:
            if not justificativa or not str(justificativa).strip():
                raise serializers.ValidationError(
                    {"justificativa": "A justificativa é obrigatória em caso de reprovação."}
                )
        
        # Validar duração contratual superior a 24 meses (Issue 174)
        if veredito == Veredito.APROVADO and contrato:
            aluno = contrato.processoId.aluno
            if contrato.data_inicio and contrato.data_termino:
                from dateutil.relativedelta import relativedelta
                limite_fim = contrato.data_inicio + relativedelta(months=24)
                if contrato.data_termino > limite_fim and not getattr(aluno, 'is_pcd', False):
                    raise serializers.ValidationError(
                        {"veredito": "O contrato não pode ser aprovado pois a vigência supera 24 meses para alunos não-PCD."}
                    )
        return attrs

class HorariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horarios
        fields = ['id', 'dia', 'turno']
