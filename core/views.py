from django.shortcuts import render
from .models import *
from .serializers import AlunoSerializer

def singleobj(request):
    data = Aluno.objects.get(id=1)
    serializer = AlunoSerializer(data)
    print(serializer.data)

