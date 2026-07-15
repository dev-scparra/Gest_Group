# Spec 015 — Captura Guiada de Combos por Votación de Mayoría

**Módulo nuevo:** `src/clasificador/capturador_combo.py`
**Depende de:** [001-grupo-algebraico](../001-grupo-algebraico/spec.md) (`operacion_G`), [002](../002-homomorfismo-analisis/spec.md) (`Homomorfismo.aplicar`), [006](../006-clasificador-gestos/spec.md) (consume el `Gesto` clasificado por frame).
**Consumido por:** [009-integracion-pipeline](../009-integracion-pipeline/spec.md) (lo instancia y lo llama en el loop), [008-visualizacion](../008-visualizacion/spec.md) (dibuja el HUD a partir de `EstadoCombo`).
**Supersede:** [014-combos-secuenciales](../014-combos-secuenciales/spec.md) como **modelo de interacción**. La 014 disparaba `φ(g₁∘g₂)` cuando dos gestos *confirmados* caían dentro de una ventana de tiempo (`ventana_s`), manteniendo además el disparo inmediato de gestos aislados. La 015 reemplaza ese disparo por una **captura guiada de un par de gestos** con votación de mayoría sobre ventanas de frames. `operacion_G` (la composición `∘` de `G`) sigue corriendo en vivo — ahora es el único camino de disparo.
**NFRs heredados:** el módulo es frame-driven y puro (no lee reloj ni cámara: recibe un `Gesto` por frame), lo que lo hace determinista y testeable sin hardware (NFR-G03 en espíritu; vive en `src/clasificador/`, no en `src/algebra/`, porque su responsabilidad es el *timing/estado de captura*, no el álgebra — solo consume `operacion_G`).

---

## 1. Propósito y motivación

La spec 014 disparaba un combo cuando el segundo gesto *confirmado* llegaba dentro de una ventana de tiempo. El problema que este spec resuelve: **los frames de transición entre un gesto y el siguiente ensucian la lectura**. Al pasar de "puño" a "1 dedo", el clasificador atraviesa poses ambiguas; con el modelo de 014, cuál gesto "gana" depende de exactamente cuándo el debounce confirma, lo que hace la lectura frágil justo en el momento del cambio.

La solución pedida: **capturar cada gesto del combo durante una ventana fija de frames y resolverlo por votación de mayoría sobre esa ventana.** Los frames de transición quedan en minoría y no cambian el resultado. Además, una fase de **espera** ("prepárate") entre el gesto 1 y el 2 aísla la transición para que no contamine la votación del segundo. Y la ventana de la cámara **asiste al usuario** con la fase actual, el gesto que va ganando, la cuenta regresiva y el resultado de la composición.

## 2. Modelo de interacción (cadencia guiada por tiempo)

Un combo se arma con **dos** gestos, capturados en secuencia:

```
INACTIVO ──(gesto ≠ E y armado)──▶ CAPTURANDO_G1 ──(frames_captura)──▶ ESPERA
                                                                          │
                          RESULTADO ◀──(frames_captura)── CAPTURANDO_G2 ◀─┘(frames_espera)
     │
     └──(frames_resultado)──▶ INACTIVO (desarmado: exige ver E para re-armar)
```

- **CAPTURANDO_G1 / CAPTURANDO_G2:** durante `frames_captura` frames se cuenta un voto por frame; al cerrar la ventana, el gesto del slot = **mayoría** (`Counter.most_common`). Si la mayoría es `E`, el combo se **cancela** (el usuario no sostuvo un gesto).
- **ESPERA:** `frames_espera` frames en los que la entrada se ignora, para que el usuario cambie de gesto sin que la transición contamine la votación del gesto 2.
- **RESULTADO:** al cerrar el gesto 2 se calcula `g₁ ∘ g₂` (`operacion_G`, 001) y se emite `disparar = g₁∘g₂` en **un solo frame** (borde). Se muestra el resultado `frames_resultado` frames.
- **Re-armado:** tras un combo (o una cancelación), hay que ver `E` (reposo) antes de iniciar otro — evita encadenar combos sin querer. El capturador nace **armado**, así que el primer gesto de la sesión arranca sin necesitar un `E` previo.

