"""Wrapper de MediaPipe Hands: frame RGB -> 21 landmarks normalizados o None.

Ver spec 004-deteccion-mediapipe. No suaviza coordenadas (eso es 005) ni
decide el gesto (eso es 006).
"""

import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands


class DetectorManos:
    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
    ):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._ultimo_resultado = None

    def procesar(self, frame_rgb: np.ndarray) -> list[tuple[float, float, float]] | None:
        """21 tuplas (x,y,z) normalizadas en [0,1], o None si no hay mano."""
        try:
            resultados = self.hands.process(frame_rgb)
        except Exception:
            self._ultimo_resultado = None
            return None

        self._ultimo_resultado = resultados
        if not resultados.multi_hand_landmarks:
            return None

        primera_mano = resultados.multi_hand_landmarks[0]
        return [(lm.x, lm.y, lm.z) for lm in primera_mano.landmark]

    def landmarks_para_dibujo(self):
        """Objeto crudo de MediaPipe (NormalizedLandmarkList) de la primera mano, o None."""
        if self._ultimo_resultado is None or not self._ultimo_resultado.multi_hand_landmarks:
            return None
        return self._ultimo_resultado.multi_hand_landmarks[0]
