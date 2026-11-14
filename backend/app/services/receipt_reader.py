import base64
import json
from abc import ABC, abstractmethod

import httpx
from app.core.config import AI_PROVIDER, GEMINI_API_KEY
from app.schemas.recibo import LecturaResponse

# Timeout estándar recomendado para llamadas a servicios externos de IA
TIMEOUT_IA_SEGUNDOS: float = 4.0


def normalizar_monto_colombiano(valor_str: str) -> float | None:
    """HU-01: Normaliza texto de monto colombiano a número
    (ej: '$85.000' -> 85000.0).
    """
    if not valor_str:
        return None
    # Eliminar símbolos de moneda y espacios
    limpio = valor_str.replace("$", "").replace("COP", "").replace(" ", "").strip()
    # En Colombia el punto separa miles: 85.000 -> 85000
    if "." in limpio and "," not in limpio:
        limpio = limpio.replace(".", "")
    elif "," in limpio:
        # Si trae coma decimal: 85.000,50
        limpio = limpio.replace(".", "").replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None


class BaseReceiptReader(ABC):
    @abstractmethod
    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        pass


class MockReceiptReader(BaseReceiptReader):
    """Lector simulado para desarrollo y pruebas rápidas sin gastar cuota de API."""

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        # Devuelve datos realistas simulados según el escenario de la HU-01
        return LecturaResponse(
            comercio="Supermercado Central",
            fecha="2026-10-15",
            monto=85000.0,
            mensaje=None,
        )


class GeminiReceiptReader(BaseReceiptReader):
    """Lector real usando Google Gemini Vision API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-1.5-flash:generateContent"
        )
        encoded_image = base64.b64encode(contenido_imagen).decode("utf-8")

        prompt = (
            "Eres un extractor de datos de recibos de compra colombianos. "
            "Devuelve UNICAMENTE un JSON valido con las claves: "
            '"comercio": string o null, "fecha": "AAAA-MM-DD" o null, '
            '"monto": numero o null (el total en pesos, sin puntos ni simbolos). '
            "NO incluyas nombre del cliente, tarjeta, direccion "
            "ni ningun otro dato sensible."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": content_type,
                                "data": encoded_image,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        # Manejo explícito de timeouts y fallos de conexión HTTP
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_IA_SEGUNDOS) as client:
                headers = {"x-goog-api-key": self.api_key}
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return LecturaResponse(
                        mensaje="Error al comunicarse con el servicio de IA"
                    )

                data = resp.json()
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(candidate_text)
                return LecturaResponse(
                    comercio=parsed.get("comercio"),
                    fecha=parsed.get("fecha"),
                    monto=(
                        float(parsed["monto"])
                        if parsed.get("monto") is not None
                        else None
                    ),
                    mensaje=(
                        "No se pudo leer el monto"
                        if parsed.get("monto") is None
                        else None
                    ),
                )
        except httpx.TimeoutException:
            return LecturaResponse(
                mensaje="El servicio de IA no responde o tardo demasiado"
            )
        except (httpx.RequestError, json.JSONDecodeError, KeyError, ValueError):
            return LecturaResponse(
                mensaje="No se pudo procesar la respuesta de la IA"
            )


def obtener_receipt_reader() -> BaseReceiptReader:
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return GeminiReceiptReader(GEMINI_API_KEY)
    return MockReceiptReader()
