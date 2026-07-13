# Spec 010 — Robustez del Ejecutor ante Fallos del Binario de SO

**Módulo:** `src/acciones/ejecutor.py` (corrección sobre [007-ejecutor-acciones](../007-ejecutor-acciones/spec.md)).
**Depende de:** 007 (ya implementado).
**Origen:** auditoría de conformidad specs↔código (2026-07-13).
**Severidad:** **ALTA** — es el único hallazgo de la auditoría que produce una excepción no controlada en runtime.
**Requerimiento violado:** 007/spec.md Sección 5, caso borde `amixer` no instalado; NFR-G02 de [000-overview](../000-overview/spec.md).

---

## 1. Problema

La Sección 5 de 007/spec.md exige, literalmente:

> **`amixer` no instalado en Linux (no todas las distros lo traen por defecto):** DEBE producir un `ResultadoEjecucion.exito=False` con el mensaje de error del `subprocess` capturado, **no una excepción no controlada que tumbe el pipeline completo** (NFR-G02).

La implementación actual de `_run()` solo inspecciona `returncode`:

```python
def _run(comando: list[str]) -> ResultadoEjecucion:
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        return ResultadoEjecucion(exito=False, mensaje=resultado.stderr or resultado.stdout)
    return ResultadoEjecucion(exito=True, mensaje=None)
```

Pero `subprocess.run` **lanza `FileNotFoundError` antes de devolver un objeto con `returncode`** cuando el ejecutable no existe. El código nunca llega a la comprobación de `returncode`.

**Reproducción (verificada, en una máquina sin `amixer`):**

```python
with patch("src.acciones.ejecutor.platform.system", return_value="Linux"):
    ejecutar_accion(Accion.A1)
# FileNotFoundError: [Errno 2] No such file or directory: 'amixer'
```

**Por qué la suite no lo detecta:** los 11 tests de `tests/test_ejecutor.py` parchean `subprocess.run` con un `MagicMock`, que por construcción **nunca lanza `FileNotFoundError`**. El único camino de código que la spec declara explícitamente como caso borde obligatorio es, precisamente, el único que el mock hace inalcanzable. Es un falso verde: el test verifica la rama `returncode != 0`, no la rama "el binario no existe".

**Alcance real:** no es solo Linux. `osascript` no existe fuera de macOS, y un `PATH` recortado (contenedores, `launchd`, servicios) puede dejar sin `osascript` a un macOS real. Además, `subprocess.run` sin `timeout` puede bloquear el hilo del pipeline indefinidamente si `osascript` se cuelga esperando el diálogo de permisos de Accesibilidad — un riesgo ya identificado en 007/plan.md Sección 5 pero no cubierto en código.

## 2. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| ROB-FR-001 | `_run()` DEBE capturar `FileNotFoundError` (binario ausente del `PATH`) y traducirlo a `ResultadoEjecucion(exito=False, mensaje=...)`, con un mensaje que nombre el binario faltante y sugiera el paquete que lo provee (p. ej. `amixer` → `alsa-utils`). |
| ROB-FR-002 | `_run()` DEBE pasar `timeout=` a `subprocess.run` (valor por defecto: **2.0 s**, suficiente para `osascript`/`amixer`, que son de milisegundos) y capturar `subprocess.TimeoutExpired` → `exito=False`. Esto cierra el riesgo de `plan.md` 007 Sección 5 (un `osascript` colgado bloquea el loop y hunde el FPS por debajo de NFR-G01). |
| ROB-FR-003 | `_run()` DEBE capturar `OSError` de forma general (superclase de `FileNotFoundError` y `PermissionError`) como red de seguridad, de modo que **ninguna** excepción de `subprocess` pueda escapar de `ejecutar_accion()` (NFR-G02). |
| ROB-FR-004 | `ejecutar_accion()` DEBE mantener su contrato actual: no lanza nunca; todo fallo se reporta en `ResultadoEjecucion` (ACC-FR-005). ROB-FR-001..003 son la implementación real de ese contrato, que hoy solo se cumple parcialmente. |
| ROB-FR-005 | La suite DEBE incluir al menos un test que **no** parchee `subprocess.run` y ejercite el camino de binario ausente (p. ej. parcheando la lista de comandos a un ejecutable inexistente, o parcheando `subprocess.run` con `side_effect=FileNotFoundError`). Un mock que solo devuelve `returncode` no puede cubrir ROB-FR-001. |

## 3. Criterios de aceptación

- **Dado** `platform.system()` mockeado a `"Linux"` y un sistema **sin** `amixer` instalado, **cuando** se llama `ejecutar_accion(Accion.A1)`, **entonces** retorna `ResultadoEjecucion(exito=False)` con un mensaje que menciona `amixer`, y **no se lanza ninguna excepción** (este es el criterio literal de 007/spec.md Sección 5, hoy incumplido).
- **Dado** `subprocess.run` parcheado con `side_effect=subprocess.TimeoutExpired(cmd="osascript", timeout=2.0)`, **cuando** se llama `ejecutar_accion(Accion.A3)`, **entonces** `exito is False` y el mensaje indica timeout.
- **Dado** `subprocess.run` parcheado con `side_effect=PermissionError`, **cuando** se llama `ejecutar_accion(Accion.A1)`, **entonces** `exito is False` (ROB-FR-003), sin excepción propagada.
- **Dado** el pipeline completo corriendo (009) en una máquina donde el binario de audio no existe, **cuando** el usuario confirma `G1`, **entonces** el loop **continúa** (se loguea el fallo) en vez de entrar en el `except` de INT-FR-008 frame tras frame — US-6 end-to-end.

## 4. Casos borde

- **`ResultadoEjecucion.exito=False` y nadie lo mira:** hoy `main.py` llama `ejecutar_accion(ultima_accion)` y **descarta el valor de retorno**. ACC-FR-005 dice que en el MVP el fallo "se reporta, aunque no se actúa sobre él más allá de loguearlo" — pero el logueo no existe. Ver [013-conformidad-menor](../013-conformidad-menor/spec.md), CNF-FR-011: `main.py` debe al menos imprimir el `mensaje` cuando `exito` es `False`, o el reporte de ROB-FR-001 muere silenciosamente y el usuario ve "no pasa nada" sin diagnóstico.
- **Permiso de Accesibilidad denegado en macOS:** sigue siendo indistinguible por `returncode` (ya documentado en 007/spec.md Sección 5). Este spec **no** lo resuelve; solo garantiza que el proceso no muera y que un cuelgue tenga cota temporal (ROB-FR-002).

## 5. No objetivos

- No añade reintentos automáticos (fuera del MVP, igual que en 007).
- No añade un backend alternativo de Linux (`pactl`, `wpctl`) cuando `amixer` falta — solo reporta el fallo con un mensaje accionable. Un backend de respaldo es trabajo futuro, no corrección de conformidad.
