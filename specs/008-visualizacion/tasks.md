# Tasks 008 — Visualización / Overlay

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 006/007 (usa sus enums).

- [ ] **T008-01** `src/visualizacion/renderer.py`: `COLORES_GESTO` + `dibujar_frame()` con landmarks, texto de gesto, texto de acción, α, y anotación algebraica fija.
- [ ] **T008-02** `tests/test_renderer.py`: llamada con frame sintético y `hand_landmarks=None`, verificar que no lanza excepción y preserva la forma del array. Depende de T008-01.
- [ ] **T008-03 [P]** `tests/test_renderer.py`: llamada con `hand_landmarks=None` pero `accion` distinta de `A_E` (simula "última acción confirmada" tras perder la mano) — confirmar que el texto de acción no se resetea (VIS-FR-003). Depende de T008-01.
- [ ] **T008-04** Checklist manual: capturar los 6 gestos en pantalla y verificar legibilidad (NFR-VIS-01). Depende de T008-01, y de que 009 tenga el pipeline cableado.

**Definición de hecho:** `pytest tests/test_renderer.py` en verde sin cámara; checklist visual confirmado por al menos un integrante.
