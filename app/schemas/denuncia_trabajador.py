from datetime import datetime

from pydantic import BaseModel


class DenunciaTrabajadorCrear(BaseModel):
    motivo: str
    descripcion: str | None = None
    id_servicio: int | None = None


class DenunciaTrabajadorResolver(BaseModel):
    resolucion: str
    # Acción que toma el admin al resolver, además de anotar la resolución.
    accion: str = "ninguna"  # ninguna | desactivar_trabajador | desactivar_servicio


class DenunciaTrabajador(BaseModel):
    id: int
    id_denunciante: int
    nombre_denunciante: str
    id_trabajador: int
    nombre_trabajador: str
    id_servicio: int | None = None
    motivo: str
    descripcion: str | None = None
    estado: str
    resolucion: str | None = None
    creado_en: datetime

    class Config:
        from_attributes = True
