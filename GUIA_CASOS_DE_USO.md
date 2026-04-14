# 📋 Como Adicionar Novos Cards de Casos de Uso

Guia passo a passo para adicionar novos casos de uso ao sistema de cards.

---

## Estrutura Atual

```
docs/Elaboracao/
├── casos_de_uso.md              ← Página principal (cards)
└── casos_de_uso/
    ├── criacao_conta.md          ← Página individual
    ├── entrada_sistema.md        ← Página individual
    └── README.md                 ← Este guia
```

---

## Passo a Passo

### 1️⃣ Criar a página individual do caso de uso

Crie um novo arquivo `.md` dentro de `docs/Elaboracao/casos_de_uso/`.

> **Dica:** Use nomes descritivos em snake_case, ex: `recuperar_senha.md`

Use este template como base:

```markdown
---
title: Nome do Caso de Uso
---

# Nome do Caso de Uso

## Atores

- Ator 1
- Ator 2

## Pré-Condições

- Condição necessária

## Fluxo Básico

1. Passo 1
2. Passo 2
3. Passo 3

## Fluxos Alternativos

- **2a.** Descrição do cenário alternativo
    - 2a1. Ação do sistema
```

---

### 2️⃣ Adicionar o card na página principal

Abra o arquivo `docs/Elaboracao/casos_de_uso.md` e adicione um novo bloco `<div>` **dentro** do `<div class="use-case-grid">`, logo antes do `</div>` de fechamento do grid:

```markdown
<div class="use-case-card" markdown>

### :material-icon-nome: Título do Card

Breve descrição do que este caso de uso faz (1-2 linhas).

**Atores:** Ator 1, Ator 2

[Ver mais :material-arrow-right:](casos_de_uso/nome_do_arquivo.md){ .use-case-btn }

</div>
```

> ⚠️ **Importante:**
> - O `markdown` no `<div>` é obrigatório para o MkDocs processar o Markdown dentro do HTML
> - O link em `Ver mais` deve apontar para `casos_de_uso/nome_do_arquivo.md`
> - A classe `{ .use-case-btn }` aplica o estilo do botão

#### 🎨 Ícones disponíveis

Troque `:material-icon-nome:` por qualquer ícone do [Material Design Icons](https://pictogrammers.com/library/mdi/). Exemplos úteis:

| Ícone | Código |
|---|---|
| 👤 Conta | `:material-account-plus:` |
| 🔑 Login | `:material-login:` |
| 🔒 Senha | `:material-lock-reset:` |
| ✏️ Edição | `:material-pencil:` |
| 👥 Perfil | `:material-account-circle:` |
| 💬 Mensagem | `:material-message:` |
| 📷 Galeria | `:material-image-multiple:` |
| 📝 Blog | `:material-post:` |
| 👥 Grupo | `:material-account-group:` |
| 🔍 Pesquisa | `:material-magnify:` |
| 🗑️ Exclusão | `:material-delete:` |

---

### 3️⃣ Registrar no `mkdocs.yml`

Abra `mkdocs.yml` na raiz do projeto e adicione a nova página na seção `nav`, dentro de **Casos de Uso**:

```yaml
  - Elaboração:
      - Index: Elaboracao/index.md
      - Requisitos: Elaboracao/das.md
      - Casos de Uso:
          - Visão Geral: Elaboracao/casos_de_uso.md
          - Criação de Conta: Elaboracao/casos_de_uso/criacao_conta.md
          - Entrada no Sistema: Elaboracao/casos_de_uso/entrada_sistema.md
          - Novo Caso: Elaboracao/casos_de_uso/novo_caso.md   # ← adicione aqui
```

---

## ✅ Checklist Rápido

Ao adicionar um novo caso de uso, confirme que:

- [ ] Arquivo `.md` criado em `docs/Elaboracao/casos_de_uso/`
- [ ] Card adicionado dentro do `<div class="use-case-grid">` em `casos_de_uso.md`
- [ ] Link do botão "Ver mais" aponta para o arquivo correto
- [ ] Entrada adicionada no `nav` do `mkdocs.yml`
- [ ] Testou localmente com `mkdocs serve`

---

## 💡 Exemplo Completo

Digamos que você quer adicionar o caso de uso **Recuperar Senha**:

**1. Criar** `docs/Elaboracao/casos_de_uso/recuperar_senha.md`:

```markdown
---
title: Recuperar Senha
---

# Recuperação de senha do usuário

## Atores
- Usuário
- Sistema

## Pré-Condições
- Usuário deve estar cadastrado

## Fluxo Básico
1. Usuário clica em "Esqueci minha senha"
2. Usuário informa o e-mail cadastrado
3. Sistema envia link de redefinição por e-mail
4. Usuário acessa o link e define nova senha
5. Sistema confirma a alteração

## Fluxos Alternativos
- **2a.** E-mail não encontrado
    - 2a1. Sistema exibe mensagem de erro
```

**2. Adicionar card** em `casos_de_uso.md`:

```markdown
<div class="use-case-card" markdown>

### :material-lock-reset: Recuperar Senha

Fluxo de recuperação de senha via link enviado por e-mail para usuários cadastrados.

**Atores:** Usuário, Sistema

[Ver mais :material-arrow-right:](casos_de_uso/recuperar_senha.md){ .use-case-btn }

</div>
```

**3. Atualizar** `mkdocs.yml`:

```yaml
          - Recuperar Senha: Elaboracao/casos_de_uso/recuperar_senha.md
```

Pronto! 🎉
