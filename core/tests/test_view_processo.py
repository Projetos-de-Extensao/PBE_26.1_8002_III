import pytest
import json
from rest_framework.test import APIClient
from core.models import Aluno
from core.enums import Unidade, Periodo,StatusProcesso
from core.serializers import *


@pytest.fixture
def processo2(aluno):
    """Retorna um payload de Processo secundário válido."""
    return {
        "nome_empresa": "Empresa 2 LTDA",
        "status": StatusProcesso.ABERTO.value,
        "matricula_aluno": aluno.matricula,
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

    def test_aluno_mais_de_um_processo_ativo(self,api_client,aluno,processo,processo2):
        resp = api_client.post('/processo/',processo2)
        matricula_aluno = processo2['matricula_aluno']
        processos = Processo.objects.all()
        ultimo_processo = processos.filter(matricula_aluno=matricula_aluno, status=StatusProcesso.ABERTO)

        assert resp.status_code == 400
        assert ultimo_processo.exists() == True
        assert ultimo_processo.count() == 1

    
    

    
    
