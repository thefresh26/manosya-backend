from pydantic import BaseModel


class Categoria(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    icono: str | None = None

    class Config:
        from_attributes = True


class CategoriaCrear(BaseModel):
    nombre: str
    descripcion: str | None = None
    icono: str | None = None
