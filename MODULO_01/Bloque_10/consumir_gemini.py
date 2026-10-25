import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from cprint import cprint
import time 
import re
import json


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


def armar_peticion(pregunta: str, system_instruction: str = "Eres un asistente útil.", response_schema: dict | None = None) -> tuple[str, dict]:
    if (type(pregunta) != str):
        raise ValueError("La pregunta debe ser una cadena de texto.")
    modelo = "gemini-3.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )
    body = {
        "systemInstruction": {
        	"parts": [ { "text": system_instruction } ]
    	},
        "contents": [{"parts": [{"text": pregunta}]}]
    }
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
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

def parsear_respuesta_json(
    texto: str, claves_esperadas: list[str] | None = None
) -> dict:
    texto_limpio = texto.strip() # Eliminar espacios en blanco al inicio y al final del texto
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio) # Eliminar el bloque de apertura de código JSON
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio) # Eliminar el bloque de cierre de código JSON
    try:
        datos = json.loads(texto_limpio)# Intentar convertir el texto limpio a un objeto JSON
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")# Lanzar un error si el JSON no es válido
    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")
    if claves_esperadas is None:
        claves_esperadas = ["rta", "fuente"]
    if not all(clave in datos for clave in claves_esperadas):
        raise ValueError("La respuesta no tiene la estructura esperada.")# Lanzar un error si la estructura del JSON no es la esperada
    return datos # Devolver el objeto JSON parseado


def obtener_dato_de_prueba(pregunta: str, system_instruction: str ,response_schema: dict = None) -> str | None:
    try:
        url, body = armar_peticion(pregunta, system_instruction, response_schema)
        datos = enviar_peticion(url, body)
        costo = calcular_costo_peticion(datos, 0.0000003, 0.0000025)
        if costo is None:
            cprint.info("No se pudo calcular el costo: faltan los metadatos de uso.")
        else:
            cprint.info(f"Costo estimado de la petición: {costo}")
        texto =  extraer_texto(datos)
        if response_schema:
            datos = parsear_respuesta_json(texto)
            return datos # Devolver el objeto JSON parseado
        else:
            return texto
    except KeyError as e:
        cprint.fatal(f"Error al extraer el dato de prueba: {e}")
        return None
    except Exception as e:
        cprint.fatal(f"Error inesperado: {e}")
        return None

    return texto
def test_latencia(ciclos: int = 5):
    latencias = []
    for i in range(ciclos):
        url, body = armar_peticion("Cuanto es 2 + 2? Dame solo el resultado", "Responde con una sola palabra")
        inicio = time.time()
        datos = enviar_peticion(url, body)
        duracion = time.time() - inicio
        cprint.info(f"Duración de la petición {i + 1}: {duracion} segundos")
        latencias.append(duracion)
    latencia_promedio = sum(latencias) / len(latencias)
    cprint.info(f"Latencia promedio después de {ciclos} ciclos: {latencia_promedio} segundos")  



# Ejemplo de uso
if __name__ == "__main__":
    cprint.ok(obtener_dato_de_prueba(
        "¿Cuál es la capital de Francia?","da respuestas de una sola palabra", {}))
    cprint.ok(obtener_dato_de_prueba(
        "¿Cuál es la capital de Escocia?","dame una respuesta detallada en 20 palabras", {}))
    cprint.ok(obtener_dato_de_prueba(
        "¿Cuál es la capital legistlativa de Sudáfrica","Utiliza solo formato JSON, clave: rta:str y fuente:str", {}))
    cprint.ok(obtener_dato_de_prueba(
        "¿Cuál es la capital de Alemania?",
        "Responde en formato JSON",
        {
            "type": "OBJECT",
            "properties": {
                "rta": {"type": "STRING"},
                "fuente": {"type": "STRING"},
            },
            "required": ["fuente", "rta"],
        },
    ))
