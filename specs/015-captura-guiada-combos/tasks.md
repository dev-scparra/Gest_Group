# Tasks 015 — Captura Guiada de Combos

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de 001/002/006/008/009 (ya implementados) y 014 (superada).

- [x] **T015-01** `src/clasificador/capturador_combo.py`: `FaseCombo`, `EstadoCombo`, `CapturadorCombo` (`actualizar`, `reset`), máquina de estados con votación de mayoría (`Counter`) según `plan.md` Sección 2. Depende de 001 (`operacion_G`).
- [x] **T015-02** `tests/test_capturador_combo.py`: camino feliz + disparo único (CAP-CMB-FR-001/004); mayoría ignora transición (CAP-CMB-FR-001); mayoría E cancela (CAP-CMB-FR-002); re-armado exige E (CAP-CMB-FR-005); primer gesto sin E previo; cuenta regresiva y líder (CAP-CMB-FR-006); espera no consume ni dispara (CAP-CMB-FR-003); ventanas configurables (CAP-CMB-FR-007); reset desarma. 9 tests en verde.
- [x] **T015-03** `config/default.yaml`: reemplazar `combinador.ventana_s` por `frames_captura: 20`, `frames_espera: 12`, `frames_resultado: 25`.
- [x] **T015-04** `src/main.py`: reescribir `procesar_frame` (recibe `capturador`, sin `estabilizador`/`combinador`/`ahora`; devuelve 3-tupla con `estado_combo`); `main()` instancia `CapturadorCombo` desde config y pasa `estado_combo` a `dibujar_frame` (INT-FR-010 revisado). Eliminar `src/algebra/combinador.py`.
- [x] **T015-05** `src/visualizacion/renderer.py`: `dibujar_frame(..., estado_combo)` + `_dibujar_hud_combo` (panel, título de fase, líder+votos, barra de progreso con cuenta regresiva, resultado `g1 o g2 = compuesto`). Retirar la línea simple de combo de 014 (VIS-FR-009 revisado).
- [x] **T015-06** `tests/test_orquestacion.py` (reescrito): combo end-to-end dispara `φ(G1∘G3)=A4`; disparo único por combo; sin par no hay acción; devuelve `estado_combo`. Filtro de prueba `alpha≈0.99` (passthrough) para aislar del EMA.
- [x] **T015-07** `tests/test_renderer.py` (actualizado): HUD en captura enciende píxeles; RESULTADO muestra la composición; INACTIVO no rompe; `estado_combo=None` funciona.
- [x] **T015-08** `tests/test_config.py` (actualizado): las 3 subclaves `combinador.*` presentes y > 0.
- [x] **T015-09** Specs: escribir 015 (spec/plan/tasks); amendar [014](../014-combos-secuenciales/spec.md) (superada como interacción), [009](../009-integracion-pipeline/spec.md) (INT-FR-010), [008](../008-visualizacion/spec.md) (VIS-FR-009 → HUD), [000](../000-overview/spec.md) (mapa).
- [x] **T015-10** Docs: `docs/axiomas_de_grupo_explicados.md` y `docs/teoria_grupos_aplicada.md` — actualizar la descripción del combo (votación por mayoría + captura guiada); `README.md` — sección de combos + conteo de tests.
- [ ] **T015-11** Verificación de campo (requiere cámara): calibrar `frames_captura/espera/resultado` — hacer 2-3 combos guiados, confirmar que la votación absorbe la transición y que el HUD acompaña cada fase; ajustar los valores si la captura se siente muy corta (falla) o muy larga (tediosa). **Pendiente — requiere cámara.**

**Definición de hecho:** `pytest` completo en verde (99 tests, incluidos `test_capturador_combo.py` y los de orquestación/renderer/config actualizados). `python -m src.main` con cámara demuestra un combo guiado disparando `φ(g₁∘g₂)`, con el HUD asistiendo cada fase. ✅ **Cumplido salvo T015-11** (verificación con cámara real).
