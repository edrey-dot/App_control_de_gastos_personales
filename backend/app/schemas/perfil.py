from pydantic import BaseModel, Field, field_validator

from app.schemas.auth import normalizar_telefono_colombiano


class PerfilResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    correo: str
    telefono: str | None = None
    tiene_foto: bool


class PerfilUpdate(BaseModel):
    nombre_usuario: str = Field(min_length=2, max_length=50)
    telefono: str | None = None

    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, valor: str) -> str:
        nombre = valor.strip()
        if len(nombre) < 2:
            raise ValueError("El nombre de usuario debe tener al menos 2 caracteres")
        return nombre

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str | None) -> str | None:
        return normalizar_telefono_colombiano(valor)
