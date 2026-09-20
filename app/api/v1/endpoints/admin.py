from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.api.deps import get_db, requerir_administrador
from app.crud import crud_usuario
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioAdmin

router = APIRouter(prefix="/admin", tags=["admin"])


def _a_usuario_admin(usuario: Usuario) -> UsuarioAdmin:
    return UsuarioAdmin(
        id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        cedula=usuario.cedula,
        celular=usuario.celular,
        ciudad=usuario.ciudad,
        direccion=usuario.direccion,
        activo=usuario.activo,
        id_rol=usuario.id_rol,
        nombre_rol=usuario.rol.nombre if usuario.rol else "",
    )


@router.get("/usuarios", response_model=list[UsuarioAdmin])
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Lista completa de personas registradas (cualquier rol). Solo accesible
    con una sesión de un usuario con rol Administrador."""
    return [_a_usuario_admin(u) for u in crud_usuario.listar_todos(db)]


@router.patch("/usuarios/{id_usuario}/desactivar", response_model=UsuarioAdmin)
def desactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_administrador),
):
    """"Desecha" a una persona: desactiva su cuenta (no la borra), para que
    deje de aparecer en el mapa público y no pueda iniciar sesión."""
    if id_usuario == admin.id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta de administrador")
    usuario = crud_usuario.obtener(db, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _a_usuario_admin(crud_usuario.desactivar(db, usuario))


@router.patch("/usuarios/{id_usuario}/reactivar", response_model=UsuarioAdmin)
def reactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Revierte una desactivación, por si fue un error."""
    usuario = crud_usuario.obtener(db, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _a_usuario_admin(crud_usuario.reactivar(db, usuario))
