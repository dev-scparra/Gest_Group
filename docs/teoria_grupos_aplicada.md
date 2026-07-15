# Teoría de grupos en GestGroup — guía detallada con ejemplos

Este documento explica, paso a paso y con números concretos, cómo se aplica la
teoría de grupos en el proyecto. Complementa (no reemplaza) a:

- `GestGroup_Contexto_Desarrollo.md` — visión general y motivación.
- `docs/demostraciones.md` — las demostraciones formales "oficiales" que van al
  reporte, con la evidencia de tests.

Aquí el objetivo es distinto: **desarrollar cada cálculo a mano**, con
suficientes ejemplos para que cualquier concepto (grupo, homomorfismo, kernel,
subgrupo normal, cociente, isomorfismo) se pueda explicar con un número real
en la mano, no solo con la definición abstracta.

---

## 0. El mapa mental: qué es cada cosa aquí

| Concepto abstracto | Quién lo encarna en GestGroup |
|---|---|
| Un grupo `(G, ∘)` | Los 6 gestos reconocibles `{E, G1, G2, G3, G4, G5}` |
| Otro grupo `(A, ∘)` | Las 6 acciones ejecutables `{A_E, A1, A2, A3, A4, A5}` |
| Un homomorfismo `φ : G → A` | La tabla que decide qué acción dispara cada gesto |
| `ker(φ)` | Los gestos que **no producen ningún efecto** |
| `G/ker(φ)` | Los "grupos de gestos que el sistema trata igual" |
| Primer Teorema de Isomorfismo | La garantía de que `G/ker(φ)` y `Im(φ)` son la misma estructura, solo con nombres distintos |

Dos aclaraciones importantes antes de entrar en detalle:

1. **La operación `∘` de `G` nació como un objeto matemático de análisis, y
   ese sigue siendo su uso principal.** Por defecto, cuando el pipeline corre
   (`src/main.py`), cada frame se clasifica a **un solo** gesto `g ∈ G` y se le
   aplica directamente `φ(g)`. La función `operacion_G` (la tabla de Cayley) se
   usa dentro de `src/algebra/` para *verificar* que `φ` es homomorfismo y para
   los tests.

   **Actualización (spec [015](../specs/015-captura-guiada-combos/spec.md), que
   supersede a la 014):** desde la funcionalidad de *combos*, `operacion_G` tiene
   además un consumidor que **sí** corre en vivo — y de hecho la interacción con
   la cámara pasó a ser por combos. El usuario captura dos gestos guiado en
   pantalla (cada uno resuelto por votación de mayoría sobre una ventana de
   frames, con una fase de "prepárate" entre ambos), y el sistema aplica
   `φ(g₁ ∘ g₂)` — combinando dos gestos consecutivos que hizo frente a la cámara,
   exactamente lo que la frase original de este punto decía que *no* pasaba. La
   composición `∘` dejó de ser exclusivamente offline:
   `src/clasificador/capturador_combo.py` (`CapturadorCombo`) la ejecuta como
   parte del pipeline. Ver `docs/axiomas_de_grupo_explicados.md` (Sección 8) para
   la explicación accesible.
2. **El módulo de álgebra (`src/algebra/`) y el clasificador geométrico
   (`src/clasificador/gestos.py`) son dos cosas independientes que comparten
   solo el nombre `Gesto`.** El clasificador decide "qué dedos están arriba"
   con landmarks reales. El módulo de álgebra decide "¿es esta tabla de 6
   símbolos legítimamente un grupo, subgrupo de `S₅`?" sin tocar una sola
   coordenada de cámara. Que ambos usen la misma enum `Gesto` es lo que
   conecta teoría con práctica — pero la permutación `σ` de la que hablamos
   abajo **no describe el movimiento físico del dedo**, es la construcción
   que le da a `G` legitimidad algebraica como subgrupo de `S₅`.

---

## 1. El grupo `G` de gestos

### 1.1 Por qué no basta un vector de booleanos

Una primera idea (la del documento de contexto original) fue representar cada
gesto como un vector `(pulgar, índice, medio, anular, meñique) ∈ {0,1}⁵`
("qué dedos están arriba"). El problema: **un vector de bits no es una
permutación**. `S₅` son las biyecciones de `{1,...,5}` en sí mismo; un vector
booleano no define ninguna biyección. Así que decir "G ≤ S₅" con esa
representación no se sostenía.

