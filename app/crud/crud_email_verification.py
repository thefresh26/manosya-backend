import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken

MINUTOS_VALIDEZ = 60 * 24  # 24 horas: más laxo que el de contraseña, porque
# no es algo tan sensible y no queremos que alguien pierda el enlace de su
# bandeja de entrada por revisarlo un día después.


def crear_token(db: Session, id_usuario: int) -> EmailVerificationToken:
    entrada = EmailVerificationToken(
        id_usuario=id_usuario,
        token=secrets.token_urlsafe(32),
        expira_en=datetime.utcnow() + timedelta(minutes=MINUTOS_VALIDEZ),
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)
    return entrada


def obtener_valido(db: Session, token: str) -> EmailVerificationToken | None:
    entrada = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
    if entrada is None:
        return None
    if entrada.usado_en is not None:
        return None
    if entrada.expira_en < datetime.utcnow():
        return None
    return entrada


def marcar_usado(db: Session, entrada: EmailVerificationToken) -> None:
    ahora = datetime.utcnow()
    (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.id_usuario == entrada.id_usuario,
            EmailVerificationToken.usado_en.is_(None),
        )
        .update({"usado_en": ahora})
    )
    db.commit()
