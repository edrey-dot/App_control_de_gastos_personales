import re

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


def normalizar_telefono_colombiano(valor: str | None) -> str | None:
    if valor is None or not valor.strip():
        return None
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) == 12 and digitos.startswith("57"):
        digitos = digitos[2:]
    if len(digitos) != 10:
        raise ValueError("El celular debe tener 10 dígitos; se acepta el prefijo +57")
    return digitos


class UsuarioCreate(BaseModel):
    correo: str
    contrasena: str
    nombre_usuario: str | None = Field(default=None, min_length=2, max_length=50)
    telefono: str | None = None

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

    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, v: str | None) -> str | None:
        if v is None:
            return None
        nombre = v.strip()
        if not nombre:
            return None
        if len(nombre) < 2:
            raise ValueError("El nombre de usuario debe tener al menos 2 caracteres")
        return nombre

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        return normalizar_telefono_colombiano(v)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    correo: str


class LoginRequest(BaseModel):
    identificador: str = Field(
        validation_alias=AliasChoices("identificador", "correo")
    )
    contrasena: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
