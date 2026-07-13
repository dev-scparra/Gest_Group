# Tasks 013 — Backlog de Conformidad Menor

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md). **CNF-FR-003 y CNF-FR-005 dependen de que [011](../011-semantica-gesto-identidad/tasks.md) esté aplicado** (ambos tocan `main.py`, que 011 reestructura).

### Grupo A — desviaciones de código

- [ ] **T013-01 [P]** `src/algebra/homomorfismo.py`: validar `set(tabla_phi) != set(Gesto)` → `ValueError` con faltantes **y** sobrantes (CNF-FR-001).
- [ ] **T013-02 [P]** `tests/test_homomorfismo.py`: `test_tabla_con_clave_espuria_falla_en_constructor` (CNF-FR-001). Depende de T013-01.
- [ ] **T013-03** `src/main.py`: sacar `dibujar_frame` / `cv2.imshow` / `cv2.waitKey` del bloque `try`; ante excepción, tratar el frame como "sin mano" y seguir renderizando (CNF-FR-002, 009/Sec.5). Depende de 011.
- [ ] **T013-04** `src/main.py`: `_log_acotado()` para no inundar la consola con un fallo persistente (CNF-FR-002). Depende de T013-03.
- [ ] **T013-05** `tests/test_orquestacion.py`: `test_excepcion_en_pipeline_no_impide_salir` (CNF-FR-002). Depende de T013-03.
- [ ] **T013-06** `src/visualizacion/renderer.py`: `dibujar_frame(..., fps: float)` dibuja el FPS; `src/main.py` deja de llamar a `cv2.putText` y solo mide (CNF-FR-003, nuevo VIS-FR-007). Depende de 011.
- [ ] **T013-07 [P]** `src/preprocesamiento/filtro_ema.py`: `return list(self.x_prev)` en el primer frame (CNF-FR-004).
- [ ] **T013-08 [P]** `tests/test_filtro_ema.py`: `test_primer_frame_devuelve_copia_no_el_estado_interno` (CNF-FR-004). Depende de T013-07.
- [ ] **T013-09** `src/main.py`: loguear `resultado.mensaje` cuando `ejecutar_accion()` devuelve `exito=False` (CNF-FR-005). Depende de 011; complementa [010](../010-robustez-ejecutor/tasks.md), sin cuyo arreglo el reporte que se loguea aquí ni siquiera llega a existir.

### Grupo B — correcciones de spec (sin código)

- [ ] **T013-10 [P]** `specs/004-deteccion-mediapipe/spec.md`: reescribir DET-FR-002 — `x`,`y` en `[0,1]`; `z` es profundidad relativa con signo, sin garantía de rango (CNF-FR-006). Revisar de paso el caso borde de 005/spec.md Sección 5, que se apoya en la afirmación errónea.
- [ ] **T013-11 [P]** `specs/008-visualizacion/spec.md`: VIS-FR-005 pasa a pedir `G/ker(phi) = Im(phi)`, documentando que las fuentes Hershey de OpenCV no tienen glifo `≅` (CNF-FR-007).
- [ ] **T013-12 [P]** `specs/009-integracion-pipeline/spec.md` Sección 2 y docstring de `src/main.py`: `python -m src.main`, no `python src/main.py` (CNF-FR-008).
- [ ] **T013-13 [P]** `specs/003-captura-video/spec.md`: CAP-FR-001 pasa a "resolución configurada y 30 FPS fijos" (CNF-FR-009, recomendación de `spec.md`).

### Grupo C — cobertura de tests que falta

- [ ] **T013-14** `tests/test_pureza_algebra.py` (nuevo): `test_capa_algebraica_es_pura` vía `ast.parse` sobre `src/algebra/*.py` (CNF-FR-010, NFR-G03, HOM-FR-010). **Verificar que el test falla** añadiendo temporalmente `import cv2` a un módulo de `src/algebra/` antes de darlo por bueno.
- [ ] **T013-15 [P]** `src/algebra/grupo_gestos.py` y `grupo_acciones.py`: exponer `ELEMENTOS_G`/`IDENTIDAD_G` y `ELEMENTOS_A`/`IDENTIDAD_A` (CNF-FR-011, ALG-FR-008).
- [ ] **T013-16 [P]** `src/algebra/verificacion.py`: corregir el docstring — ni `grupo_gestos.py` ni `grupo_acciones.py` delegan en `verificar_axiomas_grupo()`; el único consumidor es la suite (CNF-FR-012).

**Definición de hecho:** los 60 tests existentes siguen en verde; los 4 tests nuevos (T013-02, T013-05, T013-08, T013-14) pasan; `grep -rn "putText" src/main.py` no devuelve nada; y añadir `import cv2` a `src/algebra/` **rompe** la suite (comprobado a mano una vez, luego revertido).
