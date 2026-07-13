# Spec 005 — Filtro EMA

**Módulo:** `src/preprocesamiento/filtro_ema.py`
**Depende de:** [004-deteccion-mediapipe](../004-deteccion-mediapipe/spec.md) (consume su salida, cuando no es `None`).
**Consumido por:** [006-clasificador-gestos](../006-clasificador-gestos/spec.md).
**Respalda:** Demostración 4 del documento de contexto (estabilidad asintótica) → SC-G05.

---

## 1. Propósito

Suavizar los 21 landmarks frame a frame con una media móvil exponencial, para que el clasificador geométrico (006) no reaccione al temblor de cámara/mano.

## 2. Contrato de interfaz

**Entradas:** `landmarks_raw: list[tuple[float,float,float]]` (21 elementos, salida de 004 cuando no es `None`), `alpha: float ∈ (0,1)`.

**Salidas:**

```python
class FiltroEMA:
    def __init__(self, alpha: float = 0.3, num_landmarks: int = 21): ...
    def aplicar(self, landmarks_raw: list[tuple[float,float,float]]) -> list[tuple[float,float,float]]: ...
    def reset(self) -> None: ...
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| EMA-FR-001 | DEBE implementar `x[n] = α·x_raw[n] + (1-α)·x[n-1]` independientemente para cada una de las 3 coordenadas de cada uno de los 21 landmarks (Sección 4.4 del documento de contexto). |
| EMA-FR-002 | En el primer frame tras instanciar o tras `reset()`, DEBE inicializar `x_prev` con el valor crudo tal cual (sin suavizado, porque no hay historia previa) — así lo fija el documento de contexto Sección 4.4. |
| EMA-FR-003 | `reset()` DEBE limpiarse explícitamente cuando 004 devuelve `None` (mano perdida) — si no se resetea, al reaparecer la mano el filtro mezclaría la posición anterior (de antes de perderse) con la nueva, produciendo un salto suavizado hacia una posición vieja irrelevante. Esta es una decisión de integración entre 004/005/006 que debe quedar explícita: **quien orquesta el pipeline (009) es responsable de llamar `reset()` cuando 004 devuelve `None`**, no este módulo por sí solo (no tiene forma de saberlo si no se le informa). |
| EMA-FR-004 | `alpha` DEBE ser configurable en la construcción, con valor por defecto 0.3 (recomendado en Sección 4.4 del documento de contexto). |
| EMA-FR-005 | DEBE aceptar cambiar `alpha` en caliente (setter o reconstrucción barata) para soportar US-4 (ajuste en vivo, P2). |

## 4. Criterios de aceptación

- **Dado** una señal de entrada constante `x_raw[n] = c` para todo n, **cuando** se aplica el filtro repetidamente, **entonces** la salida converge a `c` (test ya esbozado en Sección 10 del documento de contexto: `test_convergencia_ema`).
- **Dado** una señal con ruido gaussiano alrededor de un valor constante, **cuando** se compara la varianza de la señal cruda contra la suavizada, **entonces** la varianza suavizada es estrictamente menor (`test_estabilidad_ruido`).
- **Dado** que se llama `reset()` y luego se aplica un nuevo landmark, **cuando** se observa la salida, **entonces** es idéntica al valor crudo de entrada (EMA-FR-002, sin mezcla con historia anterior).
- **Dado** α cercano a 1, **cuando** se aplica el filtro, **entonces** la salida sigue de cerca la entrada cruda (poco retraso); **dado** α cercano a 0, **entonces** la salida cambia lentamente (Sección 4.4 del documento de contexto) — criterio cualitativo, útil para la demo de US-4, no un test numérico estricto.

## 5. Casos borde

- `alpha` fuera de `(0,1)` (p. ej. 0 o 1 o negativo): el documento de contexto no especifica manejo de error para esto. Se decide aquí: el constructor DEBE validar `0 < alpha < 1` y fallar explícitamente si no — con `alpha=0` el filtro nunca se movería del primer valor (inútil), con `alpha≥1` no hay suavizado real y con `alpha<0` la Demostración 4 (estabilidad) deja de sostenerse matemáticamente (la prueba requiere `|1-α|<1`).
- Landmarks con `NaN` o fuera de `[0,1]` (posible si MediaPipe extrapola una mano parcialmente fuera de cuadro, ver caso borde de 004): este módulo no valida ni corrige rangos, los suaviza tal cual — la responsabilidad de sanidad de rango, si se decide añadir, sería de 006 (clasificador), no de este filtro genérico.

## 6. No objetivos de este módulo

- No decide cuándo llamar `reset()` (esa decisión de orquestación es de 009, ver EMA-FR-003).
- No sabe nada de gestos ni de qué landmark corresponde a qué dedo — trata los 21 puntos de forma uniforme.
