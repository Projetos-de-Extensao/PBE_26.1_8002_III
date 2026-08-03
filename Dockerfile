FROM python:3.12-slim

# Evita prompts interativos e bufferiza stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Instala uv (gerenciador de pacotes rápido)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copia arquivos de dependência primeiro (cache de camada Docker)
COPY pyproject.toml uv.lock ./

# Instala dependências do projeto no ambiente virtual (/app/.venv)
RUN uv sync --frozen --no-dev

# Copia o restante do código da aplicação
COPY . .

EXPOSE 8000

# Comando padrão: roda o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

