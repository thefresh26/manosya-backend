from datetime import datetime

from pydantic import BaseModel


class SolicitudCrear(BaseModel):
    mensaje: str | None = None


class Solicitud(BaseModel):
    """Lo que ve el trabajador cuando un cliente lo solicita: incluye los
    datos de contacto del cliente para que lo llame directamente."""

    id: int
    id_servicio: int
    titulo_servicio: str
    nombre_cliente: str
    correo_cliente: str
    celular_cliente: str
    mensaje: str | None = None
    atendida: bool
    completada: bool
    # None si el trabajador todavia no la marca como completada (no hay
    # cobro creado todavia). Una vez existe, el cliente ve el monto y si
    # ya quedo aprobado, declinado, o sigue pendiente de pago.
    estado_pago: str | None = None
    monto_pago: float | None = None
    creado_en: datetime

    class Config:
        from_attributes = True
