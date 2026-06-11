from rest_framework.permissions import BasePermission
from .models import Aluno, Secretaria, Coordenador


class IsAluno(BasePermission):
    """
    Verifica se o usuário autenticado via JWT pertence ao grupo 'Aluno'.
    Como essa validação é chamada a cada request, utilizamos cache na própria
    instância do request (`_cached_is_aluno`) para não sobrecarregar o banco
    quando a mesma permissão for chamada mais de uma vez durante o fluxo.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Cache para evitar queries repetidas no mesmo request
        if not hasattr(request, '_cached_is_aluno'):
            request._cached_is_aluno = hasattr(request.user, 'aluno')
        return request._cached_is_aluno
    
class IsCoordenador(BasePermission):
    """
    Garante que o endpoint só será acessível por Coordenadores (ex: Avaliar Relatórios).
    Também possui mecanismo de cache por request para performance.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request, '_cached_is_coordenador'):
            request._cached_is_coordenador = hasattr(request.user, 'coordenador')
        return request._cached_is_coordenador
    
class IsSecretaria(BasePermission):
    """
    Garante que o endpoint só será acessível pela Secretaria (ex: Validar Contratos).
    Utiliza cache no nível de requisição para evitar latência desnecessária.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request, '_cached_is_secretaria'):
            request._cached_is_secretaria = hasattr(request.user, 'secretaria')
        return request._cached_is_secretaria