Peor aún: esa primera idea también asumía que **cada gesto es su propio
inverso** (`gᵢ ∘ gᵢ = E`). Esto es imposible para un grupo de 6 elementos:

> Si todo elemento `x` de un grupo cumple `x² = e`, entonces el grupo es un
> espacio vectorial sobre `ℤ/2ℤ`, y su orden es una potencia de 2. Pero
> `6 = 2·3` no es potencia de 2. **Contradicción.**
>
> Dicho de otro modo (teorema de Cauchy): todo grupo de orden 6 tiene un
> elemento de orden 3 (porque 3 divide a 6). Un elemento de orden 3 nunca
> puede ser su propio inverso (si `x³ = e` y `x ≠ e`, entonces `x² ≠ e`).

Por eso el código actual (`src/algebra/grupo_gestos.py`) usa una
representación distinta, genuina.

### 1.2 La construcción real: `G` como subgrupo cíclico de `S₅`

Se define una permutación concreta de 5 elementos:

```
σ = (1 2 3)(4 5)  ∈ S₅
```

Leída como función: `1→2, 2→3, 3→1, 4→5, 5→4`. Es producto de un ciclo de
longitud 3 y uno de longitud 2, disjuntos, así que su orden es
`orden(σ) = mcm(3, 2) = 6`.

Los seis gestos son, literalmente, las seis potencias de `σ`:

```
E  = σ⁰ = identidad
G1 = σ¹
G2 = σ²
G3 = σ³
G4 = σ⁴
G5 = σ⁵
```

**Ejemplo — calculando `σ¹` a `σ⁵` explícitamente** (en notación 0-indexada,
`perm[i]` = imagen de `i`; el código las deriva en
`scripts/derivar_cayley.py`):

```
σ⁰ = (0,1,2,3,4)   -> E   (identidad)
σ¹ = (1,2,0,4,3)   -> G1  (el ciclo (0 1 2) más el ciclo (3 4))
σ² = (2,0,1,3,4)   -> G2  (el ciclo (0 2 1); 4 y 5 ya vuelven a su lugar)
σ³ = (0,1,2,4,3)   -> G3  (0,1,2 vuelven a su lugar; queda solo (3 4))
σ⁴ = (1,2,0,3,4)   -> G4  (el ciclo (0 1 2) otra vez; 4,5 en su lugar)
σ⁵ = (2,0,1,4,3)   -> G5  (el ciclo (0 2 1) más el ciclo (3 4))
```

Nótese algo bonito: `G3 = σ³` es **exactamente la transposición `(4 5)`**,
sin tocar 1,2,3. Es el único elemento no-identidad que es su propio inverso
(los otros vienen del ciclo de longitud 3, que tiene orden 3, no 2).

### 1.3 Verificando los axiomas con números reales

**Clausura — ejemplo.** Tomemos `G4 ∘ G5`. Como exponentes, "debería" dar
`σ⁴⁺⁵ = σ⁹`, pero `9` no es un exponente válido en `{0,...,5}`. La clausura
dice que igual cae dentro de `G`, porque `σ⁶ = σ⁰ = E` (el orden es 6), así
que `σ⁹ = σ⁶⁺³ = σ³ = G3`. Verificándolo por composición real de
permutaciones (`componer(f,g)(x) = f(g(x))`, de derecha a izquierda):

```
σ⁴ = (1,2,0,3,4)      σ⁵ = (2,0,1,4,3)

(σ⁴ ∘ σ⁵)(x) = σ⁴[σ⁵[x]]:
  x=0: σ⁵[0]=2 → σ⁴[2]=0
  x=1: σ⁵[1]=0 → σ⁴[0]=1
  x=2: σ⁵[2]=1 → σ⁴[1]=2
  x=3: σ⁵[3]=4 → σ⁴[4]=4
  x=4: σ⁵[4]=3 → σ⁴[3]=3

resultado = (0,1,2,4,3) = σ³ = G3   ✓ (coincide con "9 mod 6 = 3")
```

Es decir: `G4 ∘ G5 = G3`, y el resultado sigue estando en `G`. Esto es
exactamente la aritmética modular `ℤ/6ℤ`: identificando `Gᵢ ↔ i`, la
operación de `G` es `Gᵢ ∘ Gⱼ = G₍ᵢ₊ⱼ mod 6₎`.

