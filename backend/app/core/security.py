from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.db.models import Usuario
from app.db.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/sesiones")


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    """Compara una contraseña plana con un hash almacenado.

    Args:
        contrasena_plana: Contraseña ingresada por el usuario.
        contrasena_hash: Hash bcrypt almacenado para la cuenta.

    Returns:
        ``True`` si la contraseña coincide; de lo contrario, ``False``.

    Raises:
        passlib.exc.UnknownHashError: Si el hash almacenado usa un formato o
            esquema que Passlib no reconoce. Otros errores de Passlib/bcrypt
            tampoco se capturan.
    """
    return pwd_context.verify(contrasena_plana, contrasena_hash)


def obtener_contrasena_hash(contrasena: str) -> str:
    """Genera un hash bcrypt de la contraseña.

    Args:
        contrasena: Contraseña plana que se debe proteger.

    Returns:
        El hash bcrypt de la contraseña, con sal generada por Passlib.

    Raises:
        Errores de Passlib o bcrypt: Si el cálculo del hash falla, las
            excepciones correspondientes se propagan al llamador.
    """
    return pwd_context.hash(contrasena)


def crear_token_acceso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Firma un token JWT con los datos y la fecha de expiración.

    Args:
        data: Claims que se incluirán en el token; no se modifica el diccionario
            recibido.
        expires_delta: Duración opcional del token. Si se omite, se usa la
            duración configurada en ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        El token JWT firmado como cadena.

    Raises:
        jwt.PyJWTError: Si PyJWT no puede codificar o firmar los claims.
        TypeError: Si los claims no se pueden serializar a JSON.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida el JWT y obtiene el usuario autenticado de la base de datos.

    Args:
        token: JWT proporcionado mediante el esquema Bearer de OAuth2.
        db: Sesión SQLAlchemy usada para buscar al usuario del token.

    Returns:
        El usuario cuyo correo coincide con el claim ``sub`` del JWT.

    Raises:
        HTTPException: Con estado 401 si el JWT es inválido, expiró, no contiene
            ``sub`` o el usuario no existe.
        SQLAlchemyError: Si falla la consulta de base de datos.
    """
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
    except jwt.PyJWTError as err:
        raise credentials_exception from err

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario is None:
        raise credentials_exception
    return usuario
