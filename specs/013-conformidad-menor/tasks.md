# Tasks 013 — Backlog de Conformidad Menor

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md). CNF-FR-003 y CNF-FR-005 tocan `main.py`, que [011](../011-semantica-gesto-identidad/tasks.md) reestructura: se aplicaron después.

### Grupo A — desviaciones de código

- [x] **T013-01** `src/algebra/homomorfismo.py`: validar `set(tabla_phi) != set(Gesto)` → `ValueError` con faltantes **y** sobrantes (CNF-FR-001).
- [x] **T013-02** `tests/test_homomorfismo.py`: `test_tabla_con_clave_espuria_falla_en_constructor` (CNF-FR-001).
- [x] **T013-03** `src/main.py`: `cv2.imshow` / `cv2.waitKey` fuera del bloque `try`; ante excepción, el frame se trata como "sin mano" y se sigue renderizando (CNF-FR-002, 009/Sec. 5). La tecla `q` (INT-FR-007) ya no puede quedar inalcanzable.
- [x] **T013-04** `src/main.py`: `_log_acotado()` — primera ocurrencia + 1 de cada 30, para que un fallo persistente no inunde la consola (CNF-FR-002).
- [x] **T013-05** `tests/test_orquestacion.py`: `test_fallo_de_accion_no_propaga_excepcion` (NFR-G02 en el loop).
- [x] **T013-06** `src/visualizacion/renderer.py`: `dibujar_frame(..., fps)` dibuja el FPS; `src/main.py` lo **mide** (`MedidorFPS`) pero ya no llama a `cv2.putText` (CNF-FR-003, nuevo VIS-FR-007).
- [x] **T013-07** `src/preprocesamiento/filtro_ema.py`: `return list(self.x_prev)` en el primer frame (CNF-FR-004).
- [x] **T013-08** `tests/test_filtro_ema.py`: `test_primer_frame_devuelve_copia_no_el_estado_interno` (CNF-FR-004).
- [x] **T013-09** `src/main.py`: loguear `resultado.mensaje` cuando `ejecutar_accion()` devuelve `exito=False` (CNF-FR-005, nuevo INT-FR-009). Sin esto, todo el reporte de errores de [010](../010-robustez-ejecutor/spec.md) moría en silencio.

### Grupo B — correcciones de spec (sin código)

- [x] **T013-10** `specs/004-deteccion-mediapipe/spec.md`: DET-FR-002 corregido — `x`,`y` en `[0,1]`; `z` es profundidad relativa con signo, sin garantía de rango (CNF-FR-006). Añadido DET-FR-006 (lateralidad, de 012).
- [x] **T013-11** `specs/008-visualizacion/spec.md`: VIS-FR-005 pasa a pedir `G/ker(phi) = Im(phi)`, documentando que las fuentes Hershey de OpenCV no tienen glifo `≅` (CNF-FR-007). Añadidos VIS-FR-007 (FPS) y VIS-FR-008 (en vivo vs. última).
- [x] **T013-12** `specs/009-integracion-pipeline/spec.md` Sección 2 y docstring de `src/main.py`: `python -m src.main`, no `python src/main.py` (CNF-FR-008).
- [x] **T013-13** `specs/003-captura-video/spec.md`: CAP-FR-001 pasa a "resolución configurada y 30 FPS fijos" (CNF-FR-009).

### Grupo C — cobertura de tests que faltaba

- [x] **T013-14** `tests/test_pureza_algebra.py` (nuevo): `test_capa_algebraica_no_importa_io_ni_vision` vía `ast.parse` sobre `src/algebra/*.py` (CNF-FR-010, NFR-G03, HOM-FR-010). **Se comprobó que el test falla**: inyectando `import cv2` en `src/algebra/analisis.py` la suite se pone en rojo; revertido. Un test de invariante que nunca se vio fallar no es un test.
- [x] **T013-15** `src/algebra/grupo_gestos.py` y `grupo_acciones.py`: `ELEMENTOS_G`/`IDENTIDAD_G` y `ELEMENTOS_A`/`IDENTIDAD_A` (CNF-FR-011, ALG-FR-008).
- [x] **T013-16** `src/algebra/verificacion.py`: docstring corregido — ni `grupo_gestos.py` ni `grupo_acciones.py` delegan en `verificar_axiomas_grupo()`; el único consumidor es la suite (CNF-FR-012).

**Definición de hecho:** los 60 tests previos siguen en verde, los nuevos pasan (86 en total), `grep -rn "putText" src/main.py` no devuelve nada, y añadir `import cv2` a `src/algebra/` **rompe** la suite (comprobado y revertido) — **cumplido**.
