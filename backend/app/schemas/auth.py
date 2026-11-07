import re
from pydantic import BaseModel, ConfigDict, field_validator


class UsuarioCreate(BaseModel):
    correo: str
    contrasena: str

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v: str) -> str:
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, v):
            raise ValueError("Correo electrónico inválido")
        return v.strip().lower()

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    correo: str


class LoginRequest(BaseModel):
    correo: str
    contrasena: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
