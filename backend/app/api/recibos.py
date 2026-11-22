import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.security import obtener_usuario_actual
from app.db.models import Usuario
from app.schemas.recibo import LecturaResponse
from app.services.receipt_reader import (
    ReceiptReaderTimeoutError,
    ReceiptReaderUnavailableError,
    obtener_receipt_reader,
)

router = APIRouter(prefix="/recibos", tags=["Lectura de Recibos (IA)"])
logger = logging.getLogger(__name__)


@router.post("/lecturas", response_model=LecturaResponse)
async def leer_recibo(
    foto: UploadFile = File(...),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """HU-01: Recibe la foto del recibo, extrae datos con IA y retorna la vista previa.

    Reglas transversales:
    - R-01: Solo extrae y devuelve comercio, fecha y monto.
    - R-02: La foto NO se almacena en el servidor ni en BD;
      se procesa en memoria y se descarta.
    """
    if not foto or not foto.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo de imagen requerido",
        )

    if not foto.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido debe ser una imagen válida",
        )

    contenido = await foto.read()
    reader = obtener_receipt_reader()
    try:
        lectura = await reader.leer_recibo(contenido, foto.content_type)
    except ReceiptReaderTimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="El servicio de IA no responde o tardo demasiado",
        ) from error
    except ReceiptReaderUnavailableError as error:
        detail = "No se pudo conectar con el proveedor de IA."
        if error.provider_status_code is not None:
            detail = (
                f"El proveedor de IA respondió HTTP {error.provider_status_code}."
            )
            if error.provider_message:
                detail += f" {error.provider_message}"
        logger.warning("Falló la lectura del recibo: %s", detail)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from error
    return lectura
