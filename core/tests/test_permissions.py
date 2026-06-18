"""
Testes de Permissão — garantir que usuários sem perfil recebem 403.

Cobre os cenários:
- Usuário não autenticado recebe 401
- Usuário autenticado SEM perfil de Aluno/Secretaria/Coordenador recebe 403
- Aluno não acessa rotas exclusivas de Secretaria
- Secretaria não acessa rotas exclusivas de Coordenador
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient

User = get_user_model()

from core.models import Aluno, Secretaria, Coordenador, Area, Curso
from core.enums import Unidade


# ── Fixtures específicas ─────────────────────────────────────────────

@pytest.fixture
def usuario_sem_perfil():
    """User do Django sem nenhum perfil (Aluno/Secretaria/Coordenador)."""
    user = User.objects.create(
        matricula="sem_perfil",
        nome="Sem Perfil",
        email="ninguem@ibmec.edu.br",
        password=make_password("test1234"),
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def usuario_aluno_only():
    """User do Django com perfil APENAS de Aluno."""
    user = User.objects.create(
        matricula="aluno_only",
        nome="Aluno Only",
        email="aluno_only@ibmec.edu.br",
        password=make_password("test1234"),
    )
    # Criar coordenador e área/curso necessários para o Aluno
    coord = Coordenador.objects.create(
        matricula="PERM_COORD01",
        nome="Coord Permissão",
        email="coord_perm@ibmec.edu.br",
        password=make_password("test"),
        unidade=Unidade.BARRA.value,
    )
    area = Area.objects.create(nome="PermArea", coordenador=coord)
    curso = Curso.objects.create(nome="PermCurso", areaId=area)

    Aluno.objects.create(
        usuario_ptr=user,
        matricula="PERM_ALU01",
        nome="Aluno Perm",
        email="aluno_only@ibmec.edu.br",
        password=make_password("test"),
        cpf="98765432100",
        unidade=Unidade.BARRA.value,
        curso=curso,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def usuario_secretaria_only():
    """User do Django com perfil APENAS de Secretaria."""
    user = User.objects.create(
        matricula="sec_only",
        nome="Sec Only",
        email="sec_only@ibmec.edu.br",
        password=make_password("test1234"),
    )
    Secretaria.objects.create(
        usuario_ptr=user,
        matricula="PERM_SEC01",
        nome="Sec Perm",
        email="sec_only@ibmec.edu.br",
        password=make_password("test"),
        unidade=Unidade.BARRA.value,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ── Testes ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUsuarioNaoAutenticado:

    def test_acesso_sem_autenticacao_processo(self):
        """Usuário não autenticado recebe 401 ao acessar /processo/."""
        client = APIClient()
        response = client.get("/processo/")
        assert response.status_code == 401

    def test_acesso_sem_autenticacao_aluno(self):
        """Usuário não autenticado recebe 401 ao acessar /aluno/."""
        client = APIClient()
        response = client.get("/aluno/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestUsuarioSemPerfil:

    def test_sem_perfil_acessa_processo_recebe_403(self, usuario_sem_perfil):
        """Usuário autenticado sem perfil recebe 403 ao acessar /processo/."""
        response = usuario_sem_perfil.get("/processo/")
        assert response.status_code == 403

    def test_sem_perfil_acessa_aluno_recebe_403(self, usuario_sem_perfil):
        """Usuário autenticado sem perfil recebe 403 ao acessar /aluno/."""
        response = usuario_sem_perfil.get("/aluno/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestPermissaoPorPerfil:

    def test_aluno_acessa_rota_aluno_list(self, usuario_aluno_only):
        """Aluno PODE acessar /aluno/ para ver seus próprios dados (status 200)."""
        response = usuario_aluno_only.get("/aluno/")
        assert response.status_code == 200

    def test_secretaria_nao_acessa_rota_de_coordenador(self, usuario_secretaria_only, processo, relatorio):
        """Secretaria não pode avaliar relatórios (rota de Coordenador)."""
        payload = {
            "observacoes": "Tentativa indevida.",
            "veredito": "aprovado",
            "avaliador": 1,
            "relatorio_id": relatorio.id,
        }
        response = usuario_secretaria_only.post("/relatorio/avaliar/", payload)
        assert response.status_code == 403
