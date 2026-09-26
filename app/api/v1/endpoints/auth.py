from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.email import enviar_correo
from app.core.rate_limit import (
    limpiar_intentos,
    registrar_intento_fallido,
    registrar_solicitud_recuperacion,
    segundos_de_bloqueo_restantes,
    segundos_de_espera_recuperacion,
)
from app.core.security import create_access_token, verify_password
from app.core.uploads import guardar_foto_perfil
from app.crud import crud_error_log, crud_password_reset, crud_usuario
from app.schemas.password_reset import RestablecerContrasena, SolicitarRecuperacion
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



@router.post("/olvide-contrasena")
def olvide_contrasena(data: SolicitarRecuperacion, db: Session = Depends(get_db)):
    """Pide un enlace para restablecer la contraseña. A propósito siempre
    responde el mismo mensaje, exista o no ese correo, para que alguien no
    pueda usar este formulario para adivinar qué correos están registrados."""
    espera = segundos_de_espera_recuperacion(data.correo)
    if espera > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Ya pediste un enlace hace poco. Intenta de nuevo en {espera // 60 + 1} minuto(s).",
        )
    registrar_solicitud_recuperacion(data.correo)

    usuario = crud_usuario.get_by_correo(db, data.correo)
    if usuario is not None and usuario.activo:
        token = crud_password_reset.crear_token(db, usuario.id)
        enlace = f"{settings.frontend_url_principal}/restablecer-contrasena?token={token.token}"
        try:
            enviar_correo(
                usuario.correo,
                "Restablece tu contraseña — Voz Profesional",
                (
                    f"<p>Hola {usuario.nombre},</p>"
                    "<p>Pediste restablecer tu contraseña en Voz Profesional. "
                    "Este enlace es válido por 1 hora:</p>"
                    f'<p><a href="{enlace}">{enlace}</a></p>'
                    "<p>Si no fuiste tú, puedes ignorar este correo: tu contraseña sigue igual.</p>"
                ),
            )
        except Exception as exc:
            # No dejamos que un problema de envío (por ejemplo, todavía no se
            # configuró RESEND_API_KEY) cambie la respuesta ni revele que el
            # correo sí existe: solo queda registrado para que el admin lo vea.
            db.rollback()
            crud_error_log.registrar(
                db,
                metodo="POST",
                ruta="/api/v1/auth/olvide-contrasena",
                tipo_error=type(exc).__name__,
                mensaje=str(exc),
                traceback=None,
            )

    return {"mensaje": "Si ese correo está registrado, te enviamos un enlace para restablecer tu contraseña."}


@router.post("/restablecer-contrasena")
def restablecer_contrasena(data: RestablecerContrasena, db: Session = Depends(get_db)):
    entrada = crud_password_reset.obtener_valido(db, data.token)
    if entrada is None:
        raise HTTPException(status_code=400, detail="Este enlace no es válido o ya expiró. Solicita uno nuevo.")

    usuario = crud_usuario.obtener(db, entrada.id_usuario)
    if usuario is None:
        raise HTTPException(status_code=400, detail="Este enlace no es válido o ya expiró. Solicita uno nuevo.")

    crud_usuario.actualizar_contrasena(db, usuario, data.nueva_contrasena)
    crud_password_reset.marcar_usado(db, entrada)
    return {"mensaje": "Tu contraseña se actualizó correctamente. Ya puedes iniciar sesión."}
