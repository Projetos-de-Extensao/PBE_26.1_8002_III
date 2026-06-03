from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from rest_framework.request import Request
import logging
from django.contrib.auth.hashers import make_password

from core.models import Aluno

def get_client_ip(request: Request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request: Request):
        usuario = request.data.get('username')
        senha = request.data.get('password')
        ip = get_client_ip(request)

        cache_key = f"login_attempts_{ip}_{usuario}"
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            return Response(
                {"message": "Muitas tentativas falhas. Conta bloqueada temporariamente por 15 minutos."}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            cache.delete(cache_key)

            try:
                aluno = Aluno.objects.get(matricula=usuario)
                if not aluno.is_ativo:
                    return Response(
                        {"message": "Conta desativada. Por favor, entre em contato com a secretaria."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                if aluno.precisa_redefinir_senha:
                    return Response(
                        {"message": "Você precisa redefinir sua senha antes de continuar."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Aluno.DoesNotExist:
                pass
        
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
            
        else:
            attempts += 1
            cache.set(cache_key, attempts, timeout=900)
            
            return Response(
                {"message": f"Credenciais inválidas. Tentativa {attempts}/5."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


logger = logging.getLogger(__name__)

class PrimeiroAcessoAPIView(APIView):
    
    authentication_classes = []
    permission_classes = []

    def post(self, request: Request):
        usuario = request.data.get('username')
        senha_atual = request.data.get('old_password')
        nova_senha = request.data.get('new_password')

        user = authenticate(request, username=usuario, password=senha_atual)
        
        if user is not None:
            try:
                aluno = Aluno.objects.get(matricula=usuario)
                
                if not aluno.precisa_redefinir_senha:
                    return Response({"message": "Sua conta já realizou o primeiro acesso."}, status=status.HTTP_400_BAD_REQUEST)

                aluno.senha = make_password(nova_senha)
                aluno.precisa_redefinir_senha = False
                aluno.save()

                user.set_password(nova_senha)
                user.save()

                logger.info(f"[SEGURANÇA] O aluno com matrícula {usuario} concluiu a redefinição de senha do primeiro acesso.")

                return Response({"message": "Senha redefinida com sucesso! Agora você pode fazer o login normalmente."}, status=status.HTTP_200_OK)

            except Aluno.DoesNotExist:
                return Response({"message": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Credenciais atuais inválidas."}, status=status.HTTP_401_UNAUTHORIZED)