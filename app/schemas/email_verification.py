from pydantic import BaseModel, EmailStr


class ReenviarVerificacion(BaseModel):
    correo: EmailStr


class VerificarCorreo(BaseModel):
    token: str
