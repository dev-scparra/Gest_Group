# Tasks 012 — Clasificador: Pulgar, Puño y Lateralidad

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 004/006 (ya implementados).

**T012-01 es bloqueante y va primero.** El signo del pulgar no se puede deducir sin cámara (ver `plan.md` Sección 2): si se implementa "a ojo" y se equivoca, los tests sintéticos pasarán igual (porque los fixtures heredarían la misma convención equivocada) y el fallo solo aparecerá en la demo, con las dos manos rotas en vez de una.

- [ ] **T012-01** 🔒 **Bloqueante.** `scripts/smoke_vision.py`: imprimir por frame la lateralidad de MediaPipe (`multi_handedness[0].classification[0].label` + `score`) y `dx = coords[4].x - coords[2].x`, sobre el frame **ya espejado**. Poner cada mano frente a la cámara con el pulgar extendido y **anotar el signo de `dx` observado para `"Left"` y para `"Right"`**. Este dato medido es la entrada de T012-03.
- [ ] **T012-02** `src/deteccion/mediapipe_handler.py`: método `lateralidad() -> str | None` + constante `SCORE_LATERALIDAD_MINIMO = 0.8` (PUL-FR-001, PUL-FR-003, PUL-FR-006).
- [ ] **T012-03** `src/clasificador/gestos.py`: `_pulgar_levantado(coords, lateralidad)` con el signo **medido en T012-01** (comentado en el código, citando la observación) + `EPSILON_PULGAR = 0.03` (PUL-FR-002, PUL-FR-005, PUL-FR-006). Depende de T012-01, T012-02.
- [ ] **T012-04** `src/clasificador/gestos.py`: propagar `lateralidad` en `dedos_levantados()` y `clasificar_gesto()`; documentar en el docstring la tabla desambiguada de 012/spec.md Sección 4 (PUL-FR-004). Depende de T012-03.
- [ ] **T012-05** `src/main.py`: pasar `detector.lateralidad()` a `clasificar_gesto()` (dentro de `procesar_frame()` si 011 ya está aplicado). Depende de T012-04.
- [ ] **T012-06 [P]** `tests/fixtures_landmarks.py`: parámetro `lateralidad` que espeje el eje x (`x → 1-x`); regenerar los 6 generadores existentes (PUL-FR-007). Depende de T012-04.
- [ ] **T012-07** `tests/test_clasificador.py`: parametrizar `G3`/`G4`/`G5` sobre `["Right", "Left"]` (PUL-FR-007). **Los 3 casos `"Left"` deben fallar contra el código actual** (`G4→E`, `G5→G3`, `G3→G5`); si pasan a la primera, el fixture no espeja. Depende de T012-06.
- [ ] **T012-08 [P]** `tests/test_clasificador.py`: `test_puno_con_pulgar_plegado_no_se_confunde_con_g5` (`|dx| < EPSILON_PULGAR` → `G3`, PUL-FR-005). Depende de T012-03.
- [ ] **T012-09 [P]** `tests/test_clasificador.py`: `test_lateralidad_ausente_degrada_a_pulgar_abajo` (`lateralidad=None` + mano abierta → `E`, sin excepción, PUL-FR-006). Depende de T012-03.
- [ ] **T012-10** Calibración de `EPSILON_PULGAR` con cámara real: cerrar el puño 10 veces y extender el pulgar 10 veces, comprobar que no hay confusión `G3`/`G5` en ninguna repetición; ajustar el valor si la hay (PUL-FR-005). Depende de T012-03.
- [ ] **T012-11** Verificación de campo (criterio de aceptación 4 de `spec.md`): los 5 gestos no-identidad disparan su acción correcta **con cada una de las dos manos** (US-3, SC-G01). Depende de T012-05, T012-10.
- [ ] **T012-12 [P]** `docs/demostraciones.md` / `README.md`: documentar que el sistema funciona con ambas manos y que la tabla 4.5 del documento de contexto queda reemplazada por la de 012/spec.md Sección 4 (PUL-FR-004).

**Definición de hecho:** los tests de `G3`/`G4`/`G5` pasan parametrizados sobre las dos lateralidades (y fallaban contra el código previo); el puño con el pulgar plegado nunca se clasifica como `G5` en 10 repeticiones reales; y en cámara, las 5 acciones se disparan correctamente **con la mano izquierda y con la derecha** — hoy solo con una, y con la otra `G3` y `G5` disparan la acción intercambiada.
