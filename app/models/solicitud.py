from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Solicitud(Base):
    """Un cliente pidiendo contactar a un trabajador por un servicio puntual.
    El trabajador ve el mensaje y los datos de contacto del cliente en su
    panel, y puede marcarla como atendida."""

    __tablename__ = "solicitud"

    id = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicio.id"), nullable=False)
    mensaje = Column(Text, nullable=True)
    atendida = Column(Boolean, nullable=False, default=False)
    # El trabajador la marca como completada cuando ya hizo el trabajo;
    # eso dispara el cobro (ver Pago) por el precio_desde del servicio.
    completada = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    cliente = relationship("Usuario", foreign_keys=[id_cliente])
    servicio = relationship("Servicio")
    pago = relationship("Pago", back_populates="solicitud", uselist=False)
