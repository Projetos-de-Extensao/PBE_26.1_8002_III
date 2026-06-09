from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from .serializers import *
from .models import Aluno, Processo, Secretaria, Coordenador
from .permissions import IsSecretaria, IsAluno, IsCoordenador
from .services.email_service import EmailNotificationService
from core.enums import Veredito, StatusContrato, StatusRelatorio, StatusProcesso

class AlunoAPIView(APIView):
    permission_classes = [IsSecretaria | IsCoordenador]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='matricula', description='Filtra por matrícula do aluno', required=False, type=str),
            OpenApiParameter(name='cpf', description='Filtra por CPF', required=False, type=str),
            OpenApiParameter(name='nome', description='Filtra por nome (busca parcial)', required=False, type=str)
        ],
        responses={200: AlunoSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        data = Aluno.objects.all()
        matricula = request.query_params.get('matricula', None)
        cpf = request.query_params.get('cpf', None)
        nome = request.query_params.get('nome', None)

        if matricula:
            data = data.filter(matricula=matricula)
            
        if cpf:
            data = data.filter(cpf=cpf)

        if nome:
            termos_da_busca = nome.split() 
            for termo in termos_da_busca:
                data = data.filter(nome__icontains=termo)

        if not data.exists():
            return Response(
                {
                    "mensagem": "Nenhum aluno encontrado com os dados informados.",
                    "sugestao": "Tente buscar apenas pelo primeiro nome ou limpe os filtros e tente novamente.",
                    "resultados": []
                }, 
                status=status.HTTP_200_OK
            )

        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = AlunoSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=AlunoSerializer,
        responses={201: AlunoSerializer}
    )
    def post(self, request, *args, **kwargs):
        parsed_data = request.data
        serializer = AlunoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Aluno criado com sucesso!"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='matricula_aluno', description='Matrícula do aluno a ser atualizado', required=True, type=str)
        ],
        request=AlunoSerializer,
        responses={200: AlunoSerializer}
    )
    def patch(self, request, *args, **kwargs):
        parsed_data = request.data
        matricula = request.query_params.get('matricula_aluno', None)
        if matricula:
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

class ProcessoAPIView(APIView):
    permission_classes = [IsAluno | IsSecretaria | IsCoordenador]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='matricula_aluno', description='Filtra por matrícula do aluno', required=False, type=str),
            OpenApiParameter(name='status', description='Filtra por status do processo', required=False, type=str),
            OpenApiParameter(name='nome_empresa', description='Filtra por nome da empresa', required=False, type=str)
        ],
        responses={200: ProcessoSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        # Verifica se o usuário logado é Secretaria ou Coordenador (acesso total)
        is_staff = Secretaria.objects.filter(email=request.user.email).exists() or \
                   Coordenador.objects.filter(email=request.user.email).exists()

        if is_staff:
            data = Processo.objects.all()
        else:
            try:
                aluno = Aluno.objects.get(email=request.user.email)
                data = Processo.objects.filter(aluno=aluno)
            except Aluno.DoesNotExist:
                data = Processo.objects.none()  

        matricula_aluno = request.query_params.get('matricula_aluno', None)
        status_filtro = request.query_params.get('status', None)
        nome_empresa = request.query_params.get('nome_empresa', None)

        if matricula_aluno is not None:
            data = data.filter(aluno=matricula_aluno)    
        
        if status_filtro is not None:
            if status_filtro == StatusContrato.PENDENTE:
                data = data.filter(contrato__status=StatusContrato.PENDENTE).distinct()
            else:
                data = data.filter(status=status_filtro)
                
        if nome_empresa is not None:
            data = data.filter(nome_empresa__icontains=nome_empresa)

        paginator = PageNumberPagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = ProcessoSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=ProcessoSerializer,
        responses={201: ProcessoSerializer}
    )
    def post(self, request, *args, **kwargs):
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
            return Response({"criado": "Processo criado com sucesso"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"falhou": "Esse processo já existe"}, status=status.HTTP_409_CONFLICT)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='processo_id', description='ID do processo a ser atualizado', required=True, type=str)
        ],
        request=ProcessoSerializer,
        responses={200: ProcessoSerializer}
    )
    def patch(self, request, *args, **kwargs):
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

class ProcessoDetailAPIView(APIView):
    permission_classes = [IsAluno | IsCoordenador | IsSecretaria]

    @extend_schema(
        summary="Detalhes do Processo de Estágio",
        description="Retorna informações detalhadas de um processo de estágio pelo ID, incluindo histórico de avaliações, contratos e relatórios.",
        responses={200: ProcessoDetailSerializer}
    )
    def get(self, request, id, *args, **kwargs):
        processo = get_object_or_404(
            Processo.objects.select_related('aluno', 'secretaria', 'coordenacao')
                            .prefetch_related('contrato_set', 'relatorio_set'),
            id=id
        )
        serializer = ProcessoDetailSerializer(processo)
        return Response(serializer.data)

