from core.models import *
from core.exceptions import *


def validarGradeContrato(AlunoId,ContratoId):
    contrato = Contrato.objects.get(id=ContratoId)
    aluno = Aluno.objects.get(id=AlunoId)

    horarios_contrato = contrato.horarios_atividade.all()
    grade_aluno = aluno.grade.all()
    
    for horario in horarios_contrato:
        if horario in grade_aluno:
            raise gradeHorariaIncompativelException
            
    
    