import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from core.validators import validar_email_institucional, validar_cpf, valida_carga_horaria, valida_limite_formatura, valida_retroatividade
from core.services.validacao_arquivos import validar_pdf_e_tamanho_seguro

class TestValidarEmailInstitucional:
    """
    Testes para o validador de e-mail institucional:
    validar_email_institucional(value)
    """

    def test_email_institucional_valido(self):
        # E-mails válidos com domínio ibmec.edu.br devem passar sem erro
        validar_email_institucional("aluno@ibmec.edu.br")
        validar_email_institucional("professor.nome@ibmec.edu.br")

    def test_email_institucional_case_insensitive(self):
        # Domínio deve ser case-insensitive
        validar_email_institucional("ALUNO@IBMEC.EDU.BR")

    def test_email_com_dominio_nao_permitido(self):
        # E-mails de outros domínios devem levantar ValidationError com código 'dominio_nao_permitido'
        with pytest.raises(ValidationError) as exc_info:
            validar_email_institucional("aluno@gmail.com")
        assert exc_info.value.code == "dominio_nao_permitido"
        assert "Apenas e-mails institucionais são aceitos" in str(exc_info.value.message)

    def test_email_com_formato_invalido(self):
        # E-mails em formatos inválidos devem falhar na validação padrão do Django
        with pytest.raises(ValidationError):
            validar_email_institucional("email_sem_arroba.com")
        with pytest.raises(ValidationError):
            validar_email_institucional("email@")
        with pytest.raises(ValidationError):
            validar_email_institucional("@ibmec.edu.br")


class TestValidarCPF:
    """
    Testes para o validador de CPF:
    validar_cpf(value)
    """

    def test_cpf_valido_com_e_sem_formatacao(self):
        # CPFs matematicamente válidos devem passar sem erros
        validar_cpf("123.456.789-09")
        validar_cpf("12345678909")
        validar_cpf("45678912364")
        validar_cpf("456.789.123-64")

    def test_cpf_tamanho_invalido(self):
        # CPFs com menos ou mais de 11 dígitos numéricos devem levantar erro
        with pytest.raises(ValidationError) as exc_info:
            validar_cpf("1234567890")  # 10 dígitos
        assert exc_info.value.code == "cpf_invalido_tamanho"

        with pytest.raises(ValidationError) as exc_info:
            validar_cpf("123456789012")  # 12 dígitos
        assert exc_info.value.code == "cpf_invalido_tamanho"

    def test_cpf_contendo_letras_limpo(self):
        # CPFs que contêm letras devem falhar após a limpeza
        with pytest.raises(ValidationError) as exc_info:
            validar_cpf("123.456.789-0A")  # 10 dígitos numéricos restantes
        assert exc_info.value.code == "cpf_invalido_tamanho"

    def test_cpf_sequencias_invalidas(self):
        # CPFs com todos os dígitos iguais são rejeitados
        invalidos = [
            "00000000000",
            "111.111.111-11",
            "999.999.999-99"
        ]
        for cpf in invalidos:
            with pytest.raises(ValidationError) as exc_info:
                validar_cpf(cpf)
            assert exc_info.value.code == "cpf_invalido_sequencia"

    def test_cpf_digitos_verificadores_incorretos(self):
        # CPFs com tamanho e formato corretos, mas dígitos de verificação errados
        with pytest.raises(ValidationError) as exc_info:
            validar_cpf("12345678903")  # O correto seria terminação 02
        assert exc_info.value.code == "cpf_invalido_digito"

        with pytest.raises(ValidationError) as exc_info:
            validar_cpf("45678912365")  # O correto seria terminação 64
        assert exc_info.value.code == "cpf_invalido_digito"


class TestValidarPDFETamanhoSeguro:
    """
    Testes para o validador de PDF e tamanho seguro do arquivo:
    validar_pdf_e_tamanho_seguro(value)
    """

    def test_pdf_valido_e_tamanho_permitido(self):
        # Arquivo menor que 5MB e com assinatura PDF válida b'%PDF-' deve passar
        conteudo = b"%PDF-1.4\n1 0 obj\nendobj"
        arquivo_fake = SimpleUploadedFile("contrato.pdf", conteudo, content_type="application/pdf")
        
        # Não deve levantar exceções
        validar_pdf_e_tamanho_seguro(arquivo_fake)

    def test_arquivo_nao_pdf(self):
        # Arquivo menor que 5MB mas sem a assinatura de PDF b'%PDF-' deve falhar
        conteudo = b"GIF89a\x01\x00\x01\x00"
        arquivo_fake = SimpleUploadedFile("imagem.gif", conteudo, content_type="image/gif")
        
        with pytest.raises(ValidationError) as exc_info:
            validar_pdf_e_tamanho_seguro(arquivo_fake)
        assert "Apenas PDFs reais são permitidos" in str(exc_info.value.message)

    def test_tamanho_excedido(self):
        # Arquivo com assinatura correta mas tamanho maior que 5MB
        # Usamos um mock para simular o tamanho sem alocar 5MB de memória
        class MockLargeFile:
            def __init__(self):
                self.size = 6 * 1024 * 1024  # 6 MB
                from io import BytesIO
                self.file = BytesIO(b"%PDF-")

        arquivo_grande = MockLargeFile()
        with pytest.raises(ValidationError) as exc_info:
            validar_pdf_e_tamanho_seguro(arquivo_grande)
        assert "O arquivo excede o limite" in str(exc_info.value.message)

    def test_reseta_ponteiro_de_leitura(self):
        # O validador deve ler os primeiros 5 bytes e retornar o ponteiro para 0 (seek(0))
        conteudo = b"%PDF-1.5 arquivo completo"
        arquivo_fake = SimpleUploadedFile("contrato.pdf", conteudo, content_type="application/pdf")
        
        validar_pdf_e_tamanho_seguro(arquivo_fake)
        
        # Se o ponteiro foi resetado corretamente, ler novamente deve retornar o conteúdo desde o início
        assert arquivo_fake.file.read() == conteudo


