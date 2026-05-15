from django.shortcuts import render
from .models import *
from .serializers import AlunoSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse,JsonResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status


def singleobj(request):
    if request.method == 'POST':
        json = request.body 
        stream = io.BytesIO(json)
        parsed_data = JSONParser().parse(stream)
        serializer = AlunoSerializer(data=parsed_data)
        if serializer.is_valid(data):
            pass
        else:
            return JsonResponse(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



    data = Aluno.objects.get(id=1)
    serializer = AlunoSerializer(data)
    json_data = JSONRenderer().render(serializer.data)
    return HttpResponse(json_data, content_type='application/json')

def multipleobj(request):
    data = Aluno.objects.all()
    serializer = AlunoSerializer(data, many=True)
    json_data = JSONRenderer().render(serializer.data)
    return HttpResponse(json_data, content_type='application/json')