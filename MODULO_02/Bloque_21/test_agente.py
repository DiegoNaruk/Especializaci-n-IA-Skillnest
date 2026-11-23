import runpy
from pathlib import Path
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessageChunk


def test_agente_inicia_con_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-de-prueba")
    with patch("dotenv.load_dotenv"), patch(
        "langchain_google_genai.ChatGoogleGenerativeAI.stream",
        side_effect=[
            iter([AIMessageChunk(content="", tool_call_chunks=[
                {"name": "calcular", "args": '{"expresion":"12 * 5"}', "id": "1", "index": 0}
            ])]),
            iter([AIMessageChunk(content="respuesta simulada")]),
        ],
    ) as modelo:
        resultado = runpy.run_path(
            str(Path(__file__).parent / "agente.py"), run_name="__main__"
        )

    assert resultado["modelo"].google_api_key.get_secret_value() == "clave-de-prueba"
    assert modelo.call_count == 2
    assert resultado["resultado"]["intermediate_steps"][0][1] == "60"


def test_agente_falla_si_no_hay_clave(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("dotenv.load_dotenv"):
        with pytest.raises(ValueError, match="Falta configurar GEMINI_API_KEY"):
            runpy.run_path(str(Path(__file__).parent / "agente.py"))
