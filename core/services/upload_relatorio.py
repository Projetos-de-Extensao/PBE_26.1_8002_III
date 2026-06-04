import os
import uuid

def upload_relatorio_path(instance, filename):
    matricula = instance.processo_id.aluno.matricula
    tipo = filename.split('.')[-1]
    nome_novo = f"{uuid.uuid4()}.{tipo}"
    return os.path.join(matricula, "relatorio", nome_novo)
