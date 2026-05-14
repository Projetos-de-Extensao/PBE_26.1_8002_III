from rest_framework import serializers
from .models import *


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome","areaId"]

class AlunoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(max_length=100)
    matricula = serializers.CharField(max_length=20)
    cpf = serializers.CharField(max_length=14)
    is_ativo = serializers.BooleanField()
