# Tasks 004 — Detección de Landmarks (MediaPipe)

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 003 (consume su salida).

- [ ] **T004-01** `src/deteccion/mediapipe_handler.py`: clase `DetectorManos` (constructor con umbrales configurables + `procesar()` + `landmarks_para_dibujo()`).
- [ ] **T004-02** `tests/test_deteccion.py`: frame sintético sin mano (ruido o negro) → `procesar()` devuelve `None`. Depende de T004-01.
- [ ] **T004-03** Extender `scripts/smoke_vision.py` (compartido con 003/005) para imprimir por consola si se detectó mano y cuántos landmarks, usando cámara real. Depende de T004-01, T003-01.
- [ ] **T004-04 [P]** Exponer `min_detection_confidence`/`min_tracking_confidence` en `config/default.yaml` (coordinar con 009).

**Definición de hecho:** `pytest tests/test_deteccion.py` en verde sin cámara; `scripts/smoke_vision.py` confirma detección real con cámara conectada.
