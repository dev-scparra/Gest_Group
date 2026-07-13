# Plan 001 — Grupo Algebraico (G, A)

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/algebra/
├── __init__.py
├── grupo_gestos.py      # Gesto (enum), CAYLEY_G (dict), operacion_G()
├── grupo_acciones.py    # Accion (enum), CAYLEY_A (dict), operacion_A()
└── verificacion.py       # verificar_axiomas_grupo() genérico, reusado por ambos
```

`verificacion.py` es una adición respecto a la estructura de repositorio original (`plan.md` de la spec monolítica anterior no lo separaba) — se aísla porque ALG-FR-005 exige que la lógica de verificación de axiomas no se duplique entre G y A.

## 2. Representación técnica

- `Gesto` y `Accion`: `enum.Enum` estándar, igual que en el documento de contexto.
- Tabla de Cayley: `dict[tuple[Gesto, Gesto], Gesto]` con las 36 entradas explícitas. **No se deriva en runtime a partir de geometría** (eso violaría NFR-G03 — la capa algebraica no puede depender de landmarks). Se deriva **una sola vez, offline, a mano o por script auxiliar**, a partir de la representación en S₅ que el equipo elija (ver spec.md Sección 5, Opción A).
- Si se adopta la Opción A de spec.md (representación real en S₅): se sugiere un pequeño script `scripts/derivar_cayley.py` (fuera de `src/`, no se importa en producción) que tome las 6 permutaciones elegidas para g₁..g₅ y `e`, calcule las 36 composiciones con una función `componer_permutaciones()`, e imprima el `dict` resultante para pegarlo literal en `grupo_gestos.py`. Esto deja trazabilidad de *cómo* se obtuvo la tabla, sin acoplar el runtime a lógica de permutaciones que no se vuelve a usar.
- `operacion_G`/`operacion_A`: lookup `O(1)` en el diccionario; sin cómputo.

## 3. Dependencias técnicas

Ninguna externa — solo `enum` de la librería estándar. Es intencional: este es el módulo con menor superficie de fallo del proyecto.

## 4. Estrategia de pruebas

- `tests/test_grupo_gestos.py`: recorre las 36 combinaciones y valida clausura; valida asociatividad sobre las 216 ternas (6³); valida identidad y valida que cada elemento es su propio inverso.
- `tests/test_grupo_acciones.py`: mismo patrón sobre A, más el chequeo de conmutatividad (ALG-FR-007).
- `tests/test_verificacion.py`: test negativo — construir una tabla deliberadamente rota (p. ej. sin inverso para un elemento) y confirmar que `verificar_axiomas_grupo` lo detecta y reporta el axioma específico que falla.

Los tres archivos corren sin hardware, en <1s.

## 5. Orden de trabajo sugerido

1. Resolver el riesgo crítico de spec.md Sección 5 (decisión de equipo, no de código) — **bloqueante para todo lo demás**.
2. Si se elige Opción A: correr `scripts/derivar_cayley.py` y fijar la tabla resultante como constante.
3. Implementar `grupo_gestos.py` y `grupo_acciones.py` con las tablas ya decididas.
4. Implementar `verificacion.py` genérico.
5. Escribir los 3 archivos de test antes de dar el módulo por cerrado (ver [tasks.md](./tasks.md)).
