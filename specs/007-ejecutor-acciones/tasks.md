# Tasks 007 — Ejecutor de Acciones

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 002 (usa el enum `Accion`).

- [x] **T007-01** `src/acciones/ejecutor.py`: `ResultadoEjecucion` (dataclass) + `ejecutar_accion()` + `_ejecutar_macos()` con las 5 acciones vía `osascript`.
- [x] **T007-02 [P]** `src/acciones/ejecutor.py`: `_ejecutar_linux()` con subir/bajar volumen vía `amixer`.
- [x] **T007-03 [P]** `src/acciones/ejecutor.py`: `_ejecutar_windows()` con las 5 acciones vía teclas virtuales (`ctypes.windll.user32.keybd_event`), paridad completa con macOS (ACC-FR-006).
- [x] **T007-04** `tests/test_ejecutor.py`: `Accion.A_E` no invoca `subprocess.run`. Depende de T007-01.
- [x] **T007-05** `tests/test_ejecutor.py`: mock de macOS con éxito, verificar comando `osascript` exacto para cada una de las 5 acciones. Depende de T007-01.
- [x] **T007-06 [P]** `tests/test_ejecutor.py`: mock de fallo (`returncode≠0`) → `ResultadoEjecucion.exito == False`. Depende de T007-01.
- [x] **T007-07 [P]** `tests/test_ejecutor.py`: mock de `platform.system()=="Windows"` con `_enviar_tecla_virtual` parcheada → VK code exacto por acción (ACC-FR-006). Depende de T007-03.
- [ ] **T007-08** Verificar manualmente permiso de Accesibilidad en macOS y documentarlo en README (riesgo de `plan.md` Sección 5). Depende de T007-01. Permiso **documentado** en README; verificación manual real **pendiente del usuario**.
- [ ] **T007-09** Checklist manual: las 5 acciones producen efecto real observable en macOS. Depende de T007-01, T007-08. **PENDIENTE — requiere macOS real con permisos concedidos.**

**Definición de hecho:** `pytest tests/test_ejecutor.py` en verde sin necesidad de macOS/Linux/Windows real (todo mockeado, 11 tests) — **cumplido**; checklist manual en macOS real pendiente de ejecución por el equipo.
