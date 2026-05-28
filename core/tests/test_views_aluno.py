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
from core.models import Aluno, Area, Curso
from core.enums import Unidade, Periodo


# ╔═══════════════════════════════════════════════════════════════════╗
# ║                         FIXTURES                                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

@pytest.fixture
def api_client():
    """
    Cria um cliente HTTP para fazer requisições de teste.
    É como um 'Postman automático' que chama as views direto em memória.
    """
    return APIClient()


@pytest.fixture
def area():
    """Cria uma Area — necessária porque Curso depende dela (FK)."""
    return Area.objects.create(nome="Exatas")


@pytest.fixture
def curso(area):
    """
    Cria um Curso no banco de testes.
    Note que essa fixture DEPENDE da fixture `area` —
    o pytest resolve a cadeia de dependências automaticamente!
    """
    return Curso.objects.create(nome="ADS", areaId=area)


@pytest.fixture
def payload_aluno_valido(curso):
    """
    Payload com todos os campos que a view precisa para criar um aluno.
    `curso` é FK → no JSON, enviamos o ID (inteiro).
    """
    return {
        "nome": "Maria Silva",
        "email": "maria@email.com",
        "senha": "senha123",
        "cpf": "123.456.789-00",
        "is_ativo": True,
        "unidade": Unidade.BARRA.value,
        "curso": curso.id,
    }


@pytest.fixture
def aluno_salvo(curso):
    """
    Cria um Aluno direto via ORM (sem usar a API).
    Útil para cenários de GET onde já precisamos de dados no banco.

    ⚠️ Criamos via ORM de propósito — o teste de GET não deve
    depender do POST estar funcionando.
    """
    return Aluno.objects.create(
        nome="João Santos",
        email="joao@email.com",
        matricula="20260001",
        senha="senha456",
        cpf="987.654.321-00",
        is_ativo=True,
        unidade=Unidade.BOTAFOGO.value,
        periodo=Periodo.TERCEIRO,
        curso=curso,
    )


# ╔═══════════════════════════════════════════════════════════════════╗
# ║                    TESTES DE GET /aluno/                         ║
# ╠═══════════════════════════════════════════════════════════════════╣
# ║  Aqui testamos a LÓGICA que nós escrevemos na view:              ║
# ║  - A listagem retorna os dados serializados corretamente         ║
# ║  - O filtro customizado por ?matricula= funciona                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

@pytest.mark.django_db
class TestAlunoGET:

    def test_filtrar_aluno_por_matricula(self, api_client, aluno_salvo):
        """
        Testa a NOSSA lógica: o filtro ?matricula=X que escrevemos na view.

        Esse filtro é código nosso (linhas 27-29 da view):
            params = request.GET.get('matricula', None)
            if params is not None:
                data = data.filter(matricula=params)

        Se amanhã alguém mudar esse filtro sem querer, o teste pega.
        """
        response = api_client.get("/aluno/", {"matricula": "20260001"})

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["matricula"] == "20260001"

    def test_filtrar_matricula_inexistente_retorna_lista_vazia(self, api_client, aluno_salvo):
        """
        Testa a NOSSA lógica de filtro quando a matrícula não existe.
        Garante que não quebra — retorna lista vazia, não erro.
        """
        response = api_client.get("/aluno/", {"matricula": "99999999"})

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data == []


# ╔═══════════════════════════════════════════════════════════════════╗
# ║                    TESTES DE POST /aluno/                        ║
# ╠═══════════════════════════════════════════════════════════════════╣
# ║  Aqui testamos a LÓGICA que nós escrevemos na view:              ║
# ║  - O aluno é realmente persistido no banco                       ║
# ║  - A resposta tem a mensagem e o status que nós definimos        ║
# ╚═══════════════════════════════════════════════════════════════════╝

@pytest.mark.django_db
class TestAlunoPOST:

    def test_criar_aluno_persiste_no_banco(self, api_client, payload_aluno_valido):
        """
        Testa a NOSSA lógica: o fluxo completo do POST.
        - O serializer.save() realmente persiste no banco?
        - A resposta tem a mensagem que nós definimos?
        - O status é 201 como nós configuramos?

        📚 Note que NÃO testamos se o serializer valida campos —
        isso é trabalho do DRF. Testamos se o NOSSO fluxo funciona:
        parse → validate → save → response.
        """
        response = api_client.post(
            "/aluno/",
            data=payload_aluno_valido,
            format="json",
        )

        # Verifica a resposta que NÓS definimos na view
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Aluno criado com sucesso!"

        # Verifica que realmente persistiu no banco
        assert Aluno.objects.count() == 1
        aluno = Aluno.objects.first()
        assert aluno.nome == "Maria Silva"
        assert aluno.email == "maria@email.com"

    def test_post_invalido_retorna_400(self, api_client):
        """
        Testa a NOSSA lógica: quando o serializer diz que é inválido,
        a view retorna 400 (e não 500, por exemplo).

        📚 Aqui NÃO estamos testando QUAIS erros o serializer retorna
        (isso é trabalho do DRF). Estamos testando que o NOSSO código
        trata corretamente o caso de erro:
            if serializer.is_valid():
                ...
            else:
                return JsonResponse(serializer.errors, status=400)  ← isso aqui
        """
        response = api_client.post(
            "/aluno/",
            data={},
            format="json",
        )

        assert response.status_code == 400


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
