"""Tests de CapturadorCombo (spec 015). Frame-driven y puro: se alimenta un gesto por
llamada, sin camara ni reloj — determinista."""

from src.algebra.grupo_gestos import Gesto, operacion_G
from src.clasificador.capturador_combo import CapturadorCombo, FaseCombo


def _alimentar(cap, gesto, n):
    """Alimenta `n` frames del mismo gesto; devuelve la lista de estados."""
    return [cap.actualizar(gesto) for _ in range(n)]


def test_camino_feliz_dispara_la_composicion_una_sola_vez():
    """G3 (5 frames) -> espera -> G1 (5 frames) => phi(G3 o G1). disparar en un solo frame."""
    cap = CapturadorCombo(frames_captura=5, frames_espera=3, frames_resultado=4)

    g1 = _alimentar(cap, Gesto.G3, 5)
    assert g1[-1].fase == FaseCombo.ESPERA
    assert g1[-1].g1 == Gesto.G3
    assert all(e.disparar is None for e in g1)

    espera = _alimentar(cap, Gesto.E, 3)  # el gesto en la espera se ignora
    assert espera[-1].fase == FaseCombo.CAPTURANDO_G2

    g2 = _alimentar(cap, Gesto.G1, 5)
    assert g2[-1].fase == FaseCombo.RESULTADO
    assert g2[-1].g2 == Gesto.G1
    assert g2[-1].compuesto == operacion_G(Gesto.G3, Gesto.G1)  # 3+1=4 -> G4
    assert g2[-1].disparar == Gesto.G4

    # borde: exactamente un frame dispara en toda la captura del gesto 2
    assert sum(e.disparar is not None for e in g1 + espera + g2) == 1


def test_votacion_por_mayoria_ignora_frames_de_transicion():
    """Unos pocos frames de otro gesto (transicion/ruido) no cambian el ganador."""
    cap = CapturadorCombo(frames_captura=5, frames_espera=1, frames_resultado=1)

    e = None
    for g in [Gesto.G3, Gesto.G3, Gesto.G3, Gesto.E, Gesto.G1]:  # G3 mayoria (3 de 5)
        e = cap.actualizar(g)

    assert e.fase == FaseCombo.ESPERA
    assert e.g1 == Gesto.G3


def test_mayoria_reposo_cancela_el_combo():
    """Si la ventana la gana E (el usuario no sostuvo un gesto), se cancela sin disparar."""
    cap = CapturadorCombo(frames_captura=5, frames_espera=1, frames_resultado=1)

    e = None
    for g in [Gesto.G3, Gesto.E, Gesto.E, Gesto.E, Gesto.E]:  # E mayoria (4 de 5)
        e = cap.actualizar(g)

    assert e.fase == FaseCombo.INACTIVO
    assert e.disparar is None
    assert e.g1 is None  # el estado se limpio


def test_tras_un_combo_exige_reposo_antes_de_armar_otro():
    """Evita encadenar combos sin querer: tras RESULTADO hay que ver E para re-armar."""
    cap = CapturadorCombo(frames_captura=2, frames_espera=1, frames_resultado=2)

    disparos = []
    # combo completo: G3 o G1 = G4
    for g in [Gesto.G3, Gesto.G3, Gesto.E, Gesto.G1, Gesto.G1]:
        disparos.append(cap.actualizar(g).disparar)
    assert Gesto.G4 in disparos

    # se agota el RESULTADO sosteniendo G1 (2 frames)
    cap.actualizar(Gesto.G1)
    e = cap.actualizar(Gesto.G1)
    assert e.fase == FaseCombo.INACTIVO

    # sigue con la mano en G1 (no-E): NO arranca combo nuevo porque no esta armado
    e = cap.actualizar(Gesto.G1)
    assert e.fase == FaseCombo.INACTIVO

    # baja la mano (E) -> re-arma -> el proximo gesto arranca un combo
    cap.actualizar(Gesto.E)
    e = cap.actualizar(Gesto.G2)
    assert e.fase == FaseCombo.CAPTURANDO_G1


def test_primer_gesto_de_la_sesion_arranca_sin_reposo_previo():
    """El capturador nace armado: el primer gesto no necesita un E antes."""
    cap = CapturadorCombo(frames_captura=3, frames_espera=1, frames_resultado=1)

    e = cap.actualizar(Gesto.G2)

    assert e.fase == FaseCombo.CAPTURANDO_G1


def test_cuenta_regresiva_y_lider_durante_la_captura():
    """El HUD necesita frames_restantes decreciente y el lider de la votacion en curso."""
    cap = CapturadorCombo(frames_captura=5, frames_espera=1, frames_resultado=1)

    e1 = cap.actualizar(Gesto.G3)
    assert e1.fase == FaseCombo.CAPTURANDO_G1
    assert e1.frames_restantes == 4  # 5 - 1
    assert e1.frames_total_fase == 5
    assert e1.lider == Gesto.G3
    assert (Gesto.G3, 1) in e1.conteo

    e2 = cap.actualizar(Gesto.G3)
    assert e2.frames_restantes == 3
    assert e2.lider == Gesto.G3


def test_espera_no_consume_el_gesto_ni_dispara():
    """La fase de espera solo cuenta frames; no vota ni dispara (deja transicionar)."""
    cap = CapturadorCombo(frames_captura=1, frames_espera=4, frames_resultado=1)

    cap.actualizar(Gesto.G3)  # 1 frame basta para cerrar g1 -> ESPERA
    espera = _alimentar(cap, Gesto.G1, 3)  # dentro de la espera aun

    assert all(e.fase == FaseCombo.ESPERA for e in espera)
    assert all(e.disparar is None for e in espera)
    assert all(e.g2 is None for e in espera)


def test_ventanas_configurables():
    """CMB/spec 015: los tamanos de ventana no estan hardcodeados."""
    cap = CapturadorCombo(frames_captura=3, frames_espera=2, frames_resultado=2)

    corto = _alimentar(cap, Gesto.G1, 3)  # 3 frames cierran g1
    assert corto[-1].fase == FaseCombo.ESPERA
    assert corto[-1].g1 == Gesto.G1


def test_reset_desarma_y_limpia():
    cap = CapturadorCombo(frames_captura=5)
    cap.actualizar(Gesto.G3)  # entra a CAPTURANDO_G1

    cap.reset()
    e = cap.actualizar(Gesto.G3)  # no-E pero desarmado -> se ignora

    assert e.fase == FaseCombo.INACTIVO
    assert e.g1 is None
