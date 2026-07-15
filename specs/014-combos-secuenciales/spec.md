# Spec 014 — Combos Secuenciales: aplicar ∘ en vivo (Opción A)

> **⚠️ SUPERADA por [015-captura-guiada-combos](../015-captura-guiada-combos/spec.md) como modelo de interacción.** La idea central de esta spec —usar la composición `∘` de `G` en vivo, `φ(g₁∘g₂)`— sigue vigente y se conserva en 015. Lo que cambió es *cómo* se capturan y disparan los dos gestos: 014 usaba una ventana de **tiempo** (`ventana_s`) sobre gestos ya confirmados por el `EstabilizadorGesto`, y mantenía el disparo inmediato de gestos aislados; 015 lo reemplaza por una **captura guiada con votación de mayoría sobre ventanas de frames** (para que la transición entre gestos no ensucie la lectura) y hace del par la única forma de disparo. El módulo `src/algebra/combinador.py` de esta spec fue **eliminado**; su reemplazo es `src/clasificador/capturador_combo.py`. Se conserva este documento por trazabilidad de la decisión (Opción A vs. Opción B) y de la primera vez que `∘` corrió en vivo.

**Módulo nuevo:** `src/algebra/combinador.py`
**Depende de:** [001-grupo-algebraico](../001-grupo-algebraico/spec.md) (`operacion_G`), [002-homomorfismo-analisis](../002-homomorfismo-analisis/spec.md) (`Homomorfismo.aplicar`), [006-clasificador-gestos](../006-clasificador-gestos/spec.md) (consume el `Gesto` confirmado por `EstabilizadorGesto`).
**Consumido por:** [009-integracion-pipeline](../009-integracion-pipeline/spec.md) (lo instancia y lo llama en el loop), [008-visualizacion](../008-visualizacion/spec.md) (opcionalmente, muestra el combo).
**Origen:** decisión de diseño discutida en `docs/axiomas_de_grupo_explicados.md` — hasta esta spec, `operacion_G` (la composición `∘` de `G`) solo se usaba como herramienta de verificación offline (tests, `homomorfismo.py::verificar_homomorfismo`), nunca durante el uso real con cámara. Esta spec le da a `∘` un segundo consumidor: uno que corre en vivo.
**NFRs heredados:** NFR-G03 (el nuevo módulo vive en `src/algebra/`, así que hereda la obligación de pureza — sin `cv2`/`mediapipe`/`subprocess` — y queda cubierto automáticamente por `tests/test_pureza_algebra.py`, que recorre todo `src/algebra/*.py`).

---

## 1. Propósito

Detectar cuándo dos gestos confirmados consecutivos ocurren dentro de una ventana de tiempo corta y, en ese caso, aplicar `φ(g₁ ∘ g₂)` en vez de `φ(g₂)` solo — usando la composición `∘` de `G` (`operacion_G`, ya existente en `src/algebra/grupo_gestos.py`) como mecanismo de ejecución, no solo de análisis.

Esta es la **Opción A** evaluada frente a la Opción B (dos manos simultáneas): se prefiere porque reutiliza infraestructura ya existente (`EstadoPipeline`, el propio `EstabilizadorGesto`, `operacion_G`) sin tocar la capa de detección (`DetectorManos` sigue con `max_num_hands=1`, DET-FR-001 no cambia) ni la capa de clasificación geométrica (`clasificar_gesto`/`dedos_levantados` no cambian).

**Punto de diseño central:** ni `grupo_gestos.py` ni `homomorfismo.py` necesitan cambiar. `operacion_G` y `Homomorfismo.aplicar` ya hacen exactamente lo que este módulo necesita — lo único nuevo es la orquestación temporal que decide *cuándo* combinar dos gestos antes de pasarlos a `φ`. Esto mantiene el cambio contenido a un módulo nuevo, pequeño y puro, más los puntos de integración en 009 (y, opcionalmente, 008).

## 2. Contrato de interfaz

**Entradas:** un `Gesto` recién confirmado (salida de `EstabilizadorGesto.actualizar()`, ver 006) y el instante `ahora: float` en que se confirmó.

**Salidas:**

