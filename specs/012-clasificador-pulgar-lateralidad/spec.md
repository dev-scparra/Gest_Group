# Spec 012 — Clasificador: Pulgar, Puño y Lateralidad de la Mano

**Módulos:** `src/clasificador/gestos.py` (006), `src/deteccion/mediapipe_handler.py` (004).
**Origen:** auditoría de conformidad specs↔código (2026-07-13).
**Severidad:** **ALTA** — con la mano "equivocada", dos gestos disparan **la acción de otro gesto** (no fallan: aciertan mal). Impacta SC-G01 (≥90% de aciertos) y US-3 (los 6 gestos producen las 6 acciones).
**Requerimientos afectados:** CLA-FR-002, CLA-FR-003 (006); DET-FR-005 (004).

---

## 1. Problema A — la heurística del pulgar solo es válida para una de las dos manos

`dedos_levantados()` decide que el pulgar está levantado con una comparación de signo fijo (CLA-FR-002, heredada del esbozo de la Sección 4.5 del documento de contexto):

```python
if punta == 4:                                    # pulgar
    levantado = coords[punta][0] < coords[mcp][0]  # x_punta < x_mcp
```

`x_punta < x_mcp` significa "la punta del pulgar está a la izquierda de su nudillo **en la imagen**". Pero el pulgar de una mano se extiende hacia la izquierda y el de la otra hacia la derecha: **el signo correcto de esa desigualdad depende de la lateralidad de la mano** (y, encima, `CAP-FR-002` espeja el frame con `cv2.flip`, lo que invierte la lateralidad aparente respecto a la mano física del usuario). El código fija un solo signo, así que la prueba del pulgar es correcta para una mano e **invertida** para la otra.

Como `G3`, `G4` y `G5` son exactamente los tres gestos que dependen del pulgar, el resultado no es una degradación suave, sino una permutación de gestos. **Verificado** ejecutando el clasificador sobre los fixtures existentes y sobre los mismos fixtures espejados (`x → 1-x`, que es justamente lo que cambia entre una mano y la otra):

| Pose del usuario | Mano que funciona | Mano opuesta | Consecuencia con la mano opuesta |
|---|---|---|---|
| Mano abierta | `G4` ✅ | **`E`** | `G4` (siguiente pista) es **inalcanzable** |
| Solo pulgar | `G5` ✅ | **`G3`** | dispara **pausa/play** en vez de pista anterior |
| Puño | `G3` ✅ | **`G5`** | dispara **pista anterior** en vez de pausa/play |

`G3` y `G5` **se intercambian silenciosamente**. Esto es peor que un fallo: el sistema responde con seguridad y ejecuta la acción equivocada, y el usuario no tiene forma de saber por qué. En una demo ante el profesor, basta con que quien presenta levante la mano contraria a la que se usó para probar.

Ningún requerimiento de 004 ni de 006 menciona la lateralidad. MediaPipe **sí** la expone (`results.multi_handedness`, con etiqueta `"Left"`/`"Right"` y su score), pero `DetectorManos` solo propaga `multi_hand_landmarks` (DET-FR-005), de modo que 006 no tiene el dato aunque quisiera usarlo.

## 2. Problema B — la tabla 4.5 del documento de contexto es contradictoria (`G3` vs `G5`)

La tabla de clasificación de la Sección 4.5 del documento de contexto lista:

| Pulgar | Índice | Medio | Anular | Meñique | Gesto |
|---|---|---|---|---|---|
| **-** | F | F | F | F | g₃ (puño) |
| **T** | F | F | F | F | g₅ (pulgar) |

La fila de `g₅` es un **caso particular** de la fila de `g₃` (que declara el pulgar como "no importa"). Son incompatibles: una entrada con pulgar arriba y el resto abajo satisface ambas. El esbozo de código de esa misma sección resuelve el empate a favor de `g₃` comprobándolo primero, lo que deja **`g₅` inalcanzable** — un gesto muerto de los seis.

La implementación **detectó y corrigió** este error (comprueba `G5` antes que `G3`, con un comentario que lo explica), lo cual es correcto. Pero la corrección **cambió la semántica de `G3`**: el puño ya no es "pulgar indiferente", ahora exige **pulgar abajo**. Esa decisión no está registrada en ninguna spec — `CLA-FR-003` sigue diciendo "según la tabla de la Sección 4.5", es decir, apunta a la tabla contradictoria.

Consecuencia práctica sobre la mano que *sí* funciona: en un puño natural el pulgar se pliega **por encima** de los otros dedos, así que `x_punta` y `x_mcp` quedan casi pegados y el signo de la comparación depende del ruido. `G3` (pausa/play) y `G5` (anterior) están a un píxel de distancia el uno del otro, sin histéresis. El filtro EMA (005) y el debounce (006) suavizan el temblor, pero **no** rescatan una frontera de decisión mal elegida: si la media de `x_punta - x_mcp` cae del lado equivocado, el gesto se confirma establemente **como el gesto equivocado**.

