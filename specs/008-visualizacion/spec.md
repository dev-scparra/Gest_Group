# Spec 008 — Visualización / Overlay

**Módulo:** `src/visualizacion/renderer.py`
**Depende de:** [006-clasificador-gestos](../006-clasificador-gestos/spec.md) (lee `Gesto`), [007-ejecutor-acciones](../007-ejecutor-acciones/spec.md) (lee `Accion`).
**Consumido por:** [009-integracion-pipeline](../009-integracion-pipeline/spec.md).
**Cubre:** US-2, US-4 de [000-overview](../000-overview/spec.md). NFR heredado: NFR-G0x no aplica ninguno adicional; añade NFR propio (Sección 4).

---

## 1. Propósito

Dar feedback visual inmediato del estado interno del sistema (qué gesto se detectó, qué acción se ejecutó, con qué α) sobre el frame de video, para que el usuario y el evaluador puedan verificar el comportamiento sin instrumentación adicional.

## 2. Contrato de interfaz

**Entradas:** `frame_bgr: np.ndarray`, `hand_landmarks` (objeto crudo de MediaPipe, de 004), `gesto: Gesto` (de 006), `accion: Accion` (resultado de φ, de 002), `alpha: float` (de 005/config).

**Salidas:** `frame_bgr` anotado (mismo array, mutado o retornado — a decidir en `plan.md`).

```python
def dibujar_frame(frame_bgr, hand_landmarks, gesto: Gesto, accion: Accion, alpha: float) -> np.ndarray: ...
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| VIS-FR-001 | DEBE dibujar los landmarks y conexiones de la mano sobre el frame cuando `hand_landmarks` no es `None` (usando `mp_drawing.draw_landmarks`). |
| VIS-FR-002 | DEBE mostrar como texto el gesto actual (`g = ...`) con un color distinto por gesto (tabla `COLORES_GESTO` de la Sección 7.6 del documento de contexto). |
| VIS-FR-003 | DEBE mostrar como texto la acción `φ(g)` del último gesto confirmado (no del gesto instantáneo — son conceptualmente distintos: el gesto instantáneo cambia cada frame, la acción mostrada debe reflejar el último disparo real de 006, para que US-2 no muestre una acción que en realidad no se ejecutó). **Quién decide ese valor es 009, no este módulo** — ver [011](../011-semantica-gesto-identidad/spec.md), SEM-FR-001: una confirmación cuya `φ(g)` es la identidad (`A_E`, un no-op) **no** desplaza a la última acción con efecto real. `accion` puede ser `None` ("aún no se ha confirmado ninguna"), que DEBE renderizarse distinto de `A_E` ("ninguna"), SEM-FR-003. |
| VIS-FR-004 | DEBE mostrar el valor de α activo. |
| VIS-FR-005 (corregido, ver 013/CNF-FR-007) | DEBE incluir la anotación fija `G/ker(phi) = Im(phi)` como recordatorio visual del marco algebraico (Sección 7.6 del documento de contexto) — valor pedagógico para la demo ante el profesor, no funcional. Se escribe `=` y **no** el `≅` matemáticamente correcto: las fuentes Hershey de OpenCV (`cv2.FONT_HERSHEY_SIMPLEX`) no tienen glifo para `≅` y lo renderizarían como `?`. Dibujar el símbolo real exigiría componer el texto con PIL/FreeType y volcarlo al frame — desproporcionado para una anotación decorativa; se descarta explícitamente. |
| VIS-FR-006 | Cuando no hay mano detectada (`hand_landmarks is None`), DEBE seguir mostrando el resto del overlay (gesto `E`, última acción, α) sin dibujar landmarks — no debe dejar la pantalla en blanco ni ocultar el resto de la información. |
| VIS-FR-007 (añadido por [013](../013-conformidad-menor/spec.md), CNF-FR-003) | DEBE dibujar el FPS sostenido cuando se le pasa (`fps: float \| None`). El FPS lo **mide** 009 (SC-G02 se lo asigna), pero **dibujarlo** es responsabilidad de este módulo: `main.py` no puede contener llamadas a `cv2.putText` sin violar 009/spec.md Secciones 1 y 6. |
| VIS-FR-008 (añadido por [011](../011-semantica-gesto-identidad/spec.md), SEM-FR-004) | DEBE distinguir visualmente el **gesto instantáneo** (en vivo, cambia cada frame) de la **última acción confirmada** (histórica, persiste entre disparos). Dibujarlos con el mismo peso y sin etiqueta induce a leer el overlay como si ambos fueran en vivo. |

## 4. Criterios de aceptación

- **Dado** un frame con `hand_landmarks` válido y `gesto=Gesto.G1`, **cuando** se llama `dibujar_frame()`, **entonces** el frame resultante contiene los landmarks dibujados y el texto `g = 1_dedo` en el color verde asignado a `G1`.
- **Dado** `hand_landmarks=None`, **cuando** se llama `dibujar_frame()`, **entonces** no se lanza excepción y el resto de las anotaciones de texto siguen presentes.
- **Dado** que el usuario sostiene `G1` (que ya disparó `A1`) y luego mueve la mano a una posición ambigua (`E` instantáneo, sin nueva confirmación), **cuando** se llama `dibujar_frame()` en ese frame, **entonces** el texto de "acción" sigue mostrando `A1` (VIS-FR-003 — la última acción confirmada, no se resetea a "ninguna" solo porque el gesto instantáneo cambió).

## 5. Casos borde

- Texto que se sale del frame (resolución muy pequeña o configuración custom): no se maneja layout responsivo en el MVP; las posiciones de texto están fijas en píxeles absolutos (igual que en el esbozo de la Sección 7.6 del documento de contexto), asumiendo 640×480.
- Colores poco legibles sobre fondos claros/oscuros de la habitación: mitigado con la elección de colores saturados de `COLORES_GESTO` (documento de contexto), no hay contraste dinámico automático (NFR propio, ver Sección 6).

## 6. Requerimiento no funcional propio

- **NFR-VIS-01 (Legibilidad de demo):** el tamaño de fuente y grosor de línea deben mantenerse legibles en una proyección de sala de clase (no solo en el monitor del desarrollador) — validar visualmente antes de la presentación, no solo en el laptop de desarrollo.

## 7. No objetivos de este módulo

- No decide qué gesto o acción mostrar — solo renderiza lo que 006/002 ya decidieron.
- No persiste ni graba video (fuera de alcance del MVP; `assets/demo.mp4` de la Sección 6 del documento de contexto se genera con una herramienta externa de grabación de pantalla, no por este módulo).
