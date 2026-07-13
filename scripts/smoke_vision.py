"""Checklist de humo manual para 003 (captura) + 004 (deteccion) + 005 (EMA) + 006.

No es parte de la suite automatizada (requiere camara real). Ejecutar con:

    python -m scripts.smoke_vision

Muestra la ventana de video con landmarks dibujados (si se detecta mano) e imprime
por consola, una vez por segundo, el estado del pipeline de vision.

**Verificacion de lateralidad (spec 012, T012-01).** Ademas del conteo de frames,
imprime la lateralidad que reporta MediaPipe y el gesto clasificado. Poner CADA MANO
frente a la camara y comprobar que los 6 gestos se clasifican igual con la izquierda
y con la derecha: el clasificador anterior intercambiaba G3 y G5 con una de las dos
(y volvia G4 inalcanzable), y ese defecto es invisible si solo se prueba con una mano.
Salir con 'q'.
"""

import time

import cv2
import mediapipe as mp

from src.captura.video_capture import CapturaVideo
from src.clasificador.gestos import clasificar_gesto, dedos_levantados
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
            gesto = None
            dedos = None

            if landmarks is not None:
                frames_con_mano += 1
                suavizados = filtro.aplicar(landmarks)
                gesto = clasificar_gesto(suavizados)
                dedos = dedos_levantados(suavizados)
                mp.solutions.drawing_utils.draw_landmarks(
                    frame_bgr,
                    detector.landmarks_para_dibujo(),
                    mp.solutions.hands.HAND_CONNECTIONS,
                )
            else:
                filtro.reset()

            ahora = time.time()
            if ahora - ultimo_reporte >= 1.0:
                print(
                    f"frames={frames_totales} con_mano={frames_con_mano} "
                    f"mano={detector.lateralidad()} "
                    f"gesto={gesto.name if gesto else '-'} "
                    f"dedos={dedos}"
                )
                ultimo_reporte = ahora

            cv2.imshow("GestGroup — smoke test", frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        captura.liberar()


if __name__ == "__main__":
    main()
