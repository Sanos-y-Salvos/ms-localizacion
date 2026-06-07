import pytest
from unittest.mock import MagicMock
from app.repositories.localizacion_repository import LocalizacionRepository
from app.services.localizacion_service import LocalizacionService
from app.models.localizacion import Localizacion


def make_localizacion(**kwargs) -> Localizacion:
    """Crea una instancia de Localizacion con valores por defecto."""
    loc = Localizacion()
    loc.id = kwargs.get("id", "test-uuid-1234")
    loc.reporte_id = kwargs.get("reporte_id", "reporte-uuid-5678")
    loc.tipo_reporte = kwargs.get("tipo_reporte", "PERDIDA")
    loc.estado_reporte = kwargs.get("estado_reporte", "EN_BUSQUEDA")
    loc.nombre_mascota = kwargs.get("nombre_mascota", "Firulais")
    loc.latitud = kwargs.get("latitud", -36.826992)
    loc.longitud = kwargs.get("longitud", -73.049771)
    loc.ubicacion = None
    loc.direccion_aproximada = kwargs.get("direccion_aproximada", None)
    loc.descripcion_lugar = kwargs.get("descripcion_lugar", None)
    loc.activo = kwargs.get("activo", True)
    return loc


@pytest.fixture
def mock_repo():
    return MagicMock(spec=LocalizacionRepository)


@pytest.fixture
def service(mock_repo):
    s = LocalizacionService.__new__(LocalizacionService)
    s.repo = mock_repo
    return s
