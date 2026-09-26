from pydantic import BaseModel, EmailStr, Field


class SolicitarRecuperacion(BaseModel):
    correo: EmailStr


class RestablecerContrasena(BaseModel):
    token: str
    nueva_contrasena: str = Field(min_length=8)
