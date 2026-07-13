import numpy as np

from src.deteccion.mediapipe_handler import DetectorManos


def test_frame_sin_mano_devuelve_none():
    detector = DetectorManos()
    frame_negro = np.zeros((480, 640, 3), dtype=np.uint8)

    resultado = detector.procesar(frame_negro)

    assert resultado is None
    assert detector.landmarks_para_dibujo() is None


def test_frame_ruido_aleatorio_devuelve_none():
    detector = DetectorManos()
    rng = np.random.default_rng(42)
    frame_ruido = rng.integers(0, 255, size=(480, 640, 3), dtype=np.uint8)

    resultado = detector.procesar(frame_ruido)

    assert resultado is None
