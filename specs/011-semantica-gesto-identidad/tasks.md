# Tasks 011 — Semántica del Gesto Identidad

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 006/008/009 (ya implementados).

- [x] **T011-01** `src/main.py`: extraer el cuerpo del loop a `procesar_frame(frame_rgb, detector, filtro, estabilizador, homomorfismo, estado)` + dataclass `EstadoPipeline`. Habilita SEM-FR-005.
- [x] **T011-02** `tests/test_orquestacion.py` (nuevo): `test_confirmacion_de_E_no_borra_la_ultima_accion` — confirmar `G1`, alimentar 12 frames de `Gesto.E`, esperar `Accion.A1`. Reproduce el escenario de `spec.md` Sección 1, que contra el código anterior devolvía `A_E` en la iteración 10.
- [x] **T011-03** `src/main.py`: guardia `if accion != Accion.A_E: estado.ultima_accion = accion` (SEM-FR-001).
- [x] **T011-04** `src/main.py`: `ultima_accion` inicial `None` en vez de `Accion.A_E` (SEM-FR-003).
- [x] **T011-05** `src/visualizacion/renderer.py`: `dibujar_frame` acepta `accion: Accion | None`; `None` → `phi(g) = --` (SEM-FR-003).
- [x] **T011-06** `tests/test_renderer.py`: `test_dibujar_frame_acepta_accion_none` (SEM-FR-003).
- [x] **T011-07** `tests/test_orquestacion.py`: `test_confirmacion_no_identidad_si_desplaza_a_la_anterior` — `G1` (→`A1`) seguido de `G3` (→`A3`) deja `A3` (SEM-FR-001 no rompe el caso normal).
- [x] **T011-08** `tests/test_orquestacion.py`: `test_confirmacion_de_E_sigue_invocando_ejecutar_accion` — una confirmación de `E` llama a `ejecutar_accion(A_E)` exactamente una vez (SEM-FR-002).
- [x] **T011-09** `src/visualizacion/renderer.py`: etiquetar el gesto como `(en vivo)` y la acción como `(ultima)` (SEM-FR-004, nuevo VIS-FR-008).
- [ ] **T011-10** Validación visual en la demo: al retirar la mano, el overlay conserva el nombre de la última acción en vez de volver a `ninguna` a los ~0.3 s. **Pendiente — requiere cámara.**

**Hallazgo colateral (T011-07).** El test de transición `G1 → G3` falló al principio con `frames_estables` frames: el filtro EMA (α=0.3) tarda **~4 frames** en que la punta del índice cruce la línea del MCP, y solo entonces empiezan a contar los 10 frames del debounce. El retardo es correcto por diseño (005 + 006), pero **se suma a la latencia gesto→acción de SC-G03**: ~14 frames a 30 FPS son ~470 ms, al borde del presupuesto de 500 ms. No es un defecto, pero conviene medirlo en campo antes de dar SC-G03 por cumplido — bajar `frames_estables` o subir α son las dos perillas si no alcanza.

**Definición de hecho:** `tests/test_orquestacion.py` existe con 6 tests en verde, incluido el que reproduce el escenario de `spec.md` Sección 1 — **cumplido**. Validación visual con cámara pendiente.
