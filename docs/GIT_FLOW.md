# 🚀 Guia de Git Flow & Boas Práticas de Versionamento

Este documento estabelece as diretrizes profissionais de versionamento, padronização de branches e fluxo de commits para a equipe de desenvolvimento do projeto.

---

## 📌 1. Estrutura de Branches

Adotamos o modelo **Git Flow** adaptado para integração contínua, estruturado da seguinte forma:

```
[main] (Produção / Estável)
  ▲
  │ (Release / Hotfix)
[release/vX.Y.Z] / [hotfix/nome]
  ▲
  │ (Merge via PR)
[develop] (Integração Principal)
  ▲
  │ (Criada a partir da develop)
[feature/nome-da-funcionalidade] / [fix/descricao-do-bug]
```

### 🔹 Branches Principais (Permanentes)

* **`main`**: Contém exclusivamente o código em estado de **produção**, testado e totalmente estável.
  * *Regra:* Nenhum commit direto é permitido na `main`. Alterações entram apenas via **Release** ou **Hotfix**. Cada publicação gera uma **Git Tag** (ex: `v1.0.0`).
* **`develop`**: Branch de **integração contínua** do projeto.
  * *Regra:* Todas as novas funcionalidades e correções aprovadas em Code Review são mescladas aqui antes de ir para a `main`.

---

### 🔸 Branches Temporárias (De Suporte)

| Tipo de Branch | Branch de Origem | Branch de Destino | Padrão de Nomenclatura | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| **Feature** | `develop` | `develop` | `feature/<nome-descritivo>` | `feature/autenticacao-jwt` |
| **Fix / Bugfix** | `develop` | `develop` | `fix/<descricao-curta>` | `fix/validacao-email` |
| **Hotfix** | `main` | `main` e `develop` | `hotfix/<versao-ou-descricao>` | `hotfix/v1.0.1-crash-login` |
| **Release** | `develop` | `main` e `develop` | `release/v<X.Y.Z>` | `release/v1.1.0` |

---

## 📝 2. Padronização de Commits (Conventional Commits)

Os commits devem seguir o padrão **Conventional Commits** em português (PT-BR), garantindo um histórico legível e auditável.

### Estrutura do Commit:
```text
<tipo>(<escopo>): <descrição no imperativo e em minúsculas>

[corpo opcional explicando o motivo e os detalhes]
```

### Tipos Permitidos:

* `feat`: Nova funcionalidade para o usuário (ex: `feat(auth): adicionar suporte a login via token JWT`).
* `fix`: Correção de um bug (ex: `fix(views): corrigir erro 500 no endpoint de cadastro`).
* `docs`: Alterações na documentação (ex: `docs(readme): atualizar instruções do ambiente local`).
* `style`: Formatação, ponto e vírgula, sem alteração de regra de negócio (ex: `style(linter): aplicar regras pep8`).
* `refactor`: Mudança no código que não corrige bug nem adiciona funcionalidade (ex: `refactor(services): simplificar extrator de pdf`).
* `test`: Adição ou correção de testes (ex: `test(relatorio): adicionar testes unitários para gerador de pdf`).
* `chore`: Tarefas de manutenção, atualização de dependências ou build (ex: `chore(deps): atualizar pacote django para 5.0.3`).
* `ci`: Alterações nos arquivos de configuração do GitHub Actions/CI (ex: `ci(github): adicionar etapa de execucao do pytest`).

---

## 🔄 3. Passo a Passo do Fluxo de Trabalho

### ⚙️ Caso A: Desenvolvendo uma Nova Funcionalidade (`feature`)

1. **Atualize a branch `develop` local:**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Crie sua branch de funcionalidade:**
   ```bash
   git checkout -b feature/geracao-relatorios-pdf
   ```

3. **Faça suas alterações e commite com mensagens padronizadas:**
   ```bash
   git add .
   git commit -m "feat(pdf): adicionar service para geracao de relatorios"
   ```

4. **Envie a branch para o repositório remoto:**
   ```bash
   git push -u origin feature/geracao-relatorios-pdf
   ```

5. **Abra um Pull Request (PR):**
   * **Base:** `develop` ◄ **Compare:** `feature/geracao-relatorios-pdf`
   * Aguarde a aprovação dos testes automatizados (CI) e o Code Review de ao menos 1 colega.

---

### 🚨 Caso B: Correção Urgente em Produção (`hotfix`)

1. **Crie a branch a partir da `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/v1.0.1-correcao-seguranca
   ```

2. **Realize a correção e commite:**
   ```bash
   git commit -m "fix(security): corrigir falha na validacao de token expirado"
   ```

3. **Abra os Pull Requests:**
   * PR 1: `hotfix/v1.0.1-correcao-seguranca` ➔ `main`
   * PR 2: `hotfix/v1.0.1-correcao-seguranca` ➔ `develop`

4. **Gere a Tag de Versão na `main`:**
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.0.1 -m "Versão 1.0.1 - Correção urgente de segurança"
   git push origin v1.0.1
   ```

---

## 🧹 4. Limpeza de Branches Locais e Remotas

Após a aprovação e merge do seu Pull Request, exclua a branch para manter o repositório limpo:

```bash
# Limpar referências remotas que já foram excluídas
git fetch --prune

# Excluir a branch localmente
git branch -d feature/geracao-relatorios-pdf
```

---

## 🛡️ 5. Boas Práticas & Segurança

* ❌ **Nunca faça push com `--force`** na branch `main` ou `develop`.
* 🔒 **Nunca suba credenciais ou segredos**: Arquivos `.env`, chaves de API ou bancos SQLite locais devidamente ignorados via `.gitignore`.
* 🧪 **Sempre rode os testes locais antes de subir o PR**:
  ```bash
  uv run pytest
  ```
