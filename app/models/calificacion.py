from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Calificacion(Base):
    __tablename__ = "calificacion"

    id = Column(Integer, primary_key=True, index=True)
    id_servicio = Column(Integer, ForeignKey("servicio.id"), nullable=False)
    nombre_cliente = Column(String, nullable=False)
    puntuacion = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    servicio = relationship("Servicio", back_populates="calificaciones")
