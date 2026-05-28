<h1 align="center">📄 Gestão de Documentação de Estágio Obrigatório</h1>

<p align="center">
  <em>API RESTful inteligente para automatizar o fluxo de documentação de estágio do Ibmec</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white" alt="MySQL">
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
| **MySQL** | Banco de dados relacional |
| **Gemini API** | Modelo de IA |
---

## 🚀 Como Executar

### 1. Instalar o `uv`

O projeto utiliza o [**uv**](https://docs.astral.sh/uv/) como gerenciador de pacotes e ambientes virtuais.

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux / macOS (wget):**

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

**Linux / macOS (curl):**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Após a instalação, reinicie o terminal para que o comando `uv` fique disponível no PATH.

### 2. Clonar o repositório

```bash
git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_III.git
cd PBE_26.1_8002_III
```

### 3. Instalar dependências

O `uv` cria o ambiente virtual automaticamente e instala tudo que está no `pyproject.toml`:

```bash
uv sync
```

### 4. Executar o servidor Django

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

### 5. Rodar a documentação localmente

```bash
uv run mkdocs serve
```

### 6. Rodar os testes

```bash
uv run pytest
```

---

## 📂 Repositórios Relacionados

| Repositório | Descrição |
|-------------|-----------|
| [**PBE_26.1_8002_III**](https://github.com/Projetos-de-Extensao/PBE_26.1_8002_III) | Repositório Oficial da API. |
