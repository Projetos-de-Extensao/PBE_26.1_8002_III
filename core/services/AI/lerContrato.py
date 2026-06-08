import json
from pathlib import Path
from google.genai import types
from .client import client

# Carrega o prompt do .md uma única vez quando o módulo é importado
_PROMPT_PATH = Path(__file__).parent / "prompts" / "leitorArquivo.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def lerContrato(texto_contrato: str) -> dict:
    """
    Envia o texto extraído do contrato para o Gemini e retorna
    um dict com os campos do model Contrato.
    """
    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=texto_contrato,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    return json.loads(resposta.text)