# Spec 003 — Captura de Video

**Módulo:** `src/captura/video_capture.py`
**Depende de:** nada.
**Consumido por:** [004-deteccion-mediapipe](../004-deteccion-mediapipe/spec.md).
**NFRs heredados:** NFR-G02 (robustez ante fallos de E/S).

---

## 1. Propósito

Encapsular OpenCV para entregar, frame a frame, una imagen BGR y su versión RGB (requerida por MediaPipe), con la cámara configurada a una resolución y FPS fijos.

## 2. Contrato de interfaz

**Entradas:** `camara_id: int` (default 0), `ancho: int` (default 640), `alto: int` (default 480).

**Salidas:**

```python
class CapturaVideo:
    def __init__(self, camara_id: int = 0, ancho: int = 640, alto: int = 480): ...
    def leer_frame(self) -> tuple[bool, np.ndarray | None, np.ndarray | None]:
        """Retorna (exito, frame_bgr, frame_rgb)."""
    def liberar(self) -> None: ...
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| CAP-FR-001 (corregido, ver 013/CNF-FR-009) | DEBE abrir la cámara indicada por `camara_id` (default 0) a la **resolución configurada** (`ancho`×`alto`, default 640×480, leída de `config/default.yaml`) y a **30 FPS fijos**. La redacción original ("resolución y FPS configurados") sugería que el FPS era configurable; no lo es, y no hay caso de uso que lo pida — añadir una perilla de config sin consumidor es superficie gratuita. Si algún día hace falta, se añade `camara.fps` a la config y se pasa al constructor. |
| CAP-FR-002 | DEBE aplicar espejo horizontal (`cv2.flip(frame, 1)`) para que el movimiento en pantalla coincida con el movimiento real del usuario frente a la cámara. |
| CAP-FR-003 | DEBE entregar tanto el frame BGR crudo como su conversión a RGB en la misma llamada, para que el módulo 004 no tenga que repetir la conversión. |
| CAP-FR-004 | `leer_frame()` DEBE devolver `(False, None, None)` si la cámara no entrega frame (desconexión, fin de stream), sin lanzar excepción. |
| CAP-FR-005 | `liberar()` DEBE liberar el dispositivo de cámara y cerrar ventanas OpenCV asociadas; DEBE ser seguro llamarla más de una vez (idempotente). |

## 4. Criterios de aceptación

- **Dado** una cámara conectada y disponible, **cuando** se llama `leer_frame()` repetidamente, **entonces** se obtiene `(True, frame_bgr, frame_rgb)` con `frame_bgr.shape == (480, 640, 3)`.
- **Dado** que la cámara se desconecta a mitad de sesión, **cuando** se llama `leer_frame()`, **entonces** se obtiene `(False, None, None)` y el proceso que consume esta clase puede decidir terminar limpio (no es este módulo el que decide qué hacer, solo reporta el fallo — NFR-G02).
- **Dado** `camara_id` inválido (sin cámara en ese índice), **cuando** se instancia `CapturaVideo`, **entonces** el fallo ocurre de forma observable en el primer `leer_frame()` (OpenCV no siempre falla en `VideoCapture()`), no de forma silenciosa indefinida.

## 5. Casos borde

- Sistema sin ninguna cámara disponible (CI, servidor headless): este módulo no se prueba con hardware real en la suite automatizada (ver `plan.md`); solo se prueba manualmente (checklist de humo).
- Cámara ocupada por otra aplicación: se espera que `cv2.VideoCapture` falle en la apertura; no hay lógica especial de reintento en el MVP (fuera de alcance).
- Permisos de cámara denegados por el SO (macOS pide permiso explícito a la app/terminal la primera vez): documentado como paso de instalación, no como manejo de error en código.

## 6. No objetivos de este módulo

- No detecta manos ni landmarks (eso es 004).
- No decide FPS objetivo del pipeline completo, solo el FPS que se le pide a la cámara — el FPS real sostenido del pipeline es responsabilidad de 009 (medición, SC-G02).
