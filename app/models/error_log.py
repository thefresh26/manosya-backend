from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.base import Base


class ErrorLog(Base):
    """Registro automatico de errores no controlados del backend (excepciones
    que se escapan de un endpoint y terminarian en un 500). Se guarda aqui en
    vez de solo en los logs de Render para que el administrador los vea desde
    el panel sin tener que entrar al dashboard de Render. No reemplaza un
    servicio externo de monitoreo (Sentry, etc.), pero cubre lo basico sin
    depender de nada mas."""

    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True, index=True)
    metodo = Column(String, nullable=False)
    ruta = Column(String, nullable=False)
    tipo_error = Column(String, nullable=False)
    mensaje = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)
    visto = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)
