"""Tests del loop de orquestacion (009) — el unico modulo que no tenia suite propia.

Esa ausencia es la razon por la que el defecto de spec 011 sobrevivio a 60 tests en
verde: VIS-FR-003 regula el valor de "ultima accion", pero ese valor lo decide 009 y
se estaba probando en la suite de 008, que solo veia el argumento ya cocinado.
"""

from unittest.mock import patch

import pytest

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.algebra.homomorfismo import Homomorfismo
from src.clasificador.estabilizador import EstabilizadorGesto
from src.main import EstadoPipeline, procesar_frame
from src.preprocesamiento.filtro_ema import FiltroEMA
from tests.fixtures_landmarks import generar_landmark_puno, generar_landmark_un_dedo

FRAMES_ESTABLES = 10
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
        "filtro": FiltroEMA(alpha=0.3),
        "estabilizador": EstabilizadorGesto(frames_estables=FRAMES_ESTABLES),
        "homomorfismo": Homomorfismo(),
        "estado": EstadoPipeline(),
    }


def _correr(detector, piezas, n_frames):
    """Corre n frames del pipeline y devuelve el (gesto, accion) del ultimo."""
    resultado = (None, None)
    for _ in range(n_frames):
        resultado = procesar_frame(
            FRAME_RGB,
            detector,
            piezas["filtro"],
            piezas["estabilizador"],
            piezas["homomorfismo"],
            piezas["estado"],
        )
    return resultado


@patch("src.main.ejecutar_accion")
def test_confirmacion_de_E_no_borra_la_ultima_accion(mock_ejecutar, piezas):
    """SEM-FR-001 / VIS-FR-003: retirar la mano no debe desplazar A1 del overlay.

    Contra el codigo anterior este test falla en el frame 10 sin mano: el
    estabilizador confirmaba E, phi(E)=A_E sobrescribia `ultima_accion`, y el overlay
    pasaba de "subir_volumen" a "ninguna" ~0.3s despues de bajar la mano.
    """
    detector = DetectorFalso(generar_landmark_un_dedo())

    _, accion = _correr(detector, piezas, FRAMES_ESTABLES)
    assert accion == Accion.A1  # el usuario sostuvo G1 y disparo subir volumen

    detector.landmarks = None  # el usuario retira la mano
    _, accion = _correr(detector, piezas, FRAMES_ESTABLES + 2)

    assert accion == Accion.A1  # sigue mostrando la ultima accion con efecto real


@patch("src.main.ejecutar_accion")
def test_confirmacion_no_identidad_si_desplaza_a_la_anterior(mock_ejecutar, piezas):
    """SEM-FR-001 no debe romper el caso normal: G3 (pausa) reemplaza a G1 (volumen).

    Se dan mas de `frames_estables` frames a la transicion a proposito: el filtro EMA
    (alpha=0.3) tarda ~4 frames en que la punta del indice cruce la linea del MCP, y
    solo entonces empiezan a contar los 10 frames del debounce. Ese retardo es
    correcto por diseno (005 + 006), pero se suma a la latencia gesto->accion de
    SC-G03: ~14 frames a 30 FPS son ~470ms, al borde del presupuesto de 500ms.
    """
    detector = DetectorFalso(generar_landmark_un_dedo())
    _, accion = _correr(detector, piezas, FRAMES_ESTABLES)
    assert accion == Accion.A1

    detector.landmarks = generar_landmark_puno()
    _, accion = _correr(detector, piezas, FRAMES_ESTABLES + 10)

    assert accion == Accion.A3


@patch("src.main.ejecutar_accion")
def test_sin_accion_confirmada_la_ultima_accion_es_None(mock_ejecutar, piezas):
    """SEM-FR-003: al arrancar sin mano, "aun no hay accion" (None) no puede
    confundirse con "se confirmo la accion identidad" (A_E, que se muestra
    'ninguna')."""
    detector = DetectorFalso(None)

    gesto, accion = _correr(detector, piezas, FRAMES_ESTABLES + 5)

    assert gesto == Gesto.E
    assert accion is None


@patch("src.main.ejecutar_accion")
def test_confirmacion_de_E_sigue_invocando_ejecutar_accion(mock_ejecutar, piezas):
    """SEM-FR-002: el fix se limita al overlay. INT-FR-005 sigue vigente: una
    confirmacion de E llama a ejecutar_accion(A_E), que es un no-op por ACC-FR-004."""
    detector = DetectorFalso(None)

    _correr(detector, piezas, FRAMES_ESTABLES)

    mock_ejecutar.assert_called_once_with(Accion.A_E)


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
    """ACC-FR-005 + NFR-G02: si 007 reporta exito=False, el pipeline lo loguea y sigue."""
    mock_ejecutar.return_value.exito = False
    mock_ejecutar.return_value.mensaje = "binario 'amixer' no encontrado en el PATH"
    detector = DetectorFalso(generar_landmark_un_dedo())

    _, accion = _correr(detector, piezas, FRAMES_ESTABLES)

    assert accion == Accion.A1  # la accion se confirmo, aunque el SO fallara
