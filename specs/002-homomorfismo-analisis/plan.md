# Plan 002 — Homomorfismo φ y Análisis Algebraico

**Depende de:** [spec.md](./spec.md), y técnicamente de [001-grupo-algebraico/plan.md](../001-grupo-algebraico/plan.md).

## 1. Ubicación en el repositorio

```
src/algebra/
├── homomorfismo.py   # clase Homomorfismo (ver contrato en spec.md)
└── analisis.py         # script CLI, punto de entrada: `python -m src.algebra.analisis`
```

## 2. Representación técnica

- `Homomorfismo` implementa exactamente lo ya esbozado en la Sección 7.4 del documento de contexto; la única adición respecto a ese esbozo es la validación de totalidad en el constructor (HOM-FR-001) y el uso de `operacion_G`/`operacion_A` reales del módulo 001 dentro de `verificar_homomorfismo()` en vez de recibirlas como parámetros genéricos `callable` — al fijar la dependencia directa con 001 se elimina la posibilidad de pasar una operación inconsistente por error.
- `ReporteHomomorfismo` (tipo de retorno de `verificar_homomorfismo`): estructura simple (`namedtuple` o `dataclass`) con `cumple: bool` y `pares_fallidos: list[tuple[Gesto,Gesto]]` — si algún par falla, `analisis.py` debe poder imprimir *cuáles* fallaron, no solo que algo falló (mismo principio que `verificar_axiomas_grupo` en 001).

## 3. Dependencias técnicas

Solo el módulo 001 (`src/algebra/grupo_gestos.py`, `grupo_acciones.py`). Sin librerías externas.

## 4. Estrategia de pruebas

- `tests/test_homomorfismo.py`: los 5 tests ya definidos en la Sección 10 del documento de contexto (identidad, kernel trivial, inyectividad, imagen completa, cardinalidad de clases = cardinalidad de imagen) **más** `test_verificar_homomorfismo_sobre_cayley` (recorre los 36 pares, cubre SC-G04 literalmente) **más** el caso de tabla φ custom con kernel no trivial (criterios de aceptación, spec.md Sección 4, último punto).
- Todos estos tests son deterministas y corren sin hardware.

## 5. `analisis.py` como entregable del reporte técnico

Este script es, en la práctica, el artefacto que se anexa como evidencia en `docs/demostraciones.md`: se ejecuta, se captura su salida, y esa salida (no una captura de pantalla de la app corriendo) es lo que respalda las Demostraciones 2 y 3 del documento de contexto ante el profesor. Por eso su formato de salida debe ser texto plano legible copy-pasteable, no solo `print(objeto)` de Python.
