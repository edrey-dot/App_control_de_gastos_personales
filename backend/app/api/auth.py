from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Usuario
from app.schemas.auth import UsuarioCreate, UsuarioResponse, LoginRequest, Token
from app.core.security import obtener_contrasena_hash, verificar_contrasena, crear_token_acceso

router = APIRouter(tags=["Autenticación"])


@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """HU-10: Registro de nuevo usuario (201 al crear, 409 si el correo ya existe)."""
    usuario_existente = db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = Usuario(
        correo=payload.correo,
        contrasena_hash=obtener_contrasena_hash(payload.contrasena)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/sesiones", response_model=Token)
def iniciar_sesion(payload: LoginRequest, db: Session = Depends(get_db)):
    """HU-10: Inicio de sesión (200 con JWT, 401 si las credenciales son incorrectas)."""
    usuario = db.query(Usuario).filter(Usuario.correo == payload.correo.strip().lower()).first()
    if not usuario or not verificar_contrasena(payload.contrasena, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token_acceso(data={"sub": usuario.correo, "id_usuario": usuario.id_usuario})
    return Token(access_token=token, token_type="bearer")