```python
@dataclass
class ResultadoCombinacion:
    gesto_efectivo: Gesto           # el gesto (crudo o combinado) al que se le debe aplicar phi
    es_combo: bool                  # True si gesto_efectivo = operacion_G(pendiente, nuevo)
    gesto_previo: Gesto | None = None  # el g1 combinado, solo si es_combo=True (para 008)


class CombinadorGestos:
    def __init__(self, ventana_s: float = 1.5): ...

    def actualizar(self, gesto: Gesto, ahora: float) -> ResultadoCombinacion:
        """Recibe un gesto YA CONFIRMADO (no crudo por frame) y el timestamp de esa
        confirmacion. Decide si combina con el gesto pendiente segun CMB-FR-001..004."""

    def reset(self) -> None:
        """Limpia el gesto pendiente. Ver Seccion 5 (casos borde) sobre cuando NO hace
        falta llamarlo explicitamente desde 009."""
```

`ahora` se recibe como parámetro (no se lee `time.time()` internamente) — ver CMB-FR-006.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| CMB-FR-001 | `CombinadorGestos` DEBE recordar el último gesto confirmado (distinto de `E`, ver CMB-FR-003) junto con el `ahora` en que se recibió. Al recibir un nuevo gesto confirmado `g₂` dentro de `ventana_s` segundos del pendiente `g₁`, `actualizar()` DEBE devolver `gesto_efectivo = operacion_G(g₁, g₂)` con `es_combo=True` — usando `operacion_G` de `src/algebra/grupo_gestos.py` (001) sin reimplementar la composición. |
| CMB-FR-002 | Si no hay gesto pendiente vigente (ninguno registrado aún, o el registrado excede `ventana_s`), `actualizar()` DEBE devolver `gesto_efectivo = gesto` (el recién confirmado, sin combinar) con `es_combo=False` — preserva exactamente el comportamiento actual para gestos aislados, sin regresión de latencia (ver Sección 6, relación con SC-G03). |
| CMB-FR-003 | `Gesto.E` NUNCA participa en una combinación, ni como pendiente ni como segundo elemento: al confirmarse `E`, `actualizar()` DEBE devolver `(E, es_combo=False)` y DEBE limpiar el pendiente (equivalente a `reset()`). **Justificación algebraica:** `E` es el elemento identidad de `G` (axioma de identidad, `E∘g = g∘E = g` para todo `g`), así que dejarlo combinar no cambiaría el resultado de `φ` — pero sí dispararía `ejecutar_accion()` una segunda vez para la misma acción, un efecto secundario espurio sin contrapartida algebraica interesante. Además, `E` se confirma automáticamente al perder la mano (INT-FR-004 de 009), así que tratarlo como frontera natural de combo también es la lectura más intuitiva para el usuario: bajar la mano termina cualquier combo en curso. |
| CMB-FR-004 | Tras cada llamada a `actualizar()` con un gesto distinto de `E`, el gesto **crudo** recién confirmado (nunca el resultado combinado) DEBE quedar registrado como el nuevo pendiente. Esto acota el alcance a **pares**: una combinación nunca encadena tres o más gestos en una sola llamada a `operacion_G` (ver No objetivos). Ejemplo: `G1` confirmado (pendiente=`G1`), luego `G3` confirmado dentro de la ventana → combo `G1∘G3=G4`, pendiente pasa a ser `G3` (no `G4`); si después llega `G2` dentro de la ventana de `G3`, el combo es `G3∘G2`, no `G4∘G2`. |
| CMB-FR-005 | `ventana_s` DEBE ser configurable vía `config/default.yaml` (`combinador.ventana_s`), con valor por defecto `1.5` — no hardcodeada en el módulo. |
| CMB-FR-006 | `CombinadorGestos` NO DEBE leer el reloj del sistema internamente (`time.time()` ni equivalentes). El timestamp `ahora` DEBE recibirse como parámetro de `actualizar()`. Esto mantiene el módulo puro y determinista para tests (se le puede pasar cualquier float sin mockear el reloj) y consistente con el resto de `src/algebra/`, que no depende de I/O de sistema. |
| CMB-FR-007 | `actualizar()` DEBE devolver, además del gesto efectivo, si el resultado provino de una combinación (`es_combo`) y, si aplica, cuál fue el gesto pendiente combinado (`gesto_previo`) — para que 009/008 puedan mostrarlo sin duplicar el estado que ya vive en `CombinadorGestos`. |

