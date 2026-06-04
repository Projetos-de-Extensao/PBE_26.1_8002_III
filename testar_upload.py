import os
import django
import requests

# 1. Inicializa o ambiente do Django para acessar os models e configurações
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Aluno, Processo, Curso, Area
from core.enums import Unidade
from rest_framework_simplejwt.tokens import RefreshToken

# Configurações do servidor local
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
PDF_PATH = "./core/services/TCE_preenchido.pdf"

def main():
    print("=== Configurando ambiente de teste no banco ===")
    
    EMAIL_TESTE = "aluno_teste@ibmec.edu.br"
    username_matricula = "20269999"
    
    # 2. Cria ou obtém o usuário de teste
    user, created = User.objects.get_or_create(username=username_matricula, defaults={
        "email": EMAIL_TESTE,
        "first_name": "Pedro",
        "last_name": "Santos"
    })
    if created:
        user.set_password("senha123")
        user.save()
        print(f"[+] Usuário Django '{username_matricula}' criado.")
    else:
        print(f"[*] Usuário Django '{username_matricula}' já existe.")
        
    # 3. Cria Aluno correspondente (necessário para passar na permissão IsAluno)
    area, _ = Area.objects.get_or_create(nome="Tecnologia")
    curso, _ = Curso.objects.get_or_create(nome="ADS", areaId=area)
    
    aluno, created = Aluno.objects.get_or_create(matricula=username_matricula, defaults={
        "nome": "Pedro Santos",
        "email": EMAIL_TESTE,
        "senha": "senha",
        "cpf": "123.456.789-99",
        "unidade": Unidade.BARRA.value,
        "curso": curso,
        "precisa_redefinir_senha": False, # Evita redirecionamento de senha
        "is_ativo": True
    })
    if created:
        print(f"[+] Aluno matriculado '{username_matricula}' criado.")
    else:
        print(f"[*] Aluno matriculado '{username_matricula}' já existe.")
        
    # 4. Cria um processo de estágio fictício
    processo, created = Processo.objects.get_or_create(
        matricula_aluno=aluno,
        nome_empresa="TechBrasil Soluções S.A.",
        defaults={"status": "ABERTO"}
    )
    if created:
        print(f"[+] Processo ID {processo.id} criado.")
    else:
        print(f"[*] Usando processo ID {processo.id} existente.")

    # 5. Gera o Token JWT para autenticar o Request HTTP
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print("[+] Token JWT de acesso gerado.")

    # 6. Verifica se o PDF existe localmente
    if not os.path.exists(PDF_PATH):
        print(f"[!] ERRO: Arquivo PDF de teste não encontrado em: {PDF_PATH}")
        return

    # 7. Faz a chamada HTTP de upload
    url = f"{BASE_URL}/processo/{processo.id}/contrato/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"\n[HTTP POST] Enviando arquivo {PDF_PATH} para: {url}...")
    
    with open(PDF_PATH, "rb") as pdf_file:
        files = {
            "arquivo": (os.path.basename(PDF_PATH), pdf_file, "application/pdf")
        } 
        
        try:
            response = requests.post(url, headers=headers, files=files)
            print(f"Status Code: {response.status_code}")
            print("\nResposta JSON:")
            import json
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        except requests.exceptions.ConnectionError:
            print(f"[!] ERRO: Não foi possível se conectar ao servidor na porta {PORT}. Verifique se o 'runserver' está ativo.")
        except Exception as e:
            print(f"[!] Ocorreu um erro na requisição: {e}")

if __name__ == "__main__":
    main()
