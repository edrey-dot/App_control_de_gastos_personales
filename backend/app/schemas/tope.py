from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class TopeCreate(BaseModel):
    id_categoria: int
    anio: int
    mes: int
    monto_tope: float

    @field_validator("mes")
    @classmethod
    def validar_mes(cls, v: int) -> int:
        if not (1 <= v <= 12):
            raise ValueError("El mes debe estar entre 1 y 12")
        return v

    @field_validator("monto_tope")
    @classmethod
    def validar_monto_tope(cls, v: float) -> float:
        # HU-07 escenario 2: "El tope debe ser mayor a $0"
        if v <= 0:
            raise ValueError("El tope debe ser mayor a $0")
        return round(float(v), 2)


class TopeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria: int
    categoria: str
    anio: int
    mes: int
    monto_tope: float
    total_gastado: float
    porcentaje: float
    alerta_80: bool
    mensaje_alerta: Optional[str] = None
