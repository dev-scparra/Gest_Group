from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from src.captura.video_capture import CapturaVideo


def _frame_conocido() -> np.ndarray:
    frame = np.zeros((2, 2, 3), dtype=np.uint8)
    frame[0, 0] = [255, 0, 0]
    frame[0, 1] = [0, 255, 0]
    frame[1, 0] = [0, 0, 255]
    frame[1, 1] = [10, 20, 30]
    return frame


@patch("src.captura.video_capture.cv2.VideoCapture")
def test_leer_frame_exito_aplica_flip_y_convierte_rgb(mock_video_capture):
    mock_cap = MagicMock()
    frame = _frame_conocido()
    mock_cap.read.return_value = (True, frame)
    mock_video_capture.return_value = mock_cap

    captura = CapturaVideo(camara_id=0, ancho=2, alto=2)
    exito, frame_bgr, frame_rgb = captura.leer_frame()

    assert exito is True
    esperado_bgr = cv2.flip(frame, 1)
    esperado_rgb = cv2.cvtColor(esperado_bgr, cv2.COLOR_BGR2RGB)
    assert np.array_equal(frame_bgr, esperado_bgr)
    assert np.array_equal(frame_rgb, esperado_rgb)


@patch("src.captura.video_capture.cv2.VideoCapture")
def test_leer_frame_fallo_no_lanza_excepcion(mock_video_capture):
    mock_cap = MagicMock()
    mock_cap.read.return_value = (False, None)
    mock_video_capture.return_value = mock_cap

    captura = CapturaVideo()
    resultado = captura.leer_frame()

    assert resultado == (False, None, None)


@patch("src.captura.video_capture.cv2.destroyAllWindows")
@patch("src.captura.video_capture.cv2.VideoCapture")
def test_liberar_es_idempotente(mock_video_capture, mock_destroy):
    mock_cap = MagicMock()
    mock_video_capture.return_value = mock_cap

    captura = CapturaVideo()
    captura.liberar()
    captura.liberar()

    assert mock_cap.release.call_count == 2
