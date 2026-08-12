import time
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class MetabaseDashboardAPIView(APIView):
    """
    Endpoint protegido por JWT que gera uma URL de Signed Embedding do Metabase.

    Regras de Acesso (RBAC):
    - Secretaria  → Dashboard configurado em METABASE_DASHBOARD_IDS['secretaria']
    - Coordenador → Dashboard configurado em METABASE_DASHBOARD_IDS['coordenador']
    - Aluno / Outros → 403 Forbidden

    O token de embedding é assinado com HS256 usando a chave secreta do Metabase
    configurada em settings.METABASE_SECRET_KEY. O token expira em 10 minutos.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obter URL de Embedding do Metabase",
        description=(
            "Retorna uma URL segura para incorporar o dashboard do Metabase via iframe. "
            "O dashboard exibido depende do perfil do usuário autenticado."
        ),
        responses={
            200: inline_serializer(
                name='MetabaseDashboardResponse',
                fields={
                    'iframe_url': serializers.CharField(),
                }
            ),
            403: inline_serializer(
                name='MetabaseDashboard403',
                fields={
                    'detail': serializers.CharField(),
                }
            ),
            503: inline_serializer(
                name='MetabaseDashboard503',
                fields={
                    'detail': serializers.CharField(),
                }
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        # 1. Verificar se existem URLs públicas (Guest/Public Embed) configuradas e retornar diretamente
        if hasattr(user, 'secretaria') and getattr(settings, 'METABASE_PUBLIC_DASHBOARD_SECRETARIA', ''):
            return Response({"iframe_url": settings.METABASE_PUBLIC_DASHBOARD_SECRETARIA}, status=status.HTTP_200_OK)
        elif hasattr(user, 'coordenador') and getattr(settings, 'METABASE_PUBLIC_DASHBOARD_COORDENADOR', ''):
            return Response({"iframe_url": settings.METABASE_PUBLIC_DASHBOARD_COORDENADOR}, status=status.HTTP_200_OK)

        # 2. Validar que o Metabase está configurado caso não use URLs públicas
        if not settings.METABASE_SECRET_KEY:
            return Response(
                {"detail": "Integração com Metabase não configurada. Defina METABASE_SECRET_KEY."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        dashboard_ids = settings.METABASE_DASHBOARD_IDS

        # Determinar o ID do dashboard com base no perfil do usuário
        params = {}
        if hasattr(user, 'secretaria'):
            dashboard_id = dashboard_ids['secretaria']
        elif hasattr(user, 'coordenador'):
            dashboard_id = dashboard_ids['coordenador']
        else:
            # Aluno ou qualquer outro perfil não autorizado
            return Response(
                {"detail": "Seu perfil não possui dashboards atribuídos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Gerar o token JWT de embedding (HS256)
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": params,
            "exp": int(time.time()) + (10 * 60),  # Expira em 10 minutos
        }

        token = jwt.encode(
            payload,
            settings.METABASE_SECRET_KEY,
            algorithm="HS256",
        )

        # Montar a URL de embedding completa
        iframe_url = (
            f"{settings.METABASE_SITE_URL}"
            f"/embed/dashboard/{token}"
            f"#bordered=false&titled=true"
        )

        return Response({"iframe_url": iframe_url}, status=status.HTTP_200_OK)
