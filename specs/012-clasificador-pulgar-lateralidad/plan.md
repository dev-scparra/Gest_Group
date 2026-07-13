# Plan 012 — Clasificador: Pulgar, Puño y Lateralidad

**Depende de:** [spec.md](./spec.md).

## 1. Cambios por archivo

| Archivo | Cambio |
|---|---|
| `src/deteccion/mediapipe_handler.py` | Guardar la lateralidad del resultado de MediaPipe; nuevo método `lateralidad() -> str \| None` (PUL-FR-001, PUL-FR-003). |
| `src/clasificador/gestos.py` | `dedos_levantados(coords, lateralidad)` y `clasificar_gesto(coords, lateralidad)`; constante `EPSILON_PULGAR`; reordenar la tabla según 012/spec.md Sección 4 (ya está reordenada — se conserva y se documenta). |
| `src/main.py` | Pasar `detector.lateralidad()` a `clasificar_gesto()`. Con 011 aplicado, el cambio vive en `procesar_frame()`. |
| `tests/fixtures_landmarks.py` | `generar_landmarks(..., lateralidad="Right")` que espeje el eje x cuando corresponda (PUL-FR-007). |
| `tests/test_clasificador.py` | Parametrizar los tests de `G3`/`G4`/`G5` sobre ambas lateralidades; test de puño con pulgar en el margen (PUL-FR-005); test de `lateralidad=None` (PUL-FR-006). |

## 2. Notas de implementación

### Lateralidad en 004

```python
def procesar(self, frame_rgb):
    ...
    self._ultimo_resultado = resultados
    if not resultados.multi_hand_landmarks:
        return None
    ...

def lateralidad(self) -> str | None:
    """'Left' / 'Right' segun MediaPipe, sobre el frame YA espejado (PUL-FR-003),
    o None si no hay mano o el score es bajo (PUL-FR-006)."""
    r = self._ultimo_resultado
    if r is None or not r.multi_handedness:
        return None
    clasificacion = r.multi_handedness[0].classification[0]
    if clasificacion.score < SCORE_LATERALIDAD_MINIMO:   # 0.8
        return None
    return clasificacion.label
```

### Signo del pulgar en 006

El punto delicado: **no basta con invertir el signo, hay que anclarlo a algo**. La formulación robusta no es "x_punta < x_mcp" ni su inverso, sino "**la punta se aleja del centro de la palma**". El signo se deriva de la lateralidad una sola vez:

```python
EPSILON_PULGAR = 0.03   # margen minimo en coords normalizadas (PUL-FR-005)

def _pulgar_levantado(coords, lateralidad) -> bool:
    if lateralidad is None:
        return False                       # degradacion segura (PUL-FR-006)
    dx = coords[4][0] - coords[2][0]       # punta - MCP, con signo
    if abs(dx) < EPSILON_PULGAR:
        return False                       # puno con el pulgar plegado -> G3 (PUL-FR-005)
    # En el frame espejado, el pulgar de una "Right" se extiende hacia -x y el de
    # una "Left" hacia +x. Fijar esta correspondencia EMPIRICAMENTE en T012-01
    # antes de escribir la linea de abajo — invertirla es el error mas facil de
    # cometer aqui y el mas dificil de ver en un test que use fixtures sinteticos.
    return dx < 0 if lateralidad == "Right" else dx > 0
```

**Advertencia de método (T012-01 es bloqueante):** la correspondencia entre la etiqueta de MediaPipe y el signo de `dx` **no se puede deducir sentado**; depende de la convención de MediaPipe *y* del `cv2.flip` de 003, y equivocarse produce un sistema que pasa todos los tests sintéticos (porque los fixtures se generarían con la misma convención equivocada) y falla en cámara con las dos manos. Hay que medirla una vez, con `scripts/smoke_vision.py`, imprimiendo `lateralidad` y `dx` con cada mano frente a la cámara, y **anotar el resultado observado en un comentario del código**. Todo lo demás en esta corrección es mecánico; esto no.

## 3. Estrategia de pruebas

El fixture espejado es el corazón de la suite nueva: es literalmente la sonda con la que se descubrió el defecto.

```python
def generar_landmarks(pulgar, indice, medio, anular, menique, lateralidad="Right"):
    lms = _construir(pulgar, indice, medio, anular, menique)   # convencion "Right"
    if lateralidad == "Left":
        lms = [(1.0 - x, y, z) for (x, y, z) in lms]           # espejo en x
    return lms


@pytest.mark.parametrize("lateralidad", ["Right", "Left"])
def test_mano_abierta_es_g4_con_ambas_manos(lateralidad):
    coords = generar_landmark_mano_abierta(lateralidad)
    assert clasificar_gesto(coords, lateralidad) == Gesto.G4
```

Contra el código actual (firma sin `lateralidad`), la variante `"Left"` de `G4` devuelve `E`, la de `G5` devuelve `G3` y la de `G3` devuelve `G5` — los tres tests nuevos deben **fallar antes** del fix. Si alguno pasa a la primera, el fixture no está espejando de verdad.

Test del margen (PUL-FR-005), que no depende de la lateralidad:

```python
def test_puno_con_pulgar_plegado_no_se_confunde_con_g5():
    coords = generar_landmark_puno()
    coords[4] = (coords[2][0] - 0.01, coords[4][1], coords[4][2])   # dx = -0.01 < EPSILON
    assert clasificar_gesto(coords, "Right") == Gesto.G3            # no G5
```

## 4. Riesgo de la corrección

**Medio-alto**, y concentrado en un solo sitio: el signo de PUL-FR-002. El resto (propagar `lateralidad` por tres funciones, parametrizar fixtures) es mecánico y de bajo riesgo. Un signo invertido no rompe ningún test sintético — solo la demo. De ahí que T012-01 (medición con cámara real) sea **bloqueante y previa** a T012-03, y no una tarea de verificación al final.

Riesgo secundario: `EPSILON_PULGAR = 0.03` es una estimación, no una medición. Si queda demasiado alto, `G5` (pulgar extendido) se vuelve difícil de disparar; demasiado bajo, y vuelve la confusión `G3`/`G5` del puño. Calibrar en T012-06 con la cámara real, no a ojo.