**Asociatividad — ejemplo con una terna concreta `(G1, G2, G3)`.**
Primero con la aritmética de índices (rápido): `(1+2)+3 = 1+(2+3) = 6 ≡ 0`,
ambos lados dan `E`. Ahora la misma cuenta **con permutaciones reales**, para
confirmar que no es un truco de la notación sino una propiedad heredada de la
composición de funciones:

```
σ¹∘σ² = G3   (ya se muestra en la sección 2, ejemplo del homomorfismo)
(σ¹∘σ²)∘σ³ = σ³∘σ³ = componer(σ³,σ³):
  σ³ = (0,1,2,4,3)
  x=0: σ³[0]=0 → σ³[0]=0
  x=1: σ³[1]=1 → σ³[1]=1
  x=2: σ³[2]=2 → σ³[2]=2
  x=3: σ³[3]=4 → σ³[4]=3
  x=4: σ³[4]=3 → σ³[3]=4
  resultado = (0,1,2,3,4) = E

σ²∘σ³ = componer(σ²,σ³), con σ²=(2,0,1,3,4), σ³=(0,1,2,4,3):
  x=0: σ³[0]=0 → σ²[0]=2
  x=1: σ³[1]=1 → σ²[1]=0
  x=2: σ³[2]=2 → σ²[2]=1
  x=3: σ³[3]=4 → σ²[4]=4
  x=4: σ³[4]=3 → σ²[3]=3
  resultado = (2,0,1,4,3) = σ⁵ = G5

σ¹∘(σ²∘σ³) = σ¹∘σ⁵ = componer(σ¹,σ⁵), con σ¹=(1,2,0,4,3), σ⁵=(2,0,1,4,3):
  x=0: σ⁵[0]=2 → σ¹[2]=0
  x=1: σ⁵[1]=0 → σ¹[0]=1
  x=2: σ⁵[2]=1 → σ¹[1]=2
  x=3: σ⁵[3]=4 → σ¹[4]=3
  x=4: σ⁵[4]=3 → σ¹[3]=4
  resultado = (0,1,2,3,4) = E
```

`(G1∘G2)∘G3 = E` y `G1∘(G2∘G3) = E`: **el mismo resultado por dos caminos
distintos**, calculado dedo por dedo con permutaciones reales, no solo con la
abreviación mod 6. (El código verifica esto para **todas** las `6³ = 216`
ternas posibles en `tests/test_grupo_gestos.py::test_asociatividad`.)

**Identidad — ejemplo.** `E ∘ G4 = G4` y `G4 ∘ E = G4`, porque `σ⁰` es la
función identidad: no mueve nada, así que componerla con cualquier `σ⁴` no
cambia el resultado.

**Inversos — ejemplo.** ¿Cuál es el inverso de `G2`? Buscamos `x` tal que
`G2 ∘ x = E`, es decir `2 + x ≡ 0 (mod 6)`, o sea `x = 4`. Entonces
`G2⁻¹ = G4`. Verificación: `G2 ∘ G4` → `2+4=6≡0` → `E`. ✓ Y al revés,
`G4 ∘ G2` → `4+2=6≡0` → `E` también (como `G` es abeliano, no importa el
orden). La tabla completa de inversos:

| Elemento | Inverso | Por qué |
|---|---|---|
| `E` | `E` | `0+0=0` |
| `G1` | `G5` | `1+5=6≡0` |
| `G2` | `G4` | `2+4=6≡0` |
| `G3` | `G3` | `3+3=6≡0` — el único autoinverso no trivial |
| `G4` | `G2` | `4+2=6≡0` |
| `G5` | `G1` | `5+1=6≡0` |

Nótese que **solo `E` y `G3` son autoinversos** — la idea original de "todo
gesto es su propio inverso" era falsa para 4 de los 6 elementos, tal como
predecía el argumento de la sección 1.1.

### 1.4 Tabla de Cayley completa de `G`

Identificando `Gᵢ ↔ i`, la operación es literalmente la suma módulo 6:

| `∘` | `E` | `G1` | `G2` | `G3` | `G4` | `G5` |
|---|---|---|---|---|---|---|
| **`E`**  | `E`  | `G1` | `G2` | `G3` | `G4` | `G5` |
| **`G1`** | `G1` | `G2` | `G3` | `G4` | `G5` | `E`  |
| **`G2`** | `G2` | `G3` | `G4` | `G5` | `E`  | `G1` |
| **`G3`** | `G3` | `G4` | `G5` | `E`  | `G1` | `G2` |
| **`G4`** | `G4` | `G5` | `E`  | `G1` | `G2` | `G3` |
| **`G5`** | `G5` | `E`  | `G1` | `G2` | `G3` | `G4` |

