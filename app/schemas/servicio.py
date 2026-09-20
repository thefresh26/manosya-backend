from datetime import datetime

from pydantic import BaseModel

from app.schemas.categoria import Categoria


class ServicioCrear(BaseModel):
    id_categoria: int
    titulo: str
    descripcion: str | None = None
    precio_desde: float | None = None
    disponibilidad: str | None = None


class Servicio(BaseModel):
    id: int
    id_usuario: int
    id_categoria: int
    titulo: str
    descripcion: str | None = None
    precio_desde: float | None = None
    disponibilidad: str | None = None
    foto_url: str | None = None
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class ServicioConCategoria(Servicio):
    """Versión que además incluye los datos de la categoría y el resumen de
    calificaciones, para no tener que hacer más consultas desde el frontend."""

    categoria: Categoria | None = None
    calificacion_promedio: float | None = None
    total_calificaciones: int = 0
    nombre_trabajador: str | None = None
    ciudad_trabajador: str | None = None

    class Config:
        from_attributes = True
