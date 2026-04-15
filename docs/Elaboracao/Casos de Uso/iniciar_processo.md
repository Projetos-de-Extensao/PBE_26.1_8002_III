---
id: iniciar_processo
title: Iniciar Processo de Estágio
---

### Iniciar Processo de Estágio 

- **Atores:**
    - Aluno / Secretaria
    - Sistema

- **Pré-Condições:**
    - O Usuário deve estar logado no sistema.
    - O Aluno não pode ter um processo de estágio "Em Andamento" que conflite com o novo.

- **Fluxo Básico:**
    1. Usuário acessa a opção "Novo Processo" ou "Iniciar Processo".
    2. Sistema exibe um formulário solicitando os dados básicos do estágio.
    3. Usuário preenche as informações (CNPJ da empresa, datas, carga horária).
    4. Usuário anexa o Termo de Compromisso de Estágio (Ação: Anexar Documento).
    5. Usuário clica em "Enviar".
    6. Sistema valida as informações e o formato do arquivo.
    7. Sistema salva o documento e exibe mensagem de sucesso.

- **Fluxos Alternativos:**
    - **6a. Formato de arquivo ou tamanho inválido**
        - 6a1. Sistema exibe mensagem de erro: *"O documento deve ser no formato PDF e ter até 5MB."*
        - 6a2. Sistema retorna ao passo 4.
    - **6b. Campos obrigatórios em branco**
        - 6b1. Sistema destaca os campos faltantes em vermelho e exibe mensagem de erro.

- **Pós-condições:**
    - Um novo processo de estágio é criado no banco de dados.
    - O status do processo é definido como "Pendente de Análise".

- **Regras de Negócio:**
    - O documento anexado deve ser obrigatoriamente um `.pdf`.
    - A data de término do contrato não pode ultrapassar o limite máximo permitido pelo vínculo universitário do aluno.
    - Se a ação for realizada pela Secretaria, ela deve selecionar previamente para qual matrícula de aluno o processo está sendo criado.