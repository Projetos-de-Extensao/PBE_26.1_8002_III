import os
import uuid

def upload_contrato_path(instance, matricula, filename):
    matricula = instance.processoId.matricula_aluno.matricula
    tipo = filename.split('.')[-1]
    nome_novo = f"{uuid.uuid4()}.{tipo}"
    return os.path.join("/media/", matricula, "contratos", nome_novo)
