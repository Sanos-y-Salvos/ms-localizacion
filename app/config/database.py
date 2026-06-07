from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.settings import settings


class Base(DeclarativeBase):
    pass


# El engine se crea lazy — solo cuando se llama get_engine()
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal


# Alias para compatibilidad con código existente
SessionLocal = type("SessionLocalProxy", (), {
    "__call__": staticmethod(lambda: get_session_local()())
})()


def get_db():
    """Dependencia FastAPI — provee sesión de BD y la cierra al terminar."""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def verificar_conexion() -> None:
    """Lanza excepción si la BD no está disponible. Usado en el bootstrap."""
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[DB] Conexión PostgreSQL+PostGIS establecida")
