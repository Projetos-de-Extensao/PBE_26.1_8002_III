import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Aluno, Coordenador, Secretaria, Curso, Area, Processo, FeatureFlag
from core.enums import Unidade, StatusProcesso
from django.contrib.auth.hashers import make_password

print("------------------------------------------------------------")
print("Iniciando a população do banco de dados (SEED)...")
print("------------------------------------------------------------")

# 1. Criar Coordenador
u_coord, _ = User.objects.get_or_create(username='coord01', email='coord@ibmec.edu.br')
u_coord.set_password('senha123')
u_coord.is_staff = True
u_coord.save()

coord, _ = Coordenador.objects.get_or_create(
    matricula='coord01', defaults={'nome': 'Coordenador Teste', 'email': 'coord@ibmec.edu.br', 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True}
)

# 2. Criar Secretaria
u_sec, _ = User.objects.get_or_create(username='sec01', email='sec@ibmec.edu.br')
u_sec.set_password('senha123')
u_sec.is_staff = True
u_sec.save()

sec, _ = Secretaria.objects.get_or_create(
    matricula='sec01', defaults={'nome': 'Secretaria Teste', 'email': 'sec@ibmec.edu.br', 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True}
)

# 3. Criar Area e Curso
area, _ = Area.objects.get_or_create(nome='Computação', defaults={'coordenador': coord})
curso, _ = Curso.objects.get_or_create(nome='Engenharia de Software', areaId=area)

# 4. Criar 3 Alunos e 3 Processos (Projetos)
alunos = []
processos = []

for i in range(1, 4):
    username = f'aluno0{i}'
    email = f'aluno{i}@ibmec.edu.br'
    matricula = f'aluno0{i}'
    cpf = f'1234567890{i}'
    
    # Criar User Aluno
    u_aluno, _ = User.objects.get_or_create(username=username, email=email)
    u_aluno.set_password('senha123')
    u_aluno.save()
    
    # Criar Model Aluno
    aluno, _ = Aluno.objects.get_or_create(
        matricula=matricula, defaults={'nome': f'Aluno Teste {i}', 'email': email, 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True, 'cpf': cpf, 'curso': curso}
    )
    alunos.append(aluno)
    
    # Criar Processo (Projeto) vinculado a este Aluno, e aos únicos Coordenador e Secretaria
    processo, _ = Processo.objects.get_or_create(
        aluno=aluno, defaults={'nome_empresa': f'Empresa Parceira {i}', 'coordenacao': coord, 'secretaria': sec, 'status': StatusProcesso.ABERTO}
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

