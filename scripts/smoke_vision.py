"""Checklist de humo manual para 003 (captura) + 004 (deteccion) + 005 (EMA).

No es parte de la suite automatizada (requiere camara real). Ejecutar con:

    python scripts/smoke_vision.py

Muestra la ventana de video con landmarks dibujados (si se detecta mano) e
imprime por consola, una vez por segundo, si hay mano detectada, cuantos
landmarks se recibieron y el efecto del filtro EMA. Salir con 'q'.
"""

import time

import cv2

from src.captura.video_capture import CapturaVideo
from src.deteccion.mediapipe_handler import DetectorManos
from src.preprocesamiento.filtro_ema import FiltroEMA


def main() -> None:
    captura = CapturaVideo()
    detector = DetectorManos()
    filtro = FiltroEMA(alpha=0.3)

    ultimo_reporte = time.time()
    frames_totales = 0
    frames_con_mano = 0

    try:
        while True:
            exito, frame_bgr, frame_rgb = captura.leer_frame()
            if not exito:
                print("Camara no disponible. Terminando.")
                break

            landmarks = detector.procesar(frame_rgb)
            frames_totales += 1
            if landmarks is not None:
                frames_con_mano += 1
                filtro.aplicar(landmarks)
                mp_landmarks = detector.landmarks_para_dibujo()
                import mediapipe as mp

                mp.solutions.drawing_utils.draw_landmarks(
                    frame_bgr, mp_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                )
            else:
                filtro.reset()

            ahora = time.time()
            if ahora - ultimo_reporte >= 1.0:
                print(
                    f"frames={frames_totales} con_mano={frames_con_mano} "
                    f"landmarks={'21' if landmarks is not None else '0'}"
                )
                ultimo_reporte = ahora

            cv2.imshow("GestGroup — smoke test", frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        captura.liberar()


if __name__ == "__main__":
    main()
