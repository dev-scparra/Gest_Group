from src.algebra.grupo_gestos import Gesto
from src.clasificador.gestos import clasificar_gesto, dedos_levantados
from tests.fixtures_landmarks import (
    generar_landmark_ambiguo_menique,
    generar_landmark_dos_dedos,
    generar_landmark_mano_abierta,
    generar_landmark_puno,
    generar_landmark_pulgar,
    generar_landmark_un_dedo,
)


def test_mano_cerrada_es_g3():
    assert clasificar_gesto(generar_landmark_puno()) == Gesto.G3


def test_indice_levantado_es_g1():
    assert clasificar_gesto(generar_landmark_un_dedo()) == Gesto.G1


def test_indice_medio_levantados_es_g2():
    assert clasificar_gesto(generar_landmark_dos_dedos()) == Gesto.G2


def test_mano_abierta_es_g4():
    assert clasificar_gesto(generar_landmark_mano_abierta()) == Gesto.G4


def test_solo_pulgar_es_g5():
    assert clasificar_gesto(generar_landmark_pulgar()) == Gesto.G5


def test_combinacion_ambigua_es_e():
    assert clasificar_gesto(generar_landmark_ambiguo_menique()) == Gesto.E


def test_dedos_levantados_orden_pulgar_indice_medio_anular_menique():
    levantados = dedos_levantados(generar_landmark_mano_abierta())
    assert levantados == [True, True, True, True, True]
    levantados = dedos_levantados(generar_landmark_puno())
    assert levantados == [False, False, False, False, False]