(Ejemplo de lectura: fila `G3`, columna `G4` → `G3 ∘ G4 = G1`, porque
`3+4=7≡1`.) Esta tabla se genera por composición real de permutaciones en
`scripts/derivar_cayley.py`, no se transcribió a mano — así se evita el error
de la sección 1.1.

**Conclusión: `G ≅ ℤ/6ℤ`**, el grupo cíclico de orden 6, realizado
concretamente como subgrupo de `S₅` generado por `σ`.

---

## 2. El grupo `A` de acciones

`A = {A_E, A1, A2, A3, A4, A5}` se modela con **la misma estructura**
`ℤ/6ℤ` (`src/algebra/grupo_acciones.py`), identificando `Aᵢ ↔ i` con suma
módulo 6:

| `∘` | `A_E` | `A1` | `A2` | `A3` | `A4` | `A5` |
|---|---|---|---|---|---|---|
| **`A_E`** | `A_E` | `A1` | `A2` | `A3` | `A4` | `A5` |
| **`A1`**  | `A1`  | `A2` | `A3` | `A4` | `A5` | `A_E` |
| **`A2`**  | `A2`  | `A3` | `A4` | `A5` | `A_E` | `A1` |
| **`A3`**  | `A3`  | `A4` | `A5` | `A_E` | `A1` | `A2` |
| **`A4`**  | `A4`  | `A5` | `A_E` | `A1` | `A2` | `A3` |
| **`A5`**  | `A5`  | `A_E` | `A1` | `A2` | `A3` | `A4` |

**Ejemplo:** `A1 ∘ A2 = A3` (subir volumen, luego bajar volumen, "equivale
en efecto acumulado" a pausa/play — esto es una convención algebraica del
modelo, no algo que el usuario perciba; el punto es que `A` es un grupo
abeliano genuino, no solo una tabla que "da bien" por casualidad).

Que `A` sea realmente `ℤ/6ℤ` (y no una tabla inventada) es importante para
el paso siguiente: hace que `φ` pueda ser, honestamente, un isomorfismo entre
dos copias del mismo grupo cíclico.

---

## 3. El homomorfismo `φ : G → A`

### 3.1 La tabla por defecto

```
φ(E)  = A_E     φ(G1) = A1     φ(G2) = A2
φ(G3) = A3      φ(G4) = A4     φ(G5) = A5
```

Como `G ↔ ℤ/6ℤ` y `A ↔ ℤ/6ℤ` con la **misma** identificación de índices,
`φ` es aquí, literalmente, la función identidad `i ↦ i` reescrita en dos
alfabetos distintos. Por eso preservar la operación es automático — pero
vale la pena verificarlo con ejemplos concretos en vez de solo argumentarlo.

### 3.2 Verificando `φ(g₁∘g₂) = φ(g₁)∘φ(g₂)` con ejemplos

**Ejemplo 1 — `(G1, G2)`:**

```
lado izquierdo:  φ(G1 ∘ G2) = φ(G3) = A3
lado derecho:    φ(G1) ∘ φ(G2) = A1 ∘ A2 = A3      (1+2=3)
```
Ambos lados dan `A3`. ✓

**Ejemplo 2 — `(G4, G5)`** (el mismo par que usamos para clausura arriba):

```
lado izquierdo:  φ(G4 ∘ G5) = φ(G3) = A3
lado derecho:    φ(G4) ∘ φ(G5) = A4 ∘ A5 = A3      (4+5=9≡3)
```
Ambos lados dan `A3`. ✓

**Ejemplo 3 — un par con la identidad, `(E, G5)`:**

```
lado izquierdo:  φ(E ∘ G5) = φ(G5) = A5
lado derecho:    φ(E) ∘ φ(G5) = A_E ∘ A5 = A5
```
Ambos lados dan `A5`. ✓ (Esto ilustra la consecuencia general
`φ(e_G) = e_A`: la identidad siempre va a la identidad.)

**Ejemplo 4 — un par con inversos, `(G2, G4)`** (recordemos `G4 = G2⁻¹`):

