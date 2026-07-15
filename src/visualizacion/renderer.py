"""Overlay de landmarks + estado algebraico sobre el frame de video.

Ver spec 008-visualizacion, spec 011 (SEM-FR-003/004) y spec 015 (HUD de combos,
VIS-FR-009). `dibujar_frame()` muta y retorna el mismo array (sin copia), coherente con
el resto del pipeline y relevante para NFR-G01 (>=15 FPS). Solo renderiza lo que
006/002/015 ya decidieron; no decide gesto ni accion ni la fase del combo.
"""

import cv2
import mediapipe as mp
import numpy as np

from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.clasificador.capturador_combo import EstadoCombo, FaseCombo

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
CIAN = (255, 255, 0)  # BGR: HUD del combo (la composicion o de G aplicada en vivo)
VERDE = (0, 220, 0)

# Se escribe "=" y no el "≅" que pedia VIS-FR-005: las fuentes Hershey de OpenCV no
# tienen glifo para ese simbolo y lo renderizarian como "?" (CNF-FR-007).
ANOTACION_ALGEBRAICA = "G/ker(phi) = Im(phi)"

# Marcador de "todavia no se ha confirmado ninguna accion", distinto de Accion.A_E
# ("ninguna"), que es una accion identidad ya confirmada (SEM-FR-003).
SIN_ACCION = "--"

_FUENTE = cv2.FONT_HERSHEY_SIMPLEX


def _barra_progreso(frame, x, y, ancho, alto, fraccion, color):
    """Dibuja el marco y el relleno proporcional (0..1) de una barra de progreso."""
    cv2.rectangle(frame, (x, y), (x + ancho, y + alto), GRIS, 1)
    relleno = int(ancho * max(0.0, min(1.0, fraccion)))
    if relleno > 0:
        cv2.rectangle(frame, (x, y), (x + relleno, y + alto), color, -1)


def _panel_oscuro(frame, x, y, ancho, alto):
    """Oscurece una region para que el texto del HUD sea legible sobre cualquier fondo."""
    alto_f, ancho_f = frame.shape[:2]
    x2, y2 = min(x + ancho, ancho_f), min(y + alto, alto_f)
    x, y = max(x, 0), max(y, 0)
    if x2 <= x or y2 <= y:
        return
    region = frame[y:y2, x:x2]
    cv2.addWeighted(np.zeros_like(region), 0.55, region, 0.45, 0, region)