## 4. Criterios de aceptación

- **Dado** `CombinadorGestos(ventana_s=1.5)`, **cuando** se llama `actualizar(Gesto.G1, ahora=0.0)` y luego `actualizar(Gesto.G3, ahora=0.8)`, **entonces** la segunda llamada devuelve `ResultadoCombinacion(gesto_efectivo=Gesto.G4, es_combo=True, gesto_previo=Gesto.G1)` — porque `operacion_G(G1,G3)=G4` (`1+3=4`) y `0.8 ≤ 1.5` (CMB-FR-001).
- **Dado** el mismo combinador, **cuando** se llama `actualizar(Gesto.G1, ahora=0.0)` y luego `actualizar(Gesto.G3, ahora=2.0)` (fuera de la ventana), **entonces** la segunda llamada devuelve `ResultadoCombinacion(gesto_efectivo=Gesto.G3, es_combo=False, gesto_previo=None)` (CMB-FR-002).
- **Dado** el mismo combinador recién creado (sin pendiente), **cuando** se llama `actualizar(Gesto.G2, ahora=5.0)`, **entonces** devuelve `(G2, es_combo=False)` — nada que combinar (CMB-FR-002).
- **Dado** `actualizar(Gesto.G1, ahora=0.0)` seguido de `actualizar(Gesto.E, ahora=0.3)`, **entonces** la segunda llamada devuelve `(E, es_combo=False)`, y una tercera llamada `actualizar(Gesto.G4, ahora=0.5)` devuelve `(G4, es_combo=False)` — `E` limpió el pendiente, `G1` no sobrevive para combinarse con `G4` (CMB-FR-003).
- **Dado** `actualizar(G1, 0.0)` → `actualizar(G3, 0.5)` (combo, pendiente pasa a `G3`) → `actualizar(G2, 0.9)` (dentro de ventana de `G3`), **entonces** la tercera llamada combina `G3∘G2` (`=G5`, `3+2=5`), **no** `G4∘G2` — confirma que el pendiente es siempre el gesto crudo anterior, no el resultado combinado (CMB-FR-004).
- **Dado** cualquier par de gestos válidos `(g₁,g₂)` con `g₁,g₂ ≠ E`, **cuando** se combinan dentro de la ventana, **entonces** `operacion_G(g₁,g₂)` siempre devuelve un elemento de `G` (clausura, heredada de 001 sin reimplementación) — por lo que `φ(g₁∘g₂)` siempre está definida y nunca requiere una acción nueva fuera de las 6 ya existentes en `A`.

## 5. Casos borde

- **¿Por qué no hace falta un `reset()` explícito al perder la mano (a diferencia de `FiltroEMA.reset()`/`EstabilizadorGesto.reset()` en 009)?** Porque la ventana de tiempo ya resuelve el caso: si el usuario deja de gesticular por más de `ventana_s`, cualquier intento de combo posterior falla el chequeo de tiempo (CMB-FR-002) sin necesitar limpieza explícita del estado. Y si la mano se pierde brevemente **dentro** de la ventana (ruido de detección, transición entre gestos) sin que `E` llegue a confirmarse vía debounce (006), el pendiente sigue vigente correctamente — es indistinguible de una transición física normal entre dos gestos. Solo una confirmación **real** de `E` (que pasó los `frames_estables` del debounce) limpia el pendiente, vía CMB-FR-003 — no cada frame sin mano.
- **Repetir el mismo gesto dos veces (`G1` luego `G1` otra vez dentro de la ventana):** produce `operacion_G(G1,G1)=G2` — una acción *distinta* a repetir `A1`. Esto puede sorprender a un usuario que solo quería "repetir" el mismo gesto. No es un defecto nuevo de este módulo: `EstabilizadorGesto` (CLA-FR-006/007) ya exige que el gesto cambie y vuelva para poder confirmarse una segunda vez, así que `G1,G1` como *combo* solo es alcanzable si el usuario efectivamente sostuvo `G1`, salió de él (a otro gesto o a `E`) y volvió a sostener `G1` — y si pasó por `E` en el medio, CMB-FR-003 ya limpió el pendiente y no hay combo. El único camino real hacia `G1∘G1` es transicionar `G1 → (otro gesto no-E, sin estabilizarse) → G1` de nuevo dentro de la ventana, lo cual es un caso de borde legítimo pero infrecuente — se documenta, no se bloquea.
- **Falsos combos (el trade-off que motivó esta spec):** dos gestos aislados que el usuario no quiso combinar, hechos por casualidad dentro de `ventana_s`, se leen como un combo real — no hay forma de distinguir "intención de combo" de "coincidencia temporal" con la información disponible (solo gesto + tiempo). Se acepta este trade-off para el MVP (ver Sección 6) y se mitiga solo calibrando `ventana_s` a un valor lo bastante corto para reducir falsos positivos sin hacer los combos intencionales imposibles de ejecutar a mano.
- **Ventana muy corta vs. muy larga:** `ventana_s` pequeño reduce falsos combos pero exige que el usuario encadene gestos muy rápido (poco realista dado que cada gesto ya necesita `frames_estables` frames de sostenimiento, ~333ms a 30 FPS con el valor por defecto de 006); `ventana_s` grande facilita el combo intencional pero aumenta falsos positivos. El valor `1.5` es un punto de partida, no una constante verificada — a calibrar con cámara real (ver `tasks.md`, T014 de verificación de campo).

