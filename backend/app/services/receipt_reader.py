import base64
import json
import math
import re
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

import httpx
from pydantic import ValidationError

from app.core.config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
)
from app.schemas.recibo import LecturaResponse

TIMEOUT_IA_SEGUNDOS: float = 30.0
INTENTOS_LECTURA = 2
PROMPT_LECTURA = (
    "Extrae los datos principales de este recibo colombiano. Responde únicamente "
    'un JSON con las claves "comercio", "fecha" (AAAA-MM-DD) y "monto" (número '
    "en pesos, sin separadores). Para retiros en cajero, usa la entidad o el "
    "cajero como comercio y el valor del retiro como monto; no confundas ese "
    "valor con el saldo disponible ni con el costo de operación. Usa null para "
    "lo que no puedas distinguir. No devuelvas números de tarjeta, cuenta, "
    "nombres de clientes, direcciones ni otros datos."
)


class ReceiptReaderTimeoutError(Exception):
    """El proveedor de lectura excedió el tiempo máximo de respuesta."""


class ReceiptReaderUnavailableError(Exception):
    """El proveedor de lectura no pudo procesar la solicitud."""

    def __init__(
        self,
        message: str = "El proveedor de IA no está disponible",
        *,
        provider_status_code: int | None = None,
        provider_message: str | None = None,
    ):
        super().__init__(message)
        self.provider_status_code = provider_status_code
        self.provider_message = provider_message


def normalizar_monto_colombiano(valor_str: str) -> float | None:
    """Convierte una cadena de monto colombiano a número."""
    if not valor_str:
        return None
    limpio = valor_str.replace("$", "").replace("COP", "").replace(" ", "").strip()
    if "." in limpio and "," not in limpio:
        limpio = limpio.replace(".", "")
    elif "," in limpio:
        limpio = limpio.replace(".", "").replace(",", ".")
    try:
        valor = float(limpio)
    except ValueError:
        return None
    return valor if math.isfinite(valor) and valor > 0 else None


def _parsear_lectura(texto: str) -> LecturaResponse:
    texto = texto.strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.IGNORECASE)
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        inicio = texto.find("{")
        if inicio < 0:
            raise
        datos, _ = json.JSONDecoder().raw_decode(texto[inicio:])

    if not isinstance(datos, dict):
        raise ValueError("La respuesta de IA debe ser un objeto JSON")

    comercio = datos.get("comercio")
    fecha = datos.get("fecha")
    monto = datos.get("monto")
    if not isinstance(comercio, str) or not comercio.strip():
        comercio = None
    else:
        comercio = comercio.strip()
    if not isinstance(fecha, str):
        fecha = None
    if isinstance(monto, str):
        monto = normalizar_monto_colombiano(monto)
    elif isinstance(monto, (int, float)) and not isinstance(monto, bool):
        monto = float(monto)
        if not math.isfinite(monto) or monto <= 0:
            monto = None
    else:
        monto = None

    return LecturaResponse(
        comercio=comercio,
        fecha=fecha,
        monto=monto,
        mensaje="No se pudo leer el monto" if monto is None else None,
    )


async def _leer_con_reintento(
    obtener_texto: Callable[[], Awaitable[str]],
) -> LecturaResponse:
    for intento in range(INTENTOS_LECTURA):
        try:
            return _parsear_lectura(await obtener_texto())
        except (json.JSONDecodeError, ValidationError, ValueError):
            if intento == INTENTOS_LECTURA - 1:
                return LecturaResponse(mensaje="No se pudo leer el monto")
    raise RuntimeError("La lectura terminó sin resultado")


class BaseReceiptReader(ABC):
    @abstractmethod
    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        """Lee los datos permitidos de una imagen de recibo."""


class MockReceiptReader(BaseReceiptReader):
    """Lector simulado para desarrollo sin llamadas a proveedores externos."""

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        return LecturaResponse(
            comercio="Supermercado Central",
            fecha="2026-10-15",
            monto=85000.0,
        )


class GeminiReceiptReader(BaseReceiptReader):
    """Lector de recibos mediante Gemini Vision."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-3.5-flash-lite:generateContent"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": PROMPT_LECTURA},
                        {
                            "inline_data": {
                                "mime_type": content_type,
                                "data": base64.b64encode(contenido_imagen).decode(
                                    "utf-8"
                                ),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async def obtener_texto() -> str:
            async with httpx.AsyncClient(
                timeout=TIMEOUT_IA_SEGUNDOS / INTENTOS_LECTURA
            ) as client:
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
            if response.status_code != 200:
                    try:
                        response_data = response.json()
                    except ValueError:
                        response_data = {}
                    error_data = (
                        response_data.get("error", {})
                        if isinstance(response_data, dict)
                        else {}
                    )
                    mensaje = (
                        error_data.get("message")
                        if isinstance(error_data, dict)
                        else None
                    )
                    if isinstance(mensaje, str):
                        mensaje = mensaje.replace(self.api_key, "[clave oculta]")[:300]
                    else:
                        mensaje = None
                    raise ReceiptReaderUnavailableError(
                        "Gemini rechazó la solicitud",
                        provider_status_code=response.status_code,
                        provider_message=mensaje,
                    )
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        try:
            return await _leer_con_reintento(obtener_texto)
        except httpx.TimeoutException as error:
            raise ReceiptReaderTimeoutError from error
        except httpx.RequestError as error:
            raise ReceiptReaderUnavailableError from error
        except (KeyError, TypeError) as error:
            raise ReceiptReaderUnavailableError from error


class OpenAIReceiptReader(BaseReceiptReader):
    """Lector de recibos mediante la API de visión de OpenAI."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        url = "https://api.openai.com/v1/chat/completions"
        imagen = base64.b64encode(contenido_imagen).decode("utf-8")
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_LECTURA},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{imagen}"
                            },
                        },
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
        }

        async def obtener_texto() -> str:
            async with httpx.AsyncClient(
                timeout=TIMEOUT_IA_SEGUNDOS / INTENTOS_LECTURA
            ) as client:
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=payload,
                )
            if response.status_code != 200:
                    raise ReceiptReaderUnavailableError(
                        "OpenAI rechazó la solicitud",
                        provider_status_code=response.status_code,
                    )
            return response.json()["choices"][0]["message"]["content"]

        try:
            return await _leer_con_reintento(obtener_texto)
        except httpx.TimeoutException as error:
            raise ReceiptReaderTimeoutError from error
        except httpx.RequestError as error:
            raise ReceiptReaderUnavailableError from error
        except (KeyError, TypeError) as error:
            raise ReceiptReaderUnavailableError from error


def obtener_receipt_reader() -> BaseReceiptReader:
    if AI_PROVIDER == "mock":
        return MockReceiptReader()
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return GeminiReceiptReader(GEMINI_API_KEY)
    if AI_PROVIDER == "openai" and OPENAI_API_KEY:
        return OpenAIReceiptReader(OPENAI_API_KEY)
    raise RuntimeError(
        f"El proveedor de IA '{AI_PROVIDER}' no está configurado correctamente."
    )
