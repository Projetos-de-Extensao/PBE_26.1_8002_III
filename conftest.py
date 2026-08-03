"""
Fixtures globais do projeto — disponíveis para TODOS os arquivos de teste.

Cada fixture cria 1 instância de um model concreto via ORM.
O pytest resolve as dependências automaticamente pela cadeia de fixtures.
"""

import os
os.environ["DEBUG"] = "True"
os.environ.setdefault("GEMINI_API_KEY", "dummy-api-key-for-tests")

import pytest
from datetime import date
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient

from core.models import (
    Area, Curso, Aluno, Coordenador, Secretaria,
    Processo, Contrato, Relatorio,
    HistoricoAvaliacaoRelatorio, HistoricoAvaliacaoContrato,
    Horarios, EmailLog,
)
from core.enums import (
    Unidade, Periodo, StatusProcesso, StatusContrato,
    StatusRelatorio, Veredito, Turno, DiasDaSemana,
)


# ── Email backend para testes (evita conexão SMTP real) ───────────────

@pytest.fixture(autouse=True)
def _use_locmem_email_backend(settings):
    """Força o uso do backend in-memory em todos os testes."""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


# ── Cliente HTTP (autenticado com todas as permissões) ────────────────

@pytest.fixture
def api_client():
    """
    Cliente HTTP autenticado que passa em TODAS as permissões
    (IsSecretaria, IsAluno, IsCoordenador).

    As permissões customizadas verificam:
        Model.objects.filter(email=request.user.email).exists()

    Por isso criamos registros de Secretaria, Aluno e Coordenador
    todos com o mesmo email do User do Django.
    Esses registros são exclusivos do client — não conflitam com
    as fixtures de model (que usam emails diferentes).
    """
    EMAIL_TEST = "testuser@ibmec.edu.br"

    from django.contrib.auth import get_user_model
    User = get_user_model()
    from django.contrib.auth.hashers import make_password

    # User do Django (agora é o nosso core.Usuario)
    user = User.objects.create(
        matricula="TEST0001",
        nome="Test User",
        email=EMAIL_TEST,
        password=make_password("test1234"),
    )

    coord_test = Coordenador.objects.create(
        usuario_ptr=user,
        matricula="TEST0001",
        nome="Test User",
        email=EMAIL_TEST,
        password=make_password("test"),
        unidade=Unidade.BARRA.value,
    )

    area_test = Area.objects.create(nome="TestArea", coordenador=coord_test)
    curso_test = Curso.objects.create(nome="TestCurso", areaId=area_test)

    # 2. Aluno
    aluno_test = Aluno.objects.create(
        usuario_ptr=user,
        matricula="TEST0001",
        nome="Test User",
        email=EMAIL_TEST,
        password=make_password("test"),
        cpf="45678912364",
        unidade=Unidade.BARRA.value,
        curso=curso_test,
    )

    # 3. Secretaria
    secretaria_test = Secretaria.objects.create(
        usuario_ptr=user,
        matricula="TEST0001",
        nome="Test User",
        email=EMAIL_TEST,
        password=make_password("test"),
        unidade=Unidade.BARRA.value,
    )

    import jwt
    from django.conf import settings
    token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    client.force_authenticate(user=user)
    return client

# ── Coordenador (sem FK extra) ───────────────────────────────────────

@pytest.fixture
def coordenador():
    """Cria um Coordenador."""
    from django.contrib.auth.hashers import make_password
    return Coordenador.objects.create(
        matricula="COORD0001",
        nome="Prof. Orientador",
        email="coordenador@ibmec.edu.br",
        password=make_password("senha123"),
        unidade=Unidade.BOTAFOGO.value,
    )


# ── Area (depende de Coordenador via OneToOne) ───────────────────────

@pytest.fixture
def area(coordenador):
    """Cria uma Area (depende de Coordenador via OneToOne)."""
    return Area.objects.create(nome="Exatas", coordenador=coordenador)


# ── Models que dependem de Area ───────────────────────────────────────

@pytest.fixture
def curso(area):
    """Cria um Curso (depende de Area via FK)."""
    return Curso.objects.create(nome="ADS", areaId=area)


# ── Models que dependem de Curso ──────────────────────────────────────

@pytest.fixture
def aluno(curso):
    """Cria um Aluno (depende de Curso via FK)."""
    from django.contrib.auth.hashers import make_password
    return Aluno.objects.create(
        matricula="20260001",
        nome="João Santos",
        email="joao@ibmec.edu.br",
        password=make_password("senha456"),
        cpf="12345678909",
        is_ativo=True,
        unidade=Unidade.BOTAFOGO.value,
        periodo=Periodo.TERCEIRO,
        curso=curso,
    )


