from rest_framework.permissions import BasePermission
from .models import Aluno, Secretaria, Coordenador

class IsAluno(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return Aluno.objects.filter(email=request.user.email).exists()
    
class IsCoordenador(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return Coordenador.objects.filter(email=request.user.email).exists()
    
class IsSecretaria(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return Secretaria.objects.filter(email=request.user.email).exists()

