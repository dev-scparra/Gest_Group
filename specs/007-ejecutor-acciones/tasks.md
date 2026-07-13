# Tasks 007 — Ejecutor de Acciones

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 002 (usa el enum `Accion`).

- [ ] **T007-01** `src/acciones/ejecutor.py`: `ResultadoEjecucion` (dataclass) + `ejecutar_accion()` + `_ejecutar_macos()` con las 5 acciones vía `osascript`.
- [ ] **T007-02 [P]** `src/acciones/ejecutor.py`: `_ejecutar_linux()` con subir/bajar volumen vía `amixer`.
- [ ] **T007-03 [P]** `src/acciones/ejecutor.py`: `_ejecutar_windows()` como no-op documentado o `NotImplementedError` explícito (ACC-FR-006).
- [ ] **T007-04** `tests/test_ejecutor.py`: `Accion.A_E` no invoca `subprocess.run`. Depende de T007-01.
- [ ] **T007-05** `tests/test_ejecutor.py`: mock de macOS con éxito, verificar comando `osascript` exacto para cada una de las 5 acciones. Depende de T007-01.
- [ ] **T007-06 [P]** `tests/test_ejecutor.py`: mock de fallo (`returncode≠0`) → `ResultadoEjecucion.exito == False`. Depende de T007-01.
- [ ] **T007-07 [P]** `tests/test_ejecutor.py`: mock de `platform.system()=="Windows"` → comportamiento de ACC-FR-006. Depende de T007-03.
- [ ] **T007-08** Verificar manualmente permiso de Accesibilidad en macOS y documentarlo en README (riesgo de `plan.md` Sección 5). Depende de T007-01.
- [ ] **T007-09** Checklist manual: las 5 acciones producen efecto real observable en macOS. Depende de T007-01, T007-08.

**Definición de hecho:** `pytest tests/test_ejecutor.py` en verde sin necesidad de macOS/Linux real (todo mockeado); checklist manual en macOS confirmado.
