from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class DenunciaTrabajador(Base):
    """Un cliente (o cualquier usuario, incluido otro trabajador actuando
    como cliente) denuncia a un trabajador por mal comportamiento, fraude,
    etc. Separado de ReporteFormulario a propósito: son bandejas distintas
    en el panel de admin, con dueños e intención distintas."""

    __tablename__ = "denuncia_trabajador"

    id = Column(Integer, primary_key=True, index=True)
    id_denunciante = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_trabajador = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("servicio.id"), nullable=True)
    motivo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String, nullable=False, default="pendiente")  # pendiente | resuelta
    resolucion = Column(Text, nullable=True)
    resuelta_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    denunciante = relationship("Usuario", foreign_keys=[id_denunciante])
    trabajador = relationship("Usuario", foreign_keys=[id_trabajador])
    servicio = relationship("Servicio")
