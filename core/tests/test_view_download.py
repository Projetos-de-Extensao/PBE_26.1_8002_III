import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User # Importante para criar o utilizador falso

@pytest.mark.django_db
class TestDownloadDocumentoAPIView:

    def test_acesso_sem_autenticacao(self):
        """Cenário 1: Tentar aceder à rota de download sem estar logado."""
        client = APIClient()
        response = client.get('/documentos/1/download/?tipo=contrato')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_erro_com_tipo_de_documento_invalido(self):
        """Cenário 2: Enviar um 'tipo' que não seja contrato ou relatorio."""
        client = APIClient()
        
        # 1. Cria um utilizador falso na base de dados de teste
        user_teste = User.objects.create_user(username='teste_400', password='123')
        # 2. Força a autenticação do client
        client.force_authenticate(user=user_teste) 
        
        response = client.get('/documentos/1/download/?tipo=foto')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_documento_nao_encontrado(self):
        """Cenário 3: Procurar um ID de contrato que não existe."""
        client = APIClient()
        
        # 1. Cria um utilizador falso na base de dados de teste
        user_teste = User.objects.create_user(username='teste_404', password='123')
        # 2. Força a autenticação do client
        client.force_authenticate(user=user_teste)
        
        response = client.get('/documentos/99999/download/?tipo=contrato')
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_bloqueio_de_idor_aluno_invasor(self):
        """Cenário 4: Segurança - Aluno B tenta baixar documento do Aluno A."""
        client_invasor = APIClient()
        
        # Para este teste funcionar na sua máquina, terá de instanciar 2 alunos:
        # 1. 'aluno_dono' (e criar um Contrato associado a ele)
        # 2. 'aluno_invasor' (e autenticar o client com este utilizador)
        
        # client_invasor.force_authenticate(user=aluno_invasor.user)
        
        # Tentar descarregar o contrato que pertence ao outro colega
        # url = f'/documentos/{contrato_do_aluno_dono.id}/download/?tipo=contrato'
        # response = client_invasor.get(url)
        
        # A View deve levantar um PermissionDenied, que se traduz no Erro 403
        # assert response.status_code == status.HTTP_403_FORBIDDEN
        pass # Remova o 'pass' e descomente as linhas acima após configurar as suas fixtures.