# Plan 006 — Clasificador de Gestos + Estabilizador

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/clasificador/
├── __init__.py
├── gestos.py           # dedos_levantados(), clasificar_gesto()
└── estabilizador.py     # EstabilizadorGesto
```

## 2. Dependencias técnicas

`Gesto` del módulo 001 (`src/algebra/grupo_gestos.py`). Sin librerías externas — es lógica geométrica pura sobre listas de tuplas de floats.

## 3. Notas de implementación

- `dedos_levantados()` y `clasificar_gesto()`: implementación directa de la Sección 4.5 del documento de contexto (`PUNTAS = [4,8,12,16,20]`, `MCPS = [2,5,9,13,17]`).
- `EstabilizadorGesto`: implementación directa de la Sección 4.5 del documento de contexto, con el `reset()` explícito añadido (spec.md Sección 6, segundo punto) que el esbozo original no tenía — se añade como método público, no como parte del constructor, para que 009 pueda invocarlo en el momento exacto en que 004 reporta pérdida de mano.

## 4. Estrategia de pruebas

- **Fixtures sintéticas de landmarks:** se necesita una función auxiliar por gesto (`generar_landmark_puno()`, `generar_landmark_un_dedo()`, etc., mencionadas en la Sección 10 del documento de contexto) que construya una lista de 21 tuplas `(x,y,z)` con las relaciones punta/MCP correctas para cada gesto. Se centralizan en `tests/fixtures_landmarks.py` para reusarlas entre `test_clasificador.py` y, si hiciera falta, `test_estabilizador.py`.
- `tests/test_clasificador.py`: un test por cada uno de los 6 elementos de G (5 gestos + `E`) más el caso ambiguo explícito (spec.md Sección 5).
- `tests/test_estabilizador.py`: los 4 casos de aceptación de debounce (spec.md Sección 4, últimos 4 puntos) — sin frames_estables-1, en frames_estables, tras confirmación, y tras reinicio por cambio de gesto.

Ambos archivos corren sin cámara ni MediaPipe real — son la razón por la que se centralizan fixtures sintéticas en vez de depender de capturas reales.

## 5. Medición de SC-G01 (≥90% de aciertos)

Este módulo es el que determina si SC-G01 se cumple, pero **no se mide con `pytest`** (los tests unitarios verifican la lógica de clasificación sobre datos sintéticos ya correctos, no la tasa de acierto de MediaPipe+geometría sobre manos reales). La medición real de SC-G01 vive en el checklist de humo de la Fase de cierre (módulo 009, `tasks.md`), donde se ejecutan repeticiones reales frente a cámara y se cuentan aciertos/fallos.
