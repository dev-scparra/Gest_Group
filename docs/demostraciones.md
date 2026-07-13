# Demostraciones formales — GestGroup

Este documento respalda el reporte técnico del curso (Matemáticas Discretas II)
con las demostraciones formales y su evidencia ejecutable (tests en verde).
Referencia cruzada: `GestGroup_Contexto_Desarrollo.md` Sección 8, y las specs
`001-grupo-algebraico` / `002-homomorfismo-analisis` / `005-filtro-ema`.

---

## Decisión D1 — Realización de G como subgrupo genuino de S₅ (resuelve T001-01)

**Contexto del problema.** El documento de contexto original (Sección 3.1,
punto 4) afirma que `G = {E,G1,G2,G3,G4,G5}` es un grupo donde **cada gesto es
su propio inverso** (`gᵢ ∘ gᵢ = E`), y por separado (Sección 3.1, "Relación con
S₅") afirma que `G ≤ S₅`, representando cada gesto como una función
`σ : {1..5} → {0,1}` (dedo arriba/abajo).

Ambas afirmaciones tienen problemas matemáticos independientes:

1. **Una función a `{0,1}` no es una permutación.** `S₅` son biyecciones
   `{1..5} → {1..5}`; un vector booleano de "dedo arriba/abajo" no define un
   elemento de `S₅`. La afirmación `G ≤ S₅` no queda demostrada así.
2. **"Todo elemento es su propio inverso" es incompatible con `|G|=6`.** Si
   `x² = e` para todo `x` de un grupo `G`, entonces:
   - `G` es abeliano: `(ab)² = e ⟹ abab = e ⟹ ab = b⁻¹a⁻¹ = ba` (usando
     `a⁻¹=a`, `b⁻¹=b`).
   - Por el teorema de estructura de grupos abelianos finitos, si todo
     elemento tiene orden que divide 2, `G` es un `ℤ/2ℤ`-espacio vectorial,
     luego `|G| = 2ⁿ` para algún `n`.
   - `6 = 2·3` no es potencia de 2. **Contradicción.**
   - Equivalente por Cauchy: todo grupo de orden 6 tiene un elemento de orden
     3 (porque 3 divide a 6), y un elemento de orden 3 no puede ser autoinverso
     (`x³=e, x≠e ⟹ x²≠e`).

   Conclusión: **ningún grupo de 6 elementos puede tener todos sus elementos
   no-identidad autoinversos.** Cualquier tabla de Cayley de 6 elementos que
   se intente rellenar a mano exigiendo esa propiedad universal, más los
   axiomas de grupo, es matemáticamente irrealizable — no es un detalle de
   implementación pendiente, es una imposibilidad estructural.

**Resolución (Opción A de `specs/001-grupo-algebraico/spec.md`, refinada).**
Se define `G` como el subgrupo cíclico genuino de `S₅` generado por:

```
σ = (1 2 3)(4 5) ∈ S₅,   orden(σ) = lcm(3,2) = 6
```

con `Gᵢ := σⁱ` para `i=1..5` y `E := σ⁰ = id`. La tabla de Cayley completa
(36 entradas) se deriva por composición real de permutaciones —
`scripts/derivar_cayley.py`— y no se transcribe a mano:

```
sigma^0 = (0,1,2,3,4)  -> E
sigma^1 = (1,2,0,4,3)  -> G1
sigma^2 = (2,0,1,3,4)  -> G2
sigma^3 = (0,1,2,4,3)  -> G3   (= la transposición (4 5), orden 2)
sigma^4 = (1,2,0,3,4)  -> G4
sigma^5 = (2,0,1,4,3)  -> G5
```

Esto da `G ≅ ℤ/6ℤ`: la operación resultante es literalmente
`Gᵢ ∘ Gⱼ = G_{(i+j) mod 6}`. Consecuencias:

- `G` es un subgrupo **real** de `S₅` (clausura, asociatividad e inversos se
  heredan de la composición de funciones — se demuestran, no se postulan).
  Se corrige también el problema (1): ya no se necesita el vector booleano.
- `G` es abeliano (los grupos cíclicos lo son), consistente con la Sección
  3.1 del documento de contexto.
- **Único costo:** no todos los elementos son autoinversos. Solo `E` y `G3`
  (`=σ³`, el único elemento de orden 2) lo son. Los inversos genuinos son:
  `E⁻¹=E`, `G1⁻¹=G5`, `G2⁻¹=G4`, `G3⁻¹=G3`, `G4⁻¹=G2`, `G5⁻¹=G1`.
  `ALG-FR-004` se revisa en consecuencia (ver `specs/001-grupo-algebraico/spec.md`
  Sección 3 y 5).
- `A` (grupo de acciones) se modela con la misma estructura de `ℤ/6ℤ`
  (`src/algebra/grupo_acciones.py`), de forma que `φ: G → A` (por defecto) es
  la biyección natural de índices entre dos copias de `ℤ/6ℤ` — un
  isomorfismo genuino, no solo una tabla que "da bien" por coincidencia.

Evidencia ejecutable: `tests/test_grupo_gestos.py::test_inversos_genuinos`,
`tests/test_grupo_gestos.py::test_asociatividad` (216 ternas),
`scripts/derivar_cayley.py` (reproducible, imprime la tabla completa).

---

## Demostración 1 — (G, ∘) es un grupo

**Proposición.** `G = {E,G1,G2,G3,G4,G5}` con la operación `∘` heredada de la
composición de permutaciones en `S₅` (Decisión D1) es un grupo abeliano.

**Prueba.**

1. **Clausura.** `G` es, por construcción, el conjunto `{σ⁰,...,σ⁵}` cerrado
   bajo composición de permutaciones: `σⁱ ∘ σʲ = σ^{(i+j) mod 6} ∈ G`. ✓
2. **Asociatividad.** Heredada de la composición de funciones en `S₅`, que es
   asociativa: `(σⁱ∘σʲ)∘σᵏ = σⁱ∘(σʲ∘σᵏ)`. ✓ (verificado computacionalmente
   sobre las 216 ternas, `tests/test_grupo_gestos.py::test_asociatividad`).
3. **Identidad.** `E = σ⁰ = id` satisface `E∘g = g∘E = g` para todo `g∈G`
   (identidad de la composición de funciones). ✓
4. **Inversos.** Para cada `gᵢ=σⁱ`, `σ^{6-i}` es su inverso:
   `σⁱ∘σ^{6-i} = σ⁶ = σ⁰ = E`. Concretamente: `G1⁻¹=G5`, `G2⁻¹=G4`,
   `G3⁻¹=G3`, `G4⁻¹=G2`, `G5⁻¹=G1`, `E⁻¹=E`. ✓

**Conclusión.** `(G,∘)` es un grupo. Además, como `G=⟨σ⟩` es cíclico,
`G` es abeliano: `σⁱ∘σʲ = σ^{i+j} = σ^{j+i} = σʲ∘σⁱ`. □

Evidencia: `tests/test_grupo_gestos.py` (5 tests, en verde).

---

## Demostración 2 — ker(φ) ◁ G

**Proposición.** `ker(φ)` es un subgrupo normal de `G`.

**Prueba (usando que φ es homomorfismo — no depende de la Decisión D1).**

Sea `k ∈ ker(φ)` y `g ∈ G` arbitrario:

```
φ(gkg⁻¹) = φ(g)·φ(k)·φ(g⁻¹)     [homomorfismo]
         = φ(g)·A_E·φ(g)⁻¹        [k ∈ ker(φ)]
         = φ(g)·φ(g)⁻¹            [A_E identidad en A]
         = A_E
```

Luego `gkg⁻¹ ∈ ker(φ)`, es decir `ker(φ) ◁ G`. □

**Nota:** como `G` es abeliano (Demostración 1), esto también se sigue
inmediatamente del Corolario 13.3 del curso (todo subgrupo de un grupo
abeliano es normal) — la prueba general de arriba es la que se ejercita en
código porque no depende de que `G` sea abeliano, es más general.

Evidencia: `tests/test_homomorfismo.py::test_kernel_contiene_solo_identidad`
(en la implementación por defecto `ker(φ)={E}`, trivialmente normal);
`tests/test_homomorfismo.py::test_verificar_homomorfismo_sobre_cayley`
confirma que φ es homomorfismo sobre los 36 pares, precondición de esta
demostración.

---

## Demostración 3 — Primer Teorema de Isomorfismo: G/ker(φ) ≅ Im(φ)

**Proposición.** `f : G/ker(φ) → Im(φ)` definida por `f(ker(φ)·g) = φ(g)` es
un isomorfismo.

**Prueba.**

- **Bien definida:** si `ker(φ)·g₁ = ker(φ)·g₂`, entonces `g₁g₂⁻¹ ∈ ker(φ)`,
  luego `φ(g₁g₂⁻¹)=A_E`, es decir `φ(g₁)=φ(g₂)`. ✓
- **Homomorfismo:** `f(ker(φ)·g₁ ∗ ker(φ)·g₂) = f(ker(φ)·g₁g₂) = φ(g₁g₂) =
  φ(g₁)·φ(g₂) = f(ker(φ)·g₁)·f(ker(φ)·g₂)`. ✓
- **Inyectiva:** si `f(ker(φ)·g₁)=f(ker(φ)·g₂)`, entonces `φ(g₁)=φ(g₂)`,
  luego `φ(g₁g₂⁻¹)=A_E`, es decir `g₁g₂⁻¹∈ker(φ)`, por tanto
  `ker(φ)·g₁=ker(φ)·g₂`. ✓
- **Sobreyectiva:** por definición, `Im(φ)={φ(g):g∈G}={f(ker(φ)·g):g∈G}`. ✓

**Conclusión.** `f` es isomorfismo, por tanto `G/ker(φ) ≅ Im(φ)`. □

**Verificación operacional (no construye `f` en runtime, ver
`002-homomorfismo-analisis/spec.md` Sección 6):** el número de clases
laterales de `ker(φ)` en `G` coincide con `|Im(φ)|` — evidencia de que la
biyección subyacente a `f` existe, sin necesidad de instanciarla en código.

**Evidencia ejecutable (salida real de `python -m src.algebra.analisis`):**

```
============================================================
GestGroup — Analisis algebraico de phi : G -> A
============================================================

G = {E, G1, G2, G3, G4, G5}   (|G| = 6)
tabla phi por defecto: {E->A_E, G1->A1, G2->A2, G3->A3, G4->A4, G5->A5}

ker(phi) = {E}   (|ker(phi)| = 1)
Im(phi)  = {A2, A4, A1, A5, A3, A_E}   (|Im(phi)| = 6)

es_inyectiva()   = True
es_sobreyectiva()= True
tipo de phi      = isomorfismo (inyectiva + sobreyectiva)

Clases laterales de ker(phi) en G (= G/ker(phi)):
    ker(phi)*g para phi(g)=A1: {G1}
    ker(phi)*g para phi(g)=A2: {G2}
    ker(phi)*g para phi(g)=A3: {G3}
    ker(phi)*g para phi(g)=A4: {G4}
    ker(phi)*g para phi(g)=A5: {G5}
    ker(phi)*g para phi(g)=A_E: {E}
  numero de clases = 6, |Im(phi)| = 6  -> coinciden (Primer Teorema de Isomorfismo verificado)

Verificacion de la propiedad de homomorfismo phi(g1 o g2) = phi(g1) o phi(g2):
  pares evaluados = 36 (|G| x |G|)
  cumple = True
============================================================
```

En la implementación base, `ker(φ)={E}` (trivial) y `φ` resulta ser un
isomorfismo completo `G ≅ A` — el caso "rico" de clases laterales no
triviales (varios gestos a la misma acción) se ejercita en
`tests/test_homomorfismo.py::test_tabla_custom_con_kernel_no_trivial` con una
tabla `φ` alternativa.

---

## Demostración 4 — Estabilidad asintótica del filtro EMA

**Proposición.** El filtro EMA `x[n] = α·x_raw[n] + (1-α)·x[n-1]` con
`α ∈ (0,1)` es asintóticamente estable.

**Prueba.** La ecuación en diferencias `x[n] - (1-α)x[n-1] = α·x_raw[n]` tiene
solución homogénea `x_h[n] = C·(1-α)ⁿ`. Como `α∈(0,1)`, `0<|1-α|<1`, luego:

```
lim_{n→∞} |x_h[n]| = lim_{n→∞} |C|·|1-α|ⁿ = 0
```

La influencia de las condiciones iniciales desaparece exponencialmente. □

**Evidencia empírica:** `tests/test_filtro_ema.py::test_convergencia_ema`
(la salida converge a la entrada constante tras 200 iteraciones, error
`<1e-6`) y `test_estabilidad_ruido` (la varianza de la señal suavizada es
estrictamente menor que la de la señal cruda con ruido gaussiano).

---

## Evidencia agregada — suite de tests

```
$ .venv/bin/python -m pytest tests/ -q
............................................................
60 passed in 0.75s
```

60/60 tests en verde, sin cámara ni hardware real (NFR-G03): 5 archivos de
`tests/test_grupo_*`/`test_verificacion`/`test_homomorfismo` cubren la capa
algebraica pura (Decisión D1 y Demostraciones 1-3); `tests/test_filtro_ema.py`
cubre la Demostración 4; el resto cubre los módulos de visión/ejecución con
mocks (sin depender de cámara, SO real, o permisos de sistema).
