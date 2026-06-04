from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from .enums import *
from .validators import validar_email_institucional
from .enums import StatusProcesso
from .services.ler_extrair_infos_pdf import ler_pdf_modo_layout, extrair_infos
from datetime import datetime

class NestedProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ["id", "nome_empresa", "status"]


class AlunoSerializer(serializers.ModelSerializer):
    processos = NestedProcessoSerializer(source="matricula_aluno", many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade', 'periodo', 'curso', 'processos']
        read_only_fields = ['id']
        extra_kwargs = {'senha': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        return Aluno.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            validated_data['senha'] = make_password(validated_data['senha'])

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
    class Meta:
        model = Processo
        fields = ["nome_empresa", "status", "matricula_aluno"]
        read_only_fields = ["id", "data_criacao"]

    def validate(self, attrs):
        matricula_aluno = attrs.get('matricula_aluno')
        status_atual = attrs.get('status')
        if status_atual == StatusProcesso.ABERTO:
            existe_processo = Processo.objects.filter(matricula_aluno=matricula_aluno, status=StatusProcesso.ABERTO).exists()
            if existe_processo:
                raise serializers.ValidationError({"status": "O aluno já tem processos em aberto"})
        return attrs

    def create(self, validated_data):
        return Processo.objects.create(**validated_data)
    

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            "id", "arquivo"
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
        read_only_fields = ['id', 'data_upload']


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