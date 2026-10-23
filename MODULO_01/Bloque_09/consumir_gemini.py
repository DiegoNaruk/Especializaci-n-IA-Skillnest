import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from cprint import cprint
import time 

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def calcular_costo_peticion(
    datos: dict, precio_entrada: float, precio_salida: float
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


def armar_peticion(pregunta: str) -> tuple[str, dict]:
    if (type(pregunta) != str):
        raise ValueError("La pregunta debe ser una cadena de texto.")
    modelo = "gemini-3.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body

def enviar_peticion(url: str, body: dict) -> dict:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("AI_API_KEY_GENAI")
        or os.getenv("AI_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "Falta configurar GEMINI_API_KEY en MODULO_01/.env."
        )

    inicio = time.time()
    respuesta = requests.post(
        url,
        headers={"x-goog-api-key": api_key},
        json=body,
        timeout=30,
    )
    duracion = time.time() - inicio
    cprint.info(f"Duración de la petición: {duracion} segundos")
    datos = respuesta.json()
    if "error" in datos:
        mensaje = datos["error"].get("message", "Error desconocido de Gemini.")
        raise RuntimeError(f"Error de Gemini: {mensaje}")
    respuesta.raise_for_status()
    return datos



def extraer_texto(datos: dict) -> str:
    uso = datos.get("usageMetadata")
    if uso:
        cprint.ok("Tokens prompt:", uso.get("promptTokenCount", 0))
        cprint.ok("Tokens candidates:", uso.get("candidatesTokenCount", 0))
        cprint.ok("Tokens total:", uso.get("totalTokenCount", 0))
    else:
        cprint.info("Gemini no devolvió los metadatos de uso de tokens.")

    return datos["candidates"][0]["content"]["parts"][0]["text"]


def obtener_dato_de_prueba(pregunta: str) -> str | None:
    try:
        url, body = armar_peticion(pregunta)
        datos = enviar_peticion(url, body)
        costo = calcular_costo_peticion(datos, 0.0000003, 0.0000025)
        if costo is None:
            cprint.info("No se pudo calcular el costo: faltan los metadatos de uso.")
        else:
            cprint.info(f"Costo estimado de la petición: {costo}")
        return extraer_texto(datos)
    except KeyError as e:
        cprint.fatal(f"Error al extraer el dato de prueba: {e}")
        return None
    except Exception as e:
        cprint.fatal(f"Error inesperado: {e}")
        return None

    
def test_latencia(ciclos: int = 5):
    latencias = []
    for i in range(ciclos):
        url, body = armar_peticion("Cuanto es 2 + 2? Dame solo el resultado")
        inicio = time.time()
        datos = enviar_peticion(url, body)
        duracion = time.time() - inicio
        cprint.info(f"Duración de la petición {i + 1}: {duracion} segundos")
        latencias.append(duracion)
    latencia_promedio = sum(latencias) / len(latencias)
    cprint.info(f"Latencia promedio después de {ciclos} ciclos: {latencia_promedio} segundos")  



# Ejemplo de uso
if __name__ == "__main__":
    cprint.ok(obtener_dato_de_prueba("¿Cuál es la capital de Escocia? Describe la ciudad"))