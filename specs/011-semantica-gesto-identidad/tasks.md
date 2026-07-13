# Tasks 011 — Semántica del Gesto Identidad

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 006/008/009 (ya implementados).

Orden deliberado: **primero el test que falla (T011-01), después el fix (T011-03)**. El defecto sobrevivió a 60 tests en verde precisamente porque 009 no tiene suite; empezar por el fix repetiría el error.

- [ ] **T011-01** `src/main.py`: extraer el cuerpo del loop a `procesar_frame(frame_rgb, detector, filtro, estabilizador, homomorfismo, estado)` + dataclass `EstadoPipeline`, sin cambiar todavía la semántica (refactor puro, comportamiento idéntico). Habilita SEM-FR-005.
- [ ] **T011-02** `tests/test_orquestacion.py` (nuevo): `test_confirmacion_de_E_no_borra_la_ultima_accion` — confirmar `G1`, alimentar 12 frames de `Gesto.E`, esperar `Accion.A1`. **Debe fallar** contra el código actual (devuelve `A_E` en la iteración 10). Depende de T011-01.
- [ ] **T011-03** `src/main.py`: guardia `if accion != Accion.A_E: estado.ultima_accion = accion` (SEM-FR-001). T011-02 pasa a verde. Depende de T011-02.
- [ ] **T011-04** `src/main.py`: `ultima_accion` inicial `None` en vez de `Accion.A_E` (SEM-FR-003). Depende de T011-03.
- [ ] **T011-05** `src/visualizacion/renderer.py`: `dibujar_frame` acepta `accion: Accion | None`; `None` → `phi(g) = --` (SEM-FR-003). Depende de T011-04.
- [ ] **T011-06 [P]** `tests/test_renderer.py`: caso `accion=None` no lanza excepción y preserva la forma del frame. Depende de T011-05.
- [ ] **T011-07 [P]** `tests/test_orquestacion.py`: `test_confirmacion_no_identidad_si_desplaza_a_la_anterior` — `G1` (→`A1`) seguido de `G3` (→`A3`) deja `A3` (SEM-FR-001 no debe romper el caso normal). Depende de T011-03.
- [ ] **T011-08 [P]** `tests/test_orquestacion.py`: `test_confirmacion_de_E_sigue_invocando_ejecutar_accion` — con `ejecutar_accion` parcheado, una confirmación de `E` lo llama una vez con `Accion.A_E` (SEM-FR-002: el fix no debe saltarse la llamada, solo la actualización del overlay). Depende de T011-03.
- [ ] **T011-09** `src/visualizacion/renderer.py`: etiquetar gesto instantáneo vs. última acción confirmada (SEM-FR-004). Validación visual, no automatizable. Depende de T011-05.

**Definición de hecho:** `tests/test_orquestacion.py` existe y está en verde, incluyendo un test que reproduce el escenario de `spec.md` Sección 1 y que **falla contra el código previo al fix**; los 60 tests existentes siguen pasando; al retirar la mano en una demo real, el overlay conserva el nombre de la última acción ejecutada en vez de volver a `ninguna` tras ~0.3 s.
