import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from core.models import Aluno, Coordenador, Secretaria, Curso, Area, Processo, Contrato, FeatureFlag
from core.enums import Unidade, StatusProcesso, StatusContrato
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

User = get_user_model()

print("------------------------------------------------------------")
print("Limpando banco de dados...")
print("------------------------------------------------------------")
# Deleta primeiro os Contratos e Processos para liberar os links com PROTECT
Contrato.objects.all().delete()
Processo.objects.all().delete()
Curso.objects.all().delete()
Area.objects.all().delete()
FeatureFlag.objects.all().delete()
User.objects.all().delete()

print("Iniciando a população do banco de dados (SEED)...")
print("------------------------------------------------------------")

# 1. Criar Coordenador
coord, created = Coordenador.objects.get_or_create(
    matricula='coord01', 
    defaults={
        'nome': 'Coordenador Teste', 
        'email': 'coord@ibmec.edu.br', 
        'unidade': Unidade.BARRA.value, 
        'precisa_redefinir_senha': False, 
        'aceite_lgpd': True
    }
)
coord.set_password('senha123')
coord.is_staff = True
coord.save()

# 2. Criar Secretaria
sec, created = Secretaria.objects.get_or_create(
    matricula='sec01', 
    defaults={
        'nome': 'Secretaria Teste', 
        'email': 'sec@ibmec.edu.br', 
        'unidade': Unidade.BARRA.value, 
        'precisa_redefinir_senha': False, 
        'aceite_lgpd': True
    }
)
sec.set_password('senha123')
sec.is_staff = True
sec.save()

# 3. Criar Area e Curso
area, _ = Area.objects.get_or_create(nome='Computação', defaults={'coordenador': coord})
curso, _ = Curso.objects.get_or_create(nome='Engenharia de Software', areaId=area)

# 4. Criar 3 Alunos, 3 Processos (Projetos) e seus respectivos Contratos pendentes
alunos = []
processos = []

pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n111\n%%EOF"

for i in range(1, 4):
    email = f'aluno{i}@ibmec.edu.br'
    matricula = f'aluno0{i}'
    cpf = f'1234567890{i}'
    
    # Criar Model Aluno
    aluno, created = Aluno.objects.get_or_create(
        matricula=matricula, 
        defaults={
            'nome': f'Aluno Teste {i}', 
            'email': email, 
            'unidade': Unidade.BARRA.value, 
            'precisa_redefinir_senha': False, 
            'aceite_lgpd': True, 
            'cpf': cpf, 
            'curso': curso
        }
    )
    aluno.set_password('senha123')
    aluno.save()
    alunos.append(aluno)
    
    # Criar Processo (Projeto) vinculado a este Aluno, e aos únicos Coordenador e Secretaria
    processo, _ = Processo.objects.get_or_create(
        aluno=aluno, 
        defaults={
            'nome_empresa': f'Empresa Parceira {i}', 
            'coordenacao': coord, 
            'secretaria': sec, 
            'status': StatusProcesso.ABERTO.value
        }
    )
    processos.append(processo)

    # Criar Contrato pendente vinculado a este Processo
    Contrato.objects.create(
        processoId=processo,
        nome_empresa=processo.nome_empresa,
        cnpj_empresa=f"1234567800010{i}",
        data_inicio="2026-06-01",
        data_termino="2027-06-01",
        apolice_seguro=f"AP-99887{i}",
        plano_atividade=True,
        arquivo=ContentFile(pdf_content, name=f"contrato_aluno_{i}.pdf"),
        status=StatusContrato.PENDENTE.value
    )

# 5. Criar Feature Flags de IA habilitadas por padrão
FeatureFlag.objects.create(name="async_contract_ai", is_enabled=True)
FeatureFlag.objects.create(name="async_report_ai", is_enabled=True)
FeatureFlag.objects.create(name="report_evaluation_ai", is_enabled=True)

print("DB Seeded Successfully!")
print("------------------------------------------------------------")
print("Credenciais de acesso para testes:")
print("------------------------------------------------------------")
print(f"COORDENADOR -> Matricula: {coord.matricula} | Senha: senha123")
print(f"SECRETARIA  -> Matricula: {sec.matricula}     | Senha: senha123")
print(f"ALUNO (ex)  -> Matricula: {alunos[0].matricula}   | Senha: senha123")
print("------------------------------------------------------------")
