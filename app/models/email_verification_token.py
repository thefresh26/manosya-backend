from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class EmailVerificationToken(Base):
    """Un enlace de un solo uso para confirmar que el correo de registro es
    real. Se crea al registrarse (y de nuevo cada vez que se reenvía), y
    expira solo. A propósito no bloquea el login si no se verifica todavía
    (ver auth.py): solo se usa para mostrar un aviso y, más adelante, para
    decidir a quién sí enviarle otras notificaciones por correo."""

    __tablename__ = "email_verification_token"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    expira_en = Column(DateTime, nullable=False)
    usado_en = Column(DateTime, nullable=True)

    usuario = relationship("Usuario")
