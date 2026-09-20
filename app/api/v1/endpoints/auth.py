from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
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
    usuario = crud_usuario.get_by_correo(db, data.correo)
    if not usuario or not verify_password(data.contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    token = create_access_token({"sub": str(usuario.id)})
    return Token(access_token=token)
