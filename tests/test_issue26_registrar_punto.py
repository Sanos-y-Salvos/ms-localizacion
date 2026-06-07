"""
Pruebas unitarias — Issue #26
Registrar punto de interés desde evento RabbitMQ (mascota.reporte.creado)

Criterios de aceptación:
- Consumidor suscrito a mascota.reporte.creado
- Crea un POINT(lng, lat) en PostGIS con los datos del evento
- Si el evento no trae coordenadas válidas, lo descarta y loguea el error
"""
import pytest
from tests.conftest import make_localizacion


class TestRegistrarDesdeEvento:

    def test_registra_localizacion_con_datos_validos(self, service, mock_repo):
        """Crea la localización cuando el evento trae coordenadas válidas."""
        mock_repo.buscar_por_reporte_id.return_value = None
        mock_repo.crear.return_value = make_localizacion()

        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud=-36.826992,
            longitud=-73.049771,
            nombre_mascota="Firulais",
        )

        mock_repo.crear.assert_called_once()
        args = mock_repo.crear.call_args.kwargs
        assert args["reporte_id"] == "reporte-uuid-5678"
        assert args["tipo_reporte"] == "PERDIDA"
        assert args["latitud"] == -36.826992
        assert args["longitud"] == -73.049771
        assert args["nombre_mascota"] == "Firulais"

    def test_descarta_si_coordenadas_ninguna(self, service, mock_repo):
        """Descarta el evento si latitud y longitud son None."""
        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud=None,
            longitud=None,
        )
        mock_repo.crear.assert_not_called()

    def test_descarta_si_latitud_fuera_de_rango(self, service, mock_repo):
        """Descarta el evento si latitud está fuera del rango válido (-90 a 90)."""
        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud=200.0,
            longitud=-73.049771,
        )
        mock_repo.crear.assert_not_called()

    def test_descarta_si_longitud_fuera_de_rango(self, service, mock_repo):
        """Descarta el evento si longitud está fuera del rango válido (-180 a 180)."""
        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud=-36.826992,
            longitud=999.0,
        )
        mock_repo.crear.assert_not_called()

    def test_descarta_si_coordenadas_no_son_numericas(self, service, mock_repo):
        """Descarta el evento si las coordenadas no son numéricas."""
        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud="no-es-numero",
            longitud=-73.049771,
        )
        mock_repo.crear.assert_not_called()

    def test_idempotencia_no_duplica_localizacion(self, service, mock_repo):
        """No crea una segunda localización si el reporte ya tiene una."""
        mock_repo.buscar_por_reporte_id.return_value = make_localizacion()

        service.registrar_desde_evento(
            reporte_id="reporte-uuid-5678",
            tipo_reporte="PERDIDA",
            latitud=-36.826992,
            longitud=-73.049771,
        )

        mock_repo.crear.assert_not_called()
