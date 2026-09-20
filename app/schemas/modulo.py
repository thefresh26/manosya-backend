from pydantic import BaseModel


class ModuloBase(BaseModel):
    nombre: str
    descripcion: str | None = None


class ModuloCreate(ModuloBase):
    pass


class Modulo(ModuloBase):
    id: int

    class Config:
        from_attributes = True
