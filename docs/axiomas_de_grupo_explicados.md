# Los 4 axiomas de un grupo, explicados desde cero (con GestGroup)

Este documento responde una pregunta puntual: **¿cómo se cumplen los cuatro
axiomas de un grupo — clausura, asociatividad, identidad e inversos — en
GestGroup?** Está escrito para alguien que no ha visto teoría de grupos
antes (o la vio una vez y no le quedó clara). Si ya conoces el tema y quieres
el detalle técnico completo (permutaciones de `S₅`, homomorfismos, kernel,
etc.), ese contenido está en `docs/teoria_grupos_aplicada.md`.

---

## 0. ¿Qué es un "grupo", en palabras simples?

Olvida por un momento la palabra "grupo" en el sentido de "grupo de amigos".
En matemáticas, un **grupo** es solo esto:

> Un conjunto de elementos + una manera de **combinar dos de ellos** para
> obtener un tercero, tal que se cumplen 4 reglas fijas.

Es exactamente como el reloj. Si son las 10:00 y avanzas 5 horas, no llegas a
"15:00" en un reloj de 12 horas — llegas a las 3:00. El reloj "combina" 10 y 5
y el resultado **se queda dentro del reloj** (entre 0 y 11). Esa idea —
combinar dos cosas y quedarte siempre dentro del mismo conjunto, de forma
predecible — es la esencia de un grupo. Las 4 reglas (axiomas) son las que
garantizan que ese comportamiento sea consistente y no un accidente.

## 1. El "reloj" concreto de GestGroup

En el proyecto, el conjunto no son horas, son **gestos de la mano**. Hay 6:

| Símbolo | Gesto (en la cámara) |
|---|---|
| `E`  | reposo (mano quieta) |
| `G1` | 1 dedo |
| `G2` | 2 dedos |
| `G3` | puño |
| `G4` | mano abierta |
| `G5` | pulgar |

A cada gesto le asignamos un número, como las horas de un reloj — pero en vez
de 12 posiciones, este "reloj" tiene solo **6**: `E=0, G1=1, G2=2, G3=3, G4=4,
G5=5`.

"Combinar" dos gestos (el proyecto usa el símbolo `∘`) funciona igual que el
reloj: **se suman sus números y, si te pasas de 5, vuelves a empezar desde
0**. En matemáticas esto se llama "suma módulo 6", y se escribe `(i+j) mod 6`.

```
G4 ∘ G5  →  4 + 5 = 9  →  9 no cabe en {0..5}, así que restamos 6: 9 - 6 = 3
         →  resultado = G3
```

Este "reloj de 6 gestos" es, matemáticamente, un grupo llamado `ℤ/6ℤ`. Por
dentro, el código (`src/algebra/grupo_gestos.py`) lo construye de una forma
más elegante — como potencias de una permutación `σ = (1 2 3)(4 5)` de
`S₅` — pero el resultado de combinar dos gestos es *exactamente* el mismo que
sumar sus números en el reloj de 6. Para esta explicación, quédate con la
imagen del reloj: es 100% fiel al resultado real.

Con esa imagen en la cabeza, veamos los 4 axiomas uno por uno.

---

## 2. Axioma 1 — Clausura (Closure)

**En palabras simples:** si combinas dos elementos cualquiera del grupo, el
resultado **nunca se sale del grupo**. No aparece un gesto "7" ni un gesto
fantasma que no esté en la lista de 6.

**Analogía del reloj:** por más que sumes horas, nunca terminas en "13:00" —
el reloj te "envuelve" de vuelta a un número válido (0 a 11, o en nuestro
caso, 0 a 5).

**Ejemplo concreto en GestGroup:**

```
G4 ∘ G5  =  (4 + 5) mod 6  =  9 mod 6  =  3   →   G3
```

`G4` (mano abierta) combinado con `G5` (pulgar) da `G3` (puño). El resultado,
`G3`, **es uno de los 6 gestos originales** — no salió nada nuevo ni raro.
Esto se cumple para **cualquier** par de los 6 gestos, no solo para este par
(en el código, `tests/test_grupo_gestos.py` lo revisa para las 36
combinaciones posibles, y `src/algebra/verificacion.py` tiene una función
genérica, `verificar_axiomas_grupo`, que hace exactamente este chequeo).

