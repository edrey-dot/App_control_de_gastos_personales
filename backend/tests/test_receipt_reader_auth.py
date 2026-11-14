import asyncio

from app.services.receipt_reader import GeminiReceiptReader


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
