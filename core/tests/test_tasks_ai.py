import pytest
from unittest.mock import patch, MagicMock
from celery.exceptions import Retry
from core.models import Contrato, Relatorio
from core.tasks import processarContratoComIa, processarRelatorioComIa, avaliarRelatorioComIa

@pytest.mark.django_db
@patch('core.tasks.processarContratoComIa.retry')
@patch('core.tasks.lerContrato')
@patch('core.tasks.ler_pdf_modo_layout')
def test_processar_contrato_com_ia_retry_on_timeout(mock_pdf, mock_ler_contrato, mock_retry, contrato):
    mock_pdf.return_value = "texto fake do contrato"
    mock_ler_contrato.side_effect = Exception("AI Connection Timeout")
    mock_retry.side_effect = Retry()

    with pytest.raises(Retry):
        processarContratoComIa(contrato.id)

    mock_retry.assert_called_once()
    kwargs = mock_retry.call_args.kwargs
    assert kwargs['countdown'] == 60
    assert "AI Connection Timeout" in str(kwargs['exc'])


@pytest.mark.django_db
@patch('core.tasks.processarRelatorioComIa.retry')
@patch('core.services.AI.lerRelatorio.lerRelatorio')
@patch('core.tasks.ler_pdf_modo_layout')
def test_processar_relatorio_com_ia_retry_on_timeout(mock_pdf, mock_ler_relatorio, mock_retry, relatorio):
    mock_pdf.return_value = "texto fake do relatorio"
    mock_ler_relatorio.side_effect = Exception("AI Service Unavailable")
    mock_retry.side_effect = Retry()

    with pytest.raises(Retry):
        processarRelatorioComIa(relatorio.id)

    mock_retry.assert_called_once()
    kwargs = mock_retry.call_args.kwargs
    assert kwargs['countdown'] == 60
    assert "AI Service Unavailable" in str(kwargs['exc'])


@pytest.mark.django_db
@patch('core.tasks.avaliarRelatorioComIa.retry')
@patch('core.services.AI.lerRelatorio.avaliarRelatorio')
def test_avaliar_relatorio_com_ia_retry_on_timeout(mock_avaliar_relatorio, mock_retry, relatorio, curso):
    from django.core.files.uploadedfile import SimpleUploadedFile
    curso.ementa_md = SimpleUploadedFile("ementa.md", b"# Ementa do Curso")
    curso.save()
    
    relatorio.processo_id.aluno.curso = curso
    relatorio.processo_id.aluno.curso.save()

    mock_avaliar_relatorio.side_effect = Exception("AI Evaluation Timeout")
    mock_retry.side_effect = Retry()

    with pytest.raises(Retry):
        avaliarRelatorioComIa(relatorio.id)

    mock_retry.assert_called_once()
    kwargs = mock_retry.call_args.kwargs
    assert kwargs['countdown'] == 60
    assert "AI Evaluation Timeout" in str(kwargs['exc'])