**¿Por qué importa para el proyecto?** Significa que no importa qué gesto
haga la persona, el sistema siempre sabe traducirlo a algo dentro del
universo conocido de 6 gestos — nunca se "cae" a un estado indefinido.

---

## 3. Axioma 2 — Asociatividad

**En palabras simples:** cuando combinas **tres o más** elementos seguidos,
no importa en qué orden agrupes las operaciones (con cuál empieces a
resolver primero) — el resultado final es el mismo.

**Analogía cotidiana:** es lo mismo que sumar números normales.
`(2 + 3) + 4` da el mismo resultado que `2 + (3 + 4)` — ambos dan `9`. Nadie
duda de esto con números; el axioma de asociatividad dice que la misma
garantía aplica a "combinar gestos", aunque combinar gestos no sea sumar
números de la vida diaria.

**Ejemplo concreto en GestGroup**, con los gestos `G1`, `G2`, `G3`:

```
Camino A — primero (G1 ∘ G2), después con G3:
  G1 ∘ G2 = (1+2) mod 6 = 3        → G3
  G3 ∘ G3 = (3+3) mod 6 = 6 mod 6 = 0  → E

Camino B — primero G1, después con (G2 ∘ G3):
  G2 ∘ G3 = (2+3) mod 6 = 5        → G5
  G1 ∘ G5 = (1+5) mod 6 = 6 mod 6 = 0  → E
```

Los dos caminos —agrupar primero los dos de la izquierda, o agrupar primero
los dos de la derecha— **llegan al mismo resultado: `E`**. Esto no es
casualidad de este trío en particular: el código lo comprueba para **las 216
combinaciones posibles** de tres gestos (`tests/test_grupo_gestos.py::test_asociatividad`).

**¿Por qué importa para el proyecto?** Cuando se combinan varios gestos en
cadena —en el análisis, en los tests, o **en vivo** con la funcionalidad de
combos (Sección 8)— el resultado no depende de detalles de implementación como
"en qué orden el código decide agrupar las operaciones internamente" — siempre
da lo mismo.

---

## 4. Axioma 3 — Identidad (elemento neutro)

**En palabras simples:** dentro del grupo existe un elemento especial que,
al combinarlo con cualquier otro, **no cambia nada**. Lo deja igual.

**Analogía cotidiana:** es como el número `0` en la suma (`5 + 0 = 5`) o el
`1` en la multiplicación (`5 × 1 = 5`). No "hace nada" cuando se combina con
otra cosa.

**En GestGroup, el elemento identidad es `E` (reposo)** — el número `0` en
nuestro reloj de 6.

**Ejemplo concreto:**

```
E ∘ G4  =  (0 + 4) mod 6  =  4   →  G4   (sin cambios)
G4 ∘ E  =  (4 + 0) mod 6  =  4   →  G4   (sin cambios, en cualquier orden)
```

Combinar `mano abierta` con `reposo` (en cualquier orden) sigue dando
`mano abierta`. Esto es válido para **los 6 gestos**, no solo para `G4`: es
justamente lo que hace que `E` (reposo) tenga sentido intuitivo como
identidad — "no hacer ningún gesto" no debería alterar nada.

**¿Por qué importa para el proyecto?** Le da sentido matemático a la idea
intuitiva de que "la mano quieta = no pasa nada". `E` es también el gesto
cuyo homomorfismo `φ(E)` produce la "acción nula" (`A_E`, ninguna acción) —
la identidad de gestos se traduce naturalmente en la identidad de acciones.

---

## 5. Axioma 4 — Inversos

**En palabras simples:** todo elemento del grupo tiene un "elemento
contrario" con el que, al combinarlo, se cancelan mutuamente y el resultado
es la identidad (el axioma 3, `E`). Es como un botón de "deshacer": cada
gesto tiene exactamente un gesto que lo "revierte" de vuelta al reposo.

