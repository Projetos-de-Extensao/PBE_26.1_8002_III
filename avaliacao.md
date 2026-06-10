# Terceira Análise — App Django REST Framework: Sistema de Estágio (Grupo III)
## **Com vários muito pequenos ajustes a nota da conformidade sobe consideravelmente.** 
**Data:** 06/06/2026  
**Repositório:** Projetos-de-Extensao/PBE_26.1_8002_III  
**Branch:** main  


---

## Contexto do Projeto

O projeto é um sistema de gestão de estágios obrigatórios para instituição de ensino superior (Ibmec), denominado **IbIntern**. Envolve os atores: **Aluno**, **Secretaria** e **Coordenador**. O fluxo principal é: aluno inicia processo → faz upload de contrato → secretaria avalia contrato → aluno envia relatório → coordenador avalia relatório → processo concluído.

---

## 1. Especificação

### Critérios avaliados

| Critério | Pontuação (1–5) | Observação |
|---|---|---|
| Requisitos funcionais documentados | 4 | Casos de uso detalhados em `docs/Elaboracao/Casos de Uso/` (iniciar_processo, anexar_contrato, validar_contrato, enviar_relatorio, etc.) |
| Requisitos não funcionais documentados | 2 | Ausência de documentação explícita de RNFs (performance, disponibilidade, SLA) |
| Modelos refletem regras de negócio | 4 | `Processo`, `Contrato`, `Relatorio` com enums de status bem definidos; fluxo de estados presente |
| Endpoints refletem casos de uso | 3 | Endpoints cobrem os fluxos principais, mas falta endpoint de `curso/` e `area/` via rota RESTful explícita |
| Documentação de API (OpenAPI/Swagger) | 4 | `drf_spectacular` integrado com `@extend_schema` em boa parte das views; `SPECTACULAR_SETTINGS` configurado |
| Consistência doc x implementação | 3 | Documentação dos casos de uso está bem estruturada, mas alguns campos dos serializers divergem dos diagramas de classes (ex: `NestedContratoSerializer` inclui `nome_empresa` que não pertence a `Contrato`) |

**Subtotal Especificação:** 20/30 → **média 3,3**

---

## 2. Codificação

### Critérios avaliados

| Critério | Pontuação (1–5) | Observação |
|---|---|---|
| Separação de concerns | 4 | Services isolados (`email_service`, `upload_contrato`, `validacao_arquivos`, `ler_extrair_infos_pdf`); permissions em arquivo próprio |
| Uso de ViewSets / Routers | 2 | Todas as views usam `APIView` manual em vez de `ViewSet`/`ModelViewSet`; sem `DefaultRouter` |
| Permissões e autenticação | 3 | Permissões customizadas bem definidas (`IsAluno`, `IsSecretaria`, `IsCoordenador`) via query no banco; JWT via `simplejwt`; porém `ProcessoAPIView` tem `permission_classes = []` (ausência de proteção) |
| Paginação | 3 | `PageNumberPagination` aplicado em `AlunoAPIView` e `ProcessoAPIView`; falta configuração global no `settings.py` |
| Filtering | 3 | Filtros manuais via `query_params`; `django_filters` instalado mas não usado nas views |
| Throttling | 1 | Sem throttling configurado |
| Código limpo e legível | 3 | Código organizado, mas há imports desnecessários em `models.py` (ex: `from django.db.models import functions`, `from enum import unique`, `import email`) |
| Tratamento de exceções | 3 | `IntegrityError` capturado em `ProcessoAPIView.post`; `get_object_or_404` em `ProcessoDetailAPIView`; porém `is_valid()` chamado duas vezes no `post` de `ProcessoAPIView` (redundante e bug lógico) |
| Validações em serializers | 4 | `validate()` no `ProcessoSerializer` impede segundo processo aberto; `make_password` no `create`; validação de CPF e email institucional |
| Queries otimizadas (N+1) | 4 | `ProcessoDetailAPIView` usa `select_related` + `prefetch_related` corretamente |
| Testes unitários e de integração | 3 | Cobertura de testes para `Processo`, `Aluno`, `Curso`, validadores, email e PDF; fixtures em `conftest.py`; ausência de testes para `UploadContrato`, `AvaliarContratoAPIView` e `AvaliarRelatorioAPIView` |

