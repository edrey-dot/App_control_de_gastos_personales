from datetime import date

from pydantic import BaseModel, field_validator


class LecturaResponse(BaseModel):
    comercio: str | None = None
    fecha: str | None = None
    monto: float | None = None
    mensaje: str | None = None

    @field_validator("fecha")
    @classmethod
    def validar_fecha_iso(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        return date.fromisoformat(valor).isoformat()
