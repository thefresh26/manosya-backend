from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Modulo(Base):
    __tablename__ = "modulo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)

    modulos_por_rol = relationship("ModuloPorRol", back_populates="modulo")
