from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Pago(Base):
    """Cobro por un servicio ya prestado, vía Wompi. Se crea cuando el
    trabajador marca la solicitud como completada: el monto es siempre el
    precio_desde ya publicado en el servicio (el trabajador no elige el
    monto, solo activa el cobro). El cliente paga en el Web Checkout de
    Wompi (un widget alojado por Wompi), así que los datos de la tarjeta
    nunca pasan por nuestro backend. `estado` se actualiza desde el webhook
    de Wompi (ver app/api/v1/endpoints/webhooks.py)."""

    __tablename__ = "pago"

    id = Column(Integer, primary_key=True, index=True)
    id_solicitud = Column(Integer, ForeignKey("solicitud.id"), nullable=False, unique=True)
    referencia = Column(String, nullable=False, unique=True, index=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String, nullable=False, default="COP")
    # pendiente: esperando que el cliente pague o que Wompi confirme.
    # aprobado / declinado / error: estados finales que reporta Wompi.
    estado = Column(String, nullable=False, default="pendiente")
    id_transaccion_wompi = Column(String, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    solicitud = relationship("Solicitud", back_populates="pago")
