# Tasks 004 — Detección de Landmarks (MediaPipe)

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 003 (consume su salida).

- [x] **T004-01** `src/deteccion/mediapipe_handler.py`: clase `DetectorManos` (constructor con umbrales configurables + `procesar()` + `landmarks_para_dibujo()`).
- [x] **T004-02** `tests/test_deteccion.py`: frame sintético sin mano (ruido o negro) → `procesar()` devuelve `None`. Depende de T004-01.
- [x] **T004-03** `scripts/smoke_vision.py` (compartido con 003/005) imprime por consola si se detectó mano y cuántos landmarks, usando cámara real. Depende de T004-01, T003-01. **Escrito; ejecución con cámara real pendiente del equipo.**
- [x] **T004-04 [P]** Exponer `min_detection_confidence`/`min_tracking_confidence` en `config/default.yaml` (coordinar con 009).

**Definición de hecho:** `pytest tests/test_deteccion.py` en verde sin cámara (2 tests, cumplido); `scripts/smoke_vision.py` listo — confirmar detección real con cámara conectada queda pendiente para el equipo.
