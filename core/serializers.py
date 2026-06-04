from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from .enums import *
from .validators import validar_email_institucional
from .enums import StatusProcesso
from .services.ler_extrair_infos_pdf import ler_pdf_modo_layout, extrair_infos 
from .validators import valida_periodo_relatorio
from datetime import datetime
from django.shortcuts import get_object_or_404


class NestedContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = ['nome_empresa', 'data_upload', 'status'] 

class NestedRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ['data_upload', 'status']

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
    processos = NestedProcessoSerializer(source="matricula_aluno", many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade', 'periodo', 'curso', 'processos']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        validated_data['nome'] = validated_data['nome'].lower().capitalize().strip()
        return Aluno.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            validated_data['senha'] = make_password(validated_data['senha'])
        
        if 'nome' in validated_data:
            validated_data['nome'] = validated_data['nome'].lower().capitalize().strip()

        instance.nome = validated_data.get("nome", instance.nome)
        instance.email = validated_data.get("email", instance.email)
        instance.matricula = validated_data.get("matricula", instance.matricula)
        instance.senha = validated_data.get("senha", instance.senha)
        instance.cpf = validated_data.get("cpf", instance.cpf)
        instance.is_ativo = validated_data.get("is_ativo", instance.is_ativo)
        instance.unidade = validated_data.get("unidade", instance.unidade)
        instance.save()
        return instance


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome"]
        read_only_fields = ["id"]
        exclude = ["areaId"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["nome"]
        read_only_fields = ["id"]


class ProcessoSerializer(serializers.ModelSerializer):
    matricula_aluno = serializers.SlugRelatedField(slug_field='matricula', queryset=Aluno.objects.all(), source='aluno')
    matricula_secretaria = serializers.SlugRelatedField(slug_field='matricula', queryset=Secretaria.objects.all(), source='secretaria')
    matricula_coordenacao = serializers.SlugRelatedField(slug_field='matricula', queryset=Coordenador.objects.all(), source='coordenacao')

    class Meta:
        model = Processo
        fields = ["nome_empresa", "status", "matricula_aluno", "matricula_secretaria", "matricula_coordenacao"]
        read_only_fields = ["id", "data_criacao"]

    def validate(self, attrs):
        aluno = attrs.get('aluno')
        status_atual = attrs.get('status')
        if status_atual == StatusProcesso.ABERTO:
            existe_processo = Processo.objects.filter(aluno=aluno, status=StatusProcesso.ABERTO).exists()
            if existe_processo:
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

    class Meta:
        model = Processo
        fields = ["nome_empresa", "status", "aluno", "secretaria", "coordenacao", "contrato", "relatorio"]

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            "id", "arquivo",'status'
        ]
        read_only_fields = ["id", "data_upload", "cnpj_empresa", "nome_empresa",
            "data_inicio", "data_termino", "apolice_seguro", "plano_atividade",
            "assinatura_aluno", "assinatura_empresa", "assinatura_faculdade",
            "processoId"]

    def create(self, validated_data):
        pdf = validated_data['arquivo']
        
        # Reseta ponteiro do arquivo para leitura do PDF
        pdf.seek(0)
        texto = ler_pdf_modo_layout(pdf)
        # Reseta o ponteiro de volta para que o Django possa salvar o arquivo corretamente
        pdf.seek(0)
        
        infos = extrair_infos(texto)
        
        extra_data = {}
        if infos:
            extra_data["cnpj_empresa"] = infos.get("cnpj_empresa", "")
            extra_data["nome_empresa"] = infos.get("nome_empresa", "")
            
            data_ini_str = infos.get("data_inicio")
            data_fim_str = infos.get("data_termino")
            
            # Converte string formatada "DD/MM/AAAA" para datetime.date
            if data_ini_str and '/' in data_ini_str:
                try:
                    extra_data["data_inicio"] = datetime.strptime(data_ini_str, "%d/%m/%Y").date()
                except ValueError:
                    pass
            if data_fim_str and '/' in data_fim_str:
                try:
                    extra_data["data_termino"] = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
                except ValueError:
                    pass
                    
            extra_data["apolice_seguro"] = infos.get("apolice_seguro", "")
            
        contrato = Contrato.objects.create(
            **validated_data,
            **extra_data
        )
        return contrato

class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade', 'areaId']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        return Coordenador.objects.create(**validated_data)


class SecretariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secretaria
        fields = ['nome', 'email', 'matricula', 'senha', 'unidade']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        return Secretaria.objects.create(**validated_data)


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = [
            'processo_id', 'arquivo', 'data_upload',
            'horas_trabalhadas', 'data_inicio', 'data_termino', 'status'
        ]
        read_only_fields = ['id', 'data_upload', 'processo_id']

    def create(self, validated_data):
        processo = validated_data['processo_id']
        contrato = Contrato.objects.filter(processoId=processo,status = StatusContrato.APROVADO).first()
        
        # Cria a instância temporária do Relatório em memória para validar
        relatorio = Relatorio(**validated_data)
        
        if contrato:
            # Valida o período e altera o status se estiver incorreto
            if not valida_periodo_relatorio(relatorio, contrato):
                validated_data['status'] = StatusRelatorio.REPROVADO
        else:
            # Se não houver contrato ativo, o relatório é reprovado
            validated_data['status'] = StatusRelatorio.REPROVADO
            
        return Relatorio.objects.create(**validated_data) 



class HistoricoAvaliacaoRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAvaliacaoRelatorio
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'relatorio_id']
        read_only_fields = ['id', 'data_avaliacao']


class HistoricoAvaliacaoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAvaliacaoContrato
        fields = ['observacoes', 'data_avaliacao', 'veredito', 'avaliador', 'contrato_id']
        read_only_fields = ['id', 'data_avaliacao']