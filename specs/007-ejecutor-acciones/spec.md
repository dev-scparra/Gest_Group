# Spec 007 — Ejecutor de Acciones

**Módulo:** `src/acciones/ejecutor.py`
**Depende de:** [002-homomorfismo-analisis](../002-homomorfismo-analisis/spec.md) (recibe `Accion = φ(g)`).
**Consumido por:** [009-integracion-pipeline](../009-integracion-pipeline/spec.md).
**Cubre:** US-3, US-7 de [000-overview](../000-overview/spec.md).

---

## 1. Propósito

Traducir un valor `Accion` (elemento abstracto del grupo A) en un efecto observable del sistema operativo: cambiar el volumen, pausar/reanudar, cambiar de pista.

Este módulo es la frontera entre el modelo algebraico y el mundo real — es intencional que sea el módulo más simple de todos en términos de lógica (un `if/elif` por SO), porque su valor no está en la complejidad sino en ser el punto donde `φ(g)` deja de ser un símbolo y se vuelve un efecto.

## 2. Contrato de interfaz

**Entradas:** `accion: Accion` (del módulo 002).

**Salidas:** ninguna (efecto de lado, sin valor de retorno significativo más allá de éxito/fallo).

```python
def ejecutar_accion(accion: Accion) -> ResultadoEjecucion:
    """Ejecuta el efecto de SO correspondiente. No lanza excepción ante fallo del SO;
    lo reporta en ResultadoEjecucion (ver ACC-FR-005)."""
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| ACC-FR-001 | DEBE detectar el sistema operativo en tiempo de ejecución con `platform.system()` (`"Darwin"`, `"Linux"`, `"Windows"`). |
| ACC-FR-002 (revisado — corrección de foco) | En macOS, subir/bajar volumen DEBE usar `osascript` (`set volume output volume ...`), que es global. Pausa/play y siguiente/anterior **NO** deben usar `osascript ... key code` vía System Events: esa tecla se entrega a la ventana **en primer plano**, que al correr el pipeline es la ventana de OpenCV, no el reproductor — el resultado es que `osascript` devuelve éxito pero la acción no llega a Spotify/Music. DEBEN usar **teclas multimedia del sistema** (`NSSystemDefined`, subtype 8: `NX_KEYTYPE_PLAY=16`, `NX_KEYTYPE_NEXT=17`, `NX_KEYTYPE_PREVIOUS=18`) posteadas con `CGEventPost` vía PyObjC (`pyobjc-framework-Quartz`/`-Cocoa`, solo macOS). Estas son globales como el volumen, independientes del foco y del reproductor concreto. La redacción original (Sección 4.6 del documento de contexto, `key code`) queda reemplazada. Si PyObjC no está instalado, el ejecutor DEBE degradar reportando `exito=False` con una sugerencia, sin lanzar excepción (NFR-G02). |
| ACC-FR-003 | En Linux, DEBE implementar al menos subir/bajar volumen vía `amixer` (NFR-G05: soporte de segundo nivel — pausa/play y cambio de pista en Linux quedan fuera del MVP). |
| ACC-FR-004 | `Accion.A_E` (identidad) DEBE ser un no-op explícito (`return` inmediato), nunca debe intentar ejecutar un comando de SO. |
| ACC-FR-005 | DEBE reportar si el `subprocess.run` subyacente falló (código de retorno distinto de 0) en vez de asumir éxito silenciosamente — esto resuelve Q2 de `000-overview`: el fallo se reporta, aunque en el MVP no se actúa sobre ese reporte más allá de loguearlo (no hay reintento automático). |
| ACC-FR-006 | En Windows, DEBE implementar las 5 acciones no-identidad con paridad completa respecto a macOS (NFR-G05, revisado): subir/bajar volumen, pausa/play, siguiente/anterior pista. Implementación vía simulación de teclas multimedia virtuales de Windows (`ctypes.windll.user32.keybd_event` con `VK_VOLUME_UP=0xAF`, `VK_VOLUME_DOWN=0xAE`, `VK_MEDIA_PLAY_PAUSE=0xB3`, `VK_MEDIA_NEXT_TRACK=0xB0`, `VK_MEDIA_PREV_TRACK=0xB1`) — no requiere dependencias de terceros (`pycaw`/`comtypes` quedan descartadas: las teclas virtuales cubren las 5 acciones con una sola API de `ctypes`, mientras que `pycaw` solo cubriría volumen). |

## 4. Criterios de aceptación

- **Dado** `Accion.A_E`, **cuando** se llama `ejecutar_accion()`, **entonces** no se invoca ningún `subprocess`.
- **Dado** `Accion.A1` (subir volumen) en macOS, **cuando** se llama `ejecutar_accion()` con permiso de Accesibilidad concedido, **entonces** el volumen del sistema sube de forma verificable (checklist manual, no automatizable).
- **Dado** un `subprocess.run` mockeado que devuelve código de retorno distinto de 0, **cuando** se llama `ejecutar_accion()`, **entonces** `ResultadoEjecucion.exito` es `False` y se puede inspeccionar por qué (test automatizado, sin necesidad de macOS real).
- **Dado** `platform.system()` mockeado a `"Windows"`, **cuando** se llama `ejecutar_accion()` con cualquier acción no-identidad, **entonces** se invoca `keybd_event` con el código de tecla virtual correspondiente (verificable por mock, sin necesidad de Windows real) y `ResultadoEjecucion.exito` es `True`.

## 5. Casos borde

- **Permiso de Accesibilidad de macOS denegado:** `osascript` puede devolver éxito de proceso (código 0) pero sin efecto real, o puede fallar según la versión de macOS — este es un caso que **no se puede distinguir de forma confiable solo con el código de retorno**. Se documenta como riesgo conocido (no resoluble en código) y se agrega al checklist de instalación del README: verificar manualmente que el volumen cambia antes de dar la demo por lista.
- **`amixer` no instalado en Linux (no todas las distros lo traen por defecto):** DEBE producir un `ResultadoEjecucion.exito=False` con el mensaje de error del `subprocess` capturado, no una excepción no controlada que tumbe el pipeline completo (NFR-G02).
- **Comando de volumen con el volumen ya en el máximo/mínimo:** el incremento/decremento de 10 unidades (Sección 4.6 del documento de contexto) simplemente no tiene efecto adicional — comportamiento nativo del SO, no requiere lógica especial aquí.

## 6. No objetivos de este módulo

- No decide qué gesto produce qué acción (eso ya está resuelto cuando este módulo recibe la `Accion`; la decisión es de φ, módulo 002).
- No implementa un backend de Linux con paridad completa (pausa/play y cambio de pista en Linux quedan fuera del MVP, ver ACC-FR-003).
