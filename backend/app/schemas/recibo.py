from pydantic import BaseModel


class LecturaResponse(BaseModel):
    comercio: str | None = None
    fecha: str | None = None
    monto: float | None = None
    mensaje: str | None = None
