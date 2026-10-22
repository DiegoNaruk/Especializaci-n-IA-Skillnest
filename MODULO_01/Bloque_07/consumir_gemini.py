import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def armar_peticion(pregunta):
    if not isinstance(pregunta, str):
        raise ValueError("La pregunta debe ser una cadena de texto.")
    modelo = os.getenv("AI_MODEL", "gemini-3.5-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body


def enviar_peticion(url, body):
    api_key = os.getenv("AI_API_KEY_GENAI") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta configurar AI_API_KEY_GENAI o GEMINI_API_KEY en el archivo .env"
        )

    try:
        respuesta = requests.post(
            url,
            headers={"x-goog-api-key": api_key},
            json=body,
            timeout=30,
        )
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo conectar con el servicio. Intenta de nuevo en unos segundos."
        ) from error

    respuesta.raise_for_status()

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del servicio no llegó en el formato esperado."
        ) from error

def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as error:
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        ) from error


def obtener_dato_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)
