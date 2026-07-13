# Spec 001 — Grupo Algebraico (G, A)

**Módulo:** `src/algebra/grupo_gestos.py`, `src/algebra/grupo_acciones.py`
**Depende de:** nada (es la base de toda la capa algebraica).
**Consumido por:** [002-homomorfismo-analisis](../002-homomorfismo-analisis/spec.md).
**NFRs heredados:** NFR-G03 (puro, sin I/O, testeable sin hardware) — ver [000-overview](../000-overview/spec.md).

---

## 1. Propósito

Definir formalmente los dos grupos que sostienen todo el proyecto:

- **G** = {e, g₁, g₂, g₃, g₄, g₅}, el grupo de gestos, con operación ∘ (composición secuencial de gestos).
- **A** = {a_e, a₁, a₂, a₃, a₄, a₅}, el grupo de acciones, con operación ∘ (composición de efectos).

Este módulo NO decide qué gesto produce qué acción (eso es φ, módulo 002). Su única responsabilidad es que (G,∘) y (A,∘) sean, verificablemente, grupos.

## 2. Contrato de interfaz

**Entradas:** ninguna (estructuras estáticas, no dependen de runtime ni de cámara).

**Salidas expuestas a otros módulos:**

```python
class Gesto(Enum):
    E, G1, G2, G3, G4, G5

class Accion(Enum):
    A_E, A1, A2, A3, A4, A5

def operacion_G(g1: Gesto, g2: Gesto) -> Gesto: ...   # g1 ∘ g2
def operacion_A(a1: Accion, a2: Accion) -> Accion: ... # a1 ∘ a2

def verificar_axiomas_grupo(elementos: set, operacion: callable, identidad) -> ReporteAxiomas:
    """Función genérica, reusada para verificar tanto G como A."""
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| ALG-FR-001 | G DEBE tener exactamente 6 elementos: `{E, G1, G2, G3, G4, G5}`, representados como `Enum`. |
| ALG-FR-002 | La operación `∘` sobre G DEBE estar definida como una tabla de Cayley explícita (36 pares ordenados), no calculada geométricamente en runtime. |
| ALG-FR-003 | `E` DEBE ser el elemento identidad: `E ∘ x = x ∘ E = x` para los 6 elementos. |
| ALG-FR-004 (revisado, ver Sección 5) | Cada elemento `gᵢ` DEBE tener un inverso en G (`∃ gⱼ : gᵢ∘gⱼ = gⱼ∘gᵢ = E`) — el diseño original del documento de contexto ("cada gesto es su propio inverso") es matemáticamente inconsistente con `\|G\|=6` (ver Sección 5) y se reemplaza por inversos genuinos derivados de la realización en S₅: `G1⁻¹=G5`, `G2⁻¹=G4`, `G3⁻¹=G3` (único no identidad autoinverso), `E⁻¹=E`. |
| ALG-FR-005 | DEBE existir una función que verifique los 4 axiomas de grupo (clausura, asociatividad, identidad, inversos) recorriendo la tabla completa, y que sea genérica (reusable para G y para A, no duplicada). |
| ALG-FR-006 | A DEBE tener exactamente 6 elementos: `{A_E, A1, A2, A3, A4, A5}`. |
| ALG-FR-007 | La operación sobre A DEBE ser abeliana (`a ∘ b = b ∘ a` para todo par), según lo fijado en el documento de contexto Sección 3.2. |
| ALG-FR-008 | Ambos grupos DEBEN quedar disponibles como constantes importables (no se instancian por request; son singletons conceptuales). |

## 4. Criterios de aceptación

- **Dado** la tabla de Cayley completa de G, **cuando** se recorre cada uno de los 36 pares (gᵢ,gⱼ), **entonces** `operacion_G(gi,gj)` siempre devuelve un elemento de G (clausura, ALG-FR-002).
- **Dado** cualquier par (gᵢ,gⱼ,gₖ), **cuando** se calcula `(gᵢ∘gⱼ)∘gₖ` y `gᵢ∘(gⱼ∘gₖ)`, **entonces** ambos resultados son iguales (asociatividad).
- **Dado** cualquier gᵢ, **cuando** se calcula `gᵢ ∘ E` y `E ∘ gᵢ`, **entonces** el resultado es `gᵢ` (identidad, ALG-FR-003).
- **Dado** cualquier gᵢ, **cuando** se busca `gⱼ ∈ G` tal que `gᵢ∘gⱼ = gⱼ∘gᵢ = E`, **entonces** existe exactamente uno (inverso, ALG-FR-004 revisado): `E⁻¹=E`, `G1⁻¹=G5`, `G2⁻¹=G4`, `G3⁻¹=G3`, `G4⁻¹=G2`, `G5⁻¹=G1`.
- **Dado** `verificar_axiomas_grupo`, **cuando** se aplica sobre A con la operación abeliana, **entonces** reporta los 4 axiomas satisfechos sin reimplementar la lógica usada para G.

## 5. Riesgo crítico (RESUELTO — ver docs/demostraciones.md, Decisión D1) — la tabla de Cayley de G no está matemáticamente cerrada en el documento de contexto

Esto **no es un detalle menor de implementación**: es un vacío en el modelo matemático que hay que resolver *antes* de escribir código, porque afecta directamente la rigurosidad que el curso va a evaluar.

El documento de contexto (Sección 3.3) muestra la tabla de Cayley de G **incompleta**:

```
∘  | e   g₁  g₂  g₃  g₄  g₅
---|----------------------------
e  | e   g₁  g₂  g₃  g₄  g₅
g₁ | g₁  e   g₁∘g₂ ...
g₂ | g₂  ...
...
```

Solo están definidos: la fila/columna de la identidad (ALG-FR-003) y la diagonal (ALG-FR-004, cada elemento es su propio inverso). **Los 20 productos restantes (por ejemplo, g₁∘g₂, g₁∘g₃, g₂∘g₄, etc.) no están definidos en ningún lugar del documento de contexto.**

Además, la justificación de que "G ≤ S₅" (Sección 3.1, "Relación con S₅") describe cada gesto como una función σ : {1,2,3,4,5} → {0,1} (dedo arriba/abajo). **Una función a {0,1} no es una permutación** (S₅ son biyecciones {1..5}→{1..5}); tal como está redactado, ese párrafo no alcanza a mostrar rigurosamente que G es subgrupo de S₅, aunque el resto del documento (Sección 2.2) sí define S₅ correctamente.

**Esto es exactamente el tipo de vacío que un profesor de Matemáticas Discretas va a señalar.** Antes de la Fase de implementación de este módulo, el equipo debe resolver una de estas dos rutas (bloqueante, no se puede posponer a "trabajo futuro"):

- **Opción A — Definir una representación real en S₅:** en vez de "dedo arriba/abajo" (vector booleano), representar cada gesto como una permutación genuina de {1,2,3,4,5} (por ejemplo, qué dedo "ocupa el lugar" de cuál otro), de modo que la composición ∘ sea literalmente composición de funciones y la tabla de Cayley completa se derive automáticamente por composición de permutaciones — no se transcribe a mano.
- **Opción B — Simplificar la afirmación:** declarar G como un grupo abstracto de 6 elementos (isomorfo a algún grupo conocido de orden 6, p. ej. ℤ/6ℤ o S₃, eligiendo la operación que sea consistente con "cada elemento es su propio inverso" — lo cual de hecho fuerza a que G sea isomorfo a (ℤ/2ℤ)³ restringido a 6 elementos o a un grupo elemental abeliano; hay que verificar que existe una operación cerrada y asociativa con esa propiedad sobre exactamente 6 elementos antes de asumirlo) y ya no afirmar `G ≤ S₅` en el reporte, o acotar esa afirmación a un ejemplo ilustrativo, no a una demostración.

Recomendación: **Opción A**, porque es la que da contenido real al Primer Teorema de Isomorfismo y a la Sección 2.2 del curso (el proyecto pierde su gancho matemático si G termina siendo "6 elementos con una tabla inventada a mano").

**Decisión tomada (T001-01): Opción A, con una precisión matemática adicional que el enunciado original de la Opción B ya anticipaba como riesgo.** Un grupo de 6 elementos no puede tener *todos* sus elementos no identidad autoinversos: si `x²=e` para todo `x`, el grupo es abeliano y, por el teorema de estructura de grupos abelianos finitos, su orden debe ser potencia de 2 — 6 no lo es (esto se sigue de que 6=2·3 y, por Cauchy, todo grupo de orden 6 tiene un elemento de orden 3, que no puede ser autoinverso). Por tanto **ALG-FR-004 se revisa**: en vez de "cada gesto es su propio inverso", `G` se realiza como el subgrupo cíclico de `S₅` generado por `σ = (1 2 3)(4 5)` (orden 6, `lcm(3,2)`), con `Gᵢ := σⁱ`. Esto da: `G ≅ ℤ/6ℤ`, subgrupo genuino de `S₅` (no un vector booleano — se corrige también el segundo gap de esta sección), abeliano, con clausura/asociatividad/inversos heredados automáticamente de la composición de permutaciones (`scripts/derivar_cayley.py`). Único costo: solo `E` y `G3` (`=σ³`, el elemento de orden 2) son autoinversos; `G1↔G5` y `G2↔G4` son pares de inversos genuinos, no autoinversos. Justificación completa en `docs/demostraciones.md`, Decisión D1.

## 6. Casos borde

- Operar con un elemento fuera del enum `Gesto`/`Accion` (p. ej. `None`) DEBE fallar explícitamente (`KeyError`/`ValueError`), no devolver un valor por defecto silencioso — este módulo es de dominio cerrado, no de entrada de usuario.
- La verificación de axiomas sobre una tabla intencionalmente rota (para test negativo) DEBE reportar cuál axioma falla, no solo `False` genérico — necesario para depurar la Opción A de la Sección 5.

## 7. No objetivos de este módulo

- No decide la relación gesto→acción (eso es φ, módulo 002).
- No conoce nada de landmarks, cámara ni geometría de la mano — eso es el módulo 006, que es quien *produce* un `Gesto` a partir de la mano; este módulo solo sabe operar sobre `Gesto` una vez que ya existe.
