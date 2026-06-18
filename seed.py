import os
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Aluno, Coordenador, Secretaria, Curso, Area, Processo, FeatureFlag
from core.enums import Unidade, StatusProcesso
from django.contrib.auth.hashers import make_password

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

# 3. Criar Area e Curso (com ementa vinculada)
area, _ = Area.objects.get_or_create(nome='Computação', defaults={'coordenador': coord})
curso, _ = Curso.objects.get_or_create(nome='Engenharia de Software', areaId=area)

# Vincular arquivo de ementa ao curso (necessário para validação IA de relatórios)
ementa_path = BASE_DIR / 'core' / 'fixtures' / 'ementas' / 'engenharia_de_software.md'
if ementa_path.exists() and not curso.ementa_md:
    from django.core.files import File
    with open(ementa_path, 'rb') as f:
        curso.ementa_md.save('engenharia_de_software.md', File(f), save=True)
    print(f"  [OK] Ementa vinculada ao curso: {curso.nome}")

# 4. Criar 3 Alunos e 3 Processos (Projetos)
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

# 5. Criar Feature Flags padrão ativas
flags = ["async_contract_ai", "async_report_ai", "report_evaluation_ai"]
for flag_name in flags:
    flag, created = FeatureFlag.objects.get_or_create(
        name=flag_name,
        defaults={'is_enabled': True}
    )
    if not created and not flag.is_enabled:
        flag.is_enabled = True
        flag.save()

# 6. Semeando Horários disponíveis (18 combinações: Segunda a Sábado x Manhã/Tarde/Noite)
from core.models import Horarios
from core.enums import DiasDaSemana, Turno
for dia_choice in DiasDaSemana.choices:
    for turno_choice in Turno.choices:
        Horarios.objects.get_or_create(dia=dia_choice[0], turno=turno_choice[0])

print("DB Seeded Successfully!")
print("------------------------------------------------------------")
print("Credenciais de acesso para testes:")
print("------------------------------------------------------------")
print(f"COORDENADOR -> Matricula: {coord.matricula} | Senha: senha123")
print(f"SECRETARIA  -> Matricula: {sec.matricula}     | Senha: senha123")
print(f"ALUNO (ex)  -> Matricula: {alunos[0].matricula}   | Senha: senha123")
print("------------------------------------------------------------")

