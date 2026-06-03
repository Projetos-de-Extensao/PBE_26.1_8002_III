"""
Fixtures globais do projeto — disponíveis para TODOS os arquivos de teste.

Cada fixture cria 1 instância de um model concreto via ORM.
O pytest resolve as dependências automaticamente pela cadeia de fixtures.
"""

import pytest
from datetime import date
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from core.models import (
    Area, Curso, Aluno, Coordenador, Secretaria,
    Processo, Contrato, Relatorio,
    HistoricoAvaliacaoRelatorio, HistoricoAvaliacaoContrato,
)
from core.enums import (
    Unidade, Periodo, StatusProcesso, StatusContrato,
    StatusRelatorio, Veredito,
)


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
    EMAIL_TEST = "testuser@test.com"

    # User do Django (necessário para autenticação)
    user = User.objects.create_user(
        username="testuser",
        email=EMAIL_TEST,
        password="test1234",
    )

    # Registros para satisfazer cada permissão customizada
    area_test = Area.objects.create(nome="TestArea")
    curso_test = Curso.objects.create(nome="TestCurso", areaId=area_test)

    Aluno.objects.create(
        matricula="TEST0001", nome="Test User", email=EMAIL_TEST,
        senha="test", cpf="000.000.000-00", unidade=Unidade.BARRA.value,
        curso=curso_test,
    )
    Secretaria.objects.create(
        matricula="TEST0002", nome="Test User", email=EMAIL_TEST,
        senha="test", unidade=Unidade.BARRA.value,
    )
    Coordenador.objects.create(
        matricula="TEST0003", nome="Test User", email=EMAIL_TEST,
        senha="test", unidade=Unidade.BARRA.value, areaId=area_test,
    )

    import jwt
    from django.conf import settings
    token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    client.force_authenticate(user=user)
    return client

# ── Models independentes ──────────────────────────────────────────────

@pytest.fixture
def area():
    """Cria uma Area."""
    return Area.objects.create(nome="Exatas")


# ── Models que dependem de Area ───────────────────────────────────────

@pytest.fixture
def curso(area):
    """Cria um Curso (depende de Area via FK)."""
    return Curso.objects.create(nome="ADS", areaId=area)


@pytest.fixture
def coordenador(area):
    """Cria um Coordenador (depende de Area via FK)."""
    return Coordenador.objects.create(
        matricula="COORD0001",
        nome="Prof. Orientador",
        email="coordenador@email.com",
        senha="senha123",
        unidade=Unidade.BOTAFOGO.value,
        areaId=area,
    )


# ── Models que dependem de Curso ──────────────────────────────────────

@pytest.fixture
def aluno(curso):
    """Cria um Aluno (depende de Curso via FK)."""
    return Aluno.objects.create(
        matricula="20260001",
        nome="João Santos",
        email="joao@email.com",
        senha="senha456",
        cpf="987.654.321-00",
        is_ativo=True,
        unidade=Unidade.BOTAFOGO.value,
        periodo=Periodo.TERCEIRO,
        curso=curso,
    )


# ── Secretaria (sem FK extra) ────────────────────────────────────────

@pytest.fixture
def secretaria():
    """Cria uma Secretaria."""
    return Secretaria.objects.create(
        matricula="SEC0001",
        nome="Ana Secretaria",
        email="secretaria@email.com",
        senha="senha789",
        unidade=Unidade.BARRA.value,
    )


# ── Processo (depende de Aluno) ──────────────────────────────────────

@pytest.fixture
def processo(aluno):
    """Cria um Processo (depende de Aluno via FK)."""
    return Processo.objects.create(
        nome_empresa="Empresa Teste LTDA",
        status=StatusProcesso.ABERTO,
        matricula_aluno=aluno,
    )


@pytest.fixture
def processo_concluido(aluno):
    """Cria um Processo concluído/encerrado (depende de Aluno via FK)."""
    return Processo.objects.create(
        nome_empresa="Empresa Antiga LTDA",
        status=StatusProcesso.CONCLUIDO,
        matricula_aluno=aluno,
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
        horas_trabalhadas=120,
        data_inicio=date(2026, 3, 1),
        data_termino=date(2026, 5, 1),
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
    )