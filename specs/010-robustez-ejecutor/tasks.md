# Tasks 010 — Robustez del Ejecutor

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 007 (ya implementado).

- [ ] **T010-01** `src/acciones/ejecutor.py`: añadir `TIMEOUT_SUBPROCESS_S = 2.0` y `_PAQUETE_POR_BINARIO`; envolver `subprocess.run` en `_run()` con `except FileNotFoundError` / `except subprocess.TimeoutExpired` / `except OSError` (ROB-FR-001, ROB-FR-002, ROB-FR-003).
- [ ] **T010-02** `src/acciones/ejecutor.py`: pasar `timeout=TIMEOUT_SUBPROCESS_S` a la llamada de `subprocess.run` (ROB-FR-002). Depende de T010-01.
- [ ] **T010-03 [P]** `tests/test_ejecutor.py`: `test_binario_ausente_reporta_fallo_sin_excepcion` con `side_effect=FileNotFoundError` sobre `platform.system()=="Linux"` → `exito is False` y `"amixer"` en el mensaje (ROB-FR-001, ROB-FR-005). Depende de T010-01.
- [ ] **T010-04 [P]** `tests/test_ejecutor.py`: `test_timeout_reporta_fallo` con `side_effect=subprocess.TimeoutExpired` (ROB-FR-002). Depende de T010-01.
- [ ] **T010-05 [P]** `tests/test_ejecutor.py`: `test_permission_error_reporta_fallo` con `side_effect=PermissionError` (ROB-FR-003). Depende de T010-01.
- [ ] **T010-06 [P]** `tests/test_ejecutor.py`: `test_run_pasa_timeout_a_subprocess` — verificar `mock_run.call_args.kwargs["timeout"] == 2.0` (ROB-FR-002). Depende de T010-02.
- [ ] **T010-07** Verificación end-to-end del criterio de aceptación 4 de `spec.md`: correr el pipeline en una máquina sin el binario de audio y confirmar que el loop sobrevive a una confirmación de `G1` (no cae en el `except` de INT-FR-008 frame tras frame). Depende de T010-01.

**Definición de hecho:** los 11 tests existentes de `tests/test_ejecutor.py` siguen en verde **y** los 4 tests nuevos (T010-03..T010-06) pasan **y** la reproducción de `spec.md` Sección 1 (`ejecutar_accion(Accion.A1)` con `platform.system()=="Linux"` en una máquina sin `amixer`) devuelve `ResultadoEjecucion(exito=False, ...)` en vez de lanzar `FileNotFoundError`.
