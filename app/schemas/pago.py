from datetime import datetime

from pydantic import BaseModel


class Pago(BaseModel):
    id: int
    id_solicitud: int
    referencia: str
    monto: float
    moneda: str
    estado: str
    creado_en: datetime

    class Config:
        from_attributes = True


class DatosCheckoutWompi(BaseModel):
    """Lo que el frontend necesita para abrir el Web Checkout de Wompi.
    `llave_publica` es pública por diseño (así funciona el widget de
    Wompi); la firma de integridad se calcula en el backend con el secreto
    que nunca sale de aquí (ver app/core/wompi.py)."""

    llave_publica: str
    referencia: str
    monto_en_centavos: int
    moneda: str
    firma_integridad: str
