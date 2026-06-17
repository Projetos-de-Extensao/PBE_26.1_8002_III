import os
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
from .serializers import *
from .models import Aluno, Processo, Secretaria, Coordenador, Contrato, HistoricoAvaliacaoContrato, Horarios, FeatureFlag
from .permissions import IsSecretaria, IsAluno, IsCoordenador
from .services.email_service import EmailNotificationService
from core.enums import Veredito, StatusContrato, StatusRelatorio, StatusProcesso
from rest_framework.exceptions import PermissionDenied

def is_user_staff(user):
    """
    Verifica se o usuário pertence à camada administrativa (Secretaria ou Coordenador).
    Utiliza um mecanismo de "cache" na requisição (adicionando '_cached_is_staff' ao user)
    para evitar bater no banco de dados múltiplas vezes na mesma view.
    """
    if hasattr(user, '_cached_is_staff'):
        return user._cached_is_staff
    is_staff = Secretaria.objects.filter(email=user.email).exists() or \
               Coordenador.objects.filter(email=user.email).exists()
    user._cached_is_staff = is_staff
    return is_staff

def get_processo_seguro(processo_id, user, prefetch=None, select=None):
    """
    PREVENÇÃO DE VULNERABILIDADE BOLA (Broken Object Level Authorization / IDOR):
    Busca um processo e garante que o usuário possui o nível de acesso correto.
    - Se for aluno: Verifica se ele é o "dono" do Processo. Retorna 403 caso tente 
      acessar dados de outro aluno forçando o ID na URL.
    - Se for staff: Passa livre.
    """
    queryset = Processo.objects.all()
    if select:
        queryset = queryset.select_related(*select)
    if prefetch:
        queryset = queryset.prefetch_related(*prefetch)
        
    processo = get_object_or_404(queryset, id=processo_id)
    
    if not is_user_staff(user):
        try:
            aluno = Aluno.objects.get(email=user.email)
            if processo.aluno != aluno:
                raise PermissionDenied("Você não tem permissão para acessar este processo.")
        except Aluno.DoesNotExist:
            raise PermissionDenied("Usuário não autorizado.")
            
    return processo

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
        """
        Lista alunos do sistema.
        O uso de `select_related('curso')` e `prefetch_related('aluno')` 
        resolve um problema grave de performance conhecido como N+1 Queries.
        Ele força o banco a carregar os dados aninhados em uma única query 
        em vez de dezenas.
        """
        data = Aluno.objects.select_related('curso').prefetch_related('aluno').all()
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
                    "detail": "Nenhum aluno encontrado com os dados informados.",
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
        return Response({"detail": "Aluno criado com sucesso!"}, status=status.HTTP_201_CREATED)

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
                return Response({"detail": "Aluno não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = AlunoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Matrícula não informada"}, status=status.HTTP_400_BAD_REQUEST)

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
        if is_user_staff(request.user):
            data = Processo.objects.select_related('aluno', 'secretaria', 'coordenacao').all()
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
        parsed_data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # UC-08: iniciar_processo (Regras de Negócio)
        try:
            aluno_logado = Aluno.objects.get(email=request.user.email)
            parsed_data['matricula_aluno'] = aluno_logado.matricula
        except Aluno.DoesNotExist:
            if 'matricula_aluno' not in parsed_data:
                return Response(
                    {"detail": "Secretaria/Coordenação deve selecionar a matrícula do aluno."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ProcessoSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)

        grupo = request.user.groups.first()
        cargo = grupo.name if grupo else ""
        nome_completo = f"{request.user.first_name} {request.user.last_name}"
        username = request.user.username
        criado_por_string = (cargo + nome_completo + username)[:100]

        try:    
            serializer.save(criado_por=criado_por_string)
            return Response({"detail": "Processo criado com sucesso"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"detail": "Esse processo já existe"}, status=status.HTTP_409_CONFLICT)

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
            old_data = get_processo_seguro(id, request.user)
            
            serializer = ProcessoSerializer(old_data, data=parsed_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Id não informado"}, status=status.HTTP_400_BAD_REQUEST)

class ProcessoDetailAPIView(APIView):
    permission_classes = [IsAluno | IsCoordenador | IsSecretaria]

    @extend_schema(
        summary="Detalhes do Processo de Estágio",
        description="Retorna informações detalhadas de um processo de estágio pelo ID, incluindo histórico de avaliações, contratos e relatórios.",
        responses={200: ProcessoDetailSerializer}
    )
    def get(self, request, id, *args, **kwargs):
        processo = get_processo_seguro(
            id, request.user,
            select=['aluno', 'secretaria', 'coordenacao'],
            prefetch=[
                'contrato_set__historicoavaliacaocontrato__avaliador',
                'relatorio_set__historicoavaliacaorelatorio__avaliador',
            ]
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
        processo = get_processo_seguro(processo_id, request.user)
        
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

        # Dispara o processamento com IA em background se a feature flag estiver ativa e não for execução de testes
        import sys
        if 'pytest' not in sys.modules and FeatureFlag.objects.is_active("async_contract_ai"):
            from core.tasks import processarContratoComIa
            processarContratoComIa.delay(contrato.id)
        
        return Response(
            {
                "detail": "Contrato enviado com sucesso e secretaria notificada!",
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
            processo = contrato.processoId
            processo.status = StatusProcesso.EM_ANDAMENTO
            processo.save()
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
            {"detail":f"Contrato avaliado como {avaliacao.veredito} e aluno notificado!"},
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
        processo = get_processo_seguro(processo_id, request.user)
        
        # Validar se o processo está ativo (Em Andamento) - Issue 148
        if processo.status != StatusProcesso.EM_ANDAMENTO:
            return Response(
                {"detail": "Não é permitido enviar relatórios para processos que não estão ativos/em andamento."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        import sys
        if 'pytest' not in sys.modules and FeatureFlag.objects.is_active("async_report_ai"):
            from core.tasks import processarRelatorioComIa
            processarRelatorioComIa.delay(relatorio.id)
            
        return Response({"detail": "Relatório enviado e coordenação notificada."}, status=status.HTTP_201_CREATED)

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
            processo = relatorio.processo_id
            processo.status = StatusProcesso.CONCLUIDO
            processo.save()
        elif avaliacao.veredito == Veredito.REPROVADO:
            relatorio.status = StatusRelatorio.REPROVADO
            processo = relatorio.processo_id
            processo.status = StatusProcesso.CANCELADO
            processo.save()
        relatorio.save()
        
        aluno = relatorio.processo_id.aluno
        
        EmailNotificationService.notificar_avaliacao(
            email_destino=aluno.email,
            nome_aluno=aluno.nome,
            status=avaliacao.veredito, 
            observacoes=avaliacao.observacoes
        )
        
        return Response({"detail": f"Relatório {avaliacao.veredito} e aluno notificado."}, status=status.HTTP_201_CREATED)
    
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
                {"detail": "Campo 'justificativa' é obrigatório para reprovação."},
                status=status.HTTP_400_BAD_REQUEST
            )

        contrato = processo.contrato_set.last()
        if not contrato:
            return Response(
                {"detail": "Nenhum contrato encontrado para este processo."},
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

class HorariosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Lista todos os horários disponíveis",
        responses={200: HorariosSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        horarios = Horarios.objects.all()
        serializer = HorariosSerializer(horarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DownloadContratoAPIView(APIView):
    # UC-06: fazer_download
    permission_classes = [IsAluno | IsSecretaria | IsCoordenador]

    @extend_schema(
        summary="Download de Contrato de Estágio",
        description="Retorna o arquivo PDF do contrato. Acesso protegido para o dono do processo, secretaria ou coordenação.",
        responses={200: OpenApiTypes.BINARY}
    )
    def get(self, request, id, *args, **kwargs):
        contrato = get_object_or_404(Contrato.objects.select_related('processoId__aluno'), id=id)
        processo = contrato.processoId
        
        # Validação de permissão (Aluno só baixa o dele)
        if not is_user_staff(request.user):
            try:
                aluno = Aluno.objects.get(email=request.user.email)
                if processo.aluno != aluno:
                    return Response({"detail": "Você não tem permissão para baixar este contrato."}, status=status.HTTP_403_FORBIDDEN)
            except Aluno.DoesNotExist:
                return Response({"detail": "Usuário não autorizado."}, status=status.HTTP_403_FORBIDDEN)
                
        if not contrato.arquivo:
            raise Http404("Arquivo não encontrado.")
            
        try:
            arquivo_open = contrato.arquivo.open('rb')
        except (FileNotFoundError, ValueError):
            raise Http404("Arquivo físico não encontrado no servidor.")
            
        return FileResponse(arquivo_open, as_attachment=True, filename=os.path.basename(contrato.arquivo.name))

class AtualizarContratoAPIView(APIView):
    permission_classes = [IsSecretaria]

    @extend_schema(
        request=AtualizarContratoSerializer,
        responses={200: AtualizarContratoSerializer}
    )
    def patch(self, request, id, *args, **kwargs):
        processo = get_object_or_404(Processo, id=id)
        contrato = processo.contrato_set.last()
        if not contrato:
            return Response({"detail": "Contrato não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AtualizarContratoSerializer(contrato, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        from core.tasks import validarContrato
        validarContrato.delay(contrato.id, processo.aluno.id)

        return Response(serializer.data, status=status.HTTP_200_OK)

class AtualizarRelatorioAPIView(APIView):
    permission_classes = [IsCoordenador]

    @extend_schema(
        request=AtualizarRelatorioSerializer,
        responses={200: AtualizarRelatorioSerializer}
    )
    def patch(self, request, id, *args, **kwargs):
        processo = get_object_or_404(Processo, id=id)
        relatorio = processo.relatorio_set.last()
        if not relatorio:
            return Response({"detail": "Relatório não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AtualizarRelatorioSerializer(relatorio, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if FeatureFlag.objects.is_active("report_evaluation_ai"):
            from core.tasks import avaliarRelatorioComIa
            avaliarRelatorioComIa.delay(relatorio.id)

        return Response(serializer.data, status=status.HTTP_200_OK)