**Subtotal Codificação:** 33/55 → **média 3,0**

---

## 3. Conformidade

### Critérios avaliados

| Critério | Pontuação (1–5) | Observação |
|---|---|---|
| Segurança — SECRET_KEY exposta | 1 | `SECRET_KEY` hardcoded no `settings.py` com valor `django-insecure-*`; crítico |
| Segurança — DEBUG em produção | 1 | `DEBUG = True` hardcoded; não controlado por variável de ambiente |
| Segurança — CORS | 2 | `corsheaders` não instalado; sem configuração de CORS |
| Segurança — SQL Injection | 4 | ORM Django usado corretamente; sem raw queries identificadas |
| Segurança — Autenticação | 3 | JWT configurado via `simplejwt`; porém permissões customizadas fazem query ao banco a cada request (sem cache) e `ProcessoAPIView` está desprotegida |
| Segurança — Validação de entrada | 4 | Validadores de CPF (algoritmo Receita Federal), email institucional, PDF com verificação de magic bytes em `validacao_arquivos` |
| Padrões REST — Verbos HTTP | 4 | GET, POST, PATCH usados corretamente; ausência de DELETE (pode ser intencional) |
| Padrões REST — Códigos de status | 3 | HTTP 200/201/400/404/409 usados; porém GET sem resultados retorna 200 com mensagem em vez de 404 |
| LGPD / Privacidade | 2 | Senha hasheada com `make_password`; CPF armazenado em texto claro (não mascarado nas respostas do serializer); sem anonimização |
| Deploy / Ambiente | 2 | `load_dotenv` presente mas `SECRET_KEY` e `DEBUG` não migrados para `.env`; banco SQLite (não adequado para produção); `ALLOWED_HOSTS = []` |
| Migrations controladas | 3 | Pasta `migrations/` presente; migrations do `core` vazias (sem migrations geradas para os models) |
| Versões de dependências | 3 | `pyproject.toml` presente; sem `requirements.txt` com versões fixadas |

**Subtotal Conformidade:** 32/60 → **média 2,7**

---

## Resumo Geral de Pontuação

| Dimensão | Média | Conceito |
|---|---|---|
| Especificação | 3,3 / 5,0 | Regular–Bom |
| Codificação | 3,0 / 5,0 | Regular |
| Conformidade | 2,7 / 5,0 | Insuficiente–Regular |
| **Geral** | **3,0 / 5,0** | **Regular** |

---

## Não Conformidades e Desvios

### Críticos 🔴
1. **`SECRET_KEY` hardcoded** em `setup/settings.py` — expõe a chave criptográfica do projeto no repositório.
2. **`DEBUG = True` fixo** — em qualquer deploy não-local, dados de traceback serão expostos.
3. **`ProcessoAPIView` sem `permission_classes`** — qualquer usuário não autenticado pode listar, criar e editar processos de estágio.
4. **Migrations vazias** — `core/migrations/` contém apenas `__init__.py`; os models `Aluno`, `Processo`, `Contrato`, `Relatorio` etc. não têm migrations geradas, impossibilitando o deploy real.

