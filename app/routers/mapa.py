from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.localizacion import Localizacion
from app.services.localizacion_service import LocalizacionService

router = APIRouter(prefix="/mapa", tags=["mapa"])

RADIO_MAXIMO_METROS = 50_000


class PuntoMapa(BaseModel):
    id: str
    reporte_id: str
    tipo_reporte: str
    nombre_mascota: str | None
    latitud: float
    longitud: float
    direccion_aproximada: str | None
    descripcion: str | None
    codigo_chip: str | None
    foto_url: str | None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

    @classmethod
    def from_orm_safe(cls, obj: Localizacion) -> "PuntoMapa":
        return cls(
            id=str(obj.id),
            reporte_id=str(obj.reporte_id),
            tipo_reporte=obj.tipo_reporte,
            nombre_mascota=obj.nombre_mascota,
            latitud=float(obj.latitud),
            longitud=float(obj.longitud),
            direccion_aproximada=obj.direccion_aproximada,
            descripcion=obj.descripcion,
            codigo_chip=obj.codigo_chip,
            foto_url=obj.foto_url,
        )


@router.get("/puntos", response_model=list[PuntoMapa])
def obtener_puntos(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radio: float = Query(5000, gt=0, le=RADIO_MAXIMO_METROS),
    db: Session = Depends(get_db),
):
    """Retorna hasta 300 reportes EN_BUSQUEDA dentro del radio dado."""
    service = LocalizacionService(db)
    puntos = service.buscar_en_radio(latitud=lat, longitud=lng, radio_metros=radio)
    return [PuntoMapa.from_orm_safe(p) for p in puntos]


@router.get("/puntos/todos", response_model=list[PuntoMapa])
def obtener_todos_los_puntos(db: Session = Depends(get_db)):
    """Solo para testing — retorna todos los registros activos sin filtro de radio."""
    puntos = db.query(Localizacion).filter(Localizacion.activo == True).all()
    return [PuntoMapa.from_orm_safe(p) for p in puntos]
