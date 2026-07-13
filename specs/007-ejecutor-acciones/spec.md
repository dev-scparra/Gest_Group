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
| ACC-FR-002 | En macOS, DEBE implementar las 5 acciones no-identidad vía `osascript` tal como se define en la Sección 4.6 del documento de contexto: subir/bajar volumen (`set volume output volume ...`), pausa/play y siguiente/anterior (`key code` vía System Events). |
| ACC-FR-003 | En Linux, DEBE implementar al menos subir/bajar volumen vía `amixer` (NFR-G05: soporte de segundo nivel — pausa/play y cambio de pista en Linux quedan fuera del MVP). |
| ACC-FR-004 | `Accion.A_E` (identidad) DEBE ser un no-op explícito (`return` inmediato), nunca debe intentar ejecutar un comando de SO. |
| ACC-FR-005 | DEBE reportar si el `subprocess.run` subyacente falló (código de retorno distinto de 0) en vez de asumir éxito silenciosamente — esto resuelve Q2 de `000-overview`: el fallo se reporta, aunque en el MVP no se actúa sobre ese reporte más allá de loguearlo (no hay reintento automático). |
| ACC-FR-006 | En Windows, el módulo puede no implementar ningún efecto real (`NotImplementedError` o no-op documentado) — Windows es explícitamente fuera de alcance del MVP (NFR-G05). No debe fingir éxito. |

## 4. Criterios de aceptación

- **Dado** `Accion.A_E`, **cuando** se llama `ejecutar_accion()`, **entonces** no se invoca ningún `subprocess`.
- **Dado** `Accion.A1` (subir volumen) en macOS, **cuando** se llama `ejecutar_accion()` con permiso de Accesibilidad concedido, **entonces** el volumen del sistema sube de forma verificable (checklist manual, no automatizable).
- **Dado** un `subprocess.run` mockeado que devuelve código de retorno distinto de 0, **cuando** se llama `ejecutar_accion()`, **entonces** `ResultadoEjecucion.exito` es `False` y se puede inspeccionar por qué (test automatizado, sin necesidad de macOS real).
- **Dado** `platform.system()` mockeado a `"Windows"`, **cuando** se llama `ejecutar_accion()` con cualquier acción no-identidad, **entonces** el comportamiento documentado (no-op o `NotImplementedError`) es explícito y testeable, no un fallo silencioso ambiguo.

## 5. Casos borde

- **Permiso de Accesibilidad de macOS denegado:** `osascript` puede devolver éxito de proceso (código 0) pero sin efecto real, o puede fallar según la versión de macOS — este es un caso que **no se puede distinguir de forma confiable solo con el código de retorno**. Se documenta como riesgo conocido (no resoluble en código) y se agrega al checklist de instalación del README: verificar manualmente que el volumen cambia antes de dar la demo por lista.
- **`amixer` no instalado en Linux (no todas las distros lo traen por defecto):** DEBE producir un `ResultadoEjecucion.exito=False` con el mensaje de error del `subprocess` capturado, no una excepción no controlada que tumbe el pipeline completo (NFR-G02).
- **Comando de volumen con el volumen ya en el máximo/mínimo:** el incremento/decremento de 10 unidades (Sección 4.6 del documento de contexto) simplemente no tiene efecto adicional — comportamiento nativo del SO, no requiere lógica especial aquí.

## 6. No objetivos de este módulo

- No decide qué gesto produce qué acción (eso ya está resuelto quand este módulo recibe la `Accion`; la decisión es de φ, módulo 002).
- No implementa Windows de forma completa (ver ACC-FR-006 y NFR-G05).
