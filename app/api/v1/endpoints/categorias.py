from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_categoria
from app.schemas.categoria import Categoria

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[Categoria])
def listar_categorias(db: Session = Depends(get_db)):
    return crud_categoria.listar(db)
