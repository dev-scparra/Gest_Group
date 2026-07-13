"""Overlay de landmarks + estado algebraico sobre el frame de video.

Ver spec 008-visualizacion y spec 011 (SEM-FR-003/004). `dibujar_frame()` muta y
retorna el mismo array (sin copia), coherente con el resto del pipeline y relevante
para NFR-G01 (>=15 FPS). Solo renderiza lo que 006/002 ya decidieron; no decide
gesto ni accion.
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

BLANCO = (255, 255, 255)
GRIS = (180, 180, 180)

# Se escribe "=" y no el "≅" que pedia VIS-FR-005: las fuentes Hershey de OpenCV no
# tienen glifo para ese simbolo y lo renderizarian como "?" (CNF-FR-007).
ANOTACION_ALGEBRAICA = "G/ker(phi) = Im(phi)"

# Marcador de "todavia no se ha confirmado ninguna accion", distinto de Accion.A_E
# ("ninguna"), que es una accion identidad ya confirmada (SEM-FR-003).
SIN_ACCION = "--"


def dibujar_frame(
    frame_bgr: np.ndarray,
    hand_landmarks,
    gesto: Gesto,
    accion: Accion | None,
    alpha: float,
    fps: float | None = None,
) -> np.ndarray:
    """Anade overlays al frame: landmarks, gesto en vivo, ultima accion phi(g), alpha, FPS.

    `gesto` es el gesto instantaneo (cambia cada frame). `accion` es la ultima accion
    confirmada (persiste entre disparos, VIS-FR-003) o None si aun no hubo ninguna.
    Los dos se etiquetan distinto en pantalla porque son conceptualmente distintos y
    verlos con el mismo peso induce a leer el overlay como si ambos fueran en vivo
    (SEM-FR-004).
    """
    if hand_landmarks is not None:
        mp_drawing.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
        )

    color = COLORES_GESTO.get(gesto, BLANCO)
    texto_accion = accion.value if accion is not None else SIN_ACCION

    cv2.putText(
        frame_bgr, f"g = {gesto.value}  (en vivo)", (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2,
    )
    cv2.putText(
        frame_bgr, f"phi(g) = {texto_accion}  (ultima)", (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, BLANCO, 2,
    )
    cv2.putText(
        frame_bgr, f"alpha (EMA) = {alpha:.2f}", (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, GRIS, 1,
    )

    if fps is not None:
        cv2.putText(
            frame_bgr, f"FPS: {fps:.1f}", (10, 470),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, GRIS, 1,
        )

    cv2.putText(
        frame_bgr, ANOTACION_ALGEBRAICA, (330, 470),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, GRIS, 1,
    )

    return frame_bgr
