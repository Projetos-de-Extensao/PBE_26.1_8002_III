from django.shortcuts import render
from .models import *
from .serializers import AlunoSerializer,ProcessoSerializer
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .permissions import IsSecretaria, IsAluno

@csrf_exempt
@api_view(['GET','POST'])
@permission_classes([IsSecretaria])
def aluno(request):

    if request.method == 'PATCH':
        parsed_data = request.data
        matricula = request.GET.get('matricula_aluno', None)
        if matricula is not None:
            try:
                old_data = Aluno.objects.get(matricula=matricula)
            except Aluno.DoesNotExist:
                return Response({"error": "Aluno não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = AlunoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Matrícula não informada"}, status=status.HTTP_400_BAD_REQUEST)


    if request.method == 'POST':
        parsed_data = request.data
        serializer = AlunoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Aluno criado com sucesso!"},status=status.HTTP_201_CREATED)


    if request.method == 'GET':
        data = Aluno.objects.all()
        matricula = request.GET.get('matricula', None)
        nome = request.GET.get('nome', None)
        if matricula is not None:
            data = data.filter(matricula=matricula)
        if nome is not None:
            data = data.filter(nome__icontains=nome)
        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = AlunoSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

   

@csrf_exempt
@api_view(['GET','POST'])
@permission_classes([IsAluno | IsSecretaria])
def processo(request):
    if request.method == 'POST':
        parsed_data = request.data
        serializer = ProcessoSerializer(data=parsed_data)
        if not serializer.is_valid():
            erros = {
                "erro": "Falha na validação dos dados.",
                "campos_com_erro": {
                    campo: mensagens for campo, mensagens in serializer.errors.items()
                }
            }
            return Response(erros, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"message": "Processo criado com sucesso!"}, status=status.HTTP_201_CREATED)
       

    if request.method == 'GET':
        data = Processo.objects.all()
        matricula_aluno = request.GET.get('matricula_aluno', None)
        status_filtro = request.GET.get('status', None)
        nome_empresa = request.GET.get('nome_empresa', None)
        if matricula_aluno is not None:
            data = data.filter(matricula_aluno__matricula=matricula_aluno)
        if status_filtro is not None:
            data = data.filter(status=status_filtro)
        if nome_empresa is not None:
            data = data.filter(nome_empresa__icontains=nome_empresa)
        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = ProcessoSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    if request.method == 'PATCH':
        parsed_data = request.data
        id = request.GET.get('processo_id', None)
        if id is not None:
            try:
                old_data = Processo.objects.get(id=id)
            except Processo.DoesNotExist:
                return Response({"error": "Processo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ProcessoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "updated"}, status=status.HTTP_200_OK)
            
        else:
            return Response({"error": "Id não informado"}, status=status.HTTP_400_BAD_REQUEST)
                

        json = request.body
        stream = io.BytesIO(json)
        parsed_data = JSONParser().parse(stream)
        id = request.GET.get('processo_id', None)
        if id is not None:
            try:
                old_data = Processo.objects.get(id=id)
            except Processo.DoesNotExist:
                return Response({"error": "Processo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ProcessoSerializer(old_data, data=parsed_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "updated"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Id não informado"}, status=status.HTTP_400_BAD_REQUEST)

        



        


