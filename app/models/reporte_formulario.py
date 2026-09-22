from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class ReporteFormulario(Base):
    """Un trabajador reporta un error en su propio formulario de servicio
    (por ejemplo un dato mal guardado, o un rechazo que le parece injusto),
    para que el administrador lo corrija. Distinto de una denuncia sobre una
    persona: aquí el reportante es el dueño del formulario."""

    __tablename__ = "reporte_formulario"

    id = Column(Integer, primary_key=True, index=True)
    id_trabajador = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicio.id"), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String, nullable=False, default="pendiente")  # pendiente | resuelto
    resolucion = Column(Text, nullable=True)
    resuelta_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    trabajador = relationship("Usuario", foreign_keys=[id_trabajador])
    servicio = relationship("Servicio")
