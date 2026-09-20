from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class ModuloPorRol(Base):
    __tablename__ = "modulo_por_rol"

    id = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("rol.id"), nullable=False)
    id_modulo = Column(Integer, ForeignKey("modulo.id"), nullable=False)

    rol = relationship("Rol", back_populates="modulos_por_rol")
    modulo = relationship("Modulo", back_populates="modulos_por_rol")