# ── Secretaria (sem FK extra) ────────────────────────────────────────

@pytest.fixture
def secretaria():
    """Cria uma Secretaria."""
    from django.contrib.auth.hashers import make_password
    return Secretaria.objects.create(
        matricula="SEC0001",
        nome="Ana Secretaria",
        email="secretaria@ibmec.edu.br",
        password=make_password("senha789"),
        unidade=Unidade.BARRA.value,
    )


# ── Processo (depende de Aluno, Coordenador e Secretaria) ────────────

@pytest.fixture
def processo(aluno, coordenador, secretaria):
    """Cria um Processo (depende de Aluno, Coordenador e Secretaria via FK)."""
    return Processo.objects.create(
        nome_empresa="Empresa Teste LTDA",
        status=StatusProcesso.ABERTO,
        aluno=aluno,
        coordenacao=coordenador,
        secretaria=secretaria,
    )


@pytest.fixture
def processo_concluido(aluno, coordenador, secretaria):
    """Cria um Processo concluído (depende de Aluno, Coordenador e Secretaria)."""
    return Processo.objects.create(
        nome_empresa="Empresa Antiga LTDA",
        status=StatusProcesso.CONCLUIDO,
        aluno=aluno,
        coordenacao=coordenador,
        secretaria=secretaria,
    )


# ── Contrato (depende de Processo) ───────────────────────────────────

@pytest.fixture
def contrato(processo):
    """Cria um Contrato (depende de Processo via FK)."""
    arquivo_fake = SimpleUploadedFile("contrato.pdf", b"conteudo fake", content_type="application/pdf")
    return Contrato.objects.create(
        arquivo=arquivo_fake,
        data_upload=date(2026, 5, 1),
        cnpj_empresa="12345678000199",
        nome_empresa="Empresa Teste LTDA",
        data_inicio=date(2026, 6, 1),
        data_termino=date(2026, 12, 1),
        apolice_seguro="AP-0001",
        plano_atividade=True,
        assinatura_aluno=True,
        assinatura_empresa=True,
        assinatura_faculdade=False,
        processoId=processo,
        status=StatusContrato.PENDENTE,
    )


# ── Relatorio (depende de Processo) ──────────────────────────────────

@pytest.fixture
def relatorio(processo):
    """Cria um Relatorio (depende de Processo via FK)."""
    arquivo_fake = SimpleUploadedFile("relatorio.pdf", b"conteudo fake", content_type="application/pdf")
    return Relatorio.objects.create(
        processo_id=processo,
        arquivo=arquivo_fake,
        data_upload=date(2026, 5, 15),
        status=StatusRelatorio.PENDENTE,
    )


# ── Históricos de Avaliação ──────────────────────────────────────────

@pytest.fixture
def historico_avaliacao_relatorio(coordenador, relatorio):
    """Cria um HistoricoAvaliacaoRelatorio (depende de Coordenador e Relatorio)."""
    return HistoricoAvaliacaoRelatorio.objects.create(
        observacoes="Relatório dentro dos padrões.",
        veredito=Veredito.APROVADO,
        avaliador=coordenador,
        relatorio_id=relatorio,
    )


@pytest.fixture
def historico_avaliacao_contrato(secretaria, contrato):
    """Cria um HistoricoAvaliacaoContrato (depende de Secretaria e Contrato)."""
    return HistoricoAvaliacaoContrato.objects.create(
        observacoes="Contrato com documentação completa.",
        veredito=Veredito.APROVADO,
        avaliador=secretaria,
        contrato_id=contrato,
        justificativa="Documentação em ordem.",
    )


# ── Horários ─────────────────────────────────────────────────────────

@pytest.fixture
def horario_segunda_manha():
    """Cria um Horario: Segunda - Manhã."""
    return Horarios.objects.create(dia=DiasDaSemana.SEGUNDA, turno=Turno.MANHA)


@pytest.fixture
def horario_segunda_tarde():
    """Cria um Horario: Segunda - Tarde."""
    return Horarios.objects.create(dia=DiasDaSemana.SEGUNDA, turno=Turno.TARDE)


@pytest.fixture
def horario_terca_noite():
    """Cria um Horario: Terça - Noite."""
    return Horarios.objects.create(dia=DiasDaSemana.TERCA, turno=Turno.NOITE)


@pytest.fixture
def horario_quarta_manha():
    """Cria um Horario: Quarta - Manhã."""
    return Horarios.objects.create(dia=DiasDaSemana.QUARTA, turno=Turno.MANHA)


@pytest.fixture
def horario_quinta_tarde():
    """Cria um Horario: Quinta - Tarde."""
    return Horarios.objects.create(dia=DiasDaSemana.QUINTA, turno=Turno.TARDE)