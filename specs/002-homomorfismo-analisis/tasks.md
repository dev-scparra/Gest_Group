# Tasks 002 — Homomorfismo φ y Análisis Algebraico

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de que 001 esté completo (`operacion_G`/`operacion_A` deben existir y estar probadas).

- [x] **T002-01** `src/algebra/homomorfismo.py`: clase `Homomorfismo` con constructor que valida totalidad (HOM-FR-001) y tabla por defecto (HOM-FR-002).
- [x] **T002-02** Implementar `aplicar`, `kernel`, `imagen`, `es_inyectiva`, `es_sobreyectiva`, `clases_laterales_kernel`. Depende de T002-01.
- [x] **T002-03** Implementar `verificar_homomorfismo()` usando `operacion_G`/`operacion_A` de 001, devolviendo `ReporteHomomorfismo` con los pares fallidos si los hay. Depende de T002-01.
- [x] **T002-04** `tests/test_homomorfismo.py`: los 5 tests base del documento de contexto (Sección 10). Depende de T002-02.
- [x] **T002-05** Añadir a `tests/test_homomorfismo.py`: `test_verificar_homomorfismo_sobre_cayley` (36 pares, SC-G04). Depende de T002-03.
- [x] **T002-06 [P]** Añadir a `tests/test_homomorfismo.py`: caso de tabla φ custom con kernel no trivial (dos gestos a la misma acción) y caso extremo de tabla constante (todos a `A_E`). Depende de T002-02.
- [x] **T002-07** `src/algebra/analisis.py`: script CLI que instancia `Homomorfismo()` por defecto e imprime ker(φ), Im(φ), clases laterales, mono/epi/iso, y el reporte de `verificar_homomorfismo()` en texto plano. Depende de T002-02, T002-03.
- [x] **T002-08** Ejecutar `analisis.py`, capturar la salida y pegarla en `docs/demostraciones.md` como evidencia de las Demostraciones 2 y 3 del documento de contexto. Depende de T002-07.

**Definición de hecho:** `pytest tests/test_homomorfismo.py` en verde (9 tests); `python -m src.algebra.analisis` corre sin cámara y su salida ya está documentada en `docs/demostraciones.md`. **CUMPLIDO.**
