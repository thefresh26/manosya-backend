from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import calificacion, modulo, modulo_por_rol, rol, servicio, usuario  # noqa: F401
from app.models.categoria import Categoria

app = FastAPI(title="Plataforma de Servicios - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fotos de perfil subidas en el registro (ver app/core/uploads.py).
DIRECTORIO_STATIC = Path(__file__).resolve().parent / "static"
DIRECTORIO_STATIC.mkdir(parents=True, exist_ok=True)
(DIRECTORIO_STATIC / "fotos").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=DIRECTORIO_STATIC), name="static")


CATEGORIAS_INICIALES = [
    {"nombre": "Plomería", "icono": "plomeria", "descripcion": "Reparación de fugas, instalaciones y destape de tuberías"},
    {"nombre": "Electricidad", "icono": "electricidad", "descripcion": "Instalaciones y reparaciones eléctricas residenciales"},
    {"nombre": "Aseo y limpieza", "icono": "limpieza", "descripcion": "Limpieza de hogares, apartamentos y oficinas"},
    {"nombre": "Jardinería", "icono": "jardineria", "descripcion": "Mantenimiento de jardines y zonas verdes"},
    {"nombre": "Pintura", "icono": "pintura", "descripcion": "Pintura de interiores y exteriores"},
    {"nombre": "Mudanzas", "icono": "mudanzas", "descripcion": "Transporte y mudanzas de hogares y oficinas"},
]


@app.on_event("startup")
def crear_tablas():
    Base.metadata.create_all(bind=engine)
    # Migración manual y minima (sin Alembic): agrega la columna `activo`
    # a usuario si la tabla ya existia de antes de que existiera este campo.
    # Necesaria para el panel de admin (desactivar cuentas en vez de borrarlas).
    with engine.begin() as conexion:
        conexion.execute(
            text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE")
        )

    # Siembra las categorías base la primera vez que arranca el backend,
    # para que el frontend no dependa de datos de ejemplo (contenido.js).
    # No se repite si ya existen (evita duplicados en cada reinicio).
    db = SessionLocal()
    try:
        if db.query(Categoria).count() == 0:
            for datos in CATEGORIAS_INICIALES:
                db.add(Categoria(**datos))
            db.commit()
    finally:
        db.close()


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"status": "ok", "mensaje": "API de la plataforma de servicios"}
