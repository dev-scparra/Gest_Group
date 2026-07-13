import pytest

from src.algebra.grupo_gestos import Gesto
from src.clasificador.gestos import (
    PULGAR_MCP,
    PULGAR_PUNTA,
    clasificar_gesto,
    dedos_levantados,
)
from tests.fixtures_landmarks import (
    generar_landmark_ambiguo_menique,
    generar_landmark_dos_dedos,
    generar_landmark_mano_abierta,
    generar_landmark_puno,
    generar_landmark_pulgar,
    generar_landmark_un_dedo,
)

# Los tres gestos que dependen del pulgar (G3, G4, G5) se prueban con LAS DOS manos.
# Contra el clasificador anterior (comparacion cruda `x_punta < x_mcp`), la variante
# "Left" daba G4->E, G5->G3 y G3->G5: los gestos no fallaban, se intercambiaban.
AMBAS_MANOS = ["Right", "Left"]


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_mano_cerrada_es_g3(lateralidad):
    assert clasificar_gesto(generar_landmark_puno(lateralidad)) == Gesto.G3


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_mano_abierta_es_g4(lateralidad):
    assert clasificar_gesto(generar_landmark_mano_abierta(lateralidad)) == Gesto.G4


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_solo_pulgar_es_g5(lateralidad):
    assert clasificar_gesto(generar_landmark_pulgar(lateralidad)) == Gesto.G5


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_indice_levantado_es_g1(lateralidad):
    assert clasificar_gesto(generar_landmark_un_dedo(lateralidad)) == Gesto.G1


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_indice_medio_levantados_es_g2(lateralidad):
    assert clasificar_gesto(generar_landmark_dos_dedos(lateralidad)) == Gesto.G2


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_combinacion_ambigua_es_e(lateralidad):
    assert clasificar_gesto(generar_landmark_ambiguo_menique(lateralidad)) == Gesto.E


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_dedos_levantados_orden_pulgar_indice_medio_anular_menique(lateralidad):
    assert dedos_levantados(generar_landmark_mano_abierta(lateralidad)) == [True] * 5
    assert dedos_levantados(generar_landmark_puno(lateralidad)) == [False] * 5


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_puno_con_pulgar_plegado_no_se_confunde_con_g5(lateralidad):
    """PUL-FR-005: en un puno natural el pulgar se pliega sobre los dedos y su punta
    queda casi encima de su MCP. Sin margen, el signo de la comparacion lo decide el
    ruido y G3 (pausa/play) se confunde con G5 (pista anterior). El umbral relativo
    al ancho de la palma exige que el pulgar se aparte de verdad."""
    coords = generar_landmark_puno(lateralidad)
    x_mcp, y_mcp, _ = coords[PULGAR_MCP]
    # Punta apenas apartada hacia el lado del pulgar: por debajo del umbral.
    desplazamiento = 0.02 if lateralidad == "Right" else -0.02
    coords[PULGAR_PUNTA] = (x_mcp + desplazamiento, y_mcp, 0.0)

    assert clasificar_gesto(coords) == Gesto.G3


@pytest.mark.parametrize("lateralidad", AMBAS_MANOS)
def test_palma_degenerada_no_lanza_y_degrada_a_pulgar_abajo(lateralidad):
    """Landmarks corruptos (todos los MCP en el mismo punto): el eje de la palma es
    indefinido. No se adivina un signo — el pulgar cuenta como abajo (PUL-FR-006)."""
    coords = [(0.5, 0.5, 0.0)] * 21

    assert dedos_levantados(coords)[0] is False
    assert clasificar_gesto(coords) == Gesto.G3  # sin excepcion
