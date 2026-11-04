import json
import time
from pathlib import Path
from MODULO_02.Bloque_10.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Responde únicamente con un JSON con las claves 'sentimiento' "
            "('positivo', 'negativo' o 'neutro') y 'confianza' (0 a 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está perfecto.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": { "type": "STRING" },
                "confianza": { "type": "NUMBER" }
            },
            "required": ["sentimiento", "confianza"]
        },
    },
    {
        "nombre": "extraer_entidades",
        "system_instruction": (
            "Extrae las entidades principales del texto proporcionado. "
            "Devuelve un JSON con las claves 'persona', 'lugar' y 'fecha'."
        ),
        "ejemplo_usuario": "María viajó a Madrid el pasado 12 de mayo para una conferencia.",
        "claves_esperadas": ["persona", "lugar", "fecha"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "persona": { "type": "STRING" },
                "lugar": { "type": "STRING" },
                "fecha": { "type": "STRING" }
            },
            "required": ["persona", "lugar", "fecha"]
        },
    },
    {
        "nombre": "clasificar_ticket_soporte",
        "system_instruction": (
            "Clasifica el ticket de soporte del cliente en una categoría "
            "('facturacion', 'tecnico', 'general') y asigna una prioridad ('baja', 'media', 'alta'). "
            "Responde únicamente con un JSON."
        ),
        "ejemplo_usuario": "No puedo iniciar sesión en mi cuenta y me urge ver mi factura.",
        "claves_esperadas": ["categoria", "prioridad"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "categoria": { "type": "STRING" },
                "prioridad": { "type": "STRING" }
            },
            "required": ["categoria", "prioridad"]
        },
    },
    {
        "nombre": "resumen_puntos_clave",
        "system_instruction": (
            "Analiza el texto y genera un resumen corto de los puntos clave. "
            "Devuelve un JSON con un array de strings llamado 'puntos_clave'."
        ),
        "ejemplo_usuario": "El lanzamiento del nuevo software superó las expectativas con más de 10,000 descargas el primer día. Los usuarios reportaron problemas menores de interfaz que ya están siendo solucionados.",
        "claves_esperadas": ["puntos_clave"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "puntos_clave": {
                    "type": "ARRAY",
                    "items": { "type": "STRING" }
                }
            },
            "required": ["puntos_clave"]
        },
    }
]


registro = {}  
 
for prompt in BANCO_DE_PROMPTS:
    exitos = 0
    intentos = 3    
    for intento in range(intentos):
        url, body = armar_peticion(
            prompt["ejemplo_usuario"],
            prompt["system_instruction"],
            prompt.get("response_schema"),
        )
        respuesta = enviar_peticion(url, body)
        texto = extraer_texto(respuesta)
        try:
            datos = parsear_respuesta_json(texto, prompt["claves_esperadas"])
            if all(clave in datos for clave in prompt["claves_esperadas"]):
                exitos += 1
        except ValueError as error:
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(1)
    print(f"{prompt['nombre']}: {exitos}/{intentos} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos}
 
carpeta_prompts = Path(__file__).resolve().parent / "prompts"
carpeta_prompts.mkdir(exist_ok=True)
with open(carpeta_prompts / "registro_resultados.json", "w", encoding="utf-8") as archivo:
    json.dump(registro, archivo, indent=2, ensure_ascii=False)
