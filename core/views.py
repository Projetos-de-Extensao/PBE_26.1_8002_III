from django.shortcuts import render
from .models import *
from .serializers import AlunoSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse

def singleobj(request):
    data = Aluno.objects.get(id=1)
    serializer = AlunoSerializer(data)
    json_data = JSONRenderer().render(serializer.data)
    return HttpResponse(json_data, content_type='application/json')

def multipleobj(request):
    data = Aluno.objects.all()
    serializer = AlunoSerializer(data, many=True)
    json_data = JSONRenderer().render(serializer.data)
    return HttpResponse(json_data, content_type='application/json')