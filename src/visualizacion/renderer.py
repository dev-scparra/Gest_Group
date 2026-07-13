"""Overlay de landmarks + estado algebraico sobre el frame de video.

Ver spec 008-visualizacion. `dibujar_frame()` muta y retorna el mismo array
(sin copia), coherente con el resto del pipeline y relevante para NFR-G01
(>=15 FPS, ver plan.md de 008). Solo renderiza lo que 006/002 ya decidieron;
no decide gesto ni accion.
"""

import cv2
import mediapipe as mp
import numpy as np

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

COLORES_GESTO = {
    Gesto.E: (200, 200, 200),  # gris
    Gesto.G1: (0, 255, 0),  # verde
    Gesto.G2: (0, 200, 255),  # amarillo
    Gesto.G3: (0, 0, 255),  # rojo
    Gesto.G4: (255, 0, 0),  # azul
    Gesto.G5: (255, 0, 255),  # magenta
}


def dibujar_frame(
    frame_bgr: np.ndarray,
    hand_landmarks,
    gesto: Gesto,
    accion: Accion,
    alpha: float,
) -> np.ndarray:
    """Anade overlays al frame: landmarks, gesto detectado, accion phi(g), alpha."""

    if hand_landmarks is not None:
        mp_drawing.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    color = COLORES_GESTO.get(gesto, (255, 255, 255))

    cv2.putText(
        frame_bgr, f"g = {gesto.value}", (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2,
    )

    cv2.putText(
        frame_bgr, f"phi(g) = {accion.value}", (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2,
    )

    cv2.putText(
        frame_bgr, f"alpha (EMA) = {alpha:.2f}", (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1,
    )

    cv2.putText(
        frame_bgr, "G/ker(phi) = Im(phi)", (350, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1,
    )

    return frame_bgr
