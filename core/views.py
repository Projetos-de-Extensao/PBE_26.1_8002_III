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
from .permissions import IsSecretaria, IsAluno
from rest_framework.test import APIClient
from drf_spectacular.utils import extend_schema, OpenApiParameter


@csrf_exempt
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='matricula', description='Filtra por matrícula do aluno', required=False, type=str)
    ],
    responses={200: AlunoSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=AlunoSerializer,
    responses={201: AlunoSerializer}
)
@extend_schema(
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='matricula_aluno', description='Matrícula do aluno a ser atualizado', required=True, type=str)
    ],
    request=AlunoSerializer,
    responses={200: AlunoSerializer}
)
@api_view(['GET','POST','PATCH'])
# @permission_classes([IsSecretaria])
def aluno(request):

    if request.method == 'PATCH':
        parsed_data = request.data
        matricula = request.query_params.get('matricula_aluno', None)
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
        params = request.query_params.get('matricula')
        if params is not None:
            data = data.filter(matricula=params)
            data_with_process = data.prefetch_related('processo')
            serializer = AlunoSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = AlunoSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   

@csrf_exempt
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='matricula_aluno', description='Filtra processos por matrícula do aluno', required=False, type=str)
    ],
    responses={200: ProcessoSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=ProcessoSerializer,
    responses={201: ProcessoSerializer}
)
@extend_schema(
    methods=['PATCH'],
    parameters=[
        OpenApiParameter(name='processo_id', description='ID do processo a ser atualizado', required=True, type=str)
    ],
    request=ProcessoSerializer,
    responses={200: ProcessoSerializer}
)
@api_view(['GET','POST','PATCH'])
# @permission_classes([IsAluno | IsSecretaria])
def processo(request):
    if request.method == 'POST':
        parsed_data = request.data
        serializer = ProcessoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)

        grupo = request.user.groups.first()
        cargo = grupo.name if grupo else ""
        nome_completo = f"{request.user.first_name} {request.user.last_name}"
        username = request.user.username
        criado_por_string = (cargo + nome_completo + username)[:100]


        try:    
            serializer.save(criado_por=criado_por_string)
            return Response({"criado":"Processo criado com sucesso"},status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"falhou":"Esse processo já existe"},status=status.HTTP_409_CONFLICT)

    if request.method == 'GET':
        data = Processo.objects.all()
        params = request.query_params.get('matricula_aluno',None)
        if params is not None:
            data = Processo.objects.select_related('matricula_aluno')
        serializer = ProcessoSerializer(data,many=True)
        return Response(serializer.data,safe=False)
    
    if request.method == 'PATCH':
        parsed_data = request.data
        id = request.query_params.get('processo_id', None)
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
                

     
        


