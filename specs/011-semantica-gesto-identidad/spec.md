# Spec 011 — Semántica del Gesto Identidad y de la "Última Acción Confirmada"

**Módulos:** `src/main.py` (009), `src/visualizacion/renderer.py` (008), `src/clasificador/estabilizador.py` (006).
**Origen:** auditoría de conformidad specs↔código (2026-07-13).
**Severidad:** **MEDIA** — no rompe el proceso, pero produce un overlay que contradice su propio criterio de aceptación, justo en la pantalla que se le muestra al profesor (US-2).
**Requerimientos en conflicto:** VIS-FR-003 (008) vs. INT-FR-004 + INT-FR-005 + INT-FR-006 (009).

---

## 1. Problema — dos specs correctas que, juntas, se contradicen

Este no es un bug de implementación: `main.py` hace **exactamente** lo que 009 le pide, y `renderer.py` hace **exactamente** lo que 008 le pide. El defecto está en que **nadie decidió si `E` es un gesto confirmable**, y las dos specs asumieron respuestas opuestas.

- **009/INT-FR-004:** "Cuando 004 devuelve `None`, DEBE alimentar `Gesto.E` a `EstabilizadorGesto.actualizar()` **en vez de omitir la llamada**".
- **009/INT-FR-005:** "Cuando `actualizar()` devuelve un `Gesto` no-`None` (confirmación), DEBE calcular `φ(g)` y llamar `ejecutar_accion()`".
- **009/INT-FR-006:** `main.py` mantiene "última acción confirmada" y se la pasa a 008.
- **008/VIS-FR-003:** el overlay muestra "la acción `φ(g)` del **último gesto confirmado**", y su criterio de aceptación exige: *"Dado que el usuario sostiene `G1` (que ya disparó `A1`) y luego mueve la mano a una posición ambigua (`E` instantáneo, sin nueva confirmación), entonces el texto de acción **sigue mostrando `A1`**"*.

Encadenadas, las tres reglas de 009 hacen que **`E` sea un gesto confirmable como cualquier otro**: si el usuario retira la mano y la deja fuera de cuadro `frames_estables` frames (10 por defecto, ~0.3 s a 30 FPS), el estabilizador confirma `E`, INT-FR-005 dispara `φ(E) = A_E`, e INT-FR-006 sobrescribe `ultima_accion = A_E`. El overlay pasa a mostrar `phi(g) = ninguna`.

**Reproducción (verificada, simulando el loop de `main.py`):**

```
frame 10:    CONFIRMA G1 -> ultima_accion = A1        # overlay: phi(g) = subir_volumen
... usuario retira la mano; main alimenta Gesto.E cada frame (INT-FR-004) ...
frame E#10:  CONFIRMA E  -> ultima_accion = A_E       # overlay: phi(g) = ninguna   <-- pierde A1
```

El criterio de aceptación de 008 se cumple durante los primeros 9 frames sin mano y **se rompe en el décimo**. Como `frames_estables=10` es exactamente el mismo umbral que confirma un gesto real, el usuario ve el nombre de su acción aparecer y desvanecerse ~0.3 s después de bajar la mano — precisamente el intervalo en que un evaluador mira la pantalla para comprobar qué pasó.

**Por qué la suite no lo detecta:** `tests/test_renderer.py` prueba `dibujar_frame(frame, None, Gesto.E, Accion.A1, 0.3)` — es decir, verifica que el *renderer* respeta la acción que le pasan. Correcto, pero VIS-FR-003 es un requerimiento sobre **quién decide el valor de ese argumento**, y ese es `main.py`. No hay ningún test que ejercite el loop de orquestación de 009 (`tests/test_config.py` solo cubre `cargar_config`). El requerimiento cae en la grieta entre dos módulos y sus dos suites.

## 2. Decisión: `A_E` no es "una acción ejecutada", es "no hacer nada"

`A_E` es el neutro de A y `ACC-FR-004` ya lo define como un **no-op explícito** ("nunca debe intentar ejecutar un comando de SO"). Confirmar `E` no produce ningún efecto observable en el sistema; por tanto **no es un "disparo real"** y no debe desplazar de la pantalla al último disparo que sí lo fue. La corrección es de una línea y va en `main.py`, no en el estabilizador ni en el renderer.

