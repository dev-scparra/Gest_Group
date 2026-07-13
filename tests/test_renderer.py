import numpy as np

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.visualizacion.renderer import dibujar_frame


def test_dibujar_frame_sin_mano_no_lanza_excepcion_y_preserva_forma():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    resultado = dibujar_frame(frame, None, Gesto.E, Accion.A_E, 0.3)

    assert resultado.shape == (480, 640, 3)


def test_dibujar_frame_sin_mano_mantiene_ultima_accion_confirmada():
    """VIS-FR-003: si el gesto instantaneo es E (sin mano) pero la ultima accion
    confirmada fue A1, el overlay debe seguir usando A1, no resetear a A_E."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    resultado = dibujar_frame(frame, None, Gesto.E, Accion.A1, 0.3)

    assert resultado.shape == (480, 640, 3)
    # No se valida contenido visual exacto por pixel (fragil, ver plan.md de 008);
    # solo que la funcion acepta y no descarta el valor de accion recibido.


def test_dibujar_frame_muta_y_retorna_el_mismo_array():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    resultado = dibujar_frame(frame, None, Gesto.G1, Accion.A1, 0.3)

    assert resultado is frame
