from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    crear_token_acceso,
    obtener_contrasena_hash,
    verificar_contrasena,
)
from app.db.models import Usuario
from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token, UsuarioCreate, UsuarioResponse

router = APIRouter(tags=["Autenticación"])


@router.post(
    "/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un usuario y almacena el hash de su contraseña.

    Args:
        payload: Correo y contraseña validados para el registro.
        db: Sesión SQLAlchemy usada para buscar y guardar el usuario.

    Returns:
        La entidad ``Usuario`` creada, serializada sin su hash de contraseña.

    Raises:
        HTTPException: Con estado 409 si el correo ya está registrado.
        SQLAlchemyError: Si falla una operación de base de datos.
        Errores de Passlib o bcrypt: Si falla el cálculo del hash de contraseña.
        FastAPI responde 422 antes de llamar esta función si el cuerpo es
        inválido.
    """
    usuario_existente = (
        db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    )
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado",
        )

    nuevo_usuario = Usuario(
        correo=payload.correo,
        contrasena_hash=obtener_contrasena_hash(payload.contrasena),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/sesiones", response_model=Token)
def iniciar_sesion(payload: LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y crea un token de acceso JWT.

    Args:
        payload: Correo y contraseña enviados para iniciar sesión.
        db: Sesión SQLAlchemy usada para buscar el usuario.

    Returns:
        Un ``Token`` con el JWT de acceso y el tipo ``bearer``.

    Raises:
        HTTPException: Con estado 401 si el usuario no existe o la contraseña
            no coincide.
        SQLAlchemyError: Si falla la consulta de base de datos. Los errores de
            Passlib al verificar el hash y de PyJWT al firmar el token no se
            capturan y se propagan.
    """
    usuario = (
        db.query(Usuario)
        .filter(Usuario.correo == payload.correo.strip().lower())
        .first()
    )
    if not usuario or not verificar_contrasena(
        payload.contrasena, usuario.contrasena_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token_acceso(
        data={"sub": usuario.correo, "id_usuario": usuario.id_usuario}
    )
    return Token(access_token=token, token_type="bearer")
