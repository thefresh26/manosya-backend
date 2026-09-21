from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rate_limit import (
    limpiar_intentos,
    registrar_intento_fallido,
    segundos_de_bloqueo_restantes,
)
from app.core.security import create_access_token, verify_password
from app.core.uploads import guardar_foto_perfil
from app.crud import crud_usuario
from app.schemas.usuario import LoginRequest, RegistroTrabajador, Token, Usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def registro(
    nombre: str = Form(...),
    apellido: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    cedula: str = Form(...),
    celular: str = Form(...),
    ciudad: str = Form(...),
    direccion: str = Form(...),
    latitud: float | None = Form(None),
    longitud: float | None = Form(None),
    foto: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    data = RegistroTrabajador(
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        contrasena=contrasena,
        cedula=cedula,
        celular=celular,
        ciudad=ciudad,
        direccion=direccion,
        latitud=latitud,
        longitud=longitud,
    )
    if crud_usuario.get_by_correo(db, data.correo):
        raise HTTPException(status_code=400, detail="Ese correo ya está registrado")
    if crud_usuario.get_by_cedula(db, data.cedula):
        raise HTTPException(status_code=400, detail="Esa cédula ya está registrada")
    foto_url = await guardar_foto_perfil(foto)
    return crud_usuario.registrar_trabajador(db, data, foto_url=foto_url)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Evita fuerza bruta: si ya fallaron demasiados intentos con este correo
    # en los últimos minutos, se bloquea temporalmente antes de siquiera
    # consultar la base de datos.
    espera = segundos_de_bloqueo_restantes(data.correo)
    if espera > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Demasiados intentos fallidos. Intenta de nuevo en {espera // 60 + 1} minuto(s).",
        )

    usuario = crud_usuario.get_by_correo(db, data.correo)
    if not usuario or not verify_password(data.contrasena, usuario.contrasena):
        registrar_intento_fallido(data.correo)
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    limpiar_intentos(data.correo)
    token = create_access_token({"sub": str(usuario.id)})
    return Token(access_token=token)
