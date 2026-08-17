<h1 align="center">📄 Gestão de Documentação de Estágio Obrigatório</h1>

<p align="center">
  <em>API RESTful inteligente para automatizar o fluxo de documentação de estágio do Ibmec</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/Gemini_API-AI-8E75B2?logo=google&logoColor=white" alt="Gemini">
</p>

---

## 📋 Sobre o Projeto

Este projeto foi desenvolvido durante a disciplina de **Projeto Back-End 26.1** com o objetivo de solucionar os gargalos operacionais enfrentados pela **Secretaria** do Ibmec na gestão e na validação da documentação de estágio obrigatório.

Atualmente, o processo de estágio envolve diversas tarefas manuais, burocráticas e repetitivas, o que aumenta a incidência de erros e a necessidade de retrabalho. Nossa solução visa **automatizar esses fluxos** e **reduzir a complexidade** associada ao recebimento, versionamento e validação de documentos.

---

## 👥 Equipe

| Membro | Papel |
|--------|-------|
| Bernardo | Desenvolvedor |
| Caio | Desenvolvedor |
| Daniel | Desenvolvedor |
| Lucas | Desenvolvedor |
| Otto | Desenvolvedor |

**Cliente:** CASA e Secretaria do Ibmec

---

## 🛠️ Tecnologias

| Tecnologia | Descrição |
|------------|-----------|
| **Python** | Linguagem principal |
| **Django + DRF** | Framework web e API RESTful |
| **Supabase** | Banco de dados PostgreSQL remoto |
| **Gemini API** | Modelo de IA |
---

## 🚀 Como Executar

O projeto pode ser executado de duas formas: através de **Containers (Docker Compose)** ou **Localmente (desenvolvimento manual)**.

---

### Método 1: Utilizando Docker Compose (Recomendado)

Esta forma inicializa automaticamente todos os serviços necessários em paralelo (Django API, RabbitMQ Broker e Celery Worker). O banco de dados é o **Supabase** (PostgreSQL remoto).

#### Pré-requisitos:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando em sua máquina.
* Conta no [Supabase](https://supabase.com/) com um projeto criado.

#### Passo a Passo:

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_III.git
   cd PBE_26.1_8002_III
   ```

2. **Configurar as Variáveis de Ambiente:**
   Duplique o arquivo `.env.example`, salve como `.env` e preencha com sua chave de API do Gemini:
   ```bash
   cp .env.example .env
   ```
   Abra o arquivo `.env` e insira sua chave:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```
   E a **connection string do Supabase** (copie de **Settings > Database > Connection string > URI** no dashboard):
   ```env
   DATABASE_URL=postgresql://postgres.SEU_PROJECT_REF:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```

3. **Subir os containers:**
   ```bash
   docker compose up --build
   ```

4. **Acessar as plataformas:**
   * **API Django & Swagger UI (Documentação):** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
   * **Dashboard Metabase:** [http://localhost:3000/](http://localhost:3000/)
   * **Painel Administrativo do RabbitMQ:** [http://localhost:15672/](http://localhost:15672/) (Login: `guest` / Senha: `guest`)

### Método 2: Execução Local (Desenvolvimento Manual)

#### Pré-requisitos:
* Ter o **RabbitMQ** instalado e rodando localmente no host na porta `5672`.
* Conta no [Supabase](https://supabase.com/) com um projeto criado.

#### Passo a Passo:

1. **Instalar o `uv`** (gerenciador de pacotes rápido e moderno):
   * **Windows (PowerShell):**
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   * **Linux / macOS (curl):**
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   *(Reinicie o terminal após instalar o uv).*

2. **Instalar as dependências e criar o ambiente virtual:**
   ```bash
   uv sync
   ```

3. **Configurar as variáveis de ambiente:**
   Copie `.env.example` para `.env`, adicione a sua `GEMINI_API_KEY` e a **connection string do Supabase** em `DATABASE_URL`.

4. **Rodar as migrações do banco de dados:**
   ```bash
   uv run python manage.py migrate
   ```

5. **Executar o servidor de desenvolvimento Django:**
   ```bash
   uv run python manage.py runserver
   ```

6. **Executar o Worker do Celery** (em outro terminal):
   ```bash
   uv run celery -A setup worker -l info
   ```

7. **Rodar a documentação local (MkDocs):**
   ```bash
   uv run mkdocs serve
   ```

8. **Rodar os testes unitários:**
   ```bash
   uv run pytest
   ```

---

## 📂 Repositórios Relacionados

| Repositório | Descrição |
|-------------|-----------|
| [**PBE_26.1_8002_III**](https://github.com/Projetos-de-Extensao/PBE_26.1_8002_III) | Repositório Oficial da API. |
