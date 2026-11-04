import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
import re
import json
from cprint import cprint


load_dotenv(
    dotenv_path=Path(__file__).resolve().parents[2] / "MODULO_01" / ".env"
)


def calcular_costo_peticion(
    datos: dict[str, Any], precio_entrada: float, precio_salida: float
) -> float | None:
    uso = datos.get("usageMetadata")
    if not uso:
        return None

    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)
    costo_entrada = tokens_entrada * precio_entrada
    costo_salida = tokens_salida * precio_salida
    costo_total = costo_entrada + costo_salida
    return costo_total


def armar_peticion(
    pregunta: str,
    system_instruction: str = "Eres un asistente útil.",
    response_schema: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    if not isinstance(pregunta, str):
        raise ValueError("La pregunta debe ser una cadena de texto.")
    modelo = "gemini-3.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    body = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [{"parts": [{"text": pregunta}]}],
    }
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body


def enviar_peticion(url: str, body: dict[str, Any]) -> dict[str, Any]:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("AI_API_KEY_GENAI")
        or os.getenv("AI_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "Falta configurar GEMINI_API_KEY en MODULO_01/.env."
        )

    try:
        respuesta = requests.post(
            url,
            headers={"x-goog-api-key": api_key},
            json=body,
            timeout=30,
        )
    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ) as error:
        raise TimeoutError(
            "No se pudo contactar al proveedor. Puede ser momentáneo."
        ) from error

    if respuesta.status_code in (401, 403):
        raise ValueError(
            "Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY."
        )
    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        retry_after = respuesta.headers.get("Retry-After")
        if retry_after:
            raise TimeoutError(
                "El proveedor no pudo procesar la petición. "
                f"Hay que esperar {retry_after} segundos y reintentar."
            )
        raise TimeoutError(
            "El proveedor no pudo procesar la petición. "
            "Hay que esperar y reintentar."
        )

    respuesta.raise_for_status()
    datos = respuesta.json()
    if not isinstance(datos, dict):
        raise RuntimeError("Gemini devolvió una respuesta con formato inesperado.")
    if "error" in datos:
        mensaje = datos["error"].get("message", "Error desconocido de Gemini.")
        raise RuntimeError(f"Error de Gemini: {mensaje}")
    return datos


def extraer_texto(datos: dict[str, Any]) -> str:
    uso = datos.get("usageMetadata")
    if uso:
        cprint.ok("Tokens prompt:", uso.get("promptTokenCount", 0))
        cprint.ok("Tokens candidates:", uso.get("candidatesTokenCount", 0))
        cprint.ok("Tokens total:", uso.get("totalTokenCount", 0))
    else:
        cprint.info("Gemini no devolvió los metadatos de uso de tokens.")

    return datos["candidates"][0]["content"]["parts"][0]["text"]

def parsear_respuesta_json(
    texto: str, claves_esperadas: list[str] | None = None
) -> dict[str, Any]:
    texto_limpio = texto.strip() # Eliminar espacios en blanco al inicio y al final del texto
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio) # Eliminar el bloque de apertura de código JSON
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio) # Eliminar el bloque de cierre de código JSON
    try:
        datos = json.loads(texto_limpio)# Intentar convertir el texto limpio a un objeto JSON
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")
    if claves_esperadas is None:
        claves_esperadas = ["rta", "fuente"]
    if not all(clave in datos for clave in claves_esperadas):
        raise ValueError("La respuesta no tiene la estructura esperada.")
    return datos


def obtener_dato_de_prueba(
    pregunta: str,
    system_instruction: str,
    response_schema: dict[str, Any] | None = None,
) -> str | dict[str, Any] | None:
    try:
        url, body = armar_peticion(pregunta, system_instruction, response_schema)
        datos = enviar_peticion(url, body)
        costo = calcular_costo_peticion(datos, 0.0000003, 0.0000025)
        if costo is None:
            cprint.info("No se pudo calcular el costo: faltan los metadatos de uso.")
        else:
            cprint.info(f"Costo estimado de la petición: {costo}")
        texto =  extraer_texto(datos)
        if response_schema is not None:
            claves = response_schema.get("required")
            if claves is None:
                claves = list(response_schema.get("properties", {}))
            return parsear_respuesta_json(texto, claves)
        return texto
    except (
        KeyError,
        ValueError,
        RuntimeError,
        TimeoutError,
        requests.exceptions.RequestException,
    ) as error:
        cprint.fatal(f"Error al obtener el dato de prueba: {error}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    print("Prueba_local")
