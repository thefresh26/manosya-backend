from sqlalchemy.orm import Session

from app.models.error_log import ErrorLog


def registrar(
    db: Session,
    *,
    metodo: str,
    ruta: str,
    tipo_error: str,
    mensaje: str,
    traceback: str | None,
) -> None:
    """Guarda un error no controlado. A propósito no deja que una falla al
    guardar (por ejemplo la propia base de datos caída) tumbe la petición
    original: quien llama debe envolver esto en su propio try/except."""
    entrada = ErrorLog(
        metodo=metodo,
        ruta=ruta,
        tipo_error=tipo_error,
        mensaje=mensaje[:2000],
        traceback=traceback[:8000] if traceback else None,
    )
    db.add(entrada)
    db.commit()


def listar_recientes(db: Session, limite: int = 100) -> list[ErrorLog]:
    return (
        db.query(ErrorLog)
        .order_by(ErrorLog.creado_en.desc())
        .limit(limite)
        .all()
    )


def contar_no_vistos(db: Session) -> int:
    return db.query(ErrorLog).filter(ErrorLog.visto.is_(False)).count()


def obtener(db: Session, id_error: int) -> ErrorLog | None:
    return db.query(ErrorLog).filter(ErrorLog.id == id_error).first()


def marcar_visto(db: Session, error: ErrorLog) -> ErrorLog:
    error.visto = True
    db.commit()
    db.refresh(error)
    return error


def marcar_todos_vistos(db: Session) -> int:
    actualizados = db.query(ErrorLog).filter(ErrorLog.visto.is_(False)).update({"visto": True})
    db.commit()
    return actualizados
