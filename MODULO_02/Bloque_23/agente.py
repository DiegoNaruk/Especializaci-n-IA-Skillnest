from datetime import datetime, timezone
import json

from cprint import cprint
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", timeout=10)

historiales = {}

TARIFAS_FLETE = {
    "camioneta": {"base": 12000, "por_km": 650, "max_kg": 800},
    "furgon": {"base": 18000, "por_km": 850, "max_kg": 1500},
    "camion_3_4": {"base": 35000, "por_km": 1300, "max_kg": 7000},
}

DISPONIBILIDAD_COMUNAS = {
    "talagante": ["camioneta", "furgon", "camion_3_4"],
    "san bernardo": ["camioneta", "camion_3_4"],
    "isla de maipo": ["camioneta", "furgon"],
}


def normalizar_respuesta(resultado):
    contenido = resultado["output"]

    if isinstance(contenido, list):
        contenido = "".join(
            bloque["text"]
            for bloque in contenido
            if isinstance(bloque, dict) and bloque.get("type") == "text"
        )

    return {**resultado, "output": AIMessage(content=contenido)}


def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
) -> None:
    """Guarda una interacción del agente como una
    línea JSON en trazas_agente.jsonl: qué se
    preguntó, qué herramientas se usaron y con qué
    argumentos, y la respuesta final. Si "resultado"
    no trae "intermediate_steps" (por ejemplo, con
    return_intermediate_steps=False), acciones queda
    como una lista vacía en vez de fallar."""

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado["output"].content,
    }

    with open("trazas_agente.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


class ConsultaCotizacionFlete(BaseModel):
    tipo_vehiculo: str = Field(
        description=(
            "Tipo de vehículo para el flete. Categorías válidas: "
            "'camioneta', 'furgon' o 'camion_3_4' (hasta 7 toneladas)."
        )
    )
    distancia_km: float = Field(
        description="Distancia estimada del traslado en kilómetros (debe ser mayor a 0)."
    )
    peso_kg: float = Field(
        description="Peso total estimado de la carga en kilogramos (debe ser mayor a 0)."
    )


class ConsultaDisponibilidadFlete(BaseModel):
    comuna: str = Field(
        description=(
            "Comuna o zona de retiro/origen del flete, por ejemplo: "
            "'Talagante', 'San Bernardo' o 'Isla de Maipo'."
        )
    )


@tool("cotizar_flete", args_schema=ConsultaCotizacionFlete)
def cotizar_flete(tipo_vehiculo: str, distancia_km: float, peso_kg: float) -> str:
    """Calcula el costo estimado de un flete o mudanza según tipo de vehículo, distancia y peso.
    Usar cuando el usuario pida cotizar o saber cuánto cuesta un traslado con distancia o carga."""
    try:
        clave = tipo_vehiculo.strip().lower().replace(" ", "_")
        if distancia_km <= 0 or peso_kg <= 0:
            return "Error de validación: la distancia y el peso deben ser mayores a 0."

        tarifa = TARIFAS_FLETE[clave]
        if peso_kg > tarifa["max_kg"]:
            return (
                f"El vehículo '{tipo_vehiculo}' admite hasta {tarifa['max_kg']} kg "
                f"y se solicitaron {peso_kg} kg. Recomienda un vehículo de mayor capacidad."
            )

        total = tarifa["base"] + (distancia_km * tarifa["por_km"])
        return (
            f"Estimación para {tipo_vehiculo}: ${total:,.0f} CLP "
            f"({distancia_km:.1f} km, {peso_kg:.0f} kg)."
        )
    except KeyError:
        opciones = ", ".join(TARIFAS_FLETE.keys())
        return f"Vehículo '{tipo_vehiculo}' no reconocido. Opciones válidas: {opciones}."
    except Exception as exc:
        return f"No se pudo calcular la cotización por un error interno: {exc}"


@tool("consultar_disponibilidad_flete", args_schema=ConsultaDisponibilidadFlete)
def consultar_disponibilidad_flete(comuna: str) -> str:
    """Consulta qué vehículos de flete están disponibles en una comuna determinada.
    Usar cuando el usuario pregunte si hay disponibilidad de fletes o vehículos en una zona/comuna."""
    try:
        clave_comuna = comuna.strip().lower()
        if not clave_comuna:
            return "Debes indicar una comuna válida para consultar disponibilidad."

        vehiculos = DISPONIBILIDAD_COMUNAS[clave_comuna]
        return f"Disponibilidad en {comuna.title()}: {', '.join(vehiculos)}."
    except KeyError:
        return f"Sin cobertura registrada para la comuna '{comuna}'."
    except Exception as exc:
        return f"Error al consultar disponibilidad en '{comuna}': {exc}"


if __name__ == "__main__":
    herramientas = [cotizar_flete, consultar_disponibilidad_flete]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres el asistente de una app de fletes y mudanzas ('Uber de fletes'). "
            "Responde en español de forma clara, práctica y concisa. "
            "Usa las herramientas solo cuando necesites cotizar un flete o revisar disponibilidad por comuna. "
            "Si el usuario hace preguntas generales (cómo funciona la app, medios de pago, soporte), "
            "responde directamente sin llamar herramientas.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

    ejecutor_agente = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )

    agente_normalizado = ejecutor_agente | RunnableLambda(normalizar_respuesta)

    agente_con_memoria = RunnableWithMessageHistory(
        agente_normalizado,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )

    config = {"configurable": {"session_id": "cliente_flete_123"}}

    entrada_1 = "¿Qué vehículos de flete tienen disponibles hoy en Talagante?"
    resultado_1 = agente_con_memoria.invoke({"entrada": entrada_1}, config)
    assert resultado_1["intermediate_steps"][0][0].tool == "consultar_disponibilidad_flete"
    cprint.err(resultado_1["output"])
    registrar_traza(
        session_id=config["configurable"]["session_id"],
        entrada=entrada_1,
        resultado=resultado_1,
    )

    entrada_2 = "¿Cuánto sale un camión 3/4 por 20 km con 2500 kg?"
    resultado_2 = agente_con_memoria.invoke({"entrada": entrada_2}, config)
    assert resultado_2["intermediate_steps"][0][0].tool == "cotizar_flete"
    cprint.err(resultado_2["output"])
    registrar_traza(
        session_id=config["configurable"]["session_id"],
        entrada=entrada_2,
        resultado=resultado_2,
    )