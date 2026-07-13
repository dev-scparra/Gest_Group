# Tasks 003 — Captura de Video

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md).

- [x] **T003-01** `src/captura/video_capture.py`: clase `CapturaVideo` (constructor + `leer_frame()` + `liberar()`).
- [x] **T003-02** `tests/test_video_capture.py`: con `unittest.mock` sobre `cv2.VideoCapture`, probar caso de éxito (flip aplicado, RGB derivado correctamente de un BGR conocido) y caso de fallo (`(False, None)` del mock → `(False, None, None)` de `leer_frame()`). Depende de T003-01.
- [ ] **T003-03** Checklist manual de humo con cámara real: instanciar `CapturaVideo()`, leer 100 frames, confirmar resolución y que no hay excepción al mover la mano fuera del cuadro. Depende de T003-01. **PENDIENTE — requiere cámara física, ejecutar `scripts/smoke_vision.py` localmente.**
- [x] **T003-04 [P]** Documentar en README el permiso de "Cámara" de macOS requerido (ver riesgo en plan.md).

**Definición de hecho:** `pytest tests/test_video_capture.py` en verde sin cámara (3 tests, cumplido); checklist manual con cámara real **pendiente de ejecución por el equipo** (requiere hardware no disponible en este entorno).
