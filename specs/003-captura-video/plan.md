# Plan 003 — Captura de Video

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/captura/
├── __init__.py
└── video_capture.py   # clase CapturaVideo (implementación base: Sección 7.1 del doc. de contexto)
```

## 2. Dependencias técnicas

`opencv-python==4.9.0.80` (única dependencia externa).

## 3. Notas de implementación

Implementación directa de la Sección 7.1 del documento de contexto; el único cambio respecto al esbozo original es que `leer_frame()` debe devolver `(False, None, None)` de forma explícita en vez de dejar que una excepción de OpenCV se propague (CAP-FR-004) — se envuelve la llamada a `self.cap.read()` sin try/except adicional porque `cv2.VideoCapture.read()` ya devuelve `(False, None)` en fallo por diseño; solo hay que respetar ese contrato en vez de asumir siempre éxito.

## 4. Estrategia de pruebas

- **No hay tests automatizados de hardware real** para este módulo (no es reproducible en CI). Se prueba con:
  - `tests/test_video_capture.py` (unitario, con mock de `cv2.VideoCapture`): verifica que `leer_frame()` propaga correctamente `(False, None, None)` cuando el mock simula fallo, y que aplica el flip cuando el mock simula éxito — esto sí es determinista y corre sin cámara real.
  - Checklist manual de humo (ver `tasks.md`) con cámara real, una sola vez por integrante antes de dar el módulo por cerrado.

## 5. Riesgo técnico

macOS exige permiso de "Cámara" para la app/terminal que ejecuta Python (distinto del permiso de Accesibilidad que necesita 007). Si no está concedido, `cv2.VideoCapture(0).isOpened()` puede devolver `False` sin mensaje claro — documentar en README como paso de instalación (mismo patrón que el riesgo de Accesibilidad en el módulo 007).
