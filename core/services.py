import os
import uuid


def upload_contrato_path(instance,matricula,filename):
    tipo = filename.split('.')[-1]
    nome_novo = f"{uuid.uuid4()}.{tipo}"
    return os.path.join({matricula},"contratos",nome_novo)

    
