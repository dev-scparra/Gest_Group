# Plan 010 — Robustez del Ejecutor

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

Cambio acotado a una sola función: `_run()` en `src/acciones/ejecutor.py`. Los tres backends (`_ejecutar_macos`, `_ejecutar_linux`, `_ejecutar_windows`) **no cambian** — todos los que usan `subprocess` pasan por `_run()`, así que arreglarla ahí cubre macOS y Linux de una vez. `_ejecutar_windows` ya envuelve su llamada en `try/except Exception` (no usa `subprocess`), por lo que ya cumple ROB-FR-004.

## 2. Notas de implementación

```python
TIMEOUT_SUBPROCESS_S = 2.0

# El binario que provee cada comando, para dar un mensaje accionable (ROB-FR-001).
_PAQUETE_POR_BINARIO = {"amixer": "alsa-utils", "osascript": "macOS (no disponible en este SO)"}


def _run(comando: list[str]) -> ResultadoEjecucion:
    binario = comando[0]
    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True, timeout=TIMEOUT_SUBPROCESS_S
        )
    except FileNotFoundError:
        sugerencia = _PAQUETE_POR_BINARIO.get(binario, "revisar el PATH")
        return ResultadoEjecucion(
            exito=False, mensaje=f"binario '{binario}' no encontrado en el PATH ({sugerencia})"
        )
    except subprocess.TimeoutExpired:
        return ResultadoEjecucion(
            exito=False, mensaje=f"'{binario}' excedio el timeout de {TIMEOUT_SUBPROCESS_S}s"
        )
    except OSError as exc:  # PermissionError y demas fallos de SO (ROB-FR-003)
        return ResultadoEjecucion(exito=False, mensaje=f"fallo al ejecutar '{binario}': {exc}")

    if resultado.returncode != 0:
        return ResultadoEjecucion(exito=False, mensaje=resultado.stderr or resultado.stdout)
    return ResultadoEjecucion(exito=True, mensaje=None)
```

`FileNotFoundError` y `PermissionError` son ambas subclases de `OSError`, así que el orden de los `except` importa: los específicos primero (para dar mensajes distintos), el genérico al final como red de seguridad. `subprocess.TimeoutExpired` **no** es un `OSError`, por eso va en su propia rama.

## 3. Estrategia de pruebas

La lección del bug es de método, no de código: **un mock que solo modela el camino feliz no puede probar el camino de error que la spec exige**. Los tests nuevos parchean `subprocess.run` con `side_effect` (una excepción), no con `return_value` (un objeto con `returncode`):

- `test_binario_ausente_reporta_fallo_sin_excepcion`: `side_effect=FileNotFoundError(...)` → `exito is False`, `"amixer" in mensaje` (ROB-FR-001, ROB-FR-005).
- `test_timeout_reporta_fallo`: `side_effect=subprocess.TimeoutExpired(cmd="osascript", timeout=2.0)` → `exito is False` (ROB-FR-002).
- `test_permission_error_reporta_fallo`: `side_effect=PermissionError(...)` → `exito is False` (ROB-FR-003).
- `test_run_pasa_timeout_a_subprocess`: verificar que `subprocess.run` se invoca con `timeout=2.0` en `kwargs` (ROB-FR-002 — sin esto, el timeout se puede "implementar" en la constante y olvidar de pasar).

Los 11 tests existentes de `tests/test_ejecutor.py` siguen pasando sin cambios: parchean `return_value`, y el camino feliz no se toca.

## 4. Riesgo de la corrección

Bajo. `_run()` es una función de 5 líneas sin estado, con un único punto de llamada por backend. El único riesgo real es elegir un `timeout` demasiado agresivo: 2 s es ~100× lo que tarda un `osascript` de volumen, pero si en la demo se observan fallos de timeout espurios (máquina muy cargada), subirlo a 5 s no compromete NFR-G01 porque el timeout solo se alcanza en el camino de fallo, no en el de éxito.
