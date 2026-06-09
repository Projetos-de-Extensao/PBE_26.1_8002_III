import pytest
from core.models import Processo, Contrato, Relatorio
from datetime import date
from core.enums import StatusRelatorio, StatusContrato
from core.validators import valida_periodo_relatorio


@pytest.fixture
def relatorio_nao_aprovado(processo):
    """Cria um Relatorio via ORM (depende de Processo via FK)."""
    return Relatorio.objects.create(
        processo_id=processo,
        arquivo=None,
        data_upload=date(2025, 5, 15),
        horas_trabalhadas=120,
        data_inicio=date(2025, 7, 1),
        data_termino=date(2025, 12, 1),
        status=StatusRelatorio.PENDENTE,
    )

@pytest.fixture
def contrato_atual(processo):
    """Cria um Contrato (depende de Processo via FK)."""
   
    return Contrato.objects.create(
        arquivo=None,
        data_upload=date(2026, 5, 1),
        cnpj_empresa="12345678000199",
        nome_empresa="Empresa Teste LTDA",
        data_inicio=date(2025, 6, 1),
        data_termino=date(2025, 5, 1),
        apolice_seguro="AP-0001",
        plano_atividade=True,
        assinatura_aluno=True,
        assinatura_empresa=True,
        assinatura_faculdade=False,
        processoId=processo,
        status=StatusContrato.PENDENTE,
    )



@pytest.mark.django_db
class TestModelProcesso:
    
    def test_valida_periodo_relatorio(self, processo, relatorio_nao_aprovado, contrato_atual):
        data_inicio_prevista = contrato_atual.data_inicio
        data_termino_prevista = contrato_atual.data_termino
        
        data_inicio_relatorio = relatorio_nao_aprovado.data_inicio
        data_termino_relatorio = relatorio_nao_aprovado.data_termino

        # Valida as asserções usando o objeto de relatório criado
        assert valida_periodo_relatorio(relatorio=relatorio_nao_aprovado, contrato=contrato_atual) == False
        assert (data_inicio_prevista <= data_inicio_relatorio) is True
        assert (data_termino_relatorio <= data_termino_prevista) is False








