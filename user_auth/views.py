from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from core.models import Aluno, Coordenador, Secretaria

from .serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    PrimeiroAcessoRequestSerializer,
    MessageResponseSerializer,
)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login",
        description="Autentica com matrícula e senha. Retorna tokens JWT.",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Matrícula ou senha inválidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.precisa_redefinir_senha:
            return Response(
                {
                    "error": "primeiro_acesso",
                    "message": "Você precisa redefinir sua senha antes de continuar.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class PrimeiroAcessoAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Primeiro acesso — redefinição de senha",
        description=(
            "Troca a senha temporária pela senha definitiva. "
            "Após isso, `precisa_redefinir_senha` é marcado como False "
            "e o usuário pode fazer login normalmente."
        ),
        request=PrimeiroAcessoRequestSerializer,
        responses={200: MessageResponseSerializer},
    )
    def post(self, request):
        serializer = PrimeiroAcessoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        user = authenticate(request, username=username, password=old_password)
        if user is None:
            return Response(
                {"error": "Matrícula ou senha temporária inválidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.set_password(new_password)
        user.precisa_redefinir_senha = False
        user.save(update_fields=["password", "precisa_redefinir_senha"])

        return Response(
            {"message": "Senha redefinida com sucesso. Faça login para continuar."},
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    """Invalida o refresh token (blacklist)."""

    @extend_schema(
        summary="Logout",
        description="Invalida o refresh token. Requer `refresh` no body.",
        responses={204: None},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Token de refresh não informado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"error": "Token inválido ou já expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)