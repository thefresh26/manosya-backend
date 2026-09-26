import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken

MINUTOS_VALIDEZ = 60


def crear_token(db: Session, id_usuario: int) -> PasswordResetToken:
    entrada = PasswordResetToken(
        id_usuario=id_usuario,
        token=secrets.token_urlsafe(32),
        expira_en=datetime.utcnow() + timedelta(minutes=MINUTOS_VALIDEZ),
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


def obtener_valido(db: Session, token: str) -> PasswordResetToken | None:
    """Devuelve el token solo si existe, no se ha usado, y no ha expirado."""
    entrada = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if entrada is None:
        return None
    if entrada.usado_en is not None:
        return None
    if entrada.expira_en < datetime.utcnow():
        return None
    return entrada


def marcar_usado(db: Session, entrada: PasswordResetToken) -> None:
    """Marca este token como usado y, de paso, invalida cualquier otro token
    sin usar del mismo usuario (por si pidió el correo varias veces antes de
    usar uno): así un enlace viejo que quedó en su bandeja de entrada no
    sirve después de que ya cambió la contraseña."""
    ahora = datetime.utcnow()
    (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.id_usuario == entrada.id_usuario,
            PasswordResetToken.usado_en.is_(None),
        )
        .update({"usado_en": ahora})
    )
    db.commit()