## 3. Contrato de interfaz

```python
class FaseCombo(Enum):
    INACTIVO, CAPTURANDO_G1, ESPERA, CAPTURANDO_G2, RESULTADO

@dataclass
class EstadoCombo:
    fase: FaseCombo
    frames_restantes: int          # cuenta regresiva de la fase actual (para el HUD)
    frames_total_fase: int         # para la fracción de la barra de progreso
    lider: Gesto | None            # gesto que va ganando la votación en curso
    conteo: list                   # most_common(3): [(Gesto, votos), ...]
    g1: Gesto | None
    g2: Gesto | None
    compuesto: Gesto | None        # g1 ∘ g2, presente desde RESULTADO
    disparar: Gesto | None         # != None SOLO en el frame borde en que se cierra g2

class CapturadorCombo:
    def __init__(self, frames_captura=20, frames_espera=12, frames_resultado=25): ...
    def actualizar(self, gesto: Gesto) -> EstadoCombo: ...   # un gesto por frame
    def reset(self) -> None: ...
```

`actualizar` recibe **un gesto clasificado por frame** (no confirmado por debounce: la votación de mayoría *es* el mecanismo de estabilización aquí, sustituyendo al `EstabilizadorGesto` en el flujo de combos).

## 4. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| CAP-CMB-FR-001 | Cada gesto del combo DEBE resolverse por **votación de mayoría** sobre una ventana de `frames_captura` frames (`Counter.most_common`). Los frames de transición/ruido, al ser minoría, NO deben cambiar el resultado. |
| CAP-CMB-FR-002 | Si la mayoría de una ventana de captura es `E`, el combo DEBE **cancelarse** (volver a INACTIVO sin disparar). `E` es reposo: significa que el usuario no sostuvo un gesto. |
| CAP-CMB-FR-003 | Entre el gesto 1 y el 2 DEBE haber una fase de ESPERA de `frames_espera` frames en la que la entrada se ignora, para que la transición de un gesto al otro no contamine la votación del gesto 2. |
| CAP-CMB-FR-004 | Al cerrar el gesto 2, DEBE calcularse `g₁ ∘ g₂` con `operacion_G` (001) y emitirse `disparar = g₁∘g₂` en **exactamente un frame** (borde), para que 009 aplique `φ` y ejecute una sola vez por combo. |
| CAP-CMB-FR-005 | Tras un combo o una cancelación, el capturador DEBE **desarmarse**: exige observar `E` antes de iniciar otro combo. Nace armado (el primer gesto de la sesión arranca sin `E` previo). |
| CAP-CMB-FR-006 | `EstadoCombo` DEBE exponer, en cada frame, la fase, la cuenta regresiva (`frames_restantes`/`frames_total_fase`), el líder de la votación en curso y su conteo, y los gestos capturados/compuesto — todo lo que 008 necesita para el HUD (VIS-FR-009) sin duplicar el estado del capturador. |
| CAP-CMB-FR-007 | `frames_captura`, `frames_espera` y `frames_resultado` DEBEN ser configurables vía `config/default.yaml` (`combinador.*`), no hardcodeados. |
| CAP-CMB-FR-008 | El módulo DEBE ser frame-driven y puro: recibe un `Gesto` por llamada, sin leer `time.time()` ni `cv2`/`mediapipe`. Esto lo hace determinista para tests (se le alimenta una secuencia de gestos literales). |

## 5. Criterios de aceptación

