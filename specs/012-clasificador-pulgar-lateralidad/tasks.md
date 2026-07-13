# Tasks 012 — Clasificador: Pulgar, Puño y Lateralidad

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 004/006 (ya implementados).

**T012-01 dejó de ser bloqueante.** La primera versión de este backlog exigía medir con cámara el signo de `dx` por lateralidad **antes** de escribir el fix, porque equivocarlo produce un sistema que pasa todos los tests sintéticos y falla en cámara con las dos manos. La Decisión D2 (proyección sobre el eje de la palma, ver `spec.md` Sección 3) **elimina esa constante**: la orientación se deriva de la geometría de la propia mano, no de la etiqueta de MediaPipe cruzada con el espejo. Ya no hay nada que adivinar.

- [x] **T012-01** ~~Medir el signo de `dx` por lateralidad con cámara~~ — **obsoleta por D2**. Sustituida por el diagnóstico de T012-12, que ya no bloquea la implementación sino que la verifica.
- [x] **T012-02** `src/deteccion/mediapipe_handler.py`: método `lateralidad() -> str | None` + `SCORE_LATERALIDAD_MINIMO = 0.8` (PUL-FR-001, PUL-FR-003). Es diagnóstico: el clasificador no lo consume.
- [x] **T012-03** `src/clasificador/gestos.py`: `_pulgar_levantado(coords)` por proyección sobre el eje meñique→índice + `UMBRAL_PULGAR = 0.15` (PUL-FR-002, PUL-FR-005, PUL-FR-006).
- [x] **T012-04** `src/clasificador/gestos.py`: documentar en el docstring la tabla desambiguada de `spec.md` Sección 5 (PUL-FR-004).
- [x] **T012-05** ~~`src/main.py`: pasar `detector.lateralidad()` a `clasificar_gesto()`~~ — **innecesaria por D2**: la firma `clasificar_gesto(coords)` no cambia.
- [x] **T012-06** `tests/fixtures_landmarks.py`: mano geométricamente plausible (nudillos separados — los fixtures previos colapsaban todos los MCP en `(0.5, 0.6)`, lo que deja el eje de la palma indefinido) + parámetro `lateralidad` que espeja el eje x (PUL-FR-007).
- [x] **T012-07** `tests/test_clasificador.py`: los 6 gestos parametrizados sobre `["Right", "Left"]` (18 tests). **Verificado que la sonda muerde:** contra el clasificador anterior, los 3 casos de la mano que fallaba dan `puño → G5`, `mano abierta → E`, `solo pulgar → G3` — el intercambio G3↔G5 exacto de `spec.md` Sección 1.
- [x] **T012-08** `tests/test_clasificador.py`: `test_puno_con_pulgar_plegado_no_se_confunde_con_g5` (proyección bajo el umbral → `G3`, PUL-FR-005), parametrizado sobre ambas manos.
- [x] **T012-09** `tests/test_clasificador.py`: `test_palma_degenerada_no_lanza_y_degrada_a_pulgar_abajo` (PUL-FR-006).
- [ ] **T012-10** Calibración de `UMBRAL_PULGAR` con cámara real: cerrar el puño 10 veces y extender el pulgar 10 veces; comprobar que no hay confusión `G3`/`G5` en ninguna repetición y ajustar el 0.15 si la hay (PUL-FR-005). **Pendiente — requiere cámara.** A diferencia del signo, equivocar el umbral falla de forma **visible y gradual** (el gesto no dispara), no silenciosa.
- [ ] **T012-11** Verificación de campo: los 5 gestos no-identidad disparan su acción correcta **con cada una de las dos manos** (US-3, SC-G01). **Pendiente — requiere cámara.** Es el criterio que cierra esta spec.
- [x] **T012-12** `scripts/smoke_vision.py`: imprime `mano=` (lateralidad), `gesto=` y `dedos=` una vez por segundo, para ejecutar T012-10 y T012-11 sin instrumentación adicional.
- [x] **T012-13** `README.md`: documentar que el sistema funciona con ambas manos y que la tabla 4.5 del documento de contexto queda reemplazada por la de `spec.md` Sección 5 (PUL-FR-004).

**Definición de hecho:** los 6 gestos pasan parametrizados sobre las dos lateralidades (18 tests), y esos mismos fixtures fallaban contra el clasificador anterior — **cumplido**. Queda la verificación de campo (T012-10, T012-11): es la única de las cuatro specs cuyo criterio de aceptación final **no se puede cerrar sin cámara**, porque el defecto era de geometría de mano real.
