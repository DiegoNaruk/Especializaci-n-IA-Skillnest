from unittest.mock import Mock, patch

import pytest

from cliente import enviar_peticion
from cliente_api import armar_peticion


def test_envia_clave_en_cabecera_y_no_en_url():
    url, cuerpo = armar_peticion("pregunta", "instrucción")
    respuesta = Mock(status_code=200)
    respuesta.json.return_value = {"resultado": "ok"}

    with patch.dict("os.environ", {"GEMINI_API_KEY": "clave-de-prueba"}), \
         patch("cliente.requests.post", return_value=respuesta) as post:
        assert enviar_peticion(url, cuerpo) == {"resultado": "ok"}
    
    assert "clave-de-prueba" not in post.call_args.args[0]
    assert "key=" not in post.call_args.args[0]
    assert post.call_args.kwargs["headers"]["x-goog-api-key"] == "clave-de-prueba"


def test_clave_ausente_no_envia_peticion():
    with patch.dict("os.environ", {}, clear=True), \
         patch("cliente.requests.post") as post:
        with pytest.raises(ValueError, match="Falta configurar GEMINI_API_KEY"):
            enviar_peticion("https://example.com", {})

    post.assert_not_called()
