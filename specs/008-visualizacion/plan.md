# Plan 008 — Visualización / Overlay

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/visualizacion/
├── __init__.py
└── renderer.py   # dibujar_frame(), COLORES_GESTO
```

## 2. Dependencias técnicas

`opencv-python` (ya presente por 003), `mediapipe` (ya presente por 004, solo para `mp.solutions.drawing_utils`).

## 3. Notas de implementación

Implementación directa de la Sección 7.6 del documento de contexto. Decisión de contrato (spec.md Sección 2): `dibujar_frame()` **muta y retorna** el mismo array `frame_bgr` (no crea copia) — coherente con el patrón ya usado por OpenCV en el resto del pipeline y evita una copia de 640×480×3 bytes por frame, relevante para NFR-G01 (≥15 FPS).

La distinción entre "gesto instantáneo" y "última acción confirmada" (VIS-FR-003) implica que 009 debe pasarle a este módulo **dos valores separados y con ciclo de vida distinto**: el `Gesto` crudo del frame actual (para el texto `g = ...`) y la `Accion` que quedó de la última confirmación de `EstabilizadorGesto` (que puede ser de varios frames atrás) — este módulo no la calcula, solo la recibe y la muestra.

## 4. Estrategia de pruebas

- `tests/test_renderer.py`: llamar `dibujar_frame()` con un frame sintético (`np.zeros((480,640,3), dtype=np.uint8)`), `hand_landmarks=None`, y valores fijos de `gesto`/`accion`/`alpha` — verificar que la función retorna sin excepción y que el array de salida tiene la misma forma que la entrada. No se valida el contenido visual exacto por test automatizado (sería frágil); la validación visual real es manual (checklist).
- Checklist manual: capturar un screenshot con cada uno de los 6 gestos activos y confirmar legibilidad (NFR-VIS-01).