**Analogía cotidiana:** en la suma normal, el inverso de `5` es `-5`, porque
`5 + (-5) = 0`. Aquí no hay números negativos (solo tenemos `0` a `5`), pero
la misma idea aplica dentro del reloj de 6: el inverso de un número es el que
le falta para completar `6` (o `0`, si ya es `0`).

**Ejemplo concreto — el inverso de `G2`:**

Buscamos qué gesto `x` cumple `G2 ∘ x = E`, o sea `2 + x ≡ 0 (mod 6)`. La
respuesta es `x = 4`, es decir `G4`:

```
G2 ∘ G4  =  (2 + 4) mod 6  =  6 mod 6  =  0   →   E   ✓
G4 ∘ G2  =  (4 + 2) mod 6  =  6 mod 6  =  0   →   E   ✓  (funciona en ambos órdenes)
```

`2 dedos` seguido de `mano abierta` se cancela y "vuelve" al reposo. La tabla
completa de inversos:

| Gesto | Su inverso | Por qué |
|---|---|---|
| `E`  (reposo)       | `E`  | `0 + 0 = 0` |
| `G1` (1 dedo)        | `G5` | `1 + 5 = 6 ≡ 0` |
| `G2` (2 dedos)        | `G4` | `2 + 4 = 6 ≡ 0` |
| `G3` (puño)          | `G3` | `3 + 3 = 6 ≡ 0` — el único que es su propio inverso |
| `G4` (mano abierta)  | `G2` | `4 + 2 = 6 ≡ 0` |
| `G5` (pulgar)        | `G1` | `5 + 1 = 6 ≡ 0` |

Un detalle curioso: **solo `E` y `G3` son "su propio inverso"** — todos los
demás necesitan otro gesto distinto para cancelarse. (Un error de una versión
temprana del proyecto asumía que *todos* los gestos eran su propio inverso;
esto resultó ser matemáticamente imposible para un grupo de 6 elementos —
está documentado en `docs/demostraciones.md`, Decisión D1, si te interesa el
porqué.)

**¿Por qué importa para el proyecto?** Garantiza que toda combinación de
gestos es "reversible" dentro del sistema algebraico — nunca hay un gesto que
te deje "atrapado" sin forma de volver al estado neutro combinándolo con otro
gesto del mismo conjunto.

---

## 6. Los 4 axiomas juntos, en una tabla

| Axioma | Pregunta que responde | Ejemplo usado arriba | ¿Se cumple? |
|---|---|---|---|
| Clausura | ¿El resultado de combinar dos gestos sigue siendo un gesto válido? | `G4 ∘ G5 = G3` | ✓ |
| Asociatividad | ¿Da igual el orden en que agrupo tres combinaciones? | `(G1∘G2)∘G3 = G1∘(G2∘G3) = E` | ✓ |
| Identidad | ¿Existe un elemento que no cambia nada al combinarse? | `E ∘ G4 = G4` | ✓ (`E`) |
| Inversos | ¿Todo elemento tiene uno que lo cancela? | `G2 ∘ G4 = E` | ✓ |

Cuando los 4 se cumplen **a la vez**, para **todos** los elementos (no solo
para los ejemplos de arriba), el conjunto con su operación es, formalmente,
un **grupo**. Eso es justo lo que el código verifica de forma exhaustiva:

- `src/algebra/verificacion.py` tiene la función `verificar_axiomas_grupo`,
  que recorre **todas** las combinaciones posibles (no solo unos ejemplos) y
  revisa los 4 axiomas.
- `tests/test_verificacion.py` y `tests/test_grupo_gestos.py` ejecutan esa
  verificación como pruebas automáticas — cada vez que el proyecto corre sus
  tests, se vuelve a confirmar que `G` (gestos) y `A` (acciones) cumplen los
  4 axiomas.

## 7. ¿Por qué te deberías importar esto, en la práctica?

Fuera de la "belleza matemática", que `G` sea un grupo genuino le da al
proyecto tres garantías concretas:

1. **Nunca hay comportamiento indefinido.** Gracias a la clausura, combinar
   gestos siempre da otro gesto conocido del sistema — nunca un caso "no
   contemplado".
2. **El orden de agrupación no genera resultados distintos.** Gracias a la
   asociatividad, cualquier análisis que combine varios gestos en cadena es
   predecible y no depende de detalles internos de cómo el código decide
   agrupar las operaciones.
