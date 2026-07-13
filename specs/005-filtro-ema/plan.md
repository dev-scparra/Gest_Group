# Plan 005 — Filtro EMA

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/preprocesamiento/
├── __init__.py
└── filtro_ema.py   # clase FiltroEMA
```

## 2. Dependencias técnicas

Ninguna externa más allá de la estructura de datos de entrada (listas/tuplas nativas). No requiere NumPy aunque podría usarse para vectorizar — con 21×3 = 63 valores por frame, el costo de no vectorizar es despreciable frente al de MediaPipe/OpenCV.

## 3. Notas de implementación

Implementación directa de la Sección 4.4/7.2 del documento de contexto, con dos adiciones respecto al esbozo original:

- Validación de `alpha ∈ (0,1)` en el constructor y en el setter de EMA-FR-005 (caso borde de spec.md Sección 5).
- `reset()` ya estaba en el esbozo original; aquí se formaliza *quién* es responsable de invocarlo (EMA-FR-003) para que no quede como detalle implícito que alguien olvide al cablear 009.

## 4. Demostración de estabilidad (Demostración 4 del documento de contexto)

Este módulo es el único cuya correctitud matemática (no solo de código) se puede demostrar analíticamente sin depender de datos empíricos: la ecuación en diferencias `x[n]-(1-α)x[n-1]=α·x_raw[n]` tiene solución homogénea `x_h[n]=C(1-α)ⁿ`, que converge a 0 para `α∈(0,1)`. El test `test_convergencia_ema` (ver `tasks.md`) es la evidencia empírica que acompaña esta demostración analítica en `docs/demostraciones.md`.

## 5. Estrategia de pruebas

- `tests/test_filtro_ema.py`: `test_convergencia_ema`, `test_estabilidad_ruido` (ambos ya definidos en la Sección 10 del documento de contexto) + `test_reset_limpia_historia` (nuevo, cubre EMA-FR-002/003) + `test_alpha_invalido_falla` (nuevo, cubre el caso borde de validación).
- 100% de estos tests son deterministas, sin cámara, corren en milisegundos.
