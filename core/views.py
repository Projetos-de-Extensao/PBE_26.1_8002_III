from django.shortcuts import render
from .models import *
from .serializers import AlunoSerializer,ProcessoSerializer
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse,JsonResponse
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from dnjango.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAP1View, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.authentication import TokenAuthentication 

@csrf_exempt
def aluno(request):
    if request.method == 'POST':
        json = request.body 
        stream = io.BytesIO(json)
        parsed_data = JSONParser().parse(stream)
        serializer = AlunoSerializer(data=parsed_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"Aluno criado com sucesso!"},status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    if request.method == 'GET':
        data = Aluno.objects.all()
        params = request.GET.get('matricula',None)
        if params is not None:
            data = data.filter(matricula=params)    
        serializer = AlunoSerializer(data, many=True)
        json_data = JSONRenderer().render(serializer.data)
        return HttpResponse(json_data, content_type='application/json')

   

@csrf_exempt
def processo(request):
    if request.method == 'POST':
        json = request.body
        stream = io.BytesIO(json)
        parsed_data = JSONParser().parse(stream)
        serializer = ProcessoSerializer(data=parsed_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"created":"successfull"},status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    if request.method == 'GET':
        data = Processo.objects.all()
        serializer = ProcessoSerializer(data,many=True)
        return JsonResponse(serializer.data,safe=False)

class MultipleObjectAPIView(ListAPIView):       
    authentication_classes = [TokenAuthentication]
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

class SingleObjectAPIView(RetrieveAPIView):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
        


