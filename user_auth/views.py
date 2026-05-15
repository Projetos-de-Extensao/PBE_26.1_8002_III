from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class LoginAPIView(APIView):
    def post(self, request):
        usuario = request.data.get('username')
        senha = request.data.get('password')

        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({"message": "Invalid credentials"}, status= status.HTTP_401_UNAUTHORIZED)
