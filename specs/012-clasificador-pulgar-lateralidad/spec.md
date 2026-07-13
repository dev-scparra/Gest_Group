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

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| PUL-FR-001 | **Amplía DET-FR-005.** `DetectorManos` DEBE exponer la lateralidad detectada por MediaPipe (`results.multi_handedness[0].classification[0].label` → `"Left"` / `"Right"`) de la primera mano, o `None` si no hay mano. Sin este dato, PUL-FR-002 es inimplementable. |
| PUL-FR-002 | **Revisa CLA-FR-002.** `dedos_levantados()` DEBE recibir la lateralidad y **orientar el signo de la comparación del pulgar** en consecuencia: la punta se considera levantada cuando se aleja del centro de la palma en el eje x, lo que corresponde a `x_punta < x_mcp` para una lateralidad y `x_punta > x_mcp` para la otra. La firma pasa a `dedos_levantados(coords, lateralidad)`. |
| PUL-FR-003 | La lateralidad DEBE determinarse a partir del frame **ya espejado** (el que 004 recibe de 003 tras `cv2.flip`, CAP-FR-002), no de la mano física del usuario. Es decir: se usa la etiqueta que MediaPipe reporta sobre el frame que efectivamente procesó, sin "des-espejarla". Fijar esta convención por escrito evita el error de signo doble (corregir el espejo dos veces deja el bug intacto). |
| PUL-FR-004 | **Reemplaza la tabla de la Sección 4.5** del documento de contexto por la tabla desambiguada de la Sección 4 de esta spec, que es total y sin solapamientos. `CLA-FR-003` DEBE citar esta tabla, no la del documento de contexto. |
| PUL-FR-005 | La distinción `G3` (puño) vs `G5` (pulgar) DEBE tener un **margen mínimo**: el pulgar se considera levantado solo si `|x_punta - x_mcp|` supera un umbral `EPSILON_PULGAR` (valor inicial sugerido: `0.03` en coordenadas normalizadas, a calibrar en T012-06); por debajo del umbral, el pulgar cuenta como **no levantado** (→ `G3`, el puño, que es el caso mayoritario y la degradación segura). Esto sustituye la comparación estricta sin epsilon que 006/spec.md Sección 5 declaró suficiente — declaración válida para el eje `y` de los otros cuatro dedos, pero **no** para el pulgar de un puño cerrado, donde la casi-igualdad es la norma y no la excepción. |
| PUL-FR-006 | Cuando la lateralidad no esté disponible (`None`: MediaPipe no la reporta, o score muy bajo), `dedos_levantados()` DEBE tratar el pulgar como **no levantado**, degradando a la familia `{G3, G1, G2}` en vez de adivinar un signo. Nunca lanzar excepción (CLA-FR-004 sigue vigente). |
| PUL-FR-007 | Los fixtures de test DEBEN cubrir **ambas lateralidades** para los tres gestos que dependen del pulgar (`G3`, `G4`, `G5`). La suite actual solo genera una, que es exactamente por lo que este defecto pasó 60 tests en verde. |

## 4. Tabla de clasificación desambiguada (reemplaza la Sección 4.5 del doc. de contexto)

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

## 5. Criterios de aceptación

- **Dado** los fixtures de mano abierta, puño y solo-pulgar generados para **ambas** lateralidades, **cuando** se llama `clasificar_gesto(coords, lateralidad)`, **entonces** se obtiene `G4`, `G3` y `G5` respectivamente **en las dos** (PUL-FR-002, PUL-FR-007) — hoy, con los fixtures espejados, se obtiene `E`, `G5` y `G3`.
- **Dado** un puño con el pulgar plegado sobre los dedos (`|x_punta - x_mcp| < EPSILON_PULGAR`), **cuando** se clasifica, **entonces** el resultado es `G3` y **nunca** `G5` (PUL-FR-005).
- **Dado** una detección sin lateralidad (`None`), **cuando** se clasifica una mano abierta, **entonces** el resultado es `E` (no `G4`) y no se lanza excepción (PUL-FR-006) — degradación segura, no adivinanza.
- **Dado** el pipeline con cámara real, **cuando** el usuario ejecuta los 5 gestos no-identidad **con cada mano**, **entonces** las 5 acciones se disparan correctamente con ambas (US-3 + SC-G01, verificación de campo — T012-07).

## 6. Casos borde

- **Mano de perfil:** 006/spec.md Sección 5 ya lo declara fuera de alcance del MVP. Esta spec **no** lo cambia; PUL-FR-002 corrige el signo del pulgar para una mano frontal, no rescata una mano rotada 90°.
- **MediaPipe reporta la lateralidad con score bajo (mano ambigua, parcialmente fuera de cuadro):** cubierto por PUL-FR-006 (tratar como `None` → pulgar abajo). Umbral de score sugerido: 0.8; se puede exponer en `config/default.yaml` junto a los otros umbrales de detección (INT-FR-001).
- **Usuario que cambia de mano a mitad de sesión:** la lateralidad se recalcula por frame, así que el cambio se absorbe solo. Pero el debounce (006) verá un gesto distinto durante la transición y reiniciará su contador — comportamiento correcto, sin acción requerida.

## 7. No objetivos

- No se implementa normalización 3D con el landmark `z` ni rotación canónica de la mano (fuera de alcance del MVP, igual que en 006).
- No se soportan dos manos simultáneas (`max_num_hands=1`, DET-FR-001 sigue vigente): la lateralidad se lee de la primera y única mano.
