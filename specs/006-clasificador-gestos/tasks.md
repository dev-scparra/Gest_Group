# Tasks 006 — Clasificador de Gestos + Estabilizador

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 001 (usa el enum `Gesto`).

- [x] **T006-01** `tests/fixtures_landmarks.py`: funciones generadoras de landmarks sintéticos para `E, G1, G2, G3, G4, G5` y para el caso ambiguo (solo meñique arriba).
- [x] **T006-02** `src/clasificador/gestos.py`: `dedos_levantados()` + `clasificar_gesto()`. Depende de T001 (enum `Gesto`). **Nota:** el orden de las ramas del `if/elif` original (heredado del documento de contexto) hacía `G5` inalcanzable (el caso "puño" lo capturaba primero, ya que ambos comparten "índice/medio/anular/meñique abajo"); corregido comprobando `G5` antes que `G3` — ver test que lo detectó, `tests/test_clasificador.py::test_solo_pulgar_es_g5`.
- [x] **T006-03** `tests/test_clasificador.py`: un test por cada uno de los 6 elementos de G + el caso ambiguo (7 tests). Depende de T006-01, T006-02.
- [x] **T006-04** `src/clasificador/estabilizador.py`: `EstabilizadorGesto` con `actualizar()` y `reset()`. Depende de T001.
- [x] **T006-05** `tests/test_estabilizador.py`: los 4 casos de aceptación de debounce (spec.md Sección 4). Depende de T006-04.
- [x] **T006-06 [P]** `tests/test_estabilizador.py`: caso de reinicio al perder/recuperar mano (`reset()` explícito, spec.md Sección 6). Depende de T006-04.
- [ ] **T006-07** Checklist de humo con cámara real: ejecutar los 6 gestos 5 veces cada uno, registrar aciertos — insumo directo para SC-G01. Depende de T006-02, T006-04, y de que 003-005 estén integrados. **PENDIENTE — requiere cámara física y al usuario ejecutando `python src/main.py`.**

**Definición de hecho:** `pytest tests/test_clasificador.py tests/test_estabilizador.py` en verde (12 tests) sin cámara — **cumplido**; checklist de humo con cámara real pendiente de ejecución por el equipo.
