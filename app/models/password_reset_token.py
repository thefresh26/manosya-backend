from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PasswordResetToken(Base):
    """Un enlace de un solo uso para restablecer la contraseña. Se crea al
    pedir "olvidé mi contraseña" y expira solo (nunca se pisa a sí mismo):
    varias solicitudes seguidas dejan varios tokens, pero al usar cualquiera
    se invalidan todos los demás del mismo usuario (ver
    crud_password_reset.marcar_usado)."""

    __tablename__ = "password_reset_token"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    expira_en = Column(DateTime, nullable=False)
    usado_en = Column(DateTime, nullable=True)

    usuario = relationship("Usuario")
