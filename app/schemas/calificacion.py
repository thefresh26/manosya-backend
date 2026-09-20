from datetime import datetime

from pydantic import BaseModel, Field


class CalificacionCrear(BaseModel):
    nombre_cliente: str
    puntuacion: int = Field(ge=1, le=5)
    comentario: str | None = None


class Calificacion(BaseModel):
    id: int
    id_servicio: int
    nombre_cliente: str
    puntuacion: int
    comentario: str | None = None
    creado_en: datetime

    class Config:
        from_attributes = True
