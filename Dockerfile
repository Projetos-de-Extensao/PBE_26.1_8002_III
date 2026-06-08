FROM python:3.12-slim

# Evita prompts interativos e bufferiza stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências de sistema para PDF (poppler, tesseract) e build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Instala uv (gerenciador de pacotes)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copia arquivos de dependência primeiro (cache de camada)
COPY pyproject.toml uv.lock ./

# Instala dependências do projeto
RUN uv sync --frozen --no-dev

# Copia o restante do projeto
COPY . .

EXPOSE 8000

# Comando padrão: roda o servidor Django
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