class TestValidarCargaHoraria:
    """
    Testes para o validador de carga horária:
    valida_carga_horaria(contrato)
    """

    class MockContrato:
        def __init__(self, horas_diarias, horas_semanais):
            self.horas_diarias = horas_diarias
            self.horas_semanais = horas_semanais

    def test_carga_horaria_dentro_do_limite(self):
        # Horas dentro do permitido pela Lei 11.788 devem passar
        contrato = self.MockContrato(horas_diarias=6, horas_semanais=30)
        assert valida_carga_horaria(contrato) is True

    def test_carga_horaria_abaixo_do_limite(self):
        # Horas abaixo do limite devem passar
        contrato = self.MockContrato(horas_diarias=4, horas_semanais=20)
        assert valida_carga_horaria(contrato) is True

    def test_horas_diarias_acima_do_limite(self):
        # Horas diárias acima de 6 devem falhar
        contrato = self.MockContrato(horas_diarias=7, horas_semanais=30)
        assert valida_carga_horaria(contrato) is False

    def test_horas_semanais_acima_do_limite(self):
        # Horas semanais acima de 30 devem falhar
        contrato = self.MockContrato(horas_diarias=6, horas_semanais=31)
        assert valida_carga_horaria(contrato) is False

    def test_ambas_acima_do_limite(self):
        # Ambas acima do limite devem falhar
        contrato = self.MockContrato(horas_diarias=8, horas_semanais=40)
        assert valida_carga_horaria(contrato) is False

    def test_campos_none_devem_passar(self):
        # Campos não preenchidos não devem bloquear
        contrato = self.MockContrato(horas_diarias=None, horas_semanais=None)
        assert valida_carga_horaria(contrato) is True


class TestValidarLimiteFormatura:
    """
    Testes para o validador de limite de formatura:
    valida_limite_formatura(contrato, aluno)
    """

    class MockContrato:
        def __init__(self, data_termino):
            self.data_termino = data_termino

    class MockAluno:
        def __init__(self, data_previsao_formatura):
            self.data_previsao_formatura = data_previsao_formatura

    def test_data_termino_antes_da_formatura(self):
        # Data de término antes da previsão de formatura deve passar
        contrato = self.MockContrato(data_termino=date(2026, 6, 1))
        aluno = self.MockAluno(data_previsao_formatura=date(2026, 12, 1))
        assert valida_limite_formatura(contrato, aluno) is True

    def test_data_termino_igual_a_formatura(self):
        # Data de término igual à previsão de formatura deve passar
        contrato = self.MockContrato(data_termino=date(2026, 12, 1))
        aluno = self.MockAluno(data_previsao_formatura=date(2026, 12, 1))
        assert valida_limite_formatura(contrato, aluno) is True

    def test_data_termino_depois_da_formatura(self):
        # Data de término após a previsão de formatura deve falhar
        contrato = self.MockContrato(data_termino=date(2027, 1, 1))
        aluno = self.MockAluno(data_previsao_formatura=date(2026, 12, 1))
        assert valida_limite_formatura(contrato, aluno) is False

    def test_campos_none_devem_passar(self):
        # Campos não preenchidos não devem bloquear
        contrato = self.MockContrato(data_termino=None)
        aluno = self.MockAluno(data_previsao_formatura=None)
        assert valida_limite_formatura(contrato, aluno) is True

    def test_previsao_formatura_none_deve_passar(self):
        # Previsão de formatura não preenchida não deve bloquear
        contrato = self.MockContrato(data_termino=date(2026, 12, 1))
        aluno = self.MockAluno(data_previsao_formatura=None)
        assert valida_limite_formatura(contrato, aluno) is True


class TestValidarRetroatividade:
    """
    Testes para o validador de retroatividade:
    valida_retroatividade(contrato)
    """

    class MockContrato:
        def __init__(self, data_inicio):
            self.data_inicio = data_inicio

    def test_data_inicio_recente(self):
        # Data de início de 10 dias atrás deve passar
        contrato = self.MockContrato(data_inicio=date.today() - timedelta(days=10))
        assert valida_retroatividade(contrato) is True

    def test_data_inicio_exatamente_30_dias(self):
        # Data de início de exatamente 30 dias atrás deve passar (limite)
        contrato = self.MockContrato(data_inicio=date.today() - timedelta(days=30))
        assert valida_retroatividade(contrato) is True

    def test_data_inicio_mais_de_30_dias(self):
        # Data de início de mais de 30 dias atrás deve falhar
        contrato = self.MockContrato(data_inicio=date.today() - timedelta(days=31))
        assert valida_retroatividade(contrato) is False

    def test_data_inicio_muito_retroativa(self):
        # Data de início de 90 dias atrás deve falhar
        contrato = self.MockContrato(data_inicio=date.today() - timedelta(days=90))
        assert valida_retroatividade(contrato) is False

    def test_data_inicio_futura(self):
        # Data de início futura deve passar
        contrato = self.MockContrato(data_inicio=date.today() + timedelta(days=10))
        assert valida_retroatividade(contrato) is True

    def test_campo_none_deve_passar(self):
        # Campo não preenchido não deve bloquear
        contrato = self.MockContrato(data_inicio=None)
        assert valida_retroatividade(contrato) is True
