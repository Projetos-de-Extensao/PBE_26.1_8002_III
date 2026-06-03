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
        
        data = response.data
        assert len(data) == 1
        assert data[0]['matricula'] == aluno.matricula
        assert data[0]['nome'] == aluno.nome
        assert data[0]['email'] == aluno.email
        
        # Valida os processos retornados
        nomes_empresas = [p['nome_empresa'] for p in data[0]['processos']]
        assert len(nomes_empresas) == 2
        assert processo.nome_empresa in nomes_empresas
        assert processo_concluido.nome_empresa in nomes_empresas
      
         
        









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
