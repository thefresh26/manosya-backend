from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Servicio(Base):
    __tablename__ = "servicio"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id"), nullable=False)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_desde = Column(Float, nullable=True)
    disponibilidad = Column(String, nullable=True)
    foto_url = Column(String, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    # Flujo de aprobación del administrador: todo formulario nuevo entra como
    # "pendiente" y no aparece en las búsquedas públicas hasta que un admin lo
    # aprueba. Si lo rechaza, motivo_rechazo explica por qué, para que el
    # trabajador sepa qué corregir.
    estado = Column(String, nullable=False, default="pendiente")
    motivo_rechazo = Column(String, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="servicios")
    categoria = relationship("Categoria", back_populates="servicios")
    calificaciones = relationship("Calificacion", back_populates="servicio")
