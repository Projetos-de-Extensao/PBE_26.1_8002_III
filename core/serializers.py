from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

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
        fields = ["status","matricula_aluno"]
        # "matricula_coordenacao","matricula_secretaria"]
        read_only_fields = ["id","data_criacao"]

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
        fields = ['nome', 'email', 'matricula', 'senha', 'cpf', 'is_ativo', 'unidade']
        extra_kwargs = { 'senha': {'write_only': True} }
        
    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        return Aluno.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            validated_data['senha'] = make_password(validated_data['senha'])

        instance.nome = validated_data.get('nome', instance.nome)
        instance.email = validated_data.get('email', instance.email)
        instance.matricula = validated_data.get('matricula', instance.matricula)
        instance.senha = validated_data.get('senha', instance.senha)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        instance.is_ativo = validated_data.get('is_ativo', instance.is_ativo)
        instance.unidade = validated_data.get('unidade', instance.unidade)
        instance.save()
        return instance
