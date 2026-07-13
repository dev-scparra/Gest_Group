"""Captura de video con OpenCV: entrega frame BGR y su version RGB.

Ver spec 003-captura-video. No detecta manos ni decide el FPS objetivo del
pipeline completo (eso es 004 y 009 respectivamente).
"""

import cv2
import numpy as np


class CapturaVideo:
    def __init__(self, camara_id: int = 0, ancho: int = 640, alto: int = 480):
        self.cap = cv2.VideoCapture(camara_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def leer_frame(self) -> tuple[bool, np.ndarray | None, np.ndarray | None]:
        """Retorna (exito, frame_bgr, frame_rgb). (False, None, None) si falla la lectura."""
        exito, frame_bgr = self.cap.read()
        if not exito:
            return False, None, None
        frame_bgr = cv2.flip(frame_bgr, 1)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return True, frame_bgr, frame_rgb

    def liberar(self) -> None:
        """Libera la camara y cierra ventanas OpenCV. Idempotente."""
        self.cap.release()
        cv2.destroyAllWindows()
