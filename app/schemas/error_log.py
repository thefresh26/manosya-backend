from datetime import datetime

from pydantic import BaseModel


class ErrorLog(BaseModel):
    id: int
    metodo: str
    ruta: str
    tipo_error: str
    mensaje: str
    traceback: str | None = None
    visto: bool
    creado_en: datetime

    class Config:
        from_attributes = True