```
lado izquierdo:  φ(G2 ∘ G4) = φ(E) = A_E
lado derecho:    φ(G2) ∘ φ(G4) = A2 ∘ A4 = A_E     (2+4=6≡0)
```
Ambos lados dan `A_E`. ✓ (Ilustra `φ(g⁻¹) = φ(g)⁻¹`.)

**¿Por qué se verifican los 36 pares y no solo unos cuantos?** `|G|=6`, así
que `G × G` tiene `6 × 6 = 36` pares ordenados `(g₁, g₂)`. Verificar la
propiedad de homomorfismo "en general" exige comprobarla en **cada uno** de
esos 36 pares — los cuatro ejemplos de arriba son una muestra ilustrativa;
`Homomorfismo.verificar_homomorfismo()` (en
`src/algebra/homomorfismo.py`) hace exactamente eso de forma exhaustiva, y
`tests/test_homomorfismo.py::test_verificar_homomorfismo_sobre_cayley` lo
confirma en verde para los 36 pares.

### 3.3 ¿Qué tipo de homomorfismo es `φ`?

- **Monomorfismo (inyectiva):** cada gesto produce una acción distinta →
  `ker(φ) = {E}` (ver sección 4.1).
- **Epimorfismo (sobreyectiva):** las 6 acciones son alcanzables →
  `Im(φ) = A` completo.
- Inyectiva + sobreyectiva = **isomorfismo**. En la tabla por defecto, `φ` es
  un isomorfismo `G ≅ A` — dos copias de `ℤ/6ℤ` puestas en correspondencia
  biunívoca que además preserva la operación.

---

## 4. El kernel: tres ejemplos, de lo trivial a lo rico

### 4.1 Caso actual — kernel trivial

```
ker(φ) = {g ∈ G : φ(g) = A_E} = {E}
```

Solo el gesto de reposo produce "ninguna acción". Esto es consistente con
que `φ` sea inyectiva: `φ` es inyectiva **si y solo si** `ker(φ) = {e_G}`.

**Ejemplo de por qué la inyectividad se sigue del kernel trivial.** Tomemos
dos gestos distintos, digamos `G1` y `G3`, y veamos que no pueden producir la
misma acción: si `φ(G1) = φ(G3)`, entonces `φ(G1 ∘ G3⁻¹) = φ(G1)∘φ(G3)⁻¹ =
A_E`, es decir `G1 ∘ G3⁻¹ ∈ ker(φ) = {E}`, luego `G1 ∘ G3⁻¹ = E`, luego
`G1 = G3` — contradicción. Numéricamente: `G3⁻¹ = G3`, así que
`G1 ∘ G3⁻¹ = G1 ∘ G3 = G4` (`1+3=4`), y `G4 ≠ E`, así que en efecto
`G1 ∘ G3⁻¹ ∉ ker(φ)` — confirma que `φ(G1) ≠ φ(G3)` (de hecho `A1 ≠ A3`).

### 4.2 Caso extremo — kernel máximo (homomorfismo constante)

Un homomorfismo válido (aunque poco útil) es enviar **todo** `G` a `A_E`:

```
φ_const(g) = A_E   para todo g ∈ G
```

Esto sí es un homomorfismo genuino: `φ_const(g₁∘g₂) = A_E = A_E ∘ A_E =
φ_const(g₁) ∘ φ_const(g₂)` se cumple trivialmente para cualquier par. Aquí:

```
ker(φ_const) = G                (los 6 gestos, todos "no hacen nada")
Im(φ_const)  = {A_E}            (una sola acción alcanzable)
```

`φ_const` no es inyectiva (`|ker|=6≠1`) ni sobreyectiva (`Im≠A`). Este caso
está cubierto por
`tests/test_homomorfismo.py::test_tabla_constante_a_identidad`.

### 4.3 Caso intermedio (extensión hipotética, no implementada hoy)

Ni la tabla por defecto ni la constante muestran un kernel "interesante" (ni
trivial ni todo `G`). Construyamos uno para entender el caso general:
definamos `φ₂ : G → A` **reduciendo módulo 2** (enviando cada gesto a si su
índice es par o impar):

```
φ₂(Gᵢ) = A_E  si i es par   (i = 0, 2, 4  →  E, G2, G4)
φ₂(Gᵢ) = A3   si i es impar (i = 1, 3, 5  →  G1, G3, G5)
```

