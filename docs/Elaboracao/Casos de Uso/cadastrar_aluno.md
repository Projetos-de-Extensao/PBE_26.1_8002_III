---
id: cadastrar_aluno
title: Cadastrar Aluno
---

### Cadastrar Aluno

- **Atores:**
    - Secretaria
    - Sistema

- **Pré-Condições:**
    - O Usuário (Secretaria) deve estar autenticado.

- **Fluxo Básico:**
    1. Secretaria acessa a tela "Gestão de Alunos" e clica em "Novo Aluno".
    2. Sistema exibe o formulário de cadastro.
    3. Secretaria preenche os dados (Nome, Matrícula, CPF, Curso, E-mail).
    4. Secretaria clica em "Salvar".
    5. Sistema valida a unicidade do CPF e da Matrícula.
    6. Sistema grava o aluno e exibe mensagem de sucesso.

- **Fluxos Alternativos:**
    - **5a. Matrícula ou CPF já cadastrados**
        - 5a1. Sistema exibe erro: *"A matrícula ou CPF informados já estão em uso por outro aluno."*
        - 5a2. Retorna ao passo 3.

- **Pós-condições:**
    - O novo aluno está apto a fazer login e iniciar processos de estágio.

- **Regras de Negócio:**
    - O CPF deve ser validado pelo algoritmo padrão da Receita Federal.
    - O formato do e-mail inserido deve ser válido (conter '@' e domínio).