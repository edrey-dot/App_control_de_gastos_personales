from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.validaciones import validar_fecha_gasto


class GastoCreate(BaseModel):
    # R-03 / HU-09: Rechazar cualquier campo extra (nombre, tarjeta, direccion)
    model_config = ConfigDict(extra="forbid", validate_default=True)

    comercio: str = ""
    fecha: date
    monto: float
    id_categoria: int = 0

    @field_validator("comercio")
    @classmethod
    def validar_comercio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El comercio es obligatorio")
        return v.strip()

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        # Reutilizamos la función pura de dominio de la HU-02
        return validar_fecha_gasto(v)

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: float) -> float:
        # HU-03: monto debe ser mayor a 0
        if v <= 0:
            raise ValueError("El monto debe ser un número mayor a 0")
        return round(float(v), 2)

    @field_validator("id_categoria")
    @classmethod
    def validar_categoria(cls, v: int) -> int:
        # HU-04: categoría obligatoria
        if not v or v <= 0:
            raise ValueError("Elige una categoría")
        return v


class GastoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_gasto: int
    comercio: str
    fecha: date
    monto: float
    id_categoria: int


class ItemResumen(BaseModel):
    id_categoria: int
    categoria: str
    total: float
    porcentaje: float


class ResumenMensualResponse(BaseModel):
    anio: int
    mes: int
    total_mes: float
    items: list[ItemResumen]
    mensaje: str | None = None
