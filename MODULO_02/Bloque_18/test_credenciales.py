import runpy
from pathlib import Path
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage


@pytest.mark.parametrize("script", ["cadena_triple.py", "langchain_test.py"])
def test_usa_gemini_api_key(monkeypatch, script):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("GOOGLE_API_KEY", "otra-clave")
    with patch("dotenv.load_dotenv"), patch(
        "langchain_google_genai.ChatGoogleGenerativeAI.invoke",
        return_value=AIMessage(content="respuesta simulada"),
    ):
        resultado = runpy.run_path(str(Path(__file__).parent / script))

    assert resultado["modelo"].google_api_key.get_secret_value() == "clave-de-prueba"


@pytest.mark.parametrize("script", ["cadena_triple.py", "langchain_test.py"])
def test_falla_si_no_hay_gemini_api_key(monkeypatch, script):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("dotenv.load_dotenv"):
        with pytest.raises(ValueError, match="Falta configurar GEMINI_API_KEY"):
            runpy.run_path(str(Path(__file__).parent / script))