- **Dado** `CapturadorCombo(frames_captura=5, frames_espera=3, frames_resultado=4)`, **cuando** se alimentan 5 frames de `G3`, luego 3 (espera), luego 5 de `G1`, **entonces** el último estado tiene `compuesto = operacion_G(G3,G1) = G4` y `disparar = G4` en un solo frame (CAP-CMB-FR-001/004). ✅ `tests/test_capturador_combo.py`.
- **Dado** una ventana de captura con `[G3,G3,G3,E,G1]`, **cuando** se cierra, **entonces** `g1 = G3` (mayoría 3 de 5) — la transición no cambia el resultado (CAP-CMB-FR-001). ✅
- **Dado** una ventana cuya mayoría es `E` (`[G3,E,E,E,E]`), **cuando** se cierra, **entonces** el combo se cancela (fase INACTIVO, sin disparar) (CAP-CMB-FR-002). ✅
- **Dado** un combo ya disparado, **cuando** el usuario sigue con la mano en un gesto (no-E), **entonces** NO arranca un combo nuevo hasta ver `E` (CAP-CMB-FR-005). ✅
- **Dado** el pipeline con dobles de prueba, **cuando** se captura `G1` y luego `G3`, **entonces** `procesar_frame` aplica `φ(G4)` y ejecuta `A4` una sola vez (INT-FR-010). ✅ `tests/test_orquestacion.py`.
- **Dado** el pipeline con cámara real, **cuando** el usuario hace un gesto, espera el "prepárate", hace el segundo y ve el resultado, **entonces** se dispara `φ(g₁∘g₂)` y el HUD acompaña cada fase. ⬜ **Pendiente:** verificación de campo (T015, requiere cámara).

## 6. Relación con criterios de éxito

- **SC-G03 (latencia):** el modelo de 015 introduce latencia deliberada (dos ventanas de captura + espera ≈ `2·frames_captura + frames_espera` frames, ~1.7s a 30 FPS con los valores por defecto). **Esto es intencional** — es el precio de la robustez por votación que el usuario pidió, y aplica a la interacción de combos, no a un disparo simple. SC-G03 se reinterpreta para combos como "latencia predecible y asistida en pantalla", no ≤500ms.
- **SC-G04 (homomorfismo):** sin cambios — `φ(g₁∘g₂)=φ(g₁)∘φ(g₂)` sigue verificado en 002. La 015 hace esa propiedad observable en vivo.
- **SC-G06 (de 014, revisado):** ≥90% de los combos intencionales (dos gestos sostenidos las ventanas completas) disparan `φ(g₁∘g₂)`; la votación de mayoría absorbe los frames de transición. Medido en la verificación de campo.

## 7. Asistencia visual (delega en 008, VIS-FR-009)

El HUD que 008 dibuja a partir de `EstadoCombo` DEBE mostrar, por fase: título de fase, gesto líder + votos durante la captura, barra de progreso con la cuenta regresiva (en frames y segundos aproximados vía FPS), los gestos ya capturados, y el resultado `g₁ o g₂ = compuesto`. El detalle de layout vive en 008; esta spec solo fija *qué* datos se exponen (CAP-CMB-FR-006).

## 8. No objetivos

- **No encadena 3+ gestos.** El alcance es pares, igual que 014 (la asociatividad de `∘` lo permitiría, pero la UX de cerrar cadenas queda fuera).
- **No conserva el disparo inmediato de gestos aislados de 014.** En 015 la interacción es *siempre* un par → `φ(g₁∘g₂)`. Es una decisión de producto: hace la composición del grupo el centro de la interacción (coherente con la tesis del proyecto). Si se quisiera un modo "gesto simple", sería un toggle de config futuro, no parte de este spec.
- **No implementa la Opción B (dos manos simultáneas).** Sigue como extensión futura (ver 014 Sección 7).
- **No reemplaza el `EstabilizadorGesto` como módulo** (006 sigue existiendo y probado); solo deja de usarse en el flujo de combos, donde la votación de mayoría cumple su rol.
