import os
import uuid

from django.core.exceptions import ValidationError

def upload_contrato_path(instance,matricula,filename):
    tipo = filename.split('.')[-1]
    nome_novo = f"{uuid.uuid4()}.{tipo}"
    return os.path.join({matricula},"contratos",nome_novo)

    
def upload_relatorio_path(instance,matricula,filename):
    tipo = filename.split('.')[-1]
    nome_novo = f"{uuid.uuid4()}.{tipo}"
    return os.path.join({matricula},"relatorio",nome_novo)


def validar_pdf_e_tamanho_seguro(value):
    """
    Valida se o arquivo tem no máximo 5MB e se é um PDF verdadeiro.
    """
    # 1. Valida o tamanho (Exemplo: 5MB)
    limite_megabytes = 5
    if value.size > limite_megabytes * 1024 * 1024:
        raise ValidationError(f'O arquivo excede o limite de {limite_megabytes}MB.')

    # 2. Valida a "Assinatura" do arquivo (Magic Number)
    assinatura = value.file.read(5) 
    
    # 3. Retorna o ponteiro de leitura para o início
    value.file.seek(0) 

    # 4. Verifica se os bytes correspondem a um PDF
    if assinatura != b'%PDF-':
        raise ValidationError('Arquivo inválido. Apenas PDFs reais são permitidos.')