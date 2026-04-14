# 📋 Como Adicionar Novos Cards de Casos de Uso

Guia passo a passo para adicionar novos cards de caso de uso.

---

## Estrutura

```
docs/Elaboracao/
├── casos_de_uso.md              ← Página principal (galeria de cards)
└── casos_de_uso/
    ├── criacao_conta.md          ← Página individual
    └── entrada_sistema.md        ← Página individual
```

---

## Passo a Passo

### 1️⃣ Criar a página individual

Crie um `.md` em `docs/Elaboracao/casos_de_uso/` usando este template:

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

## Fluxos Alternativos
- **2a.** Descrição do cenário alternativo
    - 2a1. Ação do sistema
```

---

### 2️⃣ Adicionar o card na galeria

Abra `docs/Elaboracao/casos_de_uso.md` e adicione um novo bloco **dentro** do `<div id="uc-grid">`:

```html
<!-- Card N -->
<div class="use-case-card" data-tags="palavras chave para busca">
    <span class="uc-badge">Módulo</span>
    <h3>Título do Caso de Uso</h3>
    <p class="uc-card-desc">Breve descrição do que este caso de uso faz (máx. 3 linhas).</p>
    <a href="casos_de_uso/nome_do_arquivo/" class="use-case-btn">Ver mais →</a>
</div>
```

> ⚠️ **Detalhes importantes:**
> - `data-tags`: palavras-chave para o filtro de busca
> - `uc-badge`: nome do módulo (ex: Conta, Perfil, Mensagem)
> - O limite da descrição é de **3 linhas**. O texto extra será cortado com `...`
> - O link usa o nome do arquivo **sem** `.md` e **com** `/` no final

---

### 3️⃣ Registrar no `mkdocs.yml`

Adicione a nova página no `nav`:

```yaml
      - Casos de Uso:
          - Visão Geral: Elaboracao/casos_de_uso.md
          - Criação de Conta: Elaboracao/casos_de_uso/criacao_conta.md
          - Entrada no Sistema: Elaboracao/casos_de_uso/entrada_sistema.md
          - Novo Caso: Elaboracao/casos_de_uso/novo_caso.md   # ← novo
```

---

## ✅ Checklist

- [ ] Arquivo `.md` criado em `docs/Elaboracao/casos_de_uso/`
- [ ] Card HTML adicionado dentro do `<div id="uc-grid">` em `casos_de_uso.md`
- [ ] `data-tags` preenchido com palavras-chave
- [ ] Entrada adicionada no `nav` do `mkdocs.yml`
- [ ] Testou com `mkdocs serve`

---

## 💡 Exemplo: Adicionando "Recuperar Senha"

**1.** Criar `docs/Elaboracao/casos_de_uso/recuperar_senha.md` com o conteúdo do caso de uso.

**2.** Adicionar card em `casos_de_uso.md`:

```html
<div class="use-case-card" data-tags="senha recuperar email redefinir">
    <span class="uc-badge">Conta</span>
    <h3>Recuperar Senha</h3>
    <p class="uc-card-desc">Recuperação de senha via link enviado por e-mail para o usuário.</p>
    <a href="casos_de_uso/recuperar_senha/" class="use-case-btn">Ver mais →</a>
</div>
```

**3.** Adicionar no `mkdocs.yml`:

```yaml
          - Recuperar Senha: Elaboracao/casos_de_uso/recuperar_senha.md
```

---

## 📌 Notas

- A **paginação** é automática — exibe 6 cards por página
- A **busca** filtra por título, descrição e `data-tags`
- Para alterar cards por página, edite `CARDS_PER_PAGE` no `<script>` em `casos_de_uso.md`
