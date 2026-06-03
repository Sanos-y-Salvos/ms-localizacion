from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
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
    descripcion_lugar: str | None

    model_config = {"from_attributes": True}


@router.get("/puntos", response_model=list[PuntoMapa])
def obtener_puntos(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del centro"),
    lng: float = Query(..., ge=-180, le=180, description="Longitud del centro"),
    radio: float = Query(5000, gt=0, le=RADIO_MAXIMO_METROS, description="Radio en metros (máx 50 000)"),
    db: Session = Depends(get_db),
):
    """
    Retorna hasta 300 reportes EN_BUSQUEDA dentro del radio dado.
    Usa ST_DWithin de PostGIS con índice GIST.
    """
    service = LocalizacionService(db)
    return service.buscar_en_radio(latitud=lat, longitud=lng, radio_metros=radio)