class UploadContrato(APIView):
    permission_classes = [IsSecretaria | IsAluno]
    serializer_class = ContratoSerializer
    
    @extend_schema(
        summary="Upload de Contrato de Estágio",
        description="Permite que alunos enviem contratos de estágio e notifica a secretaria sobre novos envios.",
        request=ContratoSerializer,
        responses={201: ContratoSerializer}
    )
    def post(self, request, *args, **kwargs):
        processo_id = kwargs.get('id')
        processo = get_object_or_404(Processo, id=processo_id)
        
        serializer = ContratoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        contrato = serializer.save(processoId=processo)
        
        aluno = contrato.processoId.aluno
        email_secretaria = "secretaria@ibmec.edu.br" 

        EmailNotificationService.notificar_novo_envio(
            email_destino=email_secretaria,
            nome_aluno=aluno.nome, 
            nome_documento="Contrato de Estágio"
        )
        
        return Response(
            {
                "message": "Contrato enviado com sucesso e secretaria notificada!",
                "data": serializer.data
            }, 
            status=status.HTTP_201_CREATED
        )

class AvaliarContratoAPIView(APIView):
    permission_classes = [IsSecretaria]

    @extend_schema(
        request=HistoricoAvaliacaoContratoSerializer,
        responses={201: HistoricoAvaliacaoContratoSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = HistoricoAvaliacaoContratoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avaliacao = serializer.save()
        contrato = avaliacao.contrato_id

        if avaliacao.veredito == Veredito.APROVADO:
            contrato.status = StatusContrato.APROVADO
        elif avaliacao.veredito == Veredito.REPROVADO:
            contrato.status = StatusContrato.REPROVADO
        
        contrato.save()
        
        aluno = contrato.processoId.aluno

        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=avaliacao.veredito,
            observacoes=avaliacao.observacoes
        )

        return Response(
            {"message":f"Contrato avaliado como {avaliacao.veredito} e aluno notificado!"},
            status=status.HTTP_201_CREATED
        )

class UploadRelatorio(APIView):
    permission_classes = [IsAluno]

    @extend_schema(
        summary="Upload de Relatório de Estágio",
        description="Permite que alunos enviem relatórios de estágio e notifica a coordenação sobre novos envios.", 
        request=RelatorioSerializer,
        responses={201: RelatorioSerializer}
    )
    def post(self, request, *args, **kwargs):
        processo_id = kwargs.get('id')
        processo = get_object_or_404(Processo, id=processo_id)
        
        serializer = RelatorioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        relatorio = serializer.save(processo_id=processo)
        
        aluno = relatorio.processo_id.aluno
        email_coordenacao = "coordenacao@ibmec.edu.br" 
        
        EmailNotificationService.notificar_novo_envio(
            email_destino=email_coordenacao,
            nome_aluno=aluno.nome, 
            nome_documento="Relatório de Estágio"
        )
        
        return Response({"message": "Relatório enviado e coordenação notificada."}, status=status.HTTP_201_CREATED)

class AvaliarRelatorioAPIView(APIView):
    permission_classes = [IsCoordenador] 

    @extend_schema(
        summary="Avaliação de Relatório de Estágio",
        description="Permite que coordenadores avaliem relatórios de estágio e notifica os alunos sobre a decisão.",
        request=HistoricoAvaliacaoRelatorioSerializer,
        responses={201: HistoricoAvaliacaoRelatorioSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = HistoricoAvaliacaoRelatorioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        avaliacao = serializer.save()
        relatorio = avaliacao.relatorio_id
        
        if avaliacao.veredito == Veredito.APROVADO:
            relatorio.status = StatusRelatorio.APROVADO 
        elif avaliacao.veredito == Veredito.REPROVADO:
            relatorio.status = StatusRelatorio.REPROVADO
        relatorio.save()
        
        aluno = relatorio.processo_id.aluno
        
        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=avaliacao.veredito, 
            observacoes=avaliacao.observacoes
        )
        
        return Response({"message": f"Relatório {avaliacao.veredito} e aluno notificado."}, status=status.HTTP_201_CREATED)
    
class ReprovarContratoAPIView(APIView):
    permission_classes = [IsSecretaria]

    @extend_schema(
        request=inline_serializer(
            name='ReprovarContratoSerializer',
            fields={
                'justificativa': serializers.CharField(required=True)
            }
        ),
        responses={200: ProcessoSerializer}
    )
    def patch(self, request, id, *args, **kwargs):
        processo = get_object_or_404(Processo, id=id)

        justificativa = request.data.get('justificativa')
        if not justificativa or not str(justificativa).strip():
            return Response(
                {"error": "Campo 'justificativa' é obrigatório para reprovação."},
                status=status.HTTP_400_BAD_REQUEST
            )

        contrato = processo.contrato_set.last()
        if not contrato:
            return Response(
                {"error": "Nenhum contrato encontrado para este processo."},
                status=status.HTTP_404_NOT_FOUND
            )

        contrato.status = StatusContrato.REPROVADO
        contrato.save()

        processo.status = StatusProcesso.REPROVADO
        processo.save()

        secretaria = get_object_or_404(Secretaria, email=request.user.email)
        HistoricoAvaliacaoContrato.objects.create(
            observacoes=justificativa,
            veredito=Veredito.REPROVADO,
            avaliador=secretaria,
            contrato_id=contrato
        )

        EmailNotificationService.notificar_avaliacao(
            email_destino=processo.aluno.email,
            nome_aluno=processo.aluno.nome,
            status=Veredito.REPROVADO,
            observacoes=justificativa
        )

        serializer = ProcessoSerializer(processo)
        return Response(serializer.data, status=status.HTTP_200_OK)