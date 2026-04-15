---
id: fazer_download
title: Fazer Download do Contrato
---

### Fazer Download do Contrato (Extend)

- **Atores:**
    - Aluno / Secretaria
    - Sistema

- **Pré-Condições:**
    - O contrato alvo já deve ter sido armazenado no banco de dados.

- **Fluxo Básico:**
    1. Usuário acessa a tela de detalhes do processo.
    2. Usuário clica no ícone de download ao lado do contrato.
    3. Sistema localiza o arquivo no servidor e inicia a transferência (Stream) para a máquina do usuário.

- **Fluxos Alternativos:**
    - **3a. Arquivo corrompido ou indisponível**
        - 3a1. Sistema informa: *"Erro: Não foi possível localizar o arquivo no servidor."*

- **Pós-condições:**
    - Uma cópia local do PDF é salva no dispositivo do usuário.

- **Regras de Negócio:**
    - A URL do contrato deve ser protegida (tokens temporários ou validação de sessão) para evitar acesso público.