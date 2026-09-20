from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_usuario
from app.schemas.usuario import TrabajadorDestacado, TrabajadorMapa

router = APIRouter(prefix="/trabajadores", tags=["trabajadores"])


@router.get("/mapa", response_model=list[TrabajadorMapa])
def mapa_trabajadores(db: Session = Depends(get_db)):
    """Trabajadores registrados con coordenadas, para pintarlos en el mapa
    público de la landing page. No incluye correo, cédula ni celular."""
    return crud_usuario.listar_trabajadores_con_ubicacion(db)


@router.get("/destacados", response_model=list[TrabajadorDestacado])
def trabajadores_destacados(db: Session = Depends(get_db)):
    """Trabajadores con al menos un servicio activo publicado, para la
    sección "Trabajadores destacados" de la landing page. Devuelve una
    lista vacía mientras nadie haya publicado servicios todavía."""
    return crud_usuario.listar_destacados(db)