### Importantes 🟡
5. **`is_valid()` chamado duas vezes** em `ProcessoAPIView.post` — o segundo bloco `if not serializer.is_valid()` nunca será executado pois `raise_exception=True` já levantou exceção; é código morto e confuso.
6. **Permissões via query ao banco** — cada request faz até 3 queries de verificação de perfil (Aluno, Secretaria, Coordenador) sem cache; potencial gargalo.
7. **Sem throttling** — endpoints de upload de PDF e criação de processo sem rate limiting.
8. **CORS não configurado** — impossibilita uso por frontend web em domínio diferente.
9. **CPF exposto no serializer** — `AlunoSerializer` retorna `cpf` na resposta; dado sensível conforme LGPD.
10. **`NestedContratoSerializer` inclui `nome_empresa`** — campo que não existe em `Contrato`, indicando inconsistência entre serializer e model.
11. **`django_filters` instalado mas não utilizado** — filtros implementados manualmente via `query_params`.

### Menores 🟢
12. **Imports desnecessários em `models.py`** — `from enum import unique`, `import email`, `from django.db.models import functions` não utilizados.
13. **`ALLOWED_HOSTS = []`** — deve ser configurado via variável de ambiente.
14. **Banco SQLite em desenvolvimento** — adequado para dev, mas deve haver configuração para produção (PostgreSQL).
15. **GET sem resultados retorna HTTP 200** — semanticamente deveria retornar 404 ou lista vazia padrão sem mensagem customizada.
16. **`areaId` como nome de ForeignKey** — nomenclatura não segue convenção Django (deveria ser `area`).

---

## Recomendações Práticas

### Segurança e Conformidade
```python
# settings.py — migrar para variáveis de ambiente
import os
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

```python
# Adicionar corsheaders
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
```

### Proteção do ProcessoAPIView
```python
class ProcessoAPIView(APIView):
    permission_classes = [IsAluno | IsSecretaria | IsCoordenador]  # era []
```

### Remover is_valid() duplicado
```python
# Remover o bloco redundante:
# if not serializer.is_valid():  ← REMOVER
#     ...
```

### Gerar Migrations
```bash
python manage.py makemigrations core
python manage.py makemigrations user_auth
```

### Throttling global
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '200/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

### Mascarar CPF
```python
class AlunoSerializer(serializers.ModelSerializer):
    cpf_mascarado = serializers.SerializerMethodField(read_only=True)
    
    def get_cpf_mascarado(self, obj):
        cpf = obj.cpf.replace('.', '').replace('-', '')
        return f"***.***.{cpf[6:9]}-**"
```

### Migrar para ViewSet (médio prazo)
```python
# Substituir APIView manual por ModelViewSet + Router para reduzir boilerplate
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet

class ProcessoViewSet(ModelViewSet):
    serializer_class = ProcessoSerializer
    permission_classes = [IsAluno | IsSecretaria | IsCoordenador]
    filterset_fields = ['status', 'nome_empresa']
    # ...

router = DefaultRouter()
router.register('processo', ProcessoViewSet)
```

### Testes em falta (aumentar cobertura)
- `UploadContrato` — testar upload válido, inválido (não-PDF), tamanho excedido
- `AvaliarContratoAPIView` — testar aprovação e reprovação
- `AvaliarRelatorioAPIView` — testar fluxo completo
- Testes de permissão — garantir que usuários sem perfil recebem 403

---

## Aspectos Positivos Reconhecidos

- ✅ Arquitetura de services bem organizada (`email_service`, `upload_*`, `ler_extrair_infos_pdf`)
- ✅ Validação de CPF com algoritmo completo da Receita Federal
- ✅ Validação de email institucional por domínio
- ✅ Validação de PDF com verificação de magic bytes (segurança contra bypass de extensão)
- ✅ `select_related` + `prefetch_related` em `ProcessoDetailAPIView` (evita N+1)
- ✅ OpenAPI documentado com `drf_spectacular` e `@extend_schema`
- ✅ Lógica de negócio correta: impede segundo processo aberto para o mesmo aluno
- ✅ Documentação de casos de uso detalhada em `docs/Elaboracao/Casos de Uso/`
- ✅ Enums centralizados com `TextChoices`/`IntegerChoices` do Django
- ✅ Suite de testes com `pytest` e fixtures reutilizáveis em `conftest.py`
