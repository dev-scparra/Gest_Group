# Plan 004 — Detección de Landmarks (MediaPipe)

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/deteccion/
├── __init__.py
└── mediapipe_handler.py   # clase DetectorManos, envuelve mp.solutions.hands.Hands
```

## 2. Dependencias técnicas

`mediapipe==0.10.9` — **fijar esta versión exacta**. La API `mp.solutions.hands` fue reemplazada por `mp.tasks` en versiones posteriores de MediaPipe; actualizar sin revisar breaking changes rompe este módulo completo.

## 3. Notas de implementación

Implementación directa de la Sección 4.3 del documento de contexto, envuelta en una clase (el documento de contexto la deja como código suelto a nivel de módulo; aquí se encapsula en `DetectorManos` para que 009 pueda instanciarla junto a `CapturaVideo` sin variables globales compartidas).

## 4. Estrategia de pruebas

Igual que 003: MediaPipe requiere una imagen real para producir resultados útiles, así que no hay un mock razonable de "detecta mano" sin fixtures de imagen. Estrategia:

- `tests/test_deteccion.py` (ligero): confirma que `procesar()` con un frame de ruido aleatorio (sin mano) devuelve `None` — esto sí es determinista y corre en CI, sin cámara, usando una imagen sintética (`np.random.randint` o un frame en negro).
- Checklist manual de humo con cámara real (compartido con 003 y 005, ver `scripts/smoke_vision.py` en `plan.md` de la spec monolítica original — este script ahora es responsabilidad conjunta de 003+004+005).

## 5. Riesgo técnico

`min_detection_confidence`/`min_tracking_confidence` (0.7/0.5 por defecto) son sensibles a la cámara del equipo de desarrollo; si en la demo el hardware es distinto (webcam de menor calidad), puede requerir ajuste — se deja configurable vía `config/default.yaml` (coordinado con 009), no hardcodeado.
