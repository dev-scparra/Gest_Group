# Spec 004 — Detección de Landmarks (MediaPipe)

**Módulo:** `src/deteccion/mediapipe_handler.py`
**Depende de:** [003-captura-video](../003-captura-video/spec.md) (consume su salida RGB).
**Consumido por:** [005-filtro-ema](../005-filtro-ema/spec.md).

---

## 1. Propósito

Envolver `mediapipe.solutions.hands` para convertir un frame RGB en, a lo sumo, una lista de 21 landmarks normalizados de una mano, o `None` si no se detecta ninguna.

## 2. Contrato de interfaz

**Entradas:** `frame_rgb: np.ndarray` (salida de 003).

**Salidas:**

```python
class DetectorManos:
    def __init__(self, min_detection_confidence: float = 0.7, min_tracking_confidence: float = 0.5): ...
    def procesar(self, frame_rgb: np.ndarray) -> list[tuple[float,float,float]] | None:
        """21 tuplas (x,y,z) normalizadas en [0,1], o None si no hay mano."""
    def landmarks_para_dibujo(self):
        """Expone el objeto crudo de MediaPipe (para 008, que necesita mp_drawing.draw_landmarks)."""
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| DET-FR-001 | DEBE configurar MediaPipe Hands con `static_image_mode=False`, `max_num_hands=1` (fuera de alcance del MVP: dos manos — ver 000-overview). |
| DET-FR-002 | DEBE devolver exactamente 21 tuplas `(x,y,z)` normalizadas en `[0,1]` cuando se detecta una mano. |
| DET-FR-003 | DEBE devolver `None` (no lista vacía, no excepción) cuando no se detecta ninguna mano en el frame. |
| DET-FR-004 | Si `results.multi_hand_landmarks` contiene más de una mano (no debería, por `max_num_hands=1`, pero MediaPipe lo permite estructuralmente), DEBE usar únicamente la primera y text ignorar el resto — consistente con FR-013 de la spec original y US-6. |
| DET-FR-005 | DEBE exponer, además de las coordenadas puras, el objeto de landmarks crudo de MediaPipe (`NormalizedLandmarkList`) para que el módulo de visualización (008) pueda dibujarlo con `mp_drawing.draw_landmarks` sin que 004 dependa de lógica de dibujo. |

## 4. Criterios de aceptación

- **Dado** un frame RGB con una mano claramente visible y bien iluminada, **cuando** se llama `procesar()`, **entonces** se obtiene una lista de 21 tuplas, cada valor en `[0,1]`.
- **Dado** un frame RGB sin mano (p. ej. una pared vacía), **cuando** se llama `procesar()`, **entonces** se obtiene `None`.
- **Dado** un frame RGB corrupto o de dimensiones inesperadas, **cuando** se llama `procesar()`, **entonces** no se lanza una excepción no controlada hacia el llamador (NFR-G02) — se documenta como `None` o se deja que la excepción de MediaPipe se capture explícitamente y se traduzca a `None`.

## 5. Casos borde

- Mano parcialmente fuera del cuadro: MediaPipe puede devolver landmarks igualmente (extrapolados) o `None`, dependiendo de cuánta mano sea visible — este módulo no corrige ni valida esa ambigüedad, la pasa tal cual a 005/006 (su corrección es responsabilidad del filtro EMA y del debounce del clasificador, no de la detección).
- Cambio brusco de iluminación entre frames: puede causar detección intermitente (mano detectada un frame, `None` el siguiente, detectada de nuevo) — este es precisamente el ruido que 005 (filtro EMA) y el `reset()` en pérdida de mano existen para mitigar; no se resuelve aquí.

## 6. No objetivos de este módulo

- No suaviza coordenadas (eso es 005).
- No decide qué gesto representan los landmarks (eso es 006).
