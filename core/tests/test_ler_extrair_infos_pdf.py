import pytest
from unittest.mock import MagicMock, patch
from core.services.ler_extrair_infos_pdf import (
    ler_pdf_modo_layout,
    extrair_data,
    separar_apolice_seguradora,
    extrair_infos,
)

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


class TestExtrairData:
    def test_extrair_data_valido(self):
        # Caso padrão com ponto e datas no formato DeDDMMAAAAaDDMM/AAAA
        inicio, fim = extrair_data("12meses.De01072025a3006/2026")
        assert inicio == "01/07/2025"
        assert fim == "30/06/2026"

    def test_extrair_data_sem_ponto(self):
        # Se não houver ponto, deve retornar a própria string original
        resultado = extrair_data("De01072025a3006/2026")
        assert resultado == "De01072025a3006/2026"

    def test_extrair_data_sem_letra_a_divisora(self):
        # Sem o caractere 'a' para dividir, deve retornar tupla vazia
        inicio, fim = extrair_data("12meses.De01072025 3006/2026")
        assert inicio == ""
        assert fim == ""

    def test_extrair_data_valores_nulos_ou_invalidos(self):
        assert extrair_data(None) == ("", "")
        assert extrair_data(12345) == ("", "")
        assert extrair_data("") == ("", "")

    def test_extrair_data_curta_invalida(self):
        # Caso a string após o ponto seja curta demais
        inicio, fim = extrair_data("12meses.De")
        assert inicio == ""
        assert fim == ""


class TestSepararApoliceSeguradora:
    def test_separar_apolice_e_seguradora_padrao(self):
        # Caso padrão: número de apólice seguido por nome da seguradora
        apolice, seguradora = separar_apolice_seguradora("APL-2025-00987654PortoSeguroS.A.")
        assert apolice == "APL-2025-00987654"
        assert seguradora == "PortoSeguroS.A."

    def test_separar_apolice_sem_numeros(self):
        # Sem números: apólice vazia, seguradora é a própria string
        apolice, seguradora = separar_apolice_seguradora("PortoSeguroS.A.")
        assert apolice == ""
        assert seguradora == "PortoSeguroS.A."

    def test_separar_apolice_numero_no_inicio(self):
        # Número apenas no começo
        apolice, seguradora = separar_apolice_seguradora("123PortoSeguro")
        assert apolice == "123"
        assert seguradora == "PortoSeguro"

    def test_separar_apolice_valores_nulos_ou_invalidos(self):
        assert separar_apolice_seguradora(None) == ("", "")
        assert separar_apolice_seguradora("") == ("", "")
        assert separar_apolice_seguradora(12345) == ("", "")


class TestExtrairInfos:
    def test_extrair_infos_sucesso(self):
        # Simula o texto retornado pela extração de PDF, onde a quebra de linha \n é o separador real de dados
        pdf_texto_mock = (
            "CONCEDENTEDOESTÁGIO(EMPRESA)\nTechBrasilSoluçõesS.A\nCNPJouCPFeRegistro\n12.345.678/0001-90\n"
            "Endereço\nCEP\nRuadasInovações\nE-mail\nTel.\nrh@techbrasil.com.br\nRepresentante\nCargo\n"
            "RicardoAlmeida\nLocaldoEstágio\nTI\nINTERVENIENTE\nCNPJ\nIbmec\nENDEREÇO\nCEP\nREPRESENTANTES\n"
            "CARGO\nSamuel\nUNIDADE\nNOMEDO(A)ESTAGIÁRIO(A)\nMATRÍCULA\nCPF\nAnaCarolina\nCURSO\nAdmin\n"
            "DURAÇÃO/PERÍODODOESTÁGIO:\n12meses.De01072025a3006/2026\nNÚMERODAAPÓLICEDESEGURO\nSEGURADORA\n"
            "APL-2025-00987654PortoSeguroS.A.\n[ ]CHECKBOX"
        )
        
        resultado = extrair_infos(pdf_texto_mock)
        
        assert resultado["nome_empresa"] == "TechBrasilSoluçõesS.A"
        assert resultado["cnpj_empresa"] == "12.345.678/0001-90"
        assert resultado["data_inicio"] == "01/07/2025"
        assert resultado["data_termino"] == "30/06/2026"
        assert resultado["apolice_seguro"] == "APL-2025-00987654"
        assert resultado["seguradora"] == "PortoSeguroS.A."

    def test_extrair_infos_sem_checkbox(self):
        # Verifica se funciona mesmo quando não há colchete de checkbox '['
        pdf_texto_mock = (
            "TechBrasilSoluçõesS.A\n12.345.678/0001-90\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n"
            "12meses.De01072025a3006/2026\nAPL-2025-00987654PortoSeguroS.A."
        )
        resultado = extrair_infos(pdf_texto_mock)
        assert resultado["nome_empresa"] == "TechBrasilSoluçõesS.A"
        assert resultado["data_inicio"] == "01/07/2025"

    def test_extrair_infos_valores_nulos_ou_invalidos(self):
        assert extrair_infos(None) == {}
        assert extrair_infos("") == {}
        assert extrair_infos(12345) == {}

    def test_extrair_infos_dados_insuficientes(self):
        # Se a lista respostas contiver menos de 17 itens, alguns campos não serão preenchidos
        pdf_texto_mock = "TechBrasilSoluçõesS.A\n12.345.678/0001-90"
        resultado = extrair_infos(pdf_texto_mock)
        
        assert resultado["nome_empresa"] == "TechBrasilSoluçõesS.A"
        assert resultado["cnpj_empresa"] == "12.345.678/0001-90"
        assert "data_inicio" not in resultado
        assert "apolice_seguro" not in resultado
