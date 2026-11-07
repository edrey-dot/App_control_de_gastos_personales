from typing import Optional
from pydantic import BaseModel


class LecturaResponse(BaseModel):
    comercio: Optional[str] = None
    fecha: Optional[str] = None
    monto: Optional[float] = None
    mensaje: Optional[str] = None
