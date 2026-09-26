from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_usuario, get_db
from app.core.config import settings
from app.core.wompi import firma_integridad, monto_en_centavos
from app.crud import crud_pago, crud_servicio, crud_solicitud
from app.models.usuario import Usuario
from app.schemas.pago import DatosCheckoutWompi
from app.schemas.solicitud import Solicitud, SolicitudCrear

router = APIRouter(tags=["solicitudes"])


def _a_solicitud(s) -> Solicitud:
    return Solicitud(
        id=s.id,
        id_servicio=s.id_servicio,
        titulo_servicio=s.servicio.titulo if s.servicio else "",
        nombre_cliente=f"{s.cliente.nombre} {s.cliente.apellido}".strip() if s.cliente else "",
        correo_cliente=s.cliente.correo if s.cliente else "",
        celular_cliente=s.cliente.celular if s.cliente else "",
        mensaje=s.mensaje,
        atendida=s.atendida,
        completada=s.completada,
        estado_pago=s.pago.estado if s.pago else None,
        monto_pago=s.pago.monto if s.pago else None,
        creado_en=s.creado_en,
    )


@router.post(
    "/servicios/{id_servicio}/solicitar",
    response_model=Solicitud,
    status_code=status.HTTP_201_CREATED,
)
def solicitar_servicio(
    id_servicio: int,
    data: SolicitudCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Cualquier usuario logueado (Cliente o Trabajador actuando como
    cliente) puede solicitar un servicio aprobado. El trabajador dueño ve
    los datos de contacto de quien lo solicita en su panel."""
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None or servicio.estado != "aprobado":
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    if servicio.id_usuario == usuario.id:
        raise HTTPException(status_code=400, detail="No puedes solicitar tu propio servicio")

    solicitud = crud_solicitud.crear(db, data, id_cliente=usuario.id, id_servicio=id_servicio)
    return _a_solicitud(crud_solicitud.obtener(db, solicitud.id))


@router.get("/solicitudes/mias", response_model=list[Solicitud])
def mis_solicitudes_recibidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Solicitudes que le han llegado a los servicios del usuario logueado."""
    return [_a_solicitud(s) for s in crud_solicitud.listar_recibidas_por_trabajador(db, usuario.id)]


@router.get("/solicitudes/mias-hechas", response_model=list[Solicitud])
def mis_solicitudes_hechas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Solicitudes que el usuario logueado ha hecho como cliente, para ver
    su estado y, si el trabajador ya la marcó como completada, pagar."""
    return [_a_solicitud(s) for s in crud_solicitud.listar_hechas_por_cliente(db, usuario.id)]


@router.patch("/solicitudes/{id_solicitud}/atender", response_model=Solicitud)
def atender_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    solicitud = crud_solicitud.obtener(db, id_solicitud)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.servicio.id_usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Esta solicitud no es tuya")
    return _a_solicitud(crud_solicitud.marcar_atendida(db, solicitud))


@router.patch("/solicitudes/{id_solicitud}/completar", response_model=Solicitud)
def completar_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """El trabajador confirma que ya hizo el trabajo. Esto crea el cobro
    (Pago) por el precio_desde del servicio; el trabajador no puede elegir
    ni cambiar ese monto. El cliente ve el estado en 'Mis solicitudes' y
    paga desde ahí con Wompi."""
    solicitud = crud_solicitud.obtener(db, id_solicitud)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.servicio.id_usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Esta solicitud no es tuya")
    if solicitud.completada:
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue marcada como completada")

    solicitud = crud_solicitud.marcar_completada(db, solicitud)

    if crud_pago.obtener_por_solicitud(db, solicitud.id) is None:
        precio = solicitud.servicio.precio_desde or 0.0
        crud_pago.crear(db, id_solicitud=solicitud.id, monto=precio)
        solicitud = crud_solicitud.obtener(db, solicitud.id)

    return _a_solicitud(solicitud)


@router.get("/solicitudes/{id_solicitud}/pago", response_model=DatosCheckoutWompi)
def obtener_datos_de_pago(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Lo que el cliente necesita para abrir el Web Checkout de Wompi y
    pagar el servicio ya completado."""
    solicitud = crud_solicitud.obtener(db, id_solicitud)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_cliente != usuario.id:
        raise HTTPException(status_code=403, detail="Esta solicitud no es tuya")
    if not solicitud.completada or solicitud.pago is None:
        raise HTTPException(
            status_code=400, detail="El trabajador todavía no marcó este servicio como completado"
        )
    if not settings.wompi_llave_publica or not settings.wompi_secreto_integridad:
        raise HTTPException(
            status_code=503,
            detail="Los pagos todavía no están configurados. Contacta al administrador.",
        )

    pago = crud_pago.regenerar_referencia_si_fallo(db, solicitud.pago)
    centavos = monto_en_centavos(pago.monto)
    return DatosCheckoutWompi(
        llave_publica=settings.wompi_llave_publica,
        referencia=pago.referencia,
        monto_en_centavos=centavos,
        moneda=pago.moneda,
        firma_integridad=firma_integridad(
            referencia=pago.referencia, monto_en_centavos=centavos, moneda=pago.moneda
        ),
    )