Esto es un homomorfismo válido porque `{A_E, A3}` es un subgrupo de `A` de
orden 2 (`A3 ∘ A3 = A_E` porque `3+3=6≡0`), y la reducción módulo 2 de
`ℤ/6ℤ` en `ℤ/2ℤ` es un homomorfismo de grupos estándar. Aquí:

```
ker(φ₂) = {E, G2, G4}      (el subgrupo cíclico de orden 3 generado por G2)
Im(φ₂)  = {A_E, A3}
```

Verificación con un ejemplo: `φ₂(G2 ∘ G4) = φ₂(E) = A_E`, y por otro lado
`φ₂(G2) ∘ φ₂(G4) = A_E ∘ A_E = A_E`. ✓ Otro: `φ₂(G1 ∘ G4) = φ₂(G5) = A3`
(`G4` es índice par, `G1` impar, la suma `1+4=5` es impar), y
`φ₂(G1) ∘ φ₂(G4) = A3 ∘ A_E = A3`. ✓

Este `φ₂` es el ejemplo que hace tangible lo que la sección "Trabajo Futuro"
del documento de contexto describe como "mapear varios gestos a la misma
acción" — con `ker(φ₂)` de tamaño 3 en vez de 1 o 6.

---

## 5. `ker(φ) ◁ G`: el subgrupo normal, con números

**La propiedad a demostrar:** para todo `k ∈ ker(φ)` y todo `g ∈ G`, el
"conjugado" `g ∘ k ∘ g⁻¹` también está en `ker(φ)`.

**Demostración general (la que corre en código, no depende de que `G` sea
abeliano):**

```
φ(g∘k∘g⁻¹) = φ(g)·φ(k)·φ(g)⁻¹ = φ(g)·A_E·φ(g)⁻¹ = φ(g)·φ(g)⁻¹ = A_E
```

**Ejemplo numérico usando el kernel intermedio `ker(φ₂) = {E, G2, G4}` de la
sección 4.3** (para tener algo menos trivial que `{E}` solo): tomemos
`k = G2 ∈ ker(φ₂)` y `g = G1` (arbitrario). Como `G` es abeliano,
`g ∘ k ∘ g⁻¹ = k` siempre (el conjugado de cualquier elemento por otro es él
mismo, `g∘k∘g⁻¹ = g∘g⁻¹∘k = k` cuando el orden no importa). Verifiquémoslo
con la aritmética de índices igual:

```
g ∘ k ∘ g⁻¹ = G1 ∘ G2 ∘ G1⁻¹ = G1 ∘ G2 ∘ G5     (G1⁻¹ = G5)
            índices: 1 + 2 + 5 = 8 ≡ 2 (mod 6)
            = G2 = k                              ✓ está en ker(φ₂)
```

**Por qué esto es "gratis" aquí:** como `G` es abeliano (sección 1, `G≅ℤ/6ℤ`),
el Corolario 13.3 del curso ("todo subgrupo de un grupo abeliano es normal")
ya garantiza que **cualquier** subconjunto de `G` que sea subgrupo —
`{E}`, `{E,G2,G4}`, o todo `G` — es automáticamente normal, sin importar cuál
sea `φ`. La demostración general de arriba (con `φ(g)·φ(g)⁻¹`) es la que se
ejercita en código porque es válida incluso si `G` no fuera abeliano.

---

## 6. Clases laterales y el grupo cociente `G/ker(φ)`

