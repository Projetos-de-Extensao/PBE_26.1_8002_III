---
id: pesquisar_alunos
title: Pesquisar Alunos
---

### Pesquisar Alunos

- **Atores:**
    - Secretaria
    - Sistema

- **Pré-Condições:**
    - O Usuário deve estar logado no sistema.

- **Fluxo Básico:**
    1. Secretaria acessa a tela de "Gestão de Alunos".
    2. Sistema exibe uma barra de busca e filtros.
    3. Secretaria digita o nome, CPF ou número de matrícula do aluno.
    4. Sistema busca na base de dados os registros correspondentes.
    5. Sistema exibe a lista de alunos encontrados.
    6. Secretaria clica no perfil desejado para consultar o histórico de documentos.

- **Fluxos Alternativos:**
    - **4a. Nenhum aluno encontrado**
        - 4a1. Sistema exibe a mensagem *"Nenhum aluno encontrado com os termos pesquisados"*.
        - 4a2. Sistema exibe opção para limpar filtros ou ir para a tela de "Cadastrar Aluno".

- **Pós-condições:**
    - A Secretaria visualiza os detalhes e todo o histórico de estágios do aluno pesquisado.

- **Regras de Negócio:**
    - A busca deve ser capaz de realizar aproximações fonéticas ou buscas parciais (ex: digitar apenas o primeiro nome).
    - O acesso a essa tela é restrito ao perfil da Secretaria ou Coordenação.