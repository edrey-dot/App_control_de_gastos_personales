from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.session import get_db
from app.db.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sesiones")


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    return pwd_context.verify(contrasena_plana, contrasena_hash)


def obtener_contrasena_hash(contrasena: str) -> str:
    """Genera el hash seguro (bcrypt) de una contraseña."""
    return pwd_context.hash(contrasena)


def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT firmado con fecha de expiración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """Dependencia para validar el token JWT y obtener el usuario autenticado (401 si falla)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación no válidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario is None:
        raise credentials_exception
    return usuario
