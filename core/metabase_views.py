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
    - Secretaria  → Dashboard ID 1
    - Coordenador → Dashboard ID 2
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
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        # Determinar o ID do dashboard com base no perfil do usuário
        # Usa o mesmo mecanismo de detecção das permission classes existentes
        if hasattr(user, 'secretaria'):
            dashboard_id = 1
        elif hasattr(user, 'coordenador'):
            dashboard_id = 2
        else:
            # Aluno ou qualquer outro perfil não autorizado
            return Response(
                {"detail": "Seu perfil não possui dashboards atribuídos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Gerar o token JWT de embedding (HS256)
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": {},
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