3. **Todo es reversible.** Gracias a los inversos (y a que `E` es identidad),
   el sistema siempre puede "volver al punto de partida" combinando el gesto
   correcto — una propiedad útil para razonar sobre el comportamiento del
   pipeline sin tener que probarlo empíricamente en cada caso.

## 8. Los combos: cuando `∘` se usa "de verdad", en vivo

Durante mucho tiempo, en este proyecto la operación `∘` (combinar dos gestos)
solo vivía en los **tests** y en el análisis matemático — nunca se usaba
mientras usabas la cámara. La funcionalidad de **combos** cambió eso: ahora
`∘` corre en vivo, y de hecho **la interacción con la cámara es por combos**.
La idea:

> Haces **dos gestos, uno tras otro**, y el sistema ejecuta la acción de la
> **combinación** `φ(g₁ ∘ g₂)`, usando exactamente la misma suma-en-el-reloj-de-6
> que explicamos arriba.

**Ejemplo concreto:** haces `G1` (1 dedo) y luego `G3` (puño). El sistema calcula:

```
G1 ∘ G3  =  (1 + 3) mod 6  =  4   →   G4   →   acción "siguiente pista"
```

¡Disparaste la acción de `G4` (mano abierta) **sin haber hecho el gesto de
mano abierta**! Solo encadenaste dos gestos más simples, y la estructura de
grupo hizo el resto.

### ¿Cómo se leen los gestos sin equivocarse? Votación por mayoría

El reto: al pasar de un gesto al siguiente, la mano atraviesa poses ambiguas
que la cámara podría leer mal. La solución (spec
[015](../specs/015-captura-guiada-combos/spec.md)) es **capturar cada gesto
durante una ventana de varios frames y quedarse con el gesto que más veces
apareció** (votación de mayoría). Así, los pocos frames "raros" de la
transición quedan en minoría y no cambian la lectura.

El flujo, guiado en pantalla (la ventana de la cámara te asiste):

1. **Gesto 1 — capturando:** sostienes el primer gesto; una barra cuenta los
   frames y muestra el gesto que va ganando.
2. **Prepárate:** una pequeña pausa para que cambies al segundo gesto sin que
   la transición ensucie la lectura.
3. **Gesto 2 — capturando:** sostienes el segundo gesto; misma votación.
4. **Resultado:** se muestra `g₁ o g₂ = resultado` y se ejecuta la acción.

Los 4 axiomas son justo lo que garantiza que esto funcione siempre:

- **Clausura:** `G1 ∘ G3` siempre da un gesto válido (nunca un "gesto 7"), así
  que la acción combinada siempre existe.
- **Identidad:** el gesto de reposo `E` **nunca** cuenta como un gesto del
  combo — si la mayoría de una ventana es "mano en reposo", el combo se
  cancela. Tiene sentido porque `E` es el elemento neutro del grupo.

Los tamaños de las ventanas (captura, espera, resultado) se ajustan en
`config/default.yaml` (`combinador.frames_captura`, `frames_espera`,
`frames_resultado`). El código vive en
`src/clasificador/capturador_combo.py` (`CapturadorCombo`), y es la primera vez
que la operación `∘` del grupo se ejecuta como parte del pipeline real y no
solo en los tests.

## 9. Para profundizar

Este documento se quedó deliberadamente en los 4 axiomas básicos y en la
imagen del "reloj de 6". Si quieres ver:

- **Cómo se construye `G` de verdad**, con permutaciones reales de `S₅`
  (no solo la analogía del reloj) → `docs/teoria_grupos_aplicada.md`,
  secciones 1–2.
- **El homomorfismo `φ: G → A`**, que traduce gestos en acciones del sistema
  (subir volumen, pausar, etc.), y conceptos más avanzados como kernel,
  subgrupo normal y el Primer Teorema de Isomorfismo →
  `docs/teoria_grupos_aplicada.md`, secciones 3–7.
- **Las demostraciones formales "oficiales"**, con la evidencia de tests que
  las respaldan → `docs/demostraciones.md`.
