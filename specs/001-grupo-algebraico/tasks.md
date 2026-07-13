# Tasks 001 — Grupo Algebraico (G, A)

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md).

- [ ] **T001-01 (bloqueante, decisión de equipo, no código):** resolver spec.md Sección 5 — elegir Opción A (representación real en S₅ con permutaciones genuinas) u Opción B (grupo abstracto de 6 elementos, sin afirmar G≤S₅). Registrar la decisión y su justificación en `docs/demostraciones.md` (se referenciará desde el reporte técnico).
- [ ] **T001-02** Si Opción A: escribir `scripts/derivar_cayley.py` que defina las 6 permutaciones de S₅ elegidas para `e,g₁..g₅`, calcule las 36 composiciones y las imprima como literal Python.
- [ ] **T001-03** `src/algebra/grupo_gestos.py`: enum `Gesto` + `CAYLEY_G` (36 entradas) + `operacion_G()`. Depende de T001-01/02.
- [ ] **T001-04 [P]** `src/algebra/grupo_acciones.py`: enum `Accion` + `CAYLEY_A` (36 entradas, abeliana — solo 21 productos únicos por conmutatividad, pero la tabla se guarda completa para lookup O(1) simétrico) + `operacion_A()`.
- [ ] **T001-05** `src/algebra/verificacion.py`: `verificar_axiomas_grupo(elementos, operacion, identidad) -> ReporteAxiomas` (clausura, asociatividad, identidad, inversos — cada uno reportado por separado, no solo un booleano agregado).
- [ ] **T001-06** `tests/test_grupo_gestos.py`: clausura (36 pares), asociatividad (216 ternas), identidad, autoinverso. Depende de T001-03, T001-05.
- [ ] **T001-07 [P]** `tests/test_grupo_acciones.py`: mismo patrón + conmutatividad. Depende de T001-04, T001-05.
- [ ] **T001-08 [P]** `tests/test_verificacion.py`: caso negativo con tabla rota a propósito, confirmar que se reporta el axioma específico que falla.

**Definición de hecho:** `pytest tests/test_grupo_gestos.py tests/test_grupo_acciones.py tests/test_verificacion.py` en verde; la decisión de T001-01 está documentada por escrito, no solo implícita en el código.
