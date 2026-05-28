from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from rest_framework.request import Request

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