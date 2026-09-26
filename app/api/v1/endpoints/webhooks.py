from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.wompi import verificar_firma_evento
from app.crud import crud_error_log, crud_pago

router = APIRouter(tags=["webhooks"])

_ESTADOS_WOMPI = {
    "APPROVED": "aprobado",
    "DECLINED": "declinado",
    "ERROR": "error",
    "VOIDED": "declinado",
    "PENDING": "pendiente",
}


@router.post("/webhooks/wompi", include_in_schema=False)
async def webhook_wompi(request: Request, db: Session = Depends(get_db)):
    """Wompi llama aquí cada vez que una transacción cambia de estado. No
    confiamos en nada de esto sin verificar la firma (ver
    app/core/wompi.py); si no coincide, se ignora en silencio (200 igual,
    para que Wompi no siga reintentando algo que nunca vamos a aceptar)."""
    try:
        payload = await request.json()
    except Exception:
        return {"recibido": False}

    if not verificar_firma_evento(payload):
        return {"recibido": False}

    try:
        transaccion = (payload.get("data") or {}).get("transaction") or {}
        referencia = transaccion.get("reference")
        estado_wompi = transaccion.get("status")
        id_transaccion = transaccion.get("id")
        if not referencia or not estado_wompi:
            return {"recibido": True}

        pago = crud_pago.obtener_por_referencia(db, referencia)
        if pago is None:
            return {"recibido": True}

        estado = _ESTADOS_WOMPI.get(estado_wompi, "error")
        crud_pago.actualizar_estado(
            db, pago, estado=estado, id_transaccion_wompi=str(id_transaccion) if id_transaccion else None
        )
    except Exception as exc:
        import traceback as traceback_module

        crud_error_log.registrar(
            db,
            metodo=request.method,
            ruta=str(request.url.path),
            tipo_error=type(exc).__name__,
            mensaje=str(exc) or "(sin mensaje)",
            traceback=traceback_module.format_exc(),
        )

    return {"recibido": True}