## 3. Decisión D2 (tomada en implementación) — orientar por la geometría de la palma, no por la etiqueta de lateralidad

La primera versión de esta spec resolvía el Problema A **condicionando el signo de la comparación a la lateralidad** que reporta MediaPipe: `dx < 0` para una mano, `dx > 0` para la otra. Su propio `plan.md` marcaba ese signo como el mayor riesgo del cambio y hacía de T012-01 (medirlo con cámara) una tarea **bloqueante**, porque la correspondencia entre la etiqueta `"Left"`/`"Right"` y el signo de `dx` depende de la convención de MediaPipe *y* del `cv2.flip` de 003, y equivocarse produce un sistema que pasa todos los tests sintéticos —los fixtures heredarían la misma convención errónea— y falla en cámara **con las dos manos** en vez de con una.

Ese riesgo es evitable. **La orientación no hace falta pedírsela a MediaPipe: está en la propia mano.** El vector que va del MCP del meñique (landmark 17) al MCP del índice (landmark 5) recorre la línea de los nudillos y apunta, por anatomía, hacia el lado del pulgar — y eso es cierto para las dos manos, esté el frame espejado o no. Proyectando `(punta − MCP)` del pulgar sobre ese eje y normalizando por el ancho de la palma se obtiene un escalar que es **invariante a la lateralidad, al espejado y a la rotación de la mano en el plano**, y además adimensional (independiente de la distancia a la cámara):

```
proyección = ((punta₄ − MCP₂) · (MCP₅ − MCP₁₇)) / |MCP₅ − MCP₁₇|²
pulgar levantado  ⟺  proyección > UMBRAL_PULGAR
```

**Se adopta esta formulación** en vez del signo condicionado a la lateralidad. Elimina por completo la constante no verificable que hacía de T012-01 un bloqueante, y reemplaza un hecho que había que medir (la convención de etiquetado de MediaPipe cruzada con el espejo) por un hecho de topología que es fijo y documentado (el landmark 5 es el nudillo del índice, el 17 el del meñique). Es, además, estrictamente más robusto: sobrevive a que el usuario incline la mano, cosa que la comparación en `x` no hace.

La lateralidad se sigue exponiendo en 004 (PUL-FR-001) porque es útil como diagnóstico y como base de un futuro soporte de dos manos, pero **el clasificador ya no depende de ella**.

## 4. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| PUL-FR-001 | **Amplía DET-FR-005.** `DetectorManos` DEBE exponer la lateralidad detectada por MediaPipe (`multi_handedness[0].classification[0].label` → `"Left"` / `"Right"`) de la primera mano, o `None` si no hay mano o el score es bajo. Tras la Decisión D2 el clasificador **no** la consume; se expone como diagnóstico (`scripts/smoke_vision.py`) y para el futuro soporte de dos manos. |
| PUL-FR-002 (revisado por D2) | **Revisa CLA-FR-002.** La detección del pulgar DEBE hacerse por **proyección sobre el eje de la palma** (meñique→índice), según la fórmula de la Sección 3 — no por comparación cruda de `x`, que solo es válida para una de las dos manos, y no por un signo condicionado a la lateralidad, que introduce una constante que no se puede verificar sin cámara. La firma `dedos_levantados(coords)` **no cambia**: la orientación se deriva de `coords`. |
| PUL-FR-003 (revisado por D2) | La convención de espejado deja de ser relevante para el clasificador: la proyección de PUL-FR-002 es invariante al `cv2.flip` de CAP-FR-002. Para el dato de lateralidad de PUL-FR-001, la etiqueta se toma tal como MediaPipe la reporta sobre el frame ya espejado (que es la convención de "selfie" que MediaPipe asume), **sin des-espejarla**. |
| PUL-FR-004 | **Reemplaza la tabla de la Sección 4.5** del documento de contexto por la tabla desambiguada de la Sección 5 de esta spec, que es total y sin solapamientos. `CLA-FR-003` DEBE citar esta tabla, no la del documento de contexto. |
| PUL-FR-005 (revisado por D2) | La distinción `G3` (puño) vs `G5` (pulgar) DEBE tener un **margen mínimo**: el pulgar cuenta como levantado solo si la proyección normalizada supera `UMBRAL_PULGAR` (valor inicial: `0.15`, es decir, un 15% del ancho de la palma; a calibrar en T012-10). Por debajo del umbral, el pulgar cuenta como **no levantado** (→ `G3`, el puño, que es el caso mayoritario y la degradación segura). Al ser relativo al ancho de la palma, el umbral no depende de la distancia de la mano a la cámara — a diferencia del `0.03` en coordenadas absolutas que proponía la versión anterior. Esto sustituye la comparación estricta sin epsilon que 006/spec.md Sección 5 declaró suficiente: declaración válida para el eje `y` de los otros cuatro dedos, pero **no** para el pulgar de un puño cerrado, donde la casi-igualdad es la norma y no la excepción. |
| PUL-FR-006 (revisado por D2) | Cuando el eje de la palma sea degenerado (`|MCP₅ − MCP₁₇| ≈ 0`, landmarks corruptos), `dedos_levantados()` DEBE tratar el pulgar como **no levantado**, degradando a la familia `{G3, G1, G2}` en vez de adivinar. Nunca lanzar excepción (CLA-FR-004 sigue vigente). |
| PUL-FR-007 | Los fixtures de test DEBEN cubrir **ambas lateralidades** para los tres gestos que dependen del pulgar (`G3`, `G4`, `G5`), espejando el eje `x`. La suite anterior solo generaba una, que es exactamente por lo que este defecto pasó 60 tests en verde. Los fixtures DEBEN además tener geometría de mano plausible (nudillos separados): los anteriores colapsaban todos los MCP en `(0.5, 0.6)`, lo que deja el eje de la palma indefinido y haría inmedible la proyección de PUL-FR-002. |

