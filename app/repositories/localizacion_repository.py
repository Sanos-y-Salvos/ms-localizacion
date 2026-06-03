from geoalchemy2.functions import ST_SetSRID, ST_MakePoint, ST_DWithin
from sqlalchemy.orm import Session

from app.models.localizacion import Localizacion

LIMITE_MARCADORES = 300


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

    def buscar_en_radio(
        self,
        latitud: float,
        longitud: float,
        radio_metros: float,
    ) -> list[Localizacion]:
        """
        Retorna hasta 300 puntos EN_BUSQUEDA dentro del radio dado.
        Usa ST_DWithin de PostGIS con índice GIST — criterio issue #28.
        """
        punto = ST_SetSRID(ST_MakePoint(longitud, latitud), 4326)
        return (
            self.db.query(Localizacion)
            .filter(
                Localizacion.activo == True,
                Localizacion.estado_reporte == "EN_BUSQUEDA",
                ST_DWithin(Localizacion.ubicacion, punto, radio_metros),
            )
            .limit(LIMITE_MARCADORES)
            .all()
        )

    def actualizar_coordenadas(
        self,
        loc: Localizacion,
        latitud: float,
        longitud: float,
        nombre_mascota: str | None = None,
        descripcion_lugar: str | None = None,
    ) -> Localizacion:
        loc.latitud = latitud
        loc.longitud = longitud
        loc.ubicacion = ST_SetSRID(ST_MakePoint(longitud, latitud), 4326)
        if nombre_mascota is not None:
            loc.nombre_mascota = nombre_mascota
        if descripcion_lugar is not None:
            loc.descripcion_lugar = descripcion_lugar
        self.db.commit()
        self.db.refresh(loc)
        return loc

    def actualizar_estado(self, loc: Localizacion, estado: str) -> Localizacion:
        loc.estado_reporte = estado
        if estado in ("RESUELTO", "OCULTO", "ABANDONADO"):
            loc.activo = False
        self.db.commit()
        self.db.refresh(loc)
        return loc

    def eliminar(self, loc: Localizacion) -> None:
        self.db.delete(loc)
        self.db.commit()
