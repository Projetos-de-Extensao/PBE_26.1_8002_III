import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from core.validators import validar_email_institucional, validar_cpf
from core.services.validacao_arquivos import validar_pdf_e_tamanho_seguro
from core.services.validacao_sistema.validaGradeContrato import validarGradeContrato
from core.exceptions import gradeHorariaIncompativelException

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


@pytest.mark.django_db
class TestValidaGradeContrato:
    """
    Testes para o validador de grade horária do contrato:
    validarGradeContrato(AlunoId, ContratoId)
    """

    def test_grade_sem_conflito(self, aluno, contrato, horario_segunda_manha, horario_terca_noite):
        """Aluno com grade em horários diferentes do contrato — deve passar sem erro."""
        # Aluno estuda segunda de manhã
        aluno.grade.add(horario_segunda_manha)
        # Contrato é terça à noite
        contrato.horarios_atividade.add(horario_terca_noite)

        # Não deve levantar exceção
        validarGradeContrato(aluno.id, contrato.id)

    def test_grade_com_conflito(self, aluno, contrato, horario_segunda_manha):
        """Aluno com grade no mesmo horário do contrato — deve levantar erro."""
        # Mesmo horário nos dois
        aluno.grade.add(horario_segunda_manha)
        contrato.horarios_atividade.add(horario_segunda_manha)

        with pytest.raises(gradeHorariaIncompativelException):
            validarGradeContrato(aluno.id, contrato.id)

    def test_contrato_sem_horarios(self, aluno, contrato, horario_segunda_manha):
        """Contrato sem horários de atividade — deve passar sem erro."""
        aluno.grade.add(horario_segunda_manha)
        # Contrato não tem horários

        validarGradeContrato(aluno.id, contrato.id)

    def test_aluno_sem_grade(self, aluno, contrato, horario_segunda_manha):
        """Aluno sem grade — deve passar sem erro."""
        # Aluno não tem grade
        contrato.horarios_atividade.add(horario_segunda_manha)

        validarGradeContrato(aluno.id, contrato.id)