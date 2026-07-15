# Plan 014 — Combos Secuenciales

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/algebra/
├── grupo_gestos.py       # (001, sin cambios) operacion_G ya existe
├── homomorfismo.py       # (002, sin cambios) Homomorfismo.aplicar ya existe
└── combinador.py         # NUEVO — CombinadorGestos, ResultadoCombinacion

src/main.py                # (009) instancia CombinadorGestos, lo cablea en procesar_frame()
src/visualizacion/renderer.py  # (008) opcional: nueva linea de overlay para combos
config/default.yaml         # nueva clave combinador.ventana_s
```

`combinador.py` se coloca en `src/algebra/` junto a `grupo_gestos.py` y `homomorfismo.py`, no en `src/clasificador/` ni como código nuevo dentro de `main.py`. Razón: ya existe precedente directo — `Homomorfismo` vive en `src/algebra/` y también se instancia una sola vez en `main()` y se llama en vivo desde `procesar_frame()` (`homomorfismo.aplicar(...)`, ver 009/spec.md INT-FR-005). `CombinadorGestos` sigue exactamente el mismo patrón: una clase pura, sin I/O, instanciada una vez, invocada por frame. Ponerlo en `main.py` violaría 009/spec.md Sección 1 ("si aparece lógica de negocio propia dentro de `main.py`, es señal de que algo se filtró del módulo que le correspondía") — el precedente ya señalado por 013/CNF-FR-003 con el dibujo de FPS.

## 2. Representación técnica

```python
# src/algebra/combinador.py
from dataclasses import dataclass

from src.algebra.grupo_gestos import Gesto, operacion_G


@dataclass
class ResultadoCombinacion:
    gesto_efectivo: Gesto
    es_combo: bool
    gesto_previo: Gesto | None = None


class CombinadorGestos:
    def __init__(self, ventana_s: float = 1.5):
        self.ventana_s = ventana_s
        self._pendiente: Gesto | None = None
        self._timestamp: float | None = None

    def actualizar(self, gesto: Gesto, ahora: float) -> ResultadoCombinacion:
        if gesto == Gesto.E:                      # CMB-FR-003
            self.reset()
            return ResultadoCombinacion(Gesto.E, es_combo=False)

        if (
            self._pendiente is not None
            and self._timestamp is not None
            and (ahora - self._timestamp) <= self.ventana_s
        ):
            combinado = operacion_G(self._pendiente, gesto)   # CMB-FR-001
            resultado = ResultadoCombinacion(combinado, es_combo=True, gesto_previo=self._pendiente)
        else:
            resultado = ResultadoCombinacion(gesto, es_combo=False)   # CMB-FR-002

        self._pendiente = gesto                    # CMB-FR-004: SIEMPRE el crudo, no el combinado
        self._timestamp = ahora
        return resultado

    def reset(self) -> None:
        self._pendiente = None
        self._timestamp = None
```

Nótese que `_pendiente` se reasigna con el gesto **crudo** (`gesto`, no `resultado.gesto_efectivo`) tanto en la rama de combo como en la de no-combo — es la línea que implementa CMB-FR-004 y evita el encadenamiento accidental de 3+ gestos.

## 3. Cambios en `src/main.py` (009)

```python
from src.algebra.combinador import CombinadorGestos

def procesar_frame(
    frame_rgb, detector, filtro, estabilizador, homomorfismo, combinador, estado,
) -> tuple[Gesto, Accion | None]:
    ...
    gesto_confirmado = estabilizador.actualizar(gesto_actual)

    if gesto_confirmado is not None:
        resultado_combo = combinador.actualizar(gesto_confirmado, time.time())   # NUEVO
        accion = homomorfismo.aplicar(resultado_combo.gesto_efectivo)             # antes: aplicar(gesto_confirmado)
        ejecutar_resultado = ejecutar_accion(accion)
        ...
        if accion != Accion.A_E:
            estado.ultima_accion = accion
            estado.ultimo_combo = resultado_combo if resultado_combo.es_combo else None  # para 008 (opcional)

    return gesto_actual, estado.ultima_accion
```

`combinador: CombinadorGestos` se añade como parámetro nuevo de `procesar_frame`, instanciado una sola vez en `main()` junto a `homomorfismo = Homomorfismo()`, leyendo `ventana_s` de config (INT-FR-010 en 009/spec.md).

Si se implementa la visualización opcional (VIS-FR-009 en 008), `EstadoPipeline` gana un campo `ultimo_combo: ResultadoCombinacion | None = None`, con la misma regla de "no se pisa con `A_E`" que ya aplica a `ultima_accion` (SEM-FR-001, spec 011) — un combo que resulta en `A_E` no debería reemplazar la última visualización de combo real, igual que una confirmación de `E` no reemplaza `ultima_accion`.

## 4. Cambios en `config/default.yaml`

```yaml
combinador:
  ventana_s: 1.5
```

`cargar_config()` en `main.py` (INT-FR-001) añade `"combinador"` a `claves_requeridas`.

## 5. Cambios en `src/visualizacion/renderer.py` (008, opcional/P2)

`dibujar_frame(..., combo: ResultadoCombinacion | None = None)`: si `combo is not None and combo.es_combo`, dibuja una línea extra, p. ej. `combo con 1_dedo -> mano_abierta`, usando `combo.gesto_previo.value` (el gesto con el que se combinó) y `combo.gesto_efectivo.value` (el resultado `g₁∘g₂`). `ResultadoCombinacion` no guarda el segundo gesto crudo por separado, así que la línea se arma solo con esos dos campos. Se puede implementar en una segunda iteración sin bloquear el resto de la spec — el pipeline funciona igual sin esta línea, solo pierde valor de demo.

## 6. Dependencias técnicas

Ninguna externa nueva. `combinador.py` solo importa `dataclasses` (estándar) y `Gesto`/`operacion_G` de 001 — mismo perfil de dependencias que `homomorfismo.py`.

## 7. Estrategia de pruebas

- `tests/test_combinador.py` (nuevo, sin cámara ni reloj real — todos los `ahora` son floats literales):
  - Combo dentro de ventana (CMB-FR-001).
  - Sin combo, ventana expirada (CMB-FR-002).
  - Sin pendiente previo (primer gesto de la sesión).
  - `E` limpia el pendiente y nunca combina (CMB-FR-003), en ambas posiciones (como pendiente y como nuevo).
  - El pendiente tras un combo es el gesto crudo, no el combinado (CMB-FR-004) — replica el ejemplo de `spec.md` Sección 4, `G1→G3→G2`.
  - `ventana_s` custom distinto del default (CMB-FR-005).
  - Determinismo: dos llamadas con los mismos argumentos (incluido `ahora` explícito) dan el mismo resultado — no hay estado oculto dependiente del reloj real (CMB-FR-006).
- `tests/test_orquestacion.py` (existente, spec 009/011): añadir un caso que verifique que `procesar_frame` con un `combinador` real produce `φ(g₁∘g₂)` cuando dos gestos se confirman con timestamps controlados dentro de la ventana — cierra el círculo end-to-end (sin cámara, con dobles de prueba para `detector` como ya hace el resto de esa suite).
- `tests/test_pureza_algebra.py` (existente): cubre `combinador.py` automáticamente por estar en `src/algebra/`, sin cambios en el test.
- `tests/test_config.py` (existente): añadir caso para la clave `combinador.ventana_s` faltante → error explícito (mismo patrón que las claves existentes).

Todos corren sin hardware, en <1s adicional.

## 8. Orden de trabajo sugerido

1. `src/algebra/combinador.py` (`CombinadorGestos`, `ResultadoCombinacion`) + `tests/test_combinador.py` — aislado, no toca nada existente.
2. `config/default.yaml` (`combinador.ventana_s`) + `cargar_config()` en `main.py`.
3. `src/main.py`: instanciar `CombinadorGestos` en `main()`, cablear en `procesar_frame()` (INT-FR-010).
4. `tests/test_orquestacion.py`: caso end-to-end del combo.
5. (P2, opcional) `src/visualizacion/renderer.py`: línea de overlay del combo (VIS-FR-009) + `tests/test_renderer.py`.
6. Verificación de campo con cámara real: calibrar `ventana_s`, confirmar que un combo intencional se siente alcanzable y que gestos aislados normales no disparan combos espurios en el uso típico (ver `tasks.md`).
