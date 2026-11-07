from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    correo = Column(String(255), unique=True, nullable=False, index=True)
    contrasena_hash = Column(String(255), nullable=False)

    gastos = relationship("Gasto", back_populates="usuario", cascade="all, delete-orphan")
    topes = relationship("TopeMensual", back_populates="usuario", cascade="all, delete-orphan")


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    gastos = relationship("Gasto", back_populates="categoria")
    topes = relationship("TopeMensual", back_populates="categoria")


class Gasto(Base):
    """Modelo de Gasto.
    Regla de Privacidad (R-01, HU-09):
    SOLO guarda comercio, fecha, monto y categoria.
    NUNCA nombre del titular, numero de tarjeta ni direccion.
    """
    __tablename__ = "gasto"

    id_gasto = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False, index=True)
    comercio = Column(String(150), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Numeric(12, 2), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)

    __table_args__ = (
        CheckConstraint("monto > 0", name="check_monto_positivo"),
    )

    usuario = relationship("Usuario", back_populates="gastos")
    categoria = relationship("Categoria", back_populates="gastos")


class TopeMensual(Base):
    """Modelo de Tope Mensual por categoría (HU-07, HU-08)."""
    __tablename__ = "tope_mensual"

    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), primary_key=True)
    anio = Column(Integer, primary_key=True)
    mes = Column(Integer, primary_key=True)
    monto_tope = Column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("mes BETWEEN 1 AND 12", name="check_mes_valido"),
        CheckConstraint("monto_tope > 0", name="check_tope_positivo"),
    )

    usuario = relationship("Usuario", back_populates="topes")
    categoria = relationship("Categoria", back_populates="topes")
