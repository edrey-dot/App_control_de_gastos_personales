import base64
import json
from abc import ABC, abstractmethod

import httpx
from app.core.config import AI_PROVIDER, GEMINI_API_KEY
from app.schemas.recibo import LecturaResponse

# Timeout estándar recomendado para llamadas a servicios externos de IA
TIMEOUT_IA_SEGUNDOS: float = 4.0


def normalizar_monto_colombiano(valor_str: str) -> float | None:
    """Convierte un monto colombiano escrito como texto a un número.

    Args:
        valor_str: Texto del monto, con símbolos opcionales y separadores
            colombianos (por ejemplo, ``"$85.000"``).

    Returns:
        El monto como ``float``; ``None`` si el texto está vacío o no se puede
        convertir a número.

    Raises:
        AttributeError: Si el argumento no es una cadena y no implementa
            ``replace``.
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
        """Lee los datos de un recibo; las subclases implementan la lectura.

        Args:
            contenido_imagen: Bytes de la imagen que se debe procesar.
            content_type: Tipo MIME de la imagen.

        Returns:
            ``None`` en este cuerpo abstracto; las implementaciones concretas
            devuelven un ``LecturaResponse``.

        Raises:
            No lanza excepciones explícitamente. La clase base no se puede
            instanciar mientras este método siga siendo abstracto.
        """
        pass


class MockReceiptReader(BaseReceiptReader):
    """Lector simulado para desarrollo y pruebas rápidas sin gastar cuota de API."""

    async def leer_recibo(
        self, contenido_imagen: bytes, content_type: str
    ) -> LecturaResponse:
        """Devuelve datos de recibo simulados sin usar la imagen ni llamar a red.

        Args:
            contenido_imagen: Imagen recibida; no se procesa en el lector mock.
            content_type: Tipo MIME recibido; no se procesa en el lector mock.

        Returns:
            Un ``LecturaResponse`` con valores de ejemplo fijos.

        Raises:
            No lanza excepciones explícitamente.
        """
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
        """Envía la imagen a Gemini y transforma su respuesta en datos de recibo.

        Args:
            contenido_imagen: Bytes de la imagen del recibo.
            content_type: Tipo MIME usado por Gemini para interpretar la imagen.

        Returns:
            Un ``LecturaResponse`` con los datos extraídos o un mensaje de error
            controlado para respuestas HTTP no exitosas, fallos de red,
            timeout o respuestas que no se pueden interpretar.

        Raises:
            No propaga ``httpx.TimeoutException``, ``httpx.RequestError``,
            ``json.JSONDecodeError``, ``KeyError`` ni ``ValueError``; los
            convierte en respuestas con mensaje. Otros errores no capturados
            se propagan.
        """
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
    """Selecciona el lector Gemini configurado o el lector simulado.

    Returns:
        ``GeminiReceiptReader`` si ``AI_PROVIDER`` es ``"gemini"`` y hay una
        clave configurada; en los demás casos, ``MockReceiptReader``.

    Raises:
        No lanza excepciones explícitamente.
    """
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return GeminiReceiptReader(GEMINI_API_KEY)
    return MockReceiptReader()
