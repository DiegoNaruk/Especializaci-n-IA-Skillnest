from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Datos de referencia para el dominio de fletes
TARIFAS_VEHICULO = {
    "camioneta": {"base": 12000, "por_km": 650, "max_kg": 800},
    "furgon": {"base": 18000, "por_km": 850, "max_kg": 1500},
    "camion_3_4": {"base": 35000, "por_km": 1300, "max_kg": 5000},
}

DISPONIBILIDAD_ZONAS = {
    "talagante": ["camioneta", "furgon", "camion_3_4"],
    "san bernardo": ["camioneta", "camion_3_4"],
    "isla de maipo": ["camioneta", "furgon"],
}


@tool
def cotizar_flete(tipo_vehiculo: str, distancia_km: float, peso_kg: float) -> str:
    """Calcula una tarifa estimada de flete según tipo de vehículo, distancia en km y peso en kg.
    Usar cuando el usuario pregunte cuánto cuesta un flete, traslado o mudanza con distancia o carga."""
    try:
        clave = tipo_vehiculo.strip().lower().replace(" ", "_")
        if distancia_km <= 0 or peso_kg <= 0:
            return "Error de validación: la distancia y el peso deben ser mayores a cero."

        tarifa = TARIFAS_VEHICULO[clave]
        if peso_kg > tarifa["max_kg"]:
            return (
                f"El vehículo '{tipo_vehiculo}' soporta hasta {tarifa['max_kg']} kg "
                f"y la carga ingresada es de {peso_kg} kg. Sugiere un vehículo de mayor capacidad."
            )

        total = tarifa["base"] + (distancia_km * tarifa["por_km"])
        return (
            f"Cotización estimada para {tipo_vehiculo} ({distancia_km:.1f} km, {peso_kg:.0f} kg): "
            f"${total:,.0f} CLP."
        )
    except KeyError:
        opciones = ", ".join(TARIFAS_VEHICULO.keys())
        return f"No existe tarifa para el vehículo '{tipo_vehiculo}'. Vehículos válidos: {opciones}."
    except Exception as exc:
        return f"No se pudo calcular la cotización por un error interno: {exc}"


@tool
def consultar_disponibilidad_zona(comuna: str) -> str:
    """Consulta qué tipos de vehículos de flete tienen disponibilidad operativa en una comuna.
    Usar cuando el usuario pregunte si hay disponibilidad de vehículos o camiones en una zona o comuna."""
    try:
        clave_comuna = comuna.strip().lower()
        if not clave_comuna:
            return "Debes indicar una comuna válida para consultar disponibilidad."

        vehiculos = DISPONIBILIDAD_ZONAS[clave_comuna]
        return f"En {comuna.title()} hay disponibilidad actual de: {', '.join(vehiculos)}."
    except KeyError:
        return f"No se encontró cobertura registrada para la comuna '{comuna}'."
    except Exception as exc:
        return f"Error al consultar disponibilidad en '{comuna}': {exc}"


# Modelo Gemini + herramientas
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)
herramientas = [cotizar_flete, consultar_disponibilidad_zona]

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente operativo de fletes y mudanzas. Responde en español de forma clara y concisa. "
        "Usa las herramientas disponibles solo cuando la consulta requiera cotizar un traslado o revisar disponibilidad por comuna. "
        "Si es una pregunta general (horarios, políticas, cómo contactar), responde directamente sin usar herramientas."
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agente = create_tool_calling_agent(llm=llm, tools=herramientas, prompt=prompt)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    return_intermediate_steps=True,
    verbose=True,
)

# Validación con intermediate_steps

# Prueba 1: Debe disparar 'cotizar_flete'
res_cotizacion = ejecutor_agente.invoke({
    "entrada": "¿Cuánto sale un flete en camión 3/4 por 25 km llevando 1800 kg?"
})
assert res_cotizacion["intermediate_steps"][0][0].tool == "cotizar_flete"
print("Respuesta 1:", res_cotizacion["output"])

# Prueba 2: Debe disparar 'consultar_disponibilidad_zona'
res_disponibilidad = ejecutor_agente.invoke({
    "entrada": "¿Qué vehículos tienen disponibles hoy en Talagante?"
})
assert res_disponibilidad["intermediate_steps"][0][0].tool == "consultar_disponibilidad_zona"
print("Respuesta 2:", res_disponibilidad["output"])

# Prueba 3: Pregunta general -> no debería usar herramientas
res_general = ejecutor_agente.invoke({
    "entrada": "¿Cuál es el horario de atención al cliente?"
})
assert res_general["intermediate_steps"] == []
print("Respuesta 3:", res_general["output"])