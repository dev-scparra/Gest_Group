"""Punto de entrada del pipeline completo. Orquestacion pura (ver spec 009):
no contiene logica de negocio propia de ningun modulo 001-008.

Ejecutar con: python src/main.py
Salir con la tecla 'q'.
"""

import time
from pathlib import Path

import cv2
import yaml

from src.acciones.ejecutor import ejecutar_accion
from src.algebra.grupo_acciones import Accion
from src.algebra.grupo_gestos import Gesto
from src.algebra.homomorfismo import Homomorfismo
from src.captura.video_capture import CapturaVideo
from src.clasificador.estabilizador import EstabilizadorGesto
from src.clasificador.gestos import clasificar_gesto
from src.deteccion.mediapipe_handler import DetectorManos
from src.preprocesamiento.filtro_ema import FiltroEMA
from src.visualizacion.renderer import dibujar_frame

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default.yaml"


def cargar_config(ruta: Path = CONFIG_PATH) -> dict:
    """Carga config/default.yaml. Falla rapido y explicito si falta o esta mal formado
    (INT-FR-001, spec 009 Seccion 5)."""
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo de configuracion: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    claves_requeridas = {"camara", "filtro_ema", "estabilizador", "deteccion"}
    faltantes = claves_requeridas - set(config or {})
    if faltantes:
        raise ValueError(f"config/default.yaml mal formado: faltan claves {faltantes}")
    return config


def main() -> None:
    config = cargar_config()

    captura = CapturaVideo(
        camara_id=config["camara"]["id"],
        ancho=config["camara"]["ancho"],
        alto=config["camara"]["alto"],
    )
    detector = DetectorManos(
        min_detection_confidence=config["deteccion"]["min_detection_confidence"],
        min_tracking_confidence=config["deteccion"]["min_tracking_confidence"],
    )
    filtro = FiltroEMA(alpha=config["filtro_ema"]["alpha"])
    estabilizador = EstabilizadorGesto(frames_estables=config["estabilizador"]["frames_estables"])
    homomorfismo = Homomorfismo()

    ultima_accion = Accion.A_E
    fps_ultimo_tick = time.time()
    fps_contador = 0
    fps_actual = 0.0

    try:
        while True:
            try:
                exito, frame_bgr, frame_rgb = captura.leer_frame()
                if not exito:
                    # Camara desconectada: distinto de "sin mano" (INT-FR-002, caso borde).
                    print("Camara desconectada o sin frames disponibles. Terminando.")
                    break

                landmarks = detector.procesar(frame_rgb)
                if landmarks is None:
                    filtro.reset()
                    gesto_actual = Gesto.E
                    gesto_confirmado = estabilizador.actualizar(Gesto.E)
                else:
                    landmarks_suav = filtro.aplicar(landmarks)
                    gesto_actual = clasificar_gesto(landmarks_suav)
                    gesto_confirmado = estabilizador.actualizar(gesto_actual)

                if gesto_confirmado is not None:
                    ultima_accion = homomorfismo.aplicar(gesto_confirmado)
                    ejecutar_accion(ultima_accion)

                dibujar_frame(
                    frame_bgr,
                    detector.landmarks_para_dibujo(),
                    gesto_actual,
                    ultima_accion,
                    filtro.alpha,
                )

                fps_contador += 1
                ahora = time.time()
                if ahora - fps_ultimo_tick >= 1.0:
                    fps_actual = fps_contador / (ahora - fps_ultimo_tick)
                    fps_contador = 0
                    fps_ultimo_tick = ahora

                cv2.putText(
                    frame_bgr, f"FPS: {fps_actual:.1f}", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1,
                )

                cv2.imshow("GestGroup", frame_bgr)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            except Exception as exc:  # NFR-G02 / INT-FR-008: un frame no puede tumbar la sesion.
                print(f"Error no anticipado en el frame actual, se ignora: {exc}")
                continue
    finally:
        captura.liberar()


if __name__ == "__main__":
    main()
