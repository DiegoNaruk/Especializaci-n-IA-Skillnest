import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

api_key = os.getenv("AI_API_KEY_GENAI") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "Falta configurar AI_API_KEY_GENAI o GEMINI_API_KEY en el archivo .env"
    )

modelo = "gemini-3.5-flash"


def armar_peticion(pregunta):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body


def enviar_peticion(url, body):
    respuesta = requests.post(
        url,
        headers={"x-goog-api-key": api_key},
        json=body,
        timeout=30,
    )
    respuesta.raise_for_status()
    return respuesta.json()


def extraer_texto(respuesta_json):
    return respuesta_json["candidates"][0]["content"]["parts"][0]["text"]


def obtener_texto_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)
