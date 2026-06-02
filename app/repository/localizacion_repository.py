from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from sqlalchemy.orm import Session

from app.models.localizacion import Localizacion


class LocalizacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def crear(
        self,
        reporte_id: str,
        tipo_reporte: str,
        latitud: float,
        longitud: float,
        nombre_mascota: str | None = None,
        descripcion_lugar: str | None = None,
        direccion_aproximada: str | None = None,
    ) -> Localizacion:
        loc = Localizacion(
            reporte_id=reporte_id,
            tipo_reporte=tipo_reporte,
            estado_reporte="EN_BUSQUEDA",
            latitud=latitud,
            longitud=longitud,
            ubicacion=ST_SetSRID(ST_MakePoint(longitud, latitud), 4326),
            nombre_mascota=nombre_mascota,
            descripcion_lugar=descripcion_lugar,
            direccion_aproximada=direccion_aproximada,
            activo=True,
        )
        self.db.add(loc)
        self.db.commit()
        self.db.refresh(loc)
        return loc

    def buscar_por_reporte_id(self, reporte_id: str) -> Localizacion | None:
        return (
            self.db.query(Localizacion)
            .filter(Localizacion.reporte_id == reporte_id)
            .first()
        )
