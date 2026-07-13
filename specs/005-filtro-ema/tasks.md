# Tasks 005 — Filtro EMA

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md).

- [ ] **T005-01** `src/preprocesamiento/filtro_ema.py`: clase `FiltroEMA` con validación de `alpha` en constructor y setter.
- [ ] **T005-02** `tests/test_filtro_ema.py`: `test_convergencia_ema` (documento de contexto, Sección 10). Depende de T005-01.
- [ ] **T005-03 [P]** `tests/test_filtro_ema.py`: `test_estabilidad_ruido` (documento de contexto, Sección 10). Depende de T005-01.
- [ ] **T005-04 [P]** `tests/test_filtro_ema.py`: `test_reset_limpia_historia` (nuevo — EMA-FR-002/003). Depende de T005-01.
- [ ] **T005-05 [P]** `tests/test_filtro_ema.py`: `test_alpha_invalido_falla` (nuevo — caso borde de validación). Depende de T005-01.
- [ ] **T005-06** Redactar en `docs/demostraciones.md` la Demostración 4 (estabilidad asintótica) enlazada a T005-02 como evidencia empírica. Depende de T005-02.

**Definición de hecho:** `pytest tests/test_filtro_ema.py` en verde (4 tests); Demostración 4 documentada con su respaldo de test.
