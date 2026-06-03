from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .models import Aluno, Processo
from .serializers import AlunoSerializer, ProcessoSerializer
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
        return Response({"message":"Aluno criado com sucesso!"}, status=status.HTTP_201_CREATED)

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

        if not serializer.is_valid():
            erros = {
                "erro": "Falha na validação dos dados.",
                "campos_com_erro": {
                    campo: mensagens for campo, mensagens in serializer.errors.items()
                }
            }
            return Response(erros, status=status.HTTP_400_BAD_REQUEST)
        try:    
            serializer.save(criado_por=criado_por_string)
            return Response({"criado":"Processo criado com sucesso"},status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"falhou":"Esse processo já existe"},status=status.HTTP_409_CONFLICT)

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


class MultipleObjectAPIView(ListAPIView):       
    authentication_classes = [JWTAuthentication]
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(request.user)
        response = super().get(request, *args, **kwargs)
        return response

class SingleObjectAPIView(RetrieveAPIView):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
