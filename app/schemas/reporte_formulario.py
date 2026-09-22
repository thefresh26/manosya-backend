from datetime import datetime

from pydantic import BaseModel


class ReporteFormularioCrear(BaseModel):
    descripcion: str


class ReporteFormularioResolver(BaseModel):
    resolucion: str


class ReporteFormulario(BaseModel):
    id: int
    id_trabajador: int
    nombre_trabajador: str
    id_servicio: int
    titulo_servicio: str
    descripcion: str
    estado: str
    resolucion: str | None = None
    creado_en: datetime

    class Config:
        from_attributes = True
