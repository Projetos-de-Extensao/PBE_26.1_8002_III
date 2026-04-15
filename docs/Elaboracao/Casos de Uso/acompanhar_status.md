---
id: acompanhar_status
title: Acompanhar Status do Processo
---

### Acompanhar Status do Processo

- **Atores:**
    - Aluno / Secretaria
    - Sistema

- **Pré-Condições:**
    - O Usuário deve estar logado no sistema.

- **Fluxo Básico:**
    1. Usuário acessa o painel/dashboard principal.
    2. Sistema busca os processos vinculados ao usuário.
    3. Sistema exibe uma lista ou linha do tempo com o status atualizado de cada envio (ex: *"Em análise", "Aprovado", "Reprovado"*).
    4. Usuário seleciona um processo para ver mais detalhes.
    5. Sistema exibe o histórico de movimentações daquele contrato.

- **Fluxos Alternativos:**
    - **2a. Usuário não possui processos iniciados**
        - 2a1. Sistema exibe a mensagem *"Você não possui processos de estágio ativos"* e mostra o botão "Iniciar Processo".
    - **5a. Usuário deseja baixar o arquivo validado (Ação: Fazer Download do Documento)**
        - 5a1. Usuário clica no ícone de download.
        - 5a2. Sistema inicia a transferência do PDF para o dispositivo do usuário.

- **Pós-condições:**
    - Nenhuma alteração é feita no banco de dados (ação apenas de leitura).

- **Regras de Negócio:**
    - O Aluno só tem permissão para visualizar os seus próprios processos.
    - A Secretaria tem permissão para visualizar os processos de todos os alunos cadastrados na instituição.