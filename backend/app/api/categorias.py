from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Categoria, Usuario
from app.schemas.categoria import CategoriaResponse
from app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """HU-04: Obtener lista de categorías disponibles."""
    return db.query(Categoria).order_by(Categoria.id_categoria).all()