## 5. Tabla de clasificación desambiguada (reemplaza la Sección 4.5 del doc. de contexto)

Evaluada **en orden**; la primera fila que calza gana. `-` = indiferente.

| # | Pulgar | Índice | Medio | Anular | Meñique | Gesto | φ(g) |
|---|---|---|---|---|---|---|---|
| 1 | **T** | F | F | F | F | `G5` (pulgar) | anterior |
| 2 | **F** | F | F | F | F | `G3` (puño) | pausa/play |
| 3 | - | T | F | F | F | `G1` (1 dedo) | subir volumen |
| 4 | - | T | T | F | F | `G2` (2 dedos) | bajar volumen |
| 5 | T | T | T | T | T | `G4` (mano abierta) | siguiente |
| 6 | *cualquier otra combinación* | | | | | `E` (reposo) | ninguna |

Cambios respecto a la tabla original: la fila de `G5` sube al primer lugar (si no, es inalcanzable) y la de `G3` pasa de "pulgar indiferente" a **"pulgar abajo"** explícito. Las filas 3 y 4 conservan el pulgar como indiferente (un `G1` con el pulgar afuera sigue siendo `G1`), tal como en el original. Esta tabla ya coincide con lo que el código hace hoy — lo que falta es que una spec lo diga.

## 6. Criterios de aceptación

- **Dado** los fixtures de mano abierta, puño y solo-pulgar generados para **ambas** lateralidades, **cuando** se llama `clasificar_gesto(coords)`, **entonces** se obtiene `G4`, `G3` y `G5` respectivamente **en las dos** (PUL-FR-002, PUL-FR-007). ✅ **Verificado:** contra el clasificador anterior, esos mismos fixtures daban `E`, `G5` y `G3` en la mano que fallaba — los 3 casos fallan antes del fix y pasan después.
- **Dado** un puño con el pulgar plegado sobre los dedos (proyección normalizada `< UMBRAL_PULGAR`), **cuando** se clasifica, **entonces** el resultado es `G3` y **nunca** `G5` (PUL-FR-005). ✅ **Verificado** en `tests/test_clasificador.py`, parametrizado sobre ambas manos.
- **Dado** landmarks con el eje de la palma degenerado, **cuando** se clasifica, **entonces** el pulgar cuenta como abajo y no se lanza excepción (PUL-FR-006). ✅ **Verificado.**
- **Dado** el pipeline con cámara real, **cuando** el usuario ejecuta los 5 gestos no-identidad **con cada mano**, **entonces** las 5 acciones se disparan correctamente con ambas (US-3 + SC-G01). ⬜ **Pendiente:** verificación de campo, T012-11 — requiere cámara y una persona delante.

## 7. Casos borde

- **Mano de perfil:** 006/spec.md Sección 5 ya lo declara fuera de alcance del MVP. Esta spec **no** lo cambia. La proyección de D2 tolera la rotación de la mano *en el plano de la imagen*, pero no una mano girada 90° en profundidad, donde el eje meñique→índice se contrae hacia cero y `UMBRAL_PULGAR` deja de tener margen — cae en PUL-FR-006 (pulgar abajo), que es la degradación segura.
- **Pulgar "hacia arriba" literal (mano rotada, pulgar apuntando al techo):** el modelo del proyecto asume el pulgar **extendido lateralmente** con la palma de frente, no el gesto de "like" con la mano girada. Igual que en la versión original de la heurística, esa pose queda fuera de alcance (limitación de uso, no defecto).
- **Usuario que cambia de mano a mitad de sesión:** con D2 no hay estado de lateralidad que arrastrar, así que el cambio se absorbe solo. El debounce (006) verá un gesto distinto durante la transición y reiniciará su contador — comportamiento correcto, sin acción requerida.

## 8. No objetivos

- No se implementa normalización 3D con el landmark `z` ni rotación canónica de la mano (fuera de alcance del MVP, igual que en 006).
- No se soportan dos manos simultáneas (`max_num_hands=1`, DET-FR-001 sigue vigente): la lateralidad se lee de la primera y única mano.
