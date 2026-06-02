import uuid
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class Localizacion(Base):
    __tablename__ = "localizaciones"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    reporte_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    tipo_reporte: Mapped[str] = mapped_column(String(20), nullable=False)  # PERDIDA | ENCONTRADA
    estado_reporte: Mapped[str] = mapped_column(String(20), nullable=False, default="EN_BUSQUEDA")
    nombre_mascota: Mapped[str | None] = mapped_column(String(100), nullable=True)

    latitud: Mapped[float] = mapped_column(nullable=False)
    longitud: Mapped[float] = mapped_column(nullable=False)

    # Columna geográfica PostGIS — POINT(lng lat), SRID 4326
    ubicacion: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )

    direccion_aproximada: Mapped[str | None] = mapped_column(nullable=True)
    descripcion_lugar: Mapped[str | None] = mapped_column(nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
