from sqlalchemy.orm import Session

from app.core.wompi import generar_referencia
from app.models.pago import Pago


def obtener_por_solicitud(db: Session, id_solicitud: int) -> Pago | None:
    return db.query(Pago).filter(Pago.id_solicitud == id_solicitud).first()


def obtener_por_referencia(db: Session, referencia: str) -> Pago | None:
    return db.query(Pago).filter(Pago.referencia == referencia).first()


def crear(db: Session, *, id_solicitud: int, monto: float) -> Pago:
    pago = Pago(
        id_solicitud=id_solicitud,
        referencia=generar_referencia(id_solicitud),
        monto=monto,
        moneda="COP",
        estado="pendiente",
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def regenerar_referencia_si_fallo(db: Session, pago: Pago) -> Pago:
    """Si el intento anterior quedó declinado o con error, genera una
    referencia nueva para que el cliente pueda volver a intentar (Wompi no
    permite reutilizar una referencia que ya tuvo un resultado final)."""
    if pago.estado in ("declinado", "error"):
        pago.referencia = generar_referencia(pago.id_solicitud)
        pago.estado = "pendiente"
        db.commit()
        db.refresh(pago)
    return pago


def actualizar_estado(
    db: Session, pago: Pago, *, estado: str, id_transaccion_wompi: str | None
) -> Pago:
    pago.estado = estado
    if id_transaccion_wompi:
        pago.id_transaccion_wompi = id_transaccion_wompi
    db.commit()
    db.refresh(pago)
    return pago
