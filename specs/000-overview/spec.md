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
| US-7 | Como usuario en macOS o Windows, el control funciona de inmediato con las 5 acciones; en Linux, al menos el control de volumen | P2 | 007 |

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

### 3.1 Specs de corrección (auditoría de conformidad, 2026-07-13)

Los módulos 001-009 están implementados y su suite (60 tests) está en verde. Una auditoría línea a línea de specs↔código encontró cuatro grupos de desviaciones, documentados como specs nuevas en vez de parchearse en silencio. **No modifican el diseño**: corrigen la distancia entre lo que las specs 001-009 dicen y lo que el código hace (o, en algunos casos, corrigen la spec, porque el código tenía razón).

| # | Spec de corrección | Prefijo | Severidad | Corrige a |
|---|---|---|---|---|
| [010](../010-robustez-ejecutor/spec.md) | Robustez del ejecutor ante fallo del binario de SO | `ROB-` | **Alta** | 007 |
| [011](../011-semantica-gesto-identidad/spec.md) | Semántica del gesto identidad y "última acción confirmada" | `SEM-` | Media | 006, 008, 009 |
| [012](../012-clasificador-pulgar-lateralidad/spec.md) | Clasificador: pulgar, puño y lateralidad de la mano | `PUL-` | **Alta** | 004, 006 |
| [013](../013-conformidad-menor/spec.md) | Backlog de conformidad menor (12 ítems transversales) | `CNF-` | Baja-Media | 001, 003, 004, 005, 008, 009 |

**Orden de aplicación recomendado:** 010 (aislado, no colisiona con nada) → 011 (reestructura `main.py` y crea la suite de orquestación que hoy no existe) → 012 (depende de la cámara para medir el signo del pulgar) → 013 (dos de sus ítems tocan el `main.py` que 011 reestructura).

**Lección transversal de la auditoría:** los tres defectos con consecuencia funcional real (010, 011, 012) sobrevivieron a 60 tests en verde, y por el mismo motivo en los tres casos — *el test modelaba el camino feliz con la misma suposición que el código*. En 010, el mock de `subprocess.run` nunca podía lanzar `FileNotFoundError`, que es justo el caso borde que la spec exigía cubrir. En 011, el requerimiento (VIS-FR-003) regula un valor que decide 009, pero se probó en la suite de 008. En 012, los fixtures sintéticos se generaron con la misma convención de lateralidad que el clasificador asume. Un test escrito desde la misma premisa que el código no verifica la premisa: la hereda. De ahí que las tres specs nuevas exijan **ver fallar el test antes de aplicar el fix**.

Nota de secuenciación: 001 y 002 no dependen de hardware y pueden construirse/probarse/defenderse el mismo día del setup, en paralelo con 003-005. El punto de integración real entre "mundo matemático" y "mundo de visión" ocurre en 007 (el ejecutor recibe φ(g) calculado por 002 a partir de un gesto clasificado por 006).

## 4. Requerimientos no funcionales globales (aplican a todos los módulos)

| ID | Requerimiento |
|---|---|
| NFR-G01 (Rendimiento) | El pipeline completo sostiene ≥15 FPS en CPU, sin GPU. |
| NFR-G02 (Robustez) | Ninguna excepción de un módulo de E/S (cámara, MediaPipe, subprocess) puede propagarse y matar el proceso; cada módulo define su degradación explícita en su propio `spec.md`. |
| NFR-G03 (Testabilidad) | Los módulos 001 y 002 (capa algebraica) son puros: sin `cv2`, sin `mediapipe`, sin `subprocess`. Se prueban con `pytest` sin hardware. |
| NFR-G04 (Privacidad) | Sin red, sin telemetría, sin persistencia de video en disco por defecto. |
| NFR-G05 (Portabilidad) | macOS y Windows soportados en el MVP con paridad completa de las 5 acciones no-identidad (un solo proyecto Python, backend por SO seleccionado en runtime vía `platform.system()` — ver 007); Linux soportado de forma secundaria (solo volumen). |

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
- **Q3 — Prioridad de SO:** macOS y Windows con paridad completa (5 acciones); Linux secundario (solo volumen). Un único proyecto Python — el ejecutor de acciones (007) selecciona el backend por SO en runtime, sin duplicar el resto del pipeline. Resuelto en 007.
- **Q4 — Config al inicio vs. hot-reload:** resuelto en 009 (config al inicio para el MVP; hot-reload de α es P2 y vive también como opción en 005/008).

---

*Orden de lectura recomendado: este documento → 001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → (correcciones) 010 → 011 → 012 → 013.*
