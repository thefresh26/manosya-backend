from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rol(Base):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)

    usuarios = relationship("Usuario", back_populates="rol")
    modulos_por_rol = relationship("ModuloPorRol", back_populates="rol")
