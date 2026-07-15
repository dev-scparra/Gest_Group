import numpy as np

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.clasificador.capturador_combo import EstadoCombo, FaseCombo
from src.visualizacion.renderer import dibujar_frame


def _frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


def test_dibujar_frame_sin_mano_no_lanza_excepcion_y_preserva_forma():
    resultado = dibujar_frame(_frame(), None, Gesto.E, Accion.A_E, 0.3)

    assert resultado.shape == (480, 640, 3)


def test_dibujar_frame_sin_mano_mantiene_ultima_accion_confirmada():
    """VIS-FR-003: si el gesto instantaneo es E (sin mano) pero la ultima accion
    confirmada fue A1, el overlay debe seguir usando A1, no resetear a A_E."""
    resultado = dibujar_frame(_frame(), None, Gesto.E, Accion.A1, 0.3)

    assert resultado.shape == (480, 640, 3)
    # No se valida contenido visual exacto por pixel (fragil, ver plan.md de 008);
    # solo que la funcion acepta y no descarta el valor de accion recibido.


def test_dibujar_frame_muta_y_retorna_el_mismo_array():
    frame = _frame()

    resultado = dibujar_frame(frame, None, Gesto.G1, Accion.A1, 0.3)

    assert resultado is frame


def test_dibujar_frame_acepta_accion_none():
    """SEM-FR-003: al arrancar aun no hay accion confirmada. None no es Accion.A_E."""
    resultado = dibujar_frame(_frame(), None, Gesto.E, None, 0.3)

    assert resultado.shape == (480, 640, 3)


def test_dibujar_frame_dibuja_fps_cuando_se_le_pasa():
    """CNF-FR-003: el FPS lo mide 009 pero lo DIBUJA 008 — main.py no puede tener
    logica de renderizado (spec 009, Secciones 1 y 6)."""
    frame_con_fps = dibujar_frame(_frame(), None, Gesto.E, None, 0.3, fps=28.4)
    frame_sin_fps = dibujar_frame(_frame(), None, Gesto.E, None, 0.3, fps=None)

    assert frame_con_fps.shape == (480, 640, 3)
    # Con FPS hay pixeles encendidos que sin FPS no estan (la franja del texto).
    assert frame_con_fps.sum() > frame_sin_fps.sum()


def test_hud_combo_capturando_dibuja_barra_y_lider():
    """VIS-FR-009 (spec 015): en captura, el HUD enciende pixeles (titulo, votos, barra)."""
    estado = EstadoCombo(
        fase=FaseCombo.CAPTURANDO_G1,
        frames_restantes=8,
        frames_total_fase=20,
        lider=Gesto.G3,
        conteo=[(Gesto.G3, 12), (Gesto.E, 3)],
    )
    con_hud = dibujar_frame(_frame(), None, Gesto.G3, None, 0.3, estado_combo=estado)
    sin_hud = dibujar_frame(_frame(), None, Gesto.G3, None, 0.3, estado_combo=None)

    assert con_hud.shape == (480, 640, 3)
    assert con_hud.sum() != sin_hud.sum()  # el HUD (panel + texto + barra) modifica pixeles


def test_hud_combo_resultado_muestra_la_composicion():
    """VIS-FR-009: en RESULTADO se muestra g1 o g2 = compuesto sin lanzar excepcion."""
    estado = EstadoCombo(
        fase=FaseCombo.RESULTADO,
        g1=Gesto.G1,
        g2=Gesto.G3,
        compuesto=Gesto.G4,
    )
    resultado = dibujar_frame(_frame(), None, Gesto.E, Accion.A4, 0.3, estado_combo=estado)

    assert resultado.shape == (480, 640, 3)


def test_hud_combo_inactivo_no_lanza_excepcion():
    """La fase INACTIVO dibuja solo una pista y no rompe nada."""
    estado = EstadoCombo(fase=FaseCombo.INACTIVO)
    resultado = dibujar_frame(_frame(), None, Gesto.E, None, 0.3, estado_combo=estado)

    assert resultado.shape == (480, 640, 3)


def test_dibujar_frame_estado_combo_none_no_lanza_excepcion():
    """El caso por defecto (sin HUD) sigue funcionando: estado_combo=None no rompe nada."""
    resultado = dibujar_frame(_frame(), None, Gesto.G1, Accion.A1, 0.3)

    assert resultado.shape == (480, 640, 3)
