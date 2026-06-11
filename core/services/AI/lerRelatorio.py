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


def avaliarRelatorio(corpo_relatorio: str, ementa_curso: str) -> dict:
    """
    Envia o corpo do relatório e a ementa do curso para o Gemini
    e retorna um dict com 'compativel' (bool) e 'justificativa' (str).
    """
    conteudo = (
        f"EMENTA DO CURSO:\n{ementa_curso}\n\n"
        f"CORPO DO RELATÓRIO:\n{corpo_relatorio}"
    )

    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=conteudo,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT_AVALIADOR,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    return json.loads(resposta.text)
