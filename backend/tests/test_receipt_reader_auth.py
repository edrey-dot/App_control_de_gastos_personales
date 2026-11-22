import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.receipt_reader import (
    GeminiReceiptReader,
    OpenAIReceiptReader,
    ReceiptReaderTimeoutError,
    ReceiptReaderUnavailableError,
)

client = TestClient(app)


def test_gemini_api_key_se_envia_en_header_y_no_en_url(monkeypatch):
    api_key_prueba = "clave-de-prueba-no-real"

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"comercio":"Tienda","fecha":null,'
                                        '"monto":1200}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            assert "?" not in url
            assert url.endswith("/models/gemini-3.5-flash-lite:generateContent")
            assert api_key_prueba not in url
            assert headers["x-goog-api-key"] == api_key_prueba
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.receipt_reader.httpx.AsyncClient", FakeAsyncClient
    )
    lector = GeminiReceiptReader(api_key_prueba)

    respuesta = asyncio.run(lector.leer_recibo(b"imagen", "image/jpeg"))

    assert respuesta.comercio == "Tienda"
    assert respuesta.monto == 1200.0
    assert respuesta.mensaje is None


@pytest.mark.parametrize(
    ("fallo", "error_esperado"),
    [
        (httpx.TimeoutException("timeout"), ReceiptReaderTimeoutError),
        (httpx.ConnectError("network unavailable"), ReceiptReaderUnavailableError),
    ],
)
def test_gemini_maneja_timeout_y_fallo_de_conexion(
    monkeypatch, fallo, error_esperado
):
    class FailingAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            raise fallo

    monkeypatch.setattr(
        "app.services.receipt_reader.httpx.AsyncClient", FailingAsyncClient
    )
    lector = GeminiReceiptReader("clave-de-prueba-no-real")

    with pytest.raises(error_esperado):
        asyncio.run(lector.leer_recibo(b"imagen", "image/jpeg"))


def test_gemini_conserva_detalle_http_del_proveedor_sin_exponer_clave(monkeypatch):
    api_key_prueba = "clave-de-prueba-no-real"

    class FakeResponse:
        status_code = 400

        def json(self):
            return {
                "error": {
                    "message": f"API key no válida: {api_key_prueba}",
                }
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.receipt_reader.httpx.AsyncClient", FakeAsyncClient
    )
    lector = GeminiReceiptReader(api_key_prueba)

    with pytest.raises(ReceiptReaderUnavailableError) as error:
        asyncio.run(lector.leer_recibo(b"imagen", "image/jpeg"))

    assert error.value.provider_status_code == 400
    assert error.value.provider_message == "API key no válida: [clave oculta]"
    assert api_key_prueba not in error.value.provider_message


def test_gemini_reintenta_json_invalido_y_descarta_campos_sensibles(monkeypatch):
    class FakeResponse:
        status_code = 200

        def __init__(self, texto):
            self.texto = texto

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": self.texto}]}}
                ]
            }

    class FakeAsyncClient:
        llamadas = 0

        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            type(self).llamadas += 1
            if type(self).llamadas == 1:
                return FakeResponse("respuesta no estructurada")
            return FakeResponse(
                '{"comercio":"Tienda","fecha":"2026-10-15",'
                '"monto":"$85.000","tarjeta":"4821"}'
            )

    monkeypatch.setattr(
        "app.services.receipt_reader.httpx.AsyncClient", FakeAsyncClient
    )
    lector = GeminiReceiptReader("clave-de-prueba-no-real")

    respuesta = asyncio.run(lector.leer_recibo(b"imagen", "image/jpeg"))

    assert FakeAsyncClient.llamadas == 2
    assert respuesta.comercio == "Tienda"
    assert respuesta.fecha == "2026-10-15"
    assert respuesta.monto == 85000
    assert not hasattr(respuesta, "tarjeta")


def test_openai_envia_imagen_y_parsea_respuesta(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"comercio":"Tienda","fecha":"2026-10-15",'
                                '"monto":1200}'
                            )
                        }
                    }
                ]
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            assert url.endswith("/v1/chat/completions")
            assert headers["Authorization"] == "Bearer clave-de-prueba-no-real"
            assert json["messages"][0]["content"][1]["image_url"]["url"].startswith(
                "data:image/jpeg;base64,"
            )
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.receipt_reader.httpx.AsyncClient", FakeAsyncClient
    )
    lector = OpenAIReceiptReader("clave-de-prueba-no-real")

    respuesta = asyncio.run(lector.leer_recibo(b"imagen", "image/jpeg"))

    assert respuesta.comercio == "Tienda"
    assert respuesta.monto == 1200


@pytest.mark.parametrize(
    ("error_lector", "estado_esperado"),
    [
        (ReceiptReaderTimeoutError(), 504),
        (
            ReceiptReaderUnavailableError(
                provider_status_code=400,
                provider_message="La clave no es válida",
            ),
            502,
        ),
    ],
)
def test_endpoint_recibo_traduce_fallos_del_proveedor(
    monkeypatch, error_lector, estado_esperado
):
    correo = f"lector-{estado_esperado}@correo.com"
    client.post(
        "/usuarios",
        json={"correo": correo, "contrasena": "clave-segura-123"},
    )
    token = client.post(
        "/sesiones",
        json={"correo": correo, "contrasena": "clave-segura-123"},
    ).json()["access_token"]

    class LectorFallido:
        async def leer_recibo(self, contenido_imagen, content_type):
            raise error_lector

    monkeypatch.setattr(
        "app.api.recibos.obtener_receipt_reader", lambda: LectorFallido()
    )
    response = client.post(
        "/recibos/lecturas",
        headers={"Authorization": f"Bearer {token}"},
        files={"foto": ("recibo.jpg", b"imagen", "image/jpeg")},
    )

    assert response.status_code == estado_esperado
    if (
        isinstance(error_lector, ReceiptReaderUnavailableError)
        and error_lector.provider_status_code is not None
    ):
        assert "HTTP" in response.json()["detail"]
        assert error_lector.provider_message in response.json()["detail"]
