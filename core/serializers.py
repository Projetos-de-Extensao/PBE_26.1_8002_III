from rest_framework import serializers
from .models import *

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["nome","areaId"]