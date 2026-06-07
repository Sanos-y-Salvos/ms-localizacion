"""
Pruebas unitarias — Issue #28
Endpoint de consulta de puntos en mapa

Criterios de aceptación:
- GET /mapa/puntos?lat=X&lng=Y&radio=Z retorna puntos dentro del radio dado
- Usa ST_DWithin de PostGIS para la consulta espacial
- Retorna máximo 300 marcadores por consulta
- Solo incluye reportes en estado EN_BUSQUEDA
"""
import pytest
from tests.conftest import make_localizacion


class TestBuscarEnRadio:

    def test_retorna_puntos_dentro_del_radio(self, service, mock_repo):
        """Retorna localizaciones cuando hay puntos dentro del radio."""
        loc1 = make_localizacion(reporte_id="r1", nombre_mascota="Firulais")
        loc2 = make_localizacion(reporte_id="r2", nombre_mascota="Cher")
        mock_repo.buscar_en_radio.return_value = [loc1, loc2]

        resultado = service.buscar_en_radio(
            latitud=-36.826992,
            longitud=-73.049771,
            radio_metros=5000,
        )

        assert len(resultado) == 2
        mock_repo.buscar_en_radio.assert_called_once_with(
            -36.826992, -73.049771, 5000
        )

    def test_retorna_lista_vacia_si_no_hay_puntos(self, service, mock_repo):
        """Retorna lista vacía si no hay reportes en el radio dado."""
        mock_repo.buscar_en_radio.return_value = []

        resultado = service.buscar_en_radio(
            latitud=-36.826992,
            longitud=-73.049771,
            radio_metros=100,
        )

        assert resultado == []

    def test_radio_maximo_50km(self, service, mock_repo):
        """Lanza error si el radio supera los 50 km."""
        with pytest.raises(Exception):
            service.buscar_en_radio(
                latitud=-36.826992,
                longitud=-73.049771,
                radio_metros=50001,
            )
        mock_repo.buscar_en_radio.assert_not_called()

    def test_radio_exactamente_50km_es_valido(self, service, mock_repo):
        """Acepta radio de exactamente 50 000 metros."""
        mock_repo.buscar_en_radio.return_value = []

        service.buscar_en_radio(
            latitud=-36.826992,
            longitud=-73.049771,
            radio_metros=50000,
        )

        mock_repo.buscar_en_radio.assert_called_once()

    def test_limite_300_marcadores_se_aplica_en_repositorio(self, service, mock_repo):
        """El límite de 300 marcadores se aplica en la capa de repositorio."""
        mock_repo.buscar_en_radio.return_value = [make_localizacion() for _ in range(300)]

        resultado = service.buscar_en_radio(
            latitud=-36.826992,
            longitud=-73.049771,
            radio_metros=5000,
        )

        assert len(resultado) == 300
