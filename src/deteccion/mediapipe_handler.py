"""Wrapper de MediaPipe Hands: frame RGB -> 21 landmarks normalizados o None.

Ver spec 004-deteccion-mediapipe. No suaviza coordenadas (eso es 005) ni
decide el gesto (eso es 006).
"""

import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands

# Por debajo de este score, la etiqueta Left/Right de MediaPipe no es fiable
# (mano ambigua o parcialmente fuera de cuadro) y se reporta None (PUL-FR-006).
SCORE_LATERALIDAD_MINIMO = 0.8


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

    def lateralidad(self) -> str | None:
        """'Left' / 'Right' de la primera mano, o None si no hay mano o el score es bajo.

        La etiqueta se refiere al frame que MediaPipe efectivamente proceso — que en
        este pipeline ya viene espejado por CAP-FR-002, la convencion de selfie que
        MediaPipe asume — asi que corresponde a la mano fisica del usuario, sin
        des-espejarla (PUL-FR-003).

        El clasificador NO usa este dato para decidir el pulgar (ver spec 012,
        Decision D2: la orientacion se deriva de la geometria de la palma, no de la
        etiqueta). Se expone como diagnostico para `scripts/smoke_vision.py` y como
        base de un futuro soporte de dos manos.
        """
        resultado = self._ultimo_resultado
        if resultado is None or not resultado.multi_handedness:
            return None
        clasificacion = resultado.multi_handedness[0].classification[0]
        if clasificacion.score < SCORE_LATERALIDAD_MINIMO:
            return None
        return clasificacion.label
