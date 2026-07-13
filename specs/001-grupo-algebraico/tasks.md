# Tasks 001 — Grupo Algebraico (G, A)

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md).

- [x] **T001-01 (bloqueante, decisión de equipo, no código):** resolver spec.md Sección 5 — Opción A elegida, con la precisión de que "todo elemento autoinverso" es imposible para |G|=6 (Cauchy). Decisión y justificación en `docs/demostraciones.md`, Decisión D1.
- [x] **T001-02** Opción A: `scripts/derivar_cayley.py` define σ=(1 2 3)(4 5) ∈ S₅, calcula las 36 composiciones de sus potencias y las imprime como literal Python.
- [x] **T001-03** `src/algebra/grupo_gestos.py`: enum `Gesto` + `CAYLEY_G` (36 entradas) + `operacion_G()`. Depende de T001-01/02.
- [x] **T001-04 [P]** `src/algebra/grupo_acciones.py`: enum `Accion` + `CAYLEY_A` (36 entradas, abeliana — solo 21 productos únicos por conmutatividad, pero la tabla se guarda completa para lookup O(1) simétrico) + `operacion_A()`.
- [x] **T001-05** `src/algebra/verificacion.py`: `verificar_axiomas_grupo(elementos, operacion, identidad) -> ReporteAxiomas` (clausura, asociatividad, identidad, inversos — cada uno reportado por separado, no solo un booleano agregado).
- [x] **T001-06** `tests/test_grupo_gestos.py`: clausura (36 pares), asociatividad (216 ternas), identidad, existencia de inverso genuino por elemento (ALG-FR-004 revisado: no autoinverso universal). Depende de T001-03, T001-05.
- [x] **T001-07 [P]** `tests/test_grupo_acciones.py`: mismo patrón + conmutatividad. Depende de T001-04, T001-05.
- [x] **T001-08 [P]** `tests/test_verificacion.py`: caso negativo con tabla rota a propósito, confirmar que se reporta el axioma específico que falla.

**Definición de hecho:** `pytest tests/test_grupo_gestos.py tests/test_grupo_acciones.py tests/test_verificacion.py` en verde (13 tests); la decisión de T001-01 está documentada por escrito en `docs/demostraciones.md` (Decisión D1). **CUMPLIDO.**
