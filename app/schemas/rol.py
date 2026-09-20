from pydantic import BaseModel


class RolBase(BaseModel):
    nombre: str
    descripcion: str | None = None


class RolCreate(RolBase):
    pass


class Rol(RolBase):
    id: int

    class Config:
        from_attributes = True
