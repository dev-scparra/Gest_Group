from src.algebra.grupo_gestos import Gesto
from src.clasificador.estabilizador import EstabilizadorGesto


def test_no_confirma_antes_de_frames_estables():
    est = EstabilizadorGesto(frames_estables=10)
    for _ in range(9):
        assert est.actualizar(Gesto.G1) is None


def test_confirma_en_el_frame_numero_frames_estables():
    est = EstabilizadorGesto(frames_estables=10)
    for _ in range(9):
        est.actualizar(Gesto.G1)
    assert est.actualizar(Gesto.G1) == Gesto.G1


def test_disparo_unico_no_se_repite_sosteniendo_el_gesto():
    est = EstabilizadorGesto(frames_estables=10)
    for _ in range(9):
        est.actualizar(Gesto.G1)
    assert est.actualizar(Gesto.G1) == Gesto.G1
    for _ in range(5):
        assert est.actualizar(Gesto.G1) is None


def test_reinicio_al_pasar_por_otro_gesto_permite_reconfirmar():
    est = EstabilizadorGesto(frames_estables=10)
    for _ in range(9):
        est.actualizar(Gesto.G1)
    assert est.actualizar(Gesto.G1) == Gesto.G1

    est.actualizar(Gesto.E)
    for _ in range(9):
        assert est.actualizar(Gesto.G1) is None
    assert est.actualizar(Gesto.G1) == Gesto.G1


def test_reset_reinicia_estado_al_perder_y_recuperar_mano():
    est = EstabilizadorGesto(frames_estables=10)
    for _ in range(9):
        est.actualizar(Gesto.G1)
    assert est.actualizar(Gesto.G1) == Gesto.G1

    est.reset()
    for _ in range(9):
        assert est.actualizar(Gesto.G1) is None
    assert est.actualizar(Gesto.G1) == Gesto.G1
