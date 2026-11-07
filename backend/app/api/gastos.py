from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.db.session import get_db
from app.db.models import Gasto, Categoria, Usuario
from app.schemas.gasto import GastoCreate, GastoResponse, ResumenMensualResponse, ItemResumen
from app.core.security import obtener_usuario_actual

router = APIRouter(tags=["Gastos"])


@router.post("/gastos", response_model=GastoResponse, status_code=status.HTTP_201_CREATED)
def crear_gasto(
    payload: GastoCreate,
    response: Response,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """HU-02, HU-03, HU-04, HU-09:
    Crea un nuevo gasto. Valida que la categoría exista.
    Retorna 201 y cabecera Location: /gastos/{id_gasto}.
    """
    categoria = db.query(Categoria).filter(Categoria.id_categoria == payload.id_categoria).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Elige una categoria"
        )

    nuevo_gasto = Gasto(
        id_usuario=usuario_actual.id_usuario,
        comercio=payload.comercio,
        fecha=payload.fecha,
        monto=payload.monto,
        id_categoria=payload.id_categoria
    )
    db.add(nuevo_gasto)
    db.commit()
    db.refresh(nuevo_gasto)

    response.headers["Location"] = f"/gastos/{nuevo_gasto.id_gasto}"
    return nuevo_gasto


@router.get("/gastos", response_model=list[GastoResponse])
def listar_gastos(
    fecha: Optional[str] = Query(None, description="Fecha en formato AAAA-MM-DD"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """HU-02 Escenario 1: Listar gastos del usuario autenticado (filtrables por fecha)."""
    consulta = db.query(Gasto).filter(Gasto.id_usuario == usuario_actual.id_usuario)

    if fecha:
        try:
            fecha_filtro = date.fromisoformat(fecha)
            consulta = consulta.filter(Gasto.fecha == fecha_filtro)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Utilice AAAA-MM-DD"
            )

    return consulta.order_by(Gasto.fecha.desc(), Gasto.id_gasto.desc()).all()


@router.get("/gastos/{id_gasto}", response_model=GastoResponse)
def obtener_gasto(
    id_gasto: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """Obtener un gasto específico. RNF-06: Si pertenece a otro usuario o no existe, retorna 404."""
    gasto = db.query(Gasto).filter(
        Gasto.id_gasto == id_gasto,
        Gasto.id_usuario == usuario_actual.id_usuario
    ).first()

    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )
    return gasto


@router.get("/resumenes", response_model=ResumenMensualResponse)
def obtener_resumen_mensual(
    anio: int = Query(..., description="Año del resumen"),
    mes: int = Query(..., ge=1, le=12, description="Mes del resumen (1-12)"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """HU-06: Resumen mensual para gráfico de pastel con porcentajes por categoría."""
    gastos_mes = (
        db.query(
            Categoria.id_categoria,
            Categoria.nombre,
            func.sum(Gasto.monto).label("total_categoria")
        )
        .join(Gasto, Gasto.id_categoria == Categoria.id_categoria)
        .filter(
            Gasto.id_usuario == usuario_actual.id_usuario,
            extract("year", Gasto.fecha) == anio,
            extract("month", Gasto.fecha) == mes
        )
        .group_by(Categoria.id_categoria, Categoria.nombre)
        .all()
    )

    total_general = sum(item.total_categoria for item in gastos_mes) if gastos_mes else 0.0

    if total_general == 0:
        return ResumenMensualResponse(
            anio=anio,
            mes=mes,
            total_mes=0.0,
            items=[],
            mensaje="No hay gastos en este mes"
        )

    items = []
    for id_cat, nombre, total_cat in gastos_mes:
        pct = round((float(total_cat) / float(total_general)) * 100, 1)
        items.append(ItemResumen(
            id_categoria=id_cat,
            categoria=nombre,
            total=round(float(total_cat), 2),
            porcentaje=pct
        ))

    return ResumenMensualResponse(
        anio=anio,
        mes=mes,
        total_mes=round(float(total_general), 2),
        items=items
    )