Se descarta la alternativa "que el estabilizador nunca confirme `E`": violaría INT-FR-004 (que existe por una razón sólida — mantener el contador de debounce alineado con la realidad para que un gesto no se confirme a caballo de una pérdida de mano) y dejaría al estabilizador con una regla especial para un elemento del grupo, rompiendo la uniformidad con la que 006 trata a `G`.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| SEM-FR-001 | **Revisa INT-FR-006.** `main.py` DEBE actualizar `ultima_accion` **solo cuando `φ(g) != Accion.A_E`**. Una confirmación de un gesto cuyo `φ(g)` es la identidad no desplaza el valor mostrado en el overlay. |
| SEM-FR-002 | INT-FR-004 e INT-FR-005 **se mantienen sin cambios**: `Gesto.E` se sigue alimentando al estabilizador en cada frame sin mano, y una confirmación de `E` sigue llamando `ejecutar_accion(A_E)` (que es un no-op por ACC-FR-004). Lo único que cambia es que esa confirmación no toca `ultima_accion`. |
| SEM-FR-003 | El valor inicial de `ultima_accion` DEBE ser distinguible de "se confirmó una acción que resultó ser la identidad". Al arrancar, el overlay DEBE mostrar un texto de "sin acción aún" (p. ej. `phi(g) = --`), no `phi(g) = ninguna`, que es el `value` de `Accion.A_E` y hoy se muestra idéntico en ambos casos. Implementación sugerida: `ultima_accion: Accion | None = None` en `main.py`, y `dibujar_frame` acepta `accion: Accion | None`. |
| SEM-FR-004 | **Amplía VIS-FR-003.** El overlay DEBE distinguir visualmente el **gesto instantáneo** (`g = ...`, cambia cada frame) de la **última acción confirmada** (`phi(g) = ...`, persiste entre disparos). Hoy ambos se dibujan con el mismo peso tipográfico y sin etiqueta que indique que uno es histórico y el otro es en vivo, lo que hace que el desvanecimiento descrito en la Sección 1 se lea como un bug del clasificador y no del overlay. |
| SEM-FR-005 | DEBE existir un test de **orquestación** (no solo de módulo) que ejercite la secuencia de la Sección 1: confirmar `G1`, luego alimentar `frames_estables + 2` frames de `Gesto.E`, y verificar que el valor pasado a `dibujar_frame` sigue siendo `Accion.A1`. Esto exige extraer el cuerpo del loop de `main.py` a una función testeable (ver `plan.md`). |

## 4. Criterios de aceptación

- **Dado** un `EstabilizadorGesto(frames_estables=10)` que acaba de confirmar `G1` (`ultima_accion == A1`), **cuando** se alimentan 12 frames consecutivos de `Gesto.E` (mano fuera de cuadro), **entonces** `ultima_accion` sigue siendo `A1` (SEM-FR-001) — este es el criterio de aceptación de 008/VIS-FR-003, hoy incumplido a partir del frame 10.
- **Dado** el pipeline recién arrancado y sin mano en cuadro, **cuando** pasan 30 frames, **entonces** el overlay muestra el marcador de "sin acción aún" y **no** `phi(g) = ninguna` (SEM-FR-003).
- **Dado** que el usuario confirma `G1` (→ `A1`) y después confirma `G3` (→ `A3`), **cuando** se observa el overlay, **entonces** muestra `A3` (una confirmación no-identidad **sí** desplaza a la anterior — SEM-FR-001 no debe romper el caso normal).
- **Dado** una confirmación de `E`, **cuando** ocurre, **entonces** `ejecutar_accion(Accion.A_E)` se sigue invocando exactamente una vez y no invoca ningún `subprocess` (SEM-FR-002 + ACC-FR-004 siguen valiendo).

## 5. Casos borde

- **Al arrancar sin mano en cuadro, el estabilizador confirma `E` en el frame 10** (su estado inicial es `gesto_actual = Gesto.E`, `contador = 0`, así que 10 frames de `E` lo confirman). Con SEM-FR-001 esto es inocuo: dispara un no-op y no toca el overlay. Se documenta aquí para dejar constancia de que es **comportamiento aceptado**, no un defecto pendiente.
- **`frames_estables` muy bajo (1 o 2):** el desvanecimiento del overlay descrito en la Sección 1 sería casi instantáneo. SEM-FR-001 lo elimina para cualquier valor de `frames_estables`, así que no hace falta acotar el rango del parámetro en config.

## 6. No objetivos

- No cambia el estabilizador (006): sigue tratando a `E` como un elemento más de `G`, sin reglas especiales.
- No añade un timeout de "expiración" de la última acción mostrada (que el overlay vuelva a "--" tras N segundos sin disparos). Sería una mejora de UX razonable, pero VIS-FR-003 pide explícitamente persistencia, no expiración — cambiarlo requeriría revisar 008, no corregirlo.