Las clases laterales de `ker(φ)` en `G` agrupan gestos que producen **la
misma acción** — es la relación de equivalencia "`g₁ ~ g₂` si `φ(g₁) =
φ(g₂)`".

**Caso trivial (tabla por defecto, sección 3.1):** como `ker(φ)={E}`, cada
clase tiene un único elemento — 6 clases de tamaño 1:

```
{E}, {G1}, {G2}, {G3}, {G4}, {G5}       →  6 clases
```

**Caso intermedio (`φ₂` de la sección 4.3):** el kernel `{E,G2,G4}` parte a
`G` en solo **2** clases de tamaño 3 cada una:

```
clase de A_E:  ker(φ₂)·E  = {E, G2, G4}   (los índices pares)
clase de A3:   ker(φ₂)·G1 = {G1, G3, G5}  (los índices impares)
```

Interpretación física-conceptual: en este `φ₂` hipotético, el sistema
"trataría igual" (produciría el mismo efecto en `A`) a reposo/2-dedos/mano
abierta por un lado, y a 1-dedo/puño/pulgar por otro — un ejemplo de cómo un
kernel no trivial colapsa gestos distintos en la misma clase de
equivalencia.

`|G/ker(φ)|` (número de clases) siempre satisface `|G| = |ker(φ)| ·
|G/ker(φ)|` (teorema de Lagrange): `6 = 1×6` en el caso trivial, `6 = 3×2` en
el caso intermedio, `6 = 6×1` en el caso constante (sección 4.2).

---

## 7. Primer Teorema de Isomorfismo, con los tres casos numéricos

**El teorema:** `G/ker(φ) ≅ Im(φ)`, vía `f(ker(φ)·g) = φ(g)`.

**Verificación operacional (la que hace el código):** en vez de construir
`f` explícitamente, se comprueba que **el número de clases coincide con
`|Im(φ)|`** — evidencia de que la biyección subyacente existe.

| Caso | `\|ker(φ)\|` | `\|G/ker(φ)\|` (nº de clases) | `\|Im(φ)\|` | ¿Coinciden? |
|---|---|---|---|---|
| Por defecto (sección 3.1) | 1 | 6 | 6 | ✓ — `G/{E} ≅ A` (isomorfismo completo) |
| `φ₂` intermedio (sección 4.3) | 3 | 2 | 2 | ✓ — `G/{E,G2,G4} ≅ {A_E,A3} ≅ ℤ/2ℤ` |
| Constante (sección 4.2) | 6 | 1 | 1 | ✓ — `G/G ≅ {A_E}` (grupo trivial) |

En los tres casos, `6 = |ker(φ)| × |G/ker(φ)|` (Lagrange) y el número de
clases coincide exactamente con `|Im(φ)|` (Primer Teorema de Isomorfismo).
El código solo ejecuta y comprueba el primer caso (`tests/test_homomorfismo.py`);
los otros dos son ejercicios manuales que muestran el mismo teorema en
situaciones que la tabla por defecto no expone.

---

## 8. Mapa: concepto → código → test

| Concepto | Archivo de código | Test que lo ejercita |
|---|---|---|
| `σ = (1 2 3)(4 5)`, potencias de `σ` | `scripts/derivar_cayley.py` | (script offline, no en `pytest`) |
| Grupo `G`, tabla de Cayley, `operacion_G` | `src/algebra/grupo_gestos.py` | `tests/test_grupo_gestos.py` |
| Grupo `A`, tabla de Cayley, `operacion_A` | `src/algebra/grupo_acciones.py` | `tests/test_grupo_acciones.py` |
| Verificación genérica de axiomas de grupo | `src/algebra/verificacion.py` | `tests/test_verificacion.py` |
| `φ`, `ker(φ)`, `Im(φ)`, clases laterales | `src/algebra/homomorfismo.py` | `tests/test_homomorfismo.py` |
| Reporte imprimible de todo lo anterior | `src/algebra/analisis.py` (`python -m src.algebra.analisis`) | evidencia citada en `docs/demostraciones.md` |
| Pureza (álgebra no depende de cámara) | — | `tests/test_pureza_algebra.py` |

---

## 9. Resumen para explicar en una frase cada uno

- **`G` es un grupo** porque es literalmente `⟨σ⟩ ≤ S₅`, y todo lo que hace
  falta (clausura, asociatividad, identidad, inversos) se hereda gratis de
  que `S₅` ya es un grupo bajo composición de funciones.
- **`φ` es un homomorfismo** porque, al ser ambos `G` y `A` la misma
  estructura `ℤ/6ℤ` bajo el capó, `φ` no es más que renombrar los mismos
  números.
- **`ker(φ)` mide cuánta información se pierde** al pasar de gestos a
  acciones: vacío de contenido (`{E}`) en la implementación actual, pero
  potencialmente grande si varios gestos se mapean a la misma acción.
- **`ker(φ) ◁ G` es automático** aquí porque `G` es abeliano — pero el código
  demuestra la versión general, que serviría igual si `G` no lo fuera.
- **El Primer Teorema de Isomorfismo** es la garantía formal de que
  "agrupar gestos por su efecto" (`G/ker(φ)`) y "mirar qué efectos son
  alcanzables" (`Im(φ)`) son, estructuralmente, la misma cosa.
