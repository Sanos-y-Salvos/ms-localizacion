from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI — provee sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_conexion() -> None:
    """Lanza excepción si la BD no está disponible. Usado en el bootstrap."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[DB] Conexión PostgreSQL+PostGIS establecida")