## 6. Relación con criterios de éxito existentes

- **SC-G03 (latencia gesto-estable→acción ≤500ms en el 95% de los disparos):** no se degrada. `φ(g₁)` sigue disparándose de inmediato en cuanto `g₁` se confirma (CMB-FR-002 se cumple para el primer gesto de cualquier secuencia, combo o no) — este módulo **nunca retiene** una confirmación esperando a ver si llega un segundo gesto. Solo el *segundo* gesto de un combo cambia qué acción dispara (`φ(g₁∘g₂)` en vez de `φ(g₂)`), no *cuándo* dispara.
- **SC-G04 (100% de los pares cumplen la propiedad de homomorfismo):** no cambia — sigue siendo una propiedad de `φ` verificada exhaustivamente en 002, independiente de si `φ` se aplica a un gesto crudo o a uno combinado; de hecho, esta spec es la primera vez que esa garantía (`φ(g₁∘g₂)=φ(g₁)∘φ(g₂)`) deja de ser solo un hecho verificado en tests y se vuelve observable en el comportamiento real del sistema.
- **Nuevo — SC-G06 (propuesto en 000-overview):** ≥90% de los combos intencionales (dos gestos distintos de `E`, hechos deliberadamente dentro de `ventana_s`) disparan `φ(g₁∘g₂)`; ningún gesto aislado hecho con más de `ventana_s` de separación de cualquier gesto anterior dispara un combo espurio. Medido en la verificación de campo de `tasks.md`.

## 7. No objetivos de este módulo

- **No encadena 3 o más gestos en una sola combinación.** `operacion_G` es asociativa (heredado de 001), así que `g₁∘g₂∘g₃` estaría bien definido matemáticamente, pero decidir *cuándo* "cerrar" una cadena de 3+ gestos (¿al tercer gesto? ¿al expirar la ventana del segundo?) introduce ambigüedad de UX que esta spec no resuelve — el alcance del MVP son combinaciones de exactamente 2 gestos (CMB-FR-004). Extensión futura explícita, no implementada aquí.
- **No resuelve el problema de "combo intencional vs. accidental"** más allá de calibrar `ventana_s` — no hay gesto de "armar combo" explícito, confirmación sonora/visual previa al disparo, ni mecanismo de deshacer. Se documenta como limitación conocida (Sección 5).
- **No cambia `grupo_gestos.py`, `grupo_acciones.py` ni `homomorfismo.py`** (001, 002) — `operacion_G` y `Homomorfismo.aplicar` se consumen tal cual existen hoy.
- **No cambia `clasificar_gesto`, `dedos_levantados` ni `EstabilizadorGesto`** (006) — el combinador solo consume gestos ya confirmados, no toca cómo se confirman.
- **No implementa la Opción B (dos manos simultáneas)** — evaluada y descartada para esta spec por mayor superficie de cambio (tocaría 004 y 006); queda como alternativa futura si se prefiere composición instantánea en vez de secuencial.
