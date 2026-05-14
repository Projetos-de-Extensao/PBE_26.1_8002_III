from rest_framework import serializers
from .models import *


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome","areaId"]

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'cpf', 'is_ativo']
