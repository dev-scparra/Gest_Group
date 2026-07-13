# Plan 009 — Integración y Configuración

**Depende de:** [spec.md](./spec.md), y transitivamente de los `plan.md` de 001-008.

## 1. Ubicación en el repositorio

```
config/
└── default.yaml        # alpha, frames_estables, camara_id, ancho, alto, umbrales mediapipe
src/
└── main.py              # loop principal, único punto de entrada del proceso
```

## 2. Estructura de `config/default.yaml`

```yaml
camara:
  id: 0
  ancho: 640
  alto: 480
filtro_ema:
  alpha: 0.3
estabilizador:
  frames_estables: 10
deteccion:
  min_detection_confidence: 0.7
  min_tracking_confidence: 0.5
```

Se lee con `pyyaml` (única dependencia nueva respecto a lo fijado en los módulos 001-008 — se añade a `requirements.txt` en esta fase).

## 3. Notas de implementación

`main.py` instancia una vez, al arrancar: `CapturaVideo`, `DetectorManos`, `FiltroEMA`, `EstabilizadorGesto`, `Homomorfismo` (por defecto). El loop por frame sigue el orden de INT-FR-002. El estado "última acción confirmada" (INT-FR-006) es una variable local del loop, inicializada en `Accion.A_E`.

Pseudocódigo de la parte crítica (manejo de mano perdida, INT-FR-003/004):

```python
landmarks = detector.procesar(frame_rgb)
if landmarks is None:
    filtro.reset()
    gesto_confirmado = estabilizador.actualizar(Gesto.E)
else:
    landmarks_suav = filtro.aplicar(landmarks)
    gesto_actual = clasificar_gesto(landmarks_suav)
    gesto_confirmado = estabilizador.actualizar(gesto_actual)

if gesto_confirmado is not None:
    ultima_accion = homomorfismo.aplicar(gesto_confirmado)
    ejecutar_accion(ultima_accion)
```

## 4. Estrategia de pruebas

- **No hay test unitario de `main.py` en el sentido estricto** (es orquestación de I/O real). En su lugar:
  - `tests/test_config.py`: cargar `config/default.yaml` real y verificar que los valores esperados están presentes con los tipos correctos — detecta config rota antes de tocar cámara.
  - Checklist de humo end-to-end (ver `tasks.md`) — es donde se mide SC-G01, SC-G02, SC-G03 con el sistema completo.

## 5. Riesgo de integración

Este módulo es el único que ve el pipeline completo, por lo que cualquier incompatibilidad de contrato entre módulos (p. ej. si 006 cambia la firma de `EstabilizadorGesto.actualizar()` sin avisar) se manifiesta aquí primero. Se recomienda que, al cerrar cada módulo 001-008, se haga una integración incremental en `main.py` (no esperar a tener los 8 módulos terminados para cablear por primera vez) — esto ya está reflejado en las fases de `plan.md` original consolidado: Fase 1 y 2 en paralelo, Fase 3 sobre 2, Fase 4 integra 1+3, etc.
