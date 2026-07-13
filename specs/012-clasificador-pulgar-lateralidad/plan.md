# Plan 012 — Clasificador: Pulgar, Puño y Lateralidad

**Depende de:** [spec.md](./spec.md). **Implementa la Decisión D2** (proyección sobre el eje de la palma), no el signo condicionado a la lateralidad que proponía la primera versión de este plan.

## 1. Cambios por archivo

| Archivo | Cambio |
|---|---|
| `src/clasificador/gestos.py` | `_pulgar_levantado(coords)` por proyección sobre el eje meñique→índice; constante `UMBRAL_PULGAR`; tabla reordenada y documentada (spec 012, Sección 5). |
| `src/deteccion/mediapipe_handler.py` | Método `lateralidad() -> str \| None` + `SCORE_LATERALIDAD_MINIMO` (PUL-FR-001). Diagnóstico, no lo consume el clasificador. |
| `tests/fixtures_landmarks.py` | Mano geométricamente plausible (nudillos separados) + parámetro `lateralidad` que espeja el eje x. |
| `tests/test_clasificador.py` | `G1`..`G5` y `E` parametrizados sobre `["Right", "Left"]`; puño con pulgar en el margen; palma degenerada. |
| `scripts/smoke_vision.py` | Imprime lateralidad + gesto + dedos por segundo, para la verificación de campo (T012-11). |

`src/main.py` **no cambia** por esta spec: la firma `clasificar_gesto(coords)` se mantiene, porque con D2 la orientación se deriva de `coords` y no hace falta inyectar la lateralidad.

## 2. Notas de implementación

```python
PULGAR_PUNTA, PULGAR_MCP = 4, 2
INDICE_MCP, MENIQUE_MCP = 5, 17
UMBRAL_PULGAR = 0.15   # fraccion del ancho de la palma (PUL-FR-005)


def _pulgar_levantado(coords) -> bool:
    eje_x = coords[INDICE_MCP][0] - coords[MENIQUE_MCP][0]
    eje_y = coords[INDICE_MCP][1] - coords[MENIQUE_MCP][1]
    ancho_palma = math.hypot(eje_x, eje_y)
    if ancho_palma < 1e-9:
        return False                                   # PUL-FR-006
    dx = coords[PULGAR_PUNTA][0] - coords[PULGAR_MCP][0]
    dy = coords[PULGAR_PUNTA][1] - coords[PULGAR_MCP][1]
    proyeccion = (dx * eje_x + dy * eje_y) / ancho_palma
    return proyeccion / ancho_palma > UMBRAL_PULGAR    # normalizada por el ancho
```

**Por qué esto no necesita cámara para ser correcto** (y el enfoque anterior sí): el único hecho externo del que depende es que el landmark 5 es el nudillo del índice y el 17 el del meñique — topología fija y documentada de MediaPipe. El enfoque anterior dependía de la convención de etiquetado `"Left"`/`"Right"` de MediaPipe *cruzada* con el `cv2.flip` de 003, que es una cadena de dos convenciones que solo se puede resolver midiendo. Esa era la constante que hacía de T012-01 un bloqueante; D2 la elimina.

## 3. Estrategia de pruebas

Los fixtures anteriores colapsaban todos los MCP en `(0.5, 0.6)`: bastaban para la comparación cruda de `x`, pero dejan el eje de la palma **indefinido** (ancho cero), así que hay que construir una mano plausible con los nudillos separados. El espejado (`x → 1-x`) es la sonda que reproduce el defecto:

```python
@pytest.mark.parametrize("lateralidad", ["Right", "Left"])
def test_mano_abierta_es_g4(lateralidad):
    assert clasificar_gesto(generar_landmark_mano_abierta(lateralidad)) == Gesto.G4
```

**Verificación de que la sonda muerde** (hecha, no prometida): corriendo el clasificador **anterior** contra los fixtures nuevos, los tres casos de la mano que fallaba dan `puño → G5`, `mano abierta → E`, `solo pulgar → G3` — el intercambio G3↔G5 exacto que describe la Sección 1 de `spec.md`. Con el clasificador nuevo, los 6 casos (3 gestos × 2 manos) pasan.

## 4. Riesgo de la corrección

**Bajo tras D2** (era medio-alto con el enfoque de signo por lateralidad). No queda ninguna constante cuyo valor correcto haya que adivinar: la orientación se deriva de la geometría.

El riesgo residual es la calibración de `UMBRAL_PULGAR = 0.15`, que es una estimación razonada, no una medición. Demasiado alto → `G5` cuesta de disparar; demasiado bajo → vuelve la confusión `G3`/`G5` en el puño. Calibrar en T012-10 con cámara real. A diferencia del signo, equivocar el umbral produce un fallo **gradual y visible** (el gesto no dispara), no un fallo silencioso que ejecuta la acción de otro gesto — que es por lo que ya no bloquea.
