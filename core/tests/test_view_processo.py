import pytest
import json
from rest_framework.test import APIClient
from core.models import Aluno
from core.enums import Unidade, Periodo,StatusProcesso
from core.serializers import *


@pytest.fixture
def processo2(aluno, coordenador, secretaria):
    """Retorna um payload de Processo secundário válido."""
    return {
        "nome_empresa": "Empresa 2 LTDA",
        "status": StatusProcesso.ABERTO.value,
        "matricula_aluno": aluno.matricula,
        "matricula_secretaria": secretaria.matricula,
        "matricula_coordenacao": coordenador.matricula,
    }


@pytest.mark.django_db
class TestPostProcesso:

    def test_aluno_existe_ativo(self,api_client,processo2):
        resp = api_client.post('/processo/',processo2)
        matricula_aluno = processo2['matricula_aluno']
        aluno_db = Aluno.objects.filter(matricula=matricula_aluno).first() 
        assert resp.status_code == 201
        assert aluno_db is not None
        assert aluno_db.is_ativo == True

    def test_aluno_mais_de_um_processo_ativo(self, api_client, secretaria, coordenador):
        aluno_logado = Aluno.objects.get(matricula="TEST0001")
        
        # Cria um processo ativo para o aluno logado
        Processo.objects.create(
            nome_empresa="Empresa 1 LTDA",
            status=StatusProcesso.ABERTO,
            aluno=aluno_logado,
            secretaria=secretaria,
            coordenacao=coordenador
        )
        
        # Tenta criar um segundo processo para o mesmo aluno
        payload = {
            "nome_empresa": "Empresa 2 LTDA",
            "status": StatusProcesso.ABERTO.value,
            "matricula_aluno": aluno_logado.matricula,
            "matricula_secretaria": secretaria.matricula,
            "matricula_coordenacao": coordenador.matricula,
        }
        
        resp = api_client.post('/processo/', payload)
        
        assert resp.status_code == 400
        assert "status" in resp.data
        assert "O aluno já tem processos em aberto" in resp.data["status"]


@pytest.mark.django_db
class TestGetProcesso:

    def test_pesquisar_processo_matricula(self, api_client, processo):
        response = api_client.get('/processo/', {'matricula_aluno': processo.aluno.matricula})
        assert response.status_code == 200
        data = response.data['results']
        assert len(data) == 1
        assert data[0]['nome_empresa'] == processo.nome_empresa

    def test_pesquisar_processo_status(self, api_client, processo):
        response = api_client.get('/processo/', {'status': processo.status})
        assert response.status_code == 200
        data = response.data['results']
        assert len(data) == 1

    def test_pesquisar_processo_nome_empresa(self, api_client, processo):
        response = api_client.get('/processo/', {'nome_empresa': 'Teste'})
        assert response.status_code == 200
        data = response.data['results']
        assert len(data) == 1


@pytest.mark.django_db
class TestPatchProcesso:

    def test_atualizar_processo_sucesso(self, api_client, processo):
        payload = {
            "nome_empresa": "Empresa Modificada LTDA"
        }
        response = api_client.patch(f'/processo/?processo_id={processo.id}', payload)
        assert response.status_code == 200
        assert response.data["message"] == "updated"
        processo.refresh_from_db()
        assert processo.nome_empresa == "Empresa Modificada LTDA"

    def test_atualizar_processo_nao_encontrado(self, api_client):
        payload = {
            "nome_empresa": "Não Existe"
        }
        response = api_client.patch('/processo/?processo_id=9999', payload)
        assert response.status_code == 404
        assert response.data["error"] == "Processo não encontrado"

    def test_atualizar_processo_sem_id(self, api_client):
        payload = {
            "nome_empresa": "Sem ID"
        }
        response = api_client.patch('/processo/', payload)
        assert response.status_code == 400
        assert response.data["error"] == "Id não informado"

    def test_atualizar_processo_mesmo_aluno_e_status_aberto(self, api_client, processo):
        """Verifica se a validação do ProcessoSerializer permite atualizar o processo sem disparar erro de 'processo em aberto' para si mesmo."""
        payload = {
            "nome_empresa": "Empresa Modificada 2 LTDA",
            "matricula_aluno": processo.aluno.matricula,
            "status": "aberto"
        }
        response = api_client.patch(f'/processo/?processo_id={processo.id}', payload)
        assert response.status_code == 200
        assert response.data["message"] == "updated"

    
    

    
    
