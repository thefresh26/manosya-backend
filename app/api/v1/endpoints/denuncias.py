from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_usuario, get_db
from app.crud import crud_denuncia_trabajador, crud_reporte_formulario, crud_servicio, crud_usuario
from app.models.usuario import Usuario
from app.schemas.denuncia_trabajador import DenunciaTrabajador, DenunciaTrabajadorCrear
from app.schemas.reporte_formulario import ReporteFormulario, ReporteFormularioCrear

router = APIRouter(tags=["denuncias"])


def _a_denuncia_trabajador(d) -> DenunciaTrabajador:
    return DenunciaTrabajador(
        id=d.id,
        id_denunciante=d.id_denunciante,
        nombre_denunciante=f"{d.denunciante.nombre} {d.denunciante.apellido}".strip() if d.denunciante else "",
        id_trabajador=d.id_trabajador,
        nombre_trabajador=f"{d.trabajador.nombre} {d.trabajador.apellido}".strip() if d.trabajador else "",
        id_servicio=d.id_servicio,
        motivo=d.motivo,
        descripcion=d.descripcion,
        estado=d.estado,
        resolucion=d.resolucion,
        creado_en=d.creado_en,
    )


def _a_reporte_formulario(r) -> ReporteFormulario:
    return ReporteFormulario(
        id=r.id,
        id_trabajador=r.id_trabajador,
        nombre_trabajador=f"{r.trabajador.nombre} {r.trabajador.apellido}".strip() if r.trabajador else "",
        id_servicio=r.id_servicio,
        titulo_servicio=r.servicio.titulo if r.servicio else "",
        descripcion=r.descripcion,
        estado=r.estado,
        resolucion=r.resolucion,
        creado_en=r.creado_en,
    )


@router.post(
    "/trabajadores/{id_trabajador}/denuncias",
    response_model=DenunciaTrabajador,
    status_code=status.HTTP_201_CREATED,
)
def denunciar_trabajador(
    id_trabajador: int,
    data: DenunciaTrabajadorCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Un cliente (o un trabajador actuando como cliente) denuncia a un
    trabajador. Va a una bandeja del admin separada de los reportes de
    errores en formularios."""
    if id_trabajador == usuario.id:
        raise HTTPException(status_code=400, detail="No puedes denunciarte a ti mismo")
    trabajador = crud_usuario.obtener(db, id_trabajador)
    if trabajador is None or trabajador.rol is None or trabajador.rol.nombre != "Trabajador":
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    denuncia = crud_denuncia_trabajador.crear(db, data, id_denunciante=usuario.id, id_trabajador=id_trabajador)
    return _a_denuncia_trabajador(crud_denuncia_trabajador.obtener(db, denuncia.id))


@router.post(
    "/servicios/{id_servicio}/reportar-error",
    response_model=ReporteFormulario,
    status_code=status.HTTP_201_CREATED,
)
def reportar_error_formulario(
    id_servicio: int,
    data: ReporteFormularioCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Solo el dueño del formulario puede reportar un error en él."""
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    if servicio.id_usuario != usuario.id:
        raise HTTPException(status_code=403, detail="No puedes reportar un formulario que no es tuyo")

    reporte = crud_reporte_formulario.crear(db, data, id_trabajador=usuario.id, id_servicio=id_servicio)
    return _a_reporte_formulario(crud_reporte_formulario.obtener(db, reporte.id))
