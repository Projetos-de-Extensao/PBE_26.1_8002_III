"""
=======================================================================
TESTES DA VIEW DE ALUNO — usando pytest + pytest-django
=======================================================================

📚 PRINCÍPIO FUNDAMENTAL:
---------------------------------------------------------------------------
  "Não teste o framework — teste o SEU código."

  O Django e o DRF já são exaustivamente testados pelos seus
  mantenedores. Não precisamos verificar se:
    ❌ EmailField rejeita e-mails inválidos
    ❌ choices rejeita valores fora do enum
    ❌ campos required retornam erro quando ausentes

  O que SIM precisamos testar é a LÓGICA QUE NÓS ESCREVEMOS:
    ✅ O filtro por matrícula (?matricula=X) funciona corretamente
    ✅ O POST realmente persiste o aluno no banco
    ✅ A resposta do POST tem a mensagem e status que definimos
    ✅ O GET retorna os dados serializados que esperamos
---------------------------------------------------------------------------

📚 CONCEITOS IMPORTANTES:
---------------------------------------------------------------------------
1. FIXTURES (@pytest.fixture)
   - São funções que preparam dados reutilizáveis para os testes.
   - O pytest injeta automaticamente pelo nome do parâmetro.

2. @pytest.mark.django_db
   - Sem esse decorator, o pytest NÃO deixa acessar o banco.
   - Cria um banco temporário destruído ao final de cada teste.

3. APIClient (do rest_framework.test)
   - Cliente HTTP fake que simula requisições sem subir o servidor.

4. ESTRUTURA DE UM TESTE (Arrange → Act → Assert)
   - Arrange: prepara os dados necessários
   - Act: executa a ação que você quer testar
   - Assert: verifica se o resultado é o esperado
---------------------------------------------------------------------------
"""

import pytest
import json
from rest_framework.test import APIClient
from core.models import Aluno
from core.enums import Unidade, Periodo





@pytest.mark.django_db
class TestGetAluno():

    def test_pesquisar_aluno_matricula(self, api_client, aluno, processo, processo_concluido):

        response = api_client.get('/aluno/', {'matricula': '20260001'})
        assert response.status_code == 200
        
        data = response.data['results']
        assert len(data) == 1
        assert data[0]['matricula'] == aluno.matricula
        assert data[0]['nome'] == aluno.nome
        assert data[0]['email'] == aluno.email
        
        # Valida os processos retornados
        nomes_empresas = [p['nome_empresa'] for p in data[0]['processos']]
        assert len(nomes_empresas) == 2
        assert processo.nome_empresa in nomes_empresas
        assert processo_concluido.nome_empresa in nomes_empresas


@pytest.mark.django_db
class TestPostAluno:

    def test_criar_aluno_sucesso(self, api_client, curso):
        payload = {
            "nome": "Pedro Santos",
            "email": "pedro@ibmec.edu.br",
            "matricula": "20260002",
            "senha": "senha_segura_123",
            "cpf": "123.456.789-09",
            "is_ativo": True,
            "unidade": Unidade.BARRA.value,
            "periodo": Periodo.PRIMEIRO.value,
            "curso": curso.id
        }
        response = api_client.post('/aluno/', payload)
        assert response.status_code == 201
        assert response.data["detail"] == "Aluno criado com sucesso!"
        assert Aluno.objects.filter(matricula="20260002").exists()


@pytest.mark.django_db
class TestPatchAluno:

    def test_atualizar_aluno_sucesso(self, api_client, aluno):
        payload = {
            "nome": "João Santos Atualizado"
        }
        response = api_client.patch(f'/aluno/?matricula_aluno={aluno.matricula}', payload)
        assert response.status_code == 200
        assert response.data["detail"] == "updated"
        aluno.refresh_from_db()
        assert aluno.nome == "João santos atualizado"

    def test_atualizar_aluno_nao_encontrado(self, api_client):
        payload = {
            "nome": "Não Existe"
        }
        response = api_client.patch('/aluno/?matricula_aluno=inexistente', payload)
        assert response.status_code == 404
        assert response.data["detail"] == "Aluno não encontrado"

    def test_atualizar_aluno_sem_matricula(self, api_client):
        payload = {
            "nome": "Não Envia Matricula"
        }
        response = api_client.patch('/aluno/', payload)
        assert response.status_code == 400
        assert response.data["detail"] == "Matrícula não informada"


@pytest.mark.django_db
class TestAlunoGradeAPIView:

    def test_get_grade_inicial_vazia(self, api_client):
        # O aluno autenticado pela fixture api_client não tem horários inicialmente
        response = api_client.get('/aluno/grade/')
        assert response.status_code == 200
        assert response.data == []

    def test_patch_grade_sucesso(self, api_client, horario_segunda_manha, horario_terca_noite):
        # Atualiza a grade horária com alguns slots
        payload = [
            {"dia": "segunda", "turno": "manha"},
            {"dia": "terca", "turno": "noite"}
        ]
        response = api_client.patch('/aluno/grade/', payload, format='json')
        assert response.status_code == 200
        
        # Verifica o retorno serializado
        assert len(response.data) == 2
        dias_retornados = [item['dia'] for item in response.data]
        turnos_retornados = [item['turno'] for item in response.data]
        assert "segunda" in dias_retornados
        assert "manha" in turnos_retornados
        assert "terca" in dias_retornados
        assert "noite" in turnos_retornados

        # Verifica se persistiu no banco para o Aluno correto
        from core.models import Aluno
        aluno_inst = Aluno.objects.get(email="testuser@ibmec.edu.br")
        assert aluno_inst.grade.count() == 2

    def test_patch_grade_invalida(self, api_client):
        # Envia turnos/dias inválidos
        payload = [
            {"dia": "domingo", "turno": "manha"},
        ]
        response = api_client.patch('/aluno/grade/', payload, format='json')
        assert response.status_code == 400
        assert "Dia 'domingo' ou Turno 'manha' inválido." in response.data["detail"]


# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      O QUE NÃO TESTAMOS                         ║
# ╠═══════════════════════════════════════════════════════════════════╣
# ║                                                                   ║
# ║  ❌ Validação de EmailField        → DRF já testa                ║
# ║  ❌ Validação de choices (enum)    → DRF já testa                ║
# ║  ❌ Validação de campos required   → DRF já testa                ║
# ║  ❌ Validação de unique            → Django ORM já testa         ║
# ║                                                                   ║
# ║  Esses comportamentos são do FRAMEWORK, não do nosso código.     ║
# ║  Se o DRF mudar como valida e-mail, o problema é deles, não      ║
# ║  nosso. Nossos testes devem quebrar só quando NOSSO código muda. ║
# ║                                                                   ║
# ╚═══════════════════════════════════════════════════════════════════╝
#
# Para rodar:
#   uv run pytest core/tests/test_views_aluno.py -v
#
# Flags úteis:
#   -v          → mostra o nome de cada teste (verbose)
#   -s          → mostra prints dentro dos testes
#   -x          → para no primeiro erro
#   --tb=short  → traceback resumido
#   -k "filtrar"→ roda só testes que contêm "filtrar" no nome