def _dibujar_hud_combo(frame_bgr, estado_combo: EstadoCombo, fps: float | None) -> None:
    """Asiste al usuario con la captura del combo (spec 015, VIS-FR-009): fase, gesto
    lider de la votacion, cuenta regresiva y el resultado de la composicion."""
    fase = estado_combo.fase
    x0, y0 = 10, 150
    _panel_oscuro(frame_bgr, x0, y0, 400, 120)

    def linea(texto, dy, color=BLANCO, escala=0.6, grosor=1):
        cv2.putText(frame_bgr, texto, (x0 + 8, y0 + dy), _FUENTE, escala, color, grosor)

    if fase == FaseCombo.INACTIVO:
        linea("[COMBO] haz un gesto para empezar", 26, CIAN)
        linea("(2 gestos -> phi(g1 o g2))", 50, GRIS, 0.5)
        return

    # Segundos aproximados desde los frames restantes, para los "tiempos de espera".
    restante_txt = f"{estado_combo.frames_restantes}f"
    if fps:
        restante_txt += f" (~{estado_combo.frames_restantes / fps:.1f}s)"
    fraccion = 0.0
    if estado_combo.frames_total_fase:
        hecho = estado_combo.frames_total_fase - estado_combo.frames_restantes
        fraccion = hecho / estado_combo.frames_total_fase

    if fase in (FaseCombo.CAPTURANDO_G1, FaseCombo.CAPTURANDO_G2):
        num = 1 if fase == FaseCombo.CAPTURANDO_G1 else 2
        linea(f"[COMBO] gesto {num} de 2 - capturando", 24, CIAN)
        lider = estado_combo.lider
        color_lider = COLORES_GESTO.get(lider, BLANCO)
        votos = estado_combo.conteo[0][1] if estado_combo.conteo else 0
        etiqueta_lider = lider.value if lider is not None else "..."
        if num == 2 and estado_combo.g1 is not None:
            linea(f"g1 = {estado_combo.g1.value}   votando g2:", 48, BLANCO, 0.55)
            linea(f"{etiqueta_lider} ({votos})", 70, color_lider, 0.55)
        else:
            linea(f"votando: {etiqueta_lider} ({votos})", 48, color_lider, 0.55)
        _barra_progreso(frame_bgr, x0 + 8, y0 + 82, 360, 12, fraccion, CIAN)
        linea(restante_txt, 106, GRIS, 0.45)

    elif fase == FaseCombo.ESPERA:
        linea("[COMBO] prepara el gesto 2...", 24, CIAN)
        g1_txt = estado_combo.g1.value if estado_combo.g1 is not None else "?"
        linea(f"g1 = {g1_txt}   g2 = ?", 50, BLANCO, 0.55)
        _barra_progreso(frame_bgr, x0 + 8, y0 + 82, 360, 12, fraccion, GRIS)
        linea(restante_txt, 106, GRIS, 0.45)

    elif fase == FaseCombo.RESULTADO:
        g1 = estado_combo.g1.value if estado_combo.g1 is not None else "?"
        g2 = estado_combo.g2.value if estado_combo.g2 is not None else "?"
        res = estado_combo.compuesto.value if estado_combo.compuesto is not None else "?"
        linea("[COMBO] resultado", 24, VERDE)
        linea(f"{g1} o {g2} = {res}", 54, VERDE, 0.6)


def dibujar_frame(
    frame_bgr: np.ndarray,
    hand_landmarks,
    gesto: Gesto,
    accion: Accion | None,
    alpha: float,
    fps: float | None = None,
    estado_combo: EstadoCombo | None = None,
) -> np.ndarray:
    """Anade overlays al frame: landmarks, gesto en vivo, ultima accion phi(g), alpha, FPS
    y el HUD de captura de combos (spec 015).

    `gesto` es el gesto instantaneo (cambia cada frame). `accion` es la ultima accion
    confirmada (persiste entre disparos, VIS-FR-003) o None si aun no hubo ninguna.
    Los dos se etiquetan distinto en pantalla porque son conceptualmente distintos y
    verlos con el mismo peso induce a leer el overlay como si ambos fueran en vivo
    (SEM-FR-004).

    `estado_combo` (VIS-FR-009) es la instantanea del CapturadorCombo: cuando no es None,
    se dibuja el HUD que asiste al usuario con la fase, la votacion en curso, la cuenta
    regresiva y el resultado de la composicion o de G — la operacion del grupo en vivo.
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

    cv2.putText(frame_bgr, f"g = {gesto.value}  (en vivo)", (10, 35), _FUENTE, 0.8, color, 2)
    cv2.putText(
        frame_bgr, f"phi(g) = {texto_accion}  (ultima)", (10, 70), _FUENTE, 0.8, BLANCO, 2
    )
    cv2.putText(frame_bgr, f"alpha (EMA) = {alpha:.2f}", (10, 100), _FUENTE, 0.55, GRIS, 1)

    if estado_combo is not None:
        _dibujar_hud_combo(frame_bgr, estado_combo, fps)

    if fps is not None:
        cv2.putText(frame_bgr, f"FPS: {fps:.1f}", (10, 470), _FUENTE, 0.55, GRIS, 1)

    cv2.putText(frame_bgr, ANOTACION_ALGEBRAICA, (330, 470), _FUENTE, 0.5, GRIS, 1)

    return frame_bgr
