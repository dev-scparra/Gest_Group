"""Ejecutor de acciones: traduce Accion (elemento de A) en un efecto de SO real.

Ver spec 007-ejecutor-acciones. Un solo modulo cross-platform: el backend se
selecciona en runtime con platform.system() (NFR-G05, revisado) — no hay
proyectos separados por SO. macOS y Windows tienen paridad completa de las 5
acciones; Linux soporta solo volumen.
"""

import platform
import subprocess
from dataclasses import dataclass

from src.algebra.grupo_acciones import Accion

# --- Windows: codigos de tecla virtual multimedia (sin dependencias de terceros) ---
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
KEYEVENTF_KEYUP = 0x0002

_VK_POR_ACCION = {
    Accion.A1: VK_VOLUME_UP,
    Accion.A2: VK_VOLUME_DOWN,
    Accion.A3: VK_MEDIA_PLAY_PAUSE,
    Accion.A4: VK_MEDIA_NEXT_TRACK,
    Accion.A5: VK_MEDIA_PREV_TRACK,
}


# Cota superior generosa: osascript/amixer responden en milisegundos. El timeout
# solo se alcanza en el camino de fallo (p. ej. un osascript colgado esperando el
# dialogo de permisos de Accesibilidad), nunca en el de exito (ROB-FR-002).
TIMEOUT_SUBPROCESS_S = 2.0

_SUGERENCIA_POR_BINARIO = {
    "amixer": "instalar el paquete 'alsa-utils'",
    "osascript": "solo existe en macOS",
}


@dataclass
class ResultadoEjecucion:
    exito: bool
    mensaje: str | None = None


def _run(comando: list[str]) -> ResultadoEjecucion:
    """Ejecuta un comando de SO y traduce CUALQUIER fallo a ResultadoEjecucion.

    `subprocess.run` lanza FileNotFoundError si el binario no existe: nunca llega a
    devolver un objeto con `returncode`. Comprobar solo el returncode deja escapar
    esa excepcion y tumba el pipeline, que es justo lo que 007/spec.md Seccion 5
    prohibe. Ver spec 010 (ROB-FR-001..003).
    """
    binario = comando[0]
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SUBPROCESS_S,
            check=False,  # el returncode se inspecciona abajo; check=True lanzaria
        )
    except FileNotFoundError:
        sugerencia = _SUGERENCIA_POR_BINARIO.get(binario, "revisar el PATH")
        return ResultadoEjecucion(
            exito=False,
            mensaje=f"binario '{binario}' no encontrado en el PATH ({sugerencia})",
        )
    except subprocess.TimeoutExpired:
        return ResultadoEjecucion(
            exito=False,
            mensaje=f"'{binario}' excedio el timeout de {TIMEOUT_SUBPROCESS_S}s",
        )
    except OSError as exc:  # PermissionError y demas fallos de SO (ROB-FR-003)
        return ResultadoEjecucion(exito=False, mensaje=f"fallo al ejecutar '{binario}': {exc}")

    if resultado.returncode != 0:
        return ResultadoEjecucion(exito=False, mensaje=resultado.stderr or resultado.stdout)
    return ResultadoEjecucion(exito=True, mensaje=None)


def _ejecutar_macos(accion: Accion) -> ResultadoEjecucion:
    if accion == Accion.A1:
        return _run(["osascript", "-e",
                     "set volume output volume (output volume of (get volume settings) + 10)"])
    if accion == Accion.A2:
        return _run(["osascript", "-e",
                     "set volume output volume (output volume of (get volume settings) - 10)"])
    if accion == Accion.A3:
        return _run(["osascript", "-e",
                     'tell application "System Events" to key code 49'])  # espacio
    if accion == Accion.A4:
        return _run(["osascript", "-e",
                     'tell application "System Events" to key code 124 using command down'])
    if accion == Accion.A5:
        return _run(["osascript", "-e",
                     'tell application "System Events" to key code 123 using command down'])
    return ResultadoEjecucion(exito=True, mensaje=None)


def _ejecutar_linux(accion: Accion) -> ResultadoEjecucion:
    if accion == Accion.A1:
        return _run(["amixer", "-q", "sset", "Master", "10%+"])
    if accion == Accion.A2:
        return _run(["amixer", "-q", "sset", "Master", "10%-"])
    return ResultadoEjecucion(
        exito=False,
        mensaje=f"{accion.name} no soportada en Linux en el MVP (solo volumen, NFR-G05)",
    )


def _enviar_tecla_virtual(vk: int) -> None:
    """Envia key-down + key-up de una tecla virtual de Windows. Aislado para poder
    parchearse en tests sin depender de que ctypes.windll exista (solo en Windows)."""
    import ctypes

    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def _ejecutar_windows(accion: Accion) -> ResultadoEjecucion:
    vk = _VK_POR_ACCION.get(accion)
    if vk is None:
        return ResultadoEjecucion(exito=True, mensaje=None)
    try:
        _enviar_tecla_virtual(vk)
    except Exception as exc:
        return ResultadoEjecucion(exito=False, mensaje=str(exc))
    return ResultadoEjecucion(exito=True, mensaje=None)


def ejecutar_accion(accion: Accion) -> ResultadoEjecucion:
    """Ejecuta el efecto de SO correspondiente. No lanza excepcion ante fallo del
    SO subyacente; lo reporta en ResultadoEjecucion (ACC-FR-005)."""
    if accion == Accion.A_E:
        return ResultadoEjecucion(exito=True, mensaje=None)

    sistema = platform.system()
    if sistema == "Darwin":
        return _ejecutar_macos(accion)
    if sistema == "Linux":
        return _ejecutar_linux(accion)
    if sistema == "Windows":
        return _ejecutar_windows(accion)
    return ResultadoEjecucion(exito=False, mensaje=f"sistema operativo no soportado: {sistema}")
