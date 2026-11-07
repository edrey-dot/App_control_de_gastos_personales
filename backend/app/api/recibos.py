from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.schemas.recibo import LecturaResponse
from app.services.receipt_reader import obtener_receipt_reader
from app.core.security import obtener_usuario_actual
from app.db.models import Usuario

router = APIRouter(prefix="/recibos", tags=["Lectura de Recibos (IA)"])


@router.post("/lecturas", response_model=LecturaResponse)
async def leer_recibo(
    foto: UploadFile = File(...),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """HU-01: Recibe la foto del recibo, extrae datos con IA y retorna la vista previa.

    Reglas transversales:
    - R-01: Solo extrae y devuelve comercio, fecha y monto.
    - R-02: La foto NO se almacena en el servidor ni en BD; se procesa en memoria y se descarta.
    """
    if not foto or not foto.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo de imagen requerido"
        )

    if not foto.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido debe ser una imagen válida"
        )

    contenido = await foto.read()
    reader = obtener_receipt_reader()
    lectura = await reader.leer_recibo(contenido, foto.content_type)
    return lectura
