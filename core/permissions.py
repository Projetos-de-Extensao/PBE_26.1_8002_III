from rest_framework.permissions import BasePermission
from .models import Aluno, Secretaria, Coordenador


class IsAluno(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Cache para evitar queries repetidas no mesmo request
        if not hasattr(request, '_cached_is_aluno'):
            request._cached_is_aluno = Aluno.objects.filter(email=request.user.email).exists()
        return request._cached_is_aluno
    
class IsCoordenador(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request, '_cached_is_coordenador'):
            request._cached_is_coordenador = Coordenador.objects.filter(email=request.user.email).exists()
        return request._cached_is_coordenador
    
class IsSecretaria(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request, '_cached_is_secretaria'):
            request._cached_is_secretaria = Secretaria.objects.filter(email=request.user.email).exists()
        return request._cached_is_secretaria
