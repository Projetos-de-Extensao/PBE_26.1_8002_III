import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Aluno, Coordenador, Secretaria, Curso, Area, Unidade
from django.contrib.auth.hashers import make_password

# 1. Create a Coordenador
u_coord, _ = User.objects.get_or_create(username='coord01', email='coord@ibmec.edu.br')
u_coord.set_password('senha123')
u_coord.save()
coord, _ = Coordenador.objects.get_or_create(
    matricula='coord01', defaults={'nome': 'Coordenador Teste', 'email': 'coord@ibmec.edu.br', 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True}
)

# 2. Create Area and Curso
area, _ = Area.objects.get_or_create(nome='Computação', defaults={'coordenador': coord})
curso, _ = Curso.objects.get_or_create(nome='Engenharia de Software', areaId=area)

# 3. Create a Secretaria
u_sec, _ = User.objects.get_or_create(username='sec01', email='sec@ibmec.edu.br')
u_sec.set_password('senha123')
u_sec.save()
sec, _ = Secretaria.objects.get_or_create(
    matricula='sec01', defaults={'nome': 'Secretaria Teste', 'email': 'sec@ibmec.edu.br', 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True}
)

# 4. Create an Aluno
u_aluno, _ = User.objects.get_or_create(username='aluno01', email='aluno@ibmec.edu.br')
u_aluno.set_password('senha123')
u_aluno.save()
aluno, _ = Aluno.objects.get_or_create(
    matricula='aluno01', defaults={'nome': 'Aluno Teste', 'email': 'aluno@ibmec.edu.br', 'senha': make_password('senha123'), 'unidade': Unidade.BARRA, 'precisa_redefinir_senha': False, 'aceite_lgpd': True, 'cpf': '12345678900', 'curso': curso}
)

# Assign auth Groups to make permissions work?
# Actually the backend uses IsUserStaff in DRF which usually checks user.is_staff
u_sec.is_staff = True
u_sec.save()
u_coord.is_staff = True
u_coord.save()

print("DB Seeded Successfully!")
