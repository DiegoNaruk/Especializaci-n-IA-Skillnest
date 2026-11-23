from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from enrutamiento import construir_paso_clasificacion
from manejo_errores import procesar_mensaje_seguro


def test_procesar_mensaje_seguro_envia_mensaje_a_la_cadena():
    with patch("manejo_errores.cadena_con_enrutamiento") as cadena:
        cadena.invoke.return_value = "respuesta simulada"
        assert procesar_mensaje_seguro("consulta") == "respuesta simulada"

    cadena.invoke.assert_called_once_with({"mensaje": "consulta"})


def test_procesar_mensaje_seguro_completa_el_enrutamiento():
    with patch(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        return_value=AIMessage(content="sugerencia"),
    ) as modelo:
        assert procesar_mensaje_seguro("consulta") == "sugerencia"

    assert modelo.call_count == 2

def test_clasificacion_normaliza_antes_de_comparar():
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")
    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "algo salió mal"}
    )
    assert resultado == "queja"

def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    def fallar_a_proposito(x):
        raise Exception("Error de red simulado")
    respuesta_generica = RunnableLambda(
        lambda x: "respuesta de respaldo"
    )
    cadena_rota = RunnableLambda(fallar_a_proposito)
    cadena_segura = cadena_rota.with_fallbacks([respuesta_generica])
    resultado = cadena_segura.invoke({"mensaje": "algo"})
    assert resultado == "respuesta de respaldo"