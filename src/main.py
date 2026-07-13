"""Punto de entrada del pipeline completo. Orquestacion pura (ver spec 009):
no contiene logica de negocio propia de ningun modulo 001-008.

Ejecutar con: python -m src.main
Salir con la tecla 'q'.
"""

import time
from dataclasses import dataclass
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

# Un fallo persistente ocurre una vez por frame: sin acotar, inunda la consola a
# ~30 lineas/segundo y entierra el primer mensaje, que es el util (CNF-FR-002).
FRECUENCIA_LOG_ERRORES = 30
_errores_logueados = 0


def _log_acotado(mensaje: str) -> None:
    """Imprime la primera ocurrencia y luego una de cada FRECUENCIA_LOG_ERRORES."""
    global _errores_logueados
    if _errores_logueados % FRECUENCIA_LOG_ERRORES == 0:
        print(mensaje)
    _errores_logueados += 1


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


@dataclass
class EstadoPipeline:
    """El unico estado mutable de la orquestacion (INT-FR-006).

    `None` significa "aun no se ha confirmado ninguna accion", que es distinto de
    `Accion.A_E` ("ninguna"), una accion identidad ya confirmada (SEM-FR-003).
    """

    ultima_accion: Accion | None = None


class MedidorFPS:
    """Mide el FPS sostenido del pipeline (SC-G02). Lo DIBUJA el modulo 008; aqui
    solo se mide, que es lo que 009 tiene que hacer (CNF-FR-003)."""

    def __init__(self):
        self._ultimo_tick = time.time()
        self._frames = 0
        self.actual = 0.0

    def tick(self) -> float:
        self._frames += 1
        ahora = time.time()
        transcurrido = ahora - self._ultimo_tick
        if transcurrido >= 1.0:
            self.actual = self._frames / transcurrido
            self._frames = 0
            self._ultimo_tick = ahora
        return self.actual


def procesar_frame(
    frame_rgb,
    detector: DetectorManos,
    filtro: FiltroEMA,
    estabilizador: EstabilizadorGesto,
    homomorfismo: Homomorfismo,
    estado: EstadoPipeline,
) -> tuple[Gesto, Accion | None]:
    """Un ciclo del pipeline: 004 -> 005 -> 006 -> phi (002) -> 007.

    Sin cv2 ni I/O de ventana, para que la orquestacion sea testeable sin camara
    (SEM-FR-005) — 009 era el unico modulo sin suite propia, y es justo donde vive
    el estado que VIS-FR-003 regula.

    Retorna (gesto instantaneo, ultima accion confirmada) para que 008 los dibuje.
    """
    landmarks = detector.procesar(frame_rgb)

    if landmarks is None:
        filtro.reset()  # INT-FR-003: sin esto, al reaparecer la mano el filtro
        gesto_actual = Gesto.E  # mezclaria la posicion vieja con la nueva.
    else:
        gesto_actual = clasificar_gesto(filtro.aplicar(landmarks))

    # INT-FR-004: se alimenta E explicitamente en los frames sin mano, en vez de
    # omitir la llamada, para que el contador de debounce no cruce una perdida de mano.
    gesto_confirmado = estabilizador.actualizar(gesto_actual)

    if gesto_confirmado is not None:
        accion = homomorfismo.aplicar(gesto_confirmado)  # INT-FR-005
        resultado = ejecutar_accion(accion)
        if not resultado.exito:
            # ACC-FR-005: el fallo se reporta. Sin esto, todo el reporte de errores
            # de 007 moria en silencio y el usuario veia "no pasa nada" (CNF-FR-005).
            _log_acotado(f"[accion] {accion.name} fallo: {resultado.mensaje}")

        # SEM-FR-001: A_E es un no-op (ACC-FR-004), no un disparo real. Confirmar E
        # -- que es lo que pasa a los `frames_estables` frames de retirar la mano --
        # no debe desplazar del overlay a la ultima accion que si tuvo efecto.
        if accion != Accion.A_E:
            estado.ultima_accion = accion

    return gesto_actual, estado.ultima_accion


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
    estabilizador = EstabilizadorGesto(
        frames_estables=config["estabilizador"]["frames_estables"]
    )
    homomorfismo = Homomorfismo()

    estado = EstadoPipeline()
    medidor = MedidorFPS()

    try:
        while True:
            exito, frame_bgr, frame_rgb = captura.leer_frame()
            if not exito:
                # Camara desconectada: distinto de "sin mano", que es un estado
                # transitorio esperado (INT-FR-002, caso borde de spec 009 Sec. 5).
                print("Camara desconectada o sin frames disponibles. Terminando.")
                break

            try:
                gesto_actual, accion = procesar_frame(
                    frame_rgb, detector, filtro, estabilizador, homomorfismo, estado
                )
                landmarks_dibujo = detector.landmarks_para_dibujo()
            except Exception as exc:  # INT-FR-008 / NFR-G02
                # El frame se trata como "sin mano" y el loop sigue (spec 009 Sec. 5).
                _log_acotado(f"Error no anticipado en el frame, se ignora: {exc}")
                gesto_actual, accion = Gesto.E, estado.ultima_accion
                landmarks_dibujo = None

            fps = medidor.tick()

            try:
                dibujar_frame(
                    frame_bgr, landmarks_dibujo, gesto_actual, accion, filtro.alpha, fps
                )
            except Exception as exc:  # NFR-G02
                _log_acotado(f"Fallo al dibujar el overlay, se muestra crudo: {exc}")

            # imshow/waitKey quedan FUERA de los try: si una excepcion recurrente los
            # saltara, la ventana se congelaria y la tecla 'q' (INT-FR-007) nunca se
            # procesaria — solo quedaria Ctrl-C (CNF-FR-002).
            cv2.imshow("GestGroup", frame_bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        captura.liberar()


if __name__ == "__main__":
    main()
