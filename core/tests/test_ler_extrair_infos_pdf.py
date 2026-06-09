import pytest
from unittest.mock import MagicMock, patch
from core.services.ler_extrair_infos_pdf import ler_pdf_modo_layout


class TestLerPdfModoLayout:
    @patch("core.services.ler_extrair_infos_pdf.PdfReader")
    def test_ler_pdf_modo_layout_sucesso(self, mock_pdf_reader):
        # Configura o mock do PdfReader para simular uma página com texto
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto extraído do PDF"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        resultado = ler_pdf_modo_layout("caminho/fake.pdf")
        
        assert resultado == "Texto extraído do PDF"
        mock_pdf_reader.assert_called_once_with("caminho/fake.pdf")
        mock_page.extract_text.assert_called_once_with(extraction_mode="layout")
