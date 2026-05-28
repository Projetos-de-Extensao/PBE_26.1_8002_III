from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from core.models import Aluno
# Create your views here.

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        usuario = request.data.get('username')
        senha = request.data.get('password')

        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            try:
                aluno = Aluno.objects.get(matricula=usuario)
                if not aluno.is_ativo:
                    return Response({"message": "User is not active"}, status=status.HTTP_403_FORBIDDEN)
            except Aluno.DoesNotExist:
                pass
        
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)