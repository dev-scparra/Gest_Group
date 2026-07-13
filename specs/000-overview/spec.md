# GestGroup — Visión General y Mapa de Módulos

**Rol de este documento:** punto de entrada a las especificaciones. No repite requerimientos detallados (esos viven en cada módulo); fija lo que es *cruzado a todos los módulos* — visión, prioridades, requerimientos no funcionales globales, criterios de éxito globales, riesgos globales y el mapa de dependencias entre specs.

**Fuente base:** `GestGroup_Contexto_Desarrollo.md`.
**Convención de esta carpeta:** cada módulo de `src/` tiene su propia carpeta `NNN-nombre-modulo/` con `spec.md` (qué/por qué del módulo, contrato de interfaz), `plan.md` (cómo técnico) y `tasks.md` (backlog granular). Los IDs de requerimiento de cada módulo usan un prefijo propio para que sean referenciables sin ambigüedad entre módulos (ver tabla de la Sección 3).

---

## 1. Visión

GestGroup es una aplicación de control por gestos en tiempo real cuyo diferenciador es que el mapeo gesto → acción está modelado como un homomorfismo de grupos φ : G → A, con G ≤ S₅. El sistema completo es un pipeline de 5 etapas (captura → detección → filtro → clasificación → φ/acción) más una capa transversal de visualización, todo orquestado por un módulo de integración.

## 2. Historias de usuario globales (priorizadas)

| ID | Historia | Prioridad | Módulos involucrados |
|---|---|---|---|
| US-1 | Como usuario, levanto el índice y sube el volumen | P1 | 003, 004, 005, 006, 002, 007, 009 |
| US-2 | Como usuario, veo en pantalla el gesto y la acción detectados | P1 | 006, 002, 008, 009 |
| US-3 | Como usuario, los 6 gestos producen las 6 acciones documentadas | P1 | 002, 006, 007 |
| US-4 | Como usuario/demo, ajusto α en caliente y veo el efecto | P2 | 005, 008, 009 |
| US-5 | Como evaluador, corro una suite que verifica ker(φ), Im(φ), G/ker(φ) y el teorema de isomorfismo sin cámara | P1 | 001, 002 |
| US-6 | Como usuario, la app no se cae si pierdo la mano de cuadro | P1 | 003, 004, 005, 006, 009 |
| US-7 | Como usuario en macOS, el control funciona de inmediato; Linux es deseable, Windows opcional | P3 | 007 |

El detalle de cada historia (criterios Given/When/Then) vive en el `spec.md` del módulo dueño (columna "Módulos involucrados", primer módulo listado).

## 3. Mapa de módulos

| # | Módulo | Paquete en `src/` | Prefijo de requerimiento | Depende de |
|---|---|---|---|---|
| [001](../001-grupo-algebraico/spec.md) | Grupo algebraico (G, A) | `src/algebra/grupo_gestos.py`, `grupo_acciones.py` | `ALG-` | — |
| [002](../002-homomorfismo-analisis/spec.md) | Homomorfismo φ y análisis | `src/algebra/homomorfismo.py`, `analisis.py` | `HOM-` | 001 |
| [003](../003-captura-video/spec.md) | Captura de video | `src/captura/video_capture.py` | `CAP-` | — |
| [004](../004-deteccion-mediapipe/spec.md) | Detección de landmarks | `src/deteccion/mediapipe_handler.py` | `DET-` | 003 |
| [005](../005-filtro-ema/spec.md) | Filtro EMA | `src/preprocesamiento/filtro_ema.py` | `EMA-` | 004 |
| [006](../006-clasificador-gestos/spec.md) | Clasificador + estabilizador | `src/clasificador/gestos.py`, `estabilizador.py` | `CLA-` | 005 |
| [007](../007-ejecutor-acciones/spec.md) | Ejecutor de acciones | `src/acciones/ejecutor.py` | `ACC-` | 002 |
| [008](../008-visualizacion/spec.md) | Visualización / overlay | `src/visualizacion/renderer.py` | `VIS-` | 006, 007 |
| [009](../009-integracion-pipeline/spec.md) | Integración y configuración | `src/main.py`, `config/default.yaml` | `INT-` | todos |

```
001 grupo-algebraico ──▶ 002 homomorfismo-analisis ─────────────────┐
                                                                     ▼
003 captura ─▶ 004 deteccion ─▶ 005 filtro-ema ─▶ 006 clasificador ─▶ (φ) ─▶ 007 acciones ─▶ 008 visualizacion ─▶ 009 integracion
```

Nota de secuenciación: 001 y 002 no dependen de hardware y pueden construirse/probarse/defenderse el mismo día del setup, en paralelo con 003-005. El punto de integración real entre "mundo matemático" y "mundo de visión" ocurre en 007 (el ejecutor recibe φ(g) calculado por 002 a partir de un gesto clasificado por 006).

## 4. Requerimientos no funcionales globales (aplican a todos los módulos)

| ID | Requerimiento |
|---|---|
| NFR-G01 (Rendimiento) | El pipeline completo sostiene ≥15 FPS en CPU, sin GPU. |
| NFR-G02 (Robustez) | Ninguna excepción de un módulo de E/S (cámara, MediaPipe, subprocess) puede propagarse y matar el proceso; cada módulo define su degradación explícita en su propio `spec.md`. |
| NFR-G03 (Testabilidad) | Los módulos 001 y 002 (capa algebraica) son puros: sin `cv2`, sin `mediapipe`, sin `subprocess`. Se prueban con `pytest` sin hardware. |
| NFR-G04 (Privacidad) | Sin red, sin telemetría, sin persistencia de video en disco por defecto. |
| NFR-G05 (Portabilidad) | macOS primario, Linux secundario, Windows fuera de alcance del MVP (detalle en 007). |

Cada módulo puede añadir NFRs propios en su `spec.md`; estos son el piso común.

## 5. Criterios de éxito globales

- **SC-G01:** ≥90% de aciertos de gesto sobre ≥20 repeticiones por gesto, en condiciones de iluminación estándar (detalle de medición en 006).
- **SC-G02:** ≥15 FPS sostenidos durante ≥5 minutos de uso continuo (detalle de medición en 009).
- **SC-G03:** latencia gesto-estable→acción ≤500ms en el 95% de los disparos (detalle en 006+007).
- **SC-G04:** 100% de los pares (gᵢ,gⱼ)∈G×G satisface φ(gᵢ∘gⱼ)=φ(gᵢ)∘φ(gⱼ), verificado automáticamente (detalle en 002).
- **SC-G05:** las 4 demostraciones formales del reporte (Sección 8 del doc. de contexto) tienen respaldo ejecutable (tests en verde) — repartido entre 001 (Demostración 1), 002 (Demostraciones 2 y 3), 005 (Demostración 4).

## 6. Riesgos globales

Ver Sección 8 de la especificación previa consolidada; cada riesgo específico de un módulo vive ahora en el `spec.md` de ese módulo. Riesgo transversal que no pertenece a ningún módulo en particular: **fragmentación excesiva** — con 9 módulos + overview, el equipo debe evitar duplicar requerimientos NFR ya cubiertos aquí dentro de cada módulo; cuando un módulo hereda un NFR global, debe referenciarlo por ID (`NFR-G0x`) en vez de redactarlo de nuevo.

## 7. Supuestos y preguntas abiertas globales

- **Q1 — Disparo único vs. repetición mientras se sostiene el gesto:** resuelto en 006 (disparo único, ver `spec.md` de 006, Sección de supuestos).
- **Q2 — Manejo de fallo silencioso de `osascript`:** resuelto en 007.
- **Q3 — Prioridad de SO:** macOS primario (entorno de desarrollo). Resuelto en 007.
- **Q4 — Config al inicio vs. hot-reload:** resuelto en 009 (config al inicio para el MVP; hot-reload de α es P2 y vive también como opción en 005/008).

---

*Orden de lectura recomendado: este documento → 001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009.*
