---
id: fazer_login
title: Fazer Login
---

### Fazer Login

- **Atores:**
    - Aluno / Secretaria 
    - Sistema

- **Pré-Condições:**
    - O Usuário deve ter um cadastro ativo no sistema da instituição.

- **Fluxo Básico:**
    1. Usuário acessa a página inicial do sistema.
    2. Usuário fornece e-mail institucional (ou matrícula) e senha.
    3. Usuário clica em "Entrar".
    4. Sistema autentica as credenciais no banco de dados.
    5. Sistema redireciona o Usuário para o painel/dashboard correspondente ao seu perfil.

- **Fluxos Alternativos:**
    - **4a. Dados do Usuário Inválidos**
        - 4a1. Sistema exibe a mensagem de erro: *"Usuário ou senha incorretos."*
        - 4a2. Sistema limpa o campo de senha e mantém o usuário na tela de login.
    - **4b. Primeiro acesso do Usuário**
        - 4b1. Sistema redireciona o Usuário para a página de redefinição de senha obrigatória.

- **Pós-condições:**
    - Uma sessão segura é iniciada para o usuário.

- **Regras de Negócio:**
    - O sistema deve bloquear o acesso após 5 tentativas incorretas consecutivas.
    - As senhas devem trafegar e ser armazenadas com criptografia.