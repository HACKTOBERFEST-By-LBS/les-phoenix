"""Unique point d'entrée vers Gemma. Tout le projet passe par ici."""
import json
import os
import re

from google import genai
from google.genai import types

MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
_client = None


class GemmaError(Exception):
    """Erreur d'appel à Gemma (clé absente, quota, réseau...)."""


def _client_get():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise GemmaError("Clé API absente : crée le fichier .env (voir README).")
        _client = genai.Client(api_key=key)
    return _client


def part_bytes(data: bytes, mime: str):
    return types.Part.from_bytes(data=data, mime_type=mime)


def call(system: str, parts: list, temperature: float = 0.2) -> str:
    try:
        r = _client_get().models.generate_content(
            model=os.getenv("GEMMA_MODEL", MODEL),
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=system, temperature=temperature
            ),
        )
        return (r.text or "").strip()
    except GemmaError:
        raise
    except Exception as e:  # quota, réseau, modèle introuvable...
        raise GemmaError(f"Gemma ne répond pas : {e}") from e


def parse_json(raw: str):
    """Extrait un objet JSON d'une réponse (avec ou sans ```json)."""
    if not raw:
        return None
    txt = re.sub(r"```(?:json)?", "", raw).strip()
    start, end = txt.find("{"), txt.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(txt[start : end + 1])
    except json.JSONDecodeError:
        return None


def call_json(system: str, parts: list, temperature: float = 0.2):
    """Appelle Gemma et exige du JSON. Un seul nouvel essai si c'est invalide."""
    raw = call(system, parts, temperature)
    data = parse_json(raw)
    if data is None:
        raw = call(
            system + "\n\nIMPORTANT : réponds UNIQUEMENT avec un objet JSON valide, sans texte autour.",
            parts,
            0.0,
        )
        data = parse_json(raw)
    return data
