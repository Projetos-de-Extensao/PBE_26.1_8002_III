from rest_framework import serializers
from .models import *


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
        fields = ["status", "matricula_aluno", "nome_empresa"]
        read_only_fields = ["id", "data_criacao", "status"]
        extra_kwargs = {
            'nome_empresa': {
                'error_messages': {
                    'required': 'O campo Nome da Empresa é obrigatório.',
                    'blank': 'O campo Nome da Empresa não pode ser vazio.',
                }
            },
            'matricula_aluno': {
                'error_messages': {
                    'required': 'O campo Matrícula do Aluno é obrigatório.',
                    'does_not_exist': 'Aluno com esta matrícula não foi encontrado.',
                    'null': 'O campo Matrícula do Aluno não pode ser nulo.',
                }
            },
        }

    def create(self, validated_data):
        return Processo.objects.create(**validated_data)
    

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = [
            "cnpj_empresa", "nome_empresa",
            "data_inicio", "data_termino", "apolice_seguro", "plano_atividade",
            "assinatura_aluno", "assinatura_empresa", "assinatura_faculdade",
            "processoId"
        ]
        read_only_fields = ["id", "arquivo", "data_upload"]

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade', 'periodo', 'curso']
    def create(self, validated_data):
        return Aluno.objects.create(**validated_data)

    def update(sekf,instance,validated_data):
        instance.name = validated_data.get("name",instance.name)
        instance.email = validated_data.get("email",instance.email)
        instance.matricula = validated_data.get("matricula",instance.matricula)
        instance.senha = validated_data.get("senha",instance.senha)
        instance.cpf = validated_data.get("cpf",instance.cpf)
        instance.is_ativo = validated_data.get("is_ativo",instance.is_ativo)
        instance.unidade = validated_data.get("unidade",instance.unidade)
        instance.save()
        return instance

