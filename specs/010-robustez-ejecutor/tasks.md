# Tasks 010 — Robustez del Ejecutor

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 007 (ya implementado).

- [x] **T010-01** `src/acciones/ejecutor.py`: añadir `TIMEOUT_SUBPROCESS_S = 2.0` y `_SUGERENCIA_POR_BINARIO`; envolver `subprocess.run` en `_run()` con `except FileNotFoundError` / `except subprocess.TimeoutExpired` / `except OSError` (ROB-FR-001, ROB-FR-002, ROB-FR-003).
- [x] **T010-02** `src/acciones/ejecutor.py`: pasar `timeout=TIMEOUT_SUBPROCESS_S` a la llamada de `subprocess.run` (ROB-FR-002).
- [x] **T010-03** `tests/test_ejecutor.py`: `test_binario_ausente_reporta_fallo_sin_excepcion` con `side_effect=FileNotFoundError` sobre `platform.system()=="Linux"` → `exito is False` y `"amixer"` + `"alsa-utils"` en el mensaje (ROB-FR-001, ROB-FR-005).
- [x] **T010-04** `tests/test_ejecutor.py`: `test_timeout_reporta_fallo` con `side_effect=subprocess.TimeoutExpired` (ROB-FR-002).
- [x] **T010-05** `tests/test_ejecutor.py`: `test_permission_error_reporta_fallo` con `side_effect=PermissionError` (ROB-FR-003).
- [x] **T010-06** `tests/test_ejecutor.py`: `test_run_pasa_timeout_a_subprocess` — `mock_run.call_args.kwargs["timeout"] == 2.0` (ROB-FR-002).
- [x] **T010-07** Reproducción del bug original: `ejecutar_accion(Accion.A1)` con `platform.system()=="Linux"` en esta máquina (sin `amixer`) lanzaba `FileNotFoundError`; ahora devuelve `ResultadoEjecucion(exito=False, mensaje="binario 'amixer' no encontrado en el PATH (instalar el paquete 'alsa-utils')")`.
- [ ] **T010-08** Verificación end-to-end en el pipeline completo: correr `python -m src.main` en una máquina sin el binario de audio y confirmar que, al confirmar `G1`, el loop sobrevive y el fallo aparece logueado una sola vez (no 30 veces/segundo). **Pendiente — requiere cámara.** El logueo lo aporta 013/CNF-FR-005 (ya implementado en `procesar_frame`).

**Definición de hecho:** los 11 tests previos de `tests/test_ejecutor.py` siguen en verde **y** los 4 nuevos pasan (14 en total) **y** la reproducción de `spec.md` Sección 1 ya no lanza excepción — **cumplido**. Verificación end-to-end con cámara pendiente.
