"""Tests del loop de orquestacion (009) — el unico modulo que no tenia suite propia.

Desde la spec 015 la interaccion es por COMBOS: `procesar_frame` alimenta el gesto
clasificado a `CapturadorCombo`, que vota por mayoria dos gestos y, al cerrar el segundo,
dispara phi(g1 o g2). Estos tests verifican ese cableado end-to-end sin camara.
"""

from unittest.mock import patch

import pytest

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto, operacion_G
from src.algebra.homomorfismo import Homomorfismo
from src.clasificador.capturador_combo import CapturadorCombo, FaseCombo
from src.main import EstadoPipeline, procesar_frame
from src.preprocesamiento.filtro_ema import FiltroEMA
from tests.fixtures_landmarks import generar_landmark_puno, generar_landmark_un_dedo

# Ventanas cortas para que los tests sean rapidos y faciles de contar.
FRAMES_CAPTURA = 5
FRAMES_ESPERA = 2
FRAMES_RESULTADO = 3
FRAME_RGB = None  # el detector esta doblado: nunca mira el frame


class DetectorFalso:
    """Doble de prueba de 004: devuelve los landmarks que se le pongan, o None."""

    def __init__(self, landmarks=None):
        self.landmarks = landmarks

    def procesar(self, _frame_rgb):
        return self.landmarks

    def landmarks_para_dibujo(self):
        return None


@pytest.fixture(name="piezas")
def fixture_piezas():
    return {
        # alpha ~1: filtro casi passthrough, para que el cambio de gesto se refleje de
        # inmediato y estos tests midan el cableado del combo, no la dinamica del EMA
        # (que se prueba en test_filtro_ema). Con el alpha real (0.3) el suavizado tarda
        # ~4 frames y una ventana de captura corta leeria el gesto anterior.
        "filtro": FiltroEMA(alpha=0.99),
        "capturador": CapturadorCombo(
            frames_captura=FRAMES_CAPTURA,
            frames_espera=FRAMES_ESPERA,
            frames_resultado=FRAMES_RESULTADO,
        ),
        "homomorfismo": Homomorfismo(),
        "estado": EstadoPipeline(),
    }


def _correr(detector, piezas, n_frames):
    """Corre n frames del pipeline y devuelve el (gesto, accion, estado_combo) del ultimo."""
    resultado = (None, None, None)
    for _ in range(n_frames):
        resultado = procesar_frame(
            FRAME_RGB,
            detector,
            piezas["filtro"],
            piezas["capturador"],
            piezas["homomorfismo"],
            piezas["estado"],
        )
    return resultado


@patch("src.main.ejecutar_accion")
def test_combo_de_dos_gestos_dispara_phi_de_la_composicion(mock_ejecutar, piezas):
    """INT-FR-010 / spec 015: capturar G1 y luego G3 dispara phi(G1 o G3) = phi(G4) = A4,
    una accion que ningun gesto por si solo produce aqui. Es la composicion o en vivo."""
    detector = DetectorFalso(generar_landmark_un_dedo())  # G1
    _correr(detector, piezas, FRAMES_CAPTURA)  # captura g1 = G1 -> ESPERA

    # Durante la espera el gesto se ignora; basta avanzar frames.
    _correr(detector, piezas, FRAMES_ESPERA)

    detector.landmarks = generar_landmark_puno()  # G3
    _, accion, estado_combo = _correr(detector, piezas, FRAMES_CAPTURA)

    assert estado_combo.compuesto == operacion_G(Gesto.G1, Gesto.G3)  # G4
    assert accion == Accion.A4  # phi(G4) = siguiente, ni A1 (G1) ni A3 (G3)


@patch("src.main.ejecutar_accion")
def test_ejecutar_accion_se_invoca_una_sola_vez_por_combo(mock_ejecutar, piezas):
    """INT-FR-005: `disparar` es un borde (un frame), asi que ejecutar_accion corre una
    sola vez aunque se sigan procesando frames en la fase de RESULTADO."""
    detector = DetectorFalso(generar_landmark_un_dedo())
    _correr(detector, piezas, FRAMES_CAPTURA + FRAMES_ESPERA)
    detector.landmarks = generar_landmark_puno()
    # de sobra para cerrar g2 y agotar todo el RESULTADO
    _correr(detector, piezas, FRAMES_CAPTURA + FRAMES_RESULTADO + 3)

    assert mock_ejecutar.call_count == 1
    mock_ejecutar.assert_called_once_with(Accion.A4)


@patch("src.main.ejecutar_accion")
def test_sin_combo_completo_no_hay_accion(mock_ejecutar, piezas):
    """Sostener un solo gesto (sin cerrar el segundo) no dispara nada: la interaccion
    exige el par. `ultima_accion` sigue None."""
    detector = DetectorFalso(generar_landmark_un_dedo())
    _, accion, estado_combo = _correr(detector, piezas, FRAMES_CAPTURA + 1)

    assert estado_combo.fase == FaseCombo.ESPERA  # cerro g1, espera el g2
    assert accion is None
    mock_ejecutar.assert_not_called()


@patch("src.main.ejecutar_accion")
def test_mano_perdida_resetea_el_filtro_ema(mock_ejecutar, piezas):
    """INT-FR-003: sin reset, al reaparecer la mano el filtro mezclaria la posicion
    de antes de perderla con la nueva."""
    detector = DetectorFalso(generar_landmark_un_dedo())
    _correr(detector, piezas, 3)
    assert piezas["filtro"].x_prev is not None

    detector.landmarks = None
    _correr(detector, piezas, 1)

    assert piezas["filtro"].x_prev is None


@patch("src.main.ejecutar_accion")
def test_fallo_de_accion_no_propaga_excepcion(mock_ejecutar, piezas):
    """ACC-FR-005 + NFR-G02: si 007 reporta exito=False, el pipeline lo loguea y sigue;
    la accion del combo igual queda registrada como ultima."""
    mock_ejecutar.return_value.exito = False
    mock_ejecutar.return_value.mensaje = "binario no encontrado"
    detector = DetectorFalso(generar_landmark_un_dedo())
    _correr(detector, piezas, FRAMES_CAPTURA + FRAMES_ESPERA)
    detector.landmarks = generar_landmark_puno()
    _, accion, _ = _correr(detector, piezas, FRAMES_CAPTURA)

    assert accion == Accion.A4  # el combo se cerro, aunque el SO fallara


@patch("src.main.ejecutar_accion")
def test_devuelve_estado_combo_para_el_hud(mock_ejecutar, piezas):
    """procesar_frame debe devolver el EstadoCombo para que 008 dibuje el HUD."""
    detector = DetectorFalso(generar_landmark_un_dedo())
    _, _, estado_combo = _correr(detector, piezas, 1)

    assert estado_combo is not None
    assert estado_combo.fase == FaseCombo.CAPTURANDO_G1
