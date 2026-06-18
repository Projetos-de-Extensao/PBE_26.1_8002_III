import json
from pathlib import Path
from google.genai import types
from .client import client

# Carrega os prompts dos .md uma única vez quando o módulo é importado
_PROMPT_EXTRATOR_PATH = Path(__file__).parent / "prompts" / "leitorRelatorio.md"
_SYSTEM_PROMPT_EXTRATOR = _PROMPT_EXTRATOR_PATH.read_text(encoding="utf-8")

_PROMPT_AVALIADOR_PATH = Path(__file__).parent / "prompts" / "avaliadorRelatorio.md"
_SYSTEM_PROMPT_AVALIADOR = _PROMPT_AVALIADOR_PATH.read_text(encoding="utf-8")


def lerRelatorio(texto_relatorio: str) -> dict:
    """
    Envia o texto extraído do relatório para o Gemini e retorna
    um dict com os campos 'titulo' e 'corpo'.
    """
    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=texto_relatorio,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT_EXTRATOR,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    return json.loads(resposta.text)


def carregar_ementa_curso(curso_nome: str) -> str:
    """
    Normaliza o nome do curso para localizar o arquivo markdown de ementa.
    Caminho esperado: ementas/nome_do_curso.md (normalizado).
    Exemplo: "Engenharia de Software" -> "engenharia_de_software.md".
    """
    import unicodedata
    import re
    from django.conf import settings

    # Normaliza o nome do curso para o padrão snake_case sem acentuação
    normalized = unicodedata.normalize('NFKD', curso_nome).encode('ascii', 'ignore').decode('utf-8')
    normalized = normalized.lower().strip()
    normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
    normalized = normalized.strip('_')
    filename = f"{normalized}.md"

    # Define os caminhos locais a serem checados
    caminhos = [
        Path(settings.BASE_DIR) / 'ementas' / filename,
        Path(settings.BASE_DIR) / 'core' / 'fixtures' / 'ementas' / filename,
        Path(settings.BASE_DIR) / 'media' / 'ementas' / filename,
    ]

    for caminho in caminhos:
        if caminho.exists():
            return caminho.read_text(encoding='utf-8')

    raise FileNotFoundError(f"Ementa para o curso '{curso_nome}' não encontrada. Arquivo esperado: {filename}")


def avaliarRelatorio(corpo_relatorio: str, ementa_curso: str) -> dict:
    """
    Envia o corpo do relatório e a ementa do curso para a IA.
    A ementa do curso é injetada como System Instruction junto com regras rígidas de avaliação.
    O corpo do relatório é enviado no User Prompt.
    Retorna um dict contendo 'status' ('APROVADO' | 'REPROVADO') e 'justificativa'.
    Garante também a chave 'compativel' (bool) para retrocompatibilidade.
    """
    import os

    # Placeholder configurável para o provedor de IA a ser utilizado
    API_PROVIDER = os.getenv("AI_API_PROVIDER", "gemini")

    system_prompt = (
        f"Você é um coordenador de estágio rigoroso. Sua única função é validar se as atividades descritas no relatório do aluno se encaixam nos tópicos desta ementa fornecida.\n\n"
        f"EMENTA DO CURSO:\n{ementa_curso}\n\n"
        f"Você NÃO PODE usar conhecimentos externos. Se as atividades não estiverem claras na ementa, você DEVE reprovar.\n"
        f"Responda em formato JSON contendo \"status\": \"APROVADO\" ou \"REPROVADO\", e \"justificativa\": \"sua explicação breve\"."
    )

    if API_PROVIDER == "gemini":
        resposta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=corpo_relatorio,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(resposta.text)
    else:
        # Placeholder para outros provedores (ex: OpenAI)
        # data = openai_client.chat.completions.create(...)
        data = {
            "status": "APROVADO",
            "justificativa": "Simulado com sucesso usando o provedor alternativo."
        }

    # Mantém a retrocompatibilidade com o banco de dados/tarefas Celery existentes
    if "compativel" not in data:
        data["compativel"] = data.get("status") == "APROVADO"

    return data

