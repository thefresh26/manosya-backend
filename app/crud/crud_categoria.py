from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCrear


def listar(db: Session) -> list[Categoria]:
    return db.query(Categoria).order_by(Categoria.nombre).all()


def obtener(db: Session, id_categoria: int) -> Categoria | None:
    return db.query(Categoria).filter(Categoria.id == id_categoria).first()


def crear(db: Session, data: CategoriaCrear) -> Categoria:
    categoria = Categoria(**data.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria
