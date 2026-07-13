# Spec 002 — Homomorfismo φ y Análisis Algebraico

**Módulo:** `src/algebra/homomorfismo.py`, `src/algebra/analisis.py`
**Depende de:** [001-grupo-algebraico](../001-grupo-algebraico/spec.md).
**Consumido por:** [007-ejecutor-acciones](../007-ejecutor-acciones/spec.md) (recibe `φ(g)` para ejecutar), reporte técnico (vía `analisis.py`).
**Cubre:** US-5 y US-3 de [000-overview](../000-overview/spec.md); SC-G04, SC-G05.

---

## 1. Propósito

Implementar φ : G → A como función total explícita, y exponer las operaciones derivadas que el curso exige analizar: kernel, imagen, clases laterales, y verificación de la propiedad de homomorfismo — todo ejecutable sin cámara, como evidencia para el reporte técnico (US-5).

## 2. Contrato de interfaz

**Entradas:** `Gesto`, `Accion`, `operacion_G`, `operacion_A` (del módulo 001).

**Salidas:**

```python
class Homomorfismo:
    def __init__(self, tabla_phi: dict[Gesto, Accion] | None = None): ...
    def aplicar(self, gesto: Gesto) -> Accion: ...
    def kernel(self) -> set[Gesto]: ...
    def imagen(self) -> set[Accion]: ...
    def es_inyectiva(self) -> bool: ...
    def es_sobreyectiva(self) -> bool: ...
    def clases_laterales_kernel(self) -> dict[Accion, list[Gesto]]: ...
    def verificar_homomorfismo(self) -> ReporteHomomorfismo:  # usa operacion_G y operacion_A de 001
```

`analisis.py` es un script/CLI (no una librería que otros módulos importen) que instancia `Homomorfismo` con la tabla por defecto e imprime un reporte legible en texto plano.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| HOM-FR-001 | φ DEBE ser una función total sobre G: la tabla `tabla_phi` DEBE tener exactamente las 6 claves de `Gesto` — si falta alguna, el constructor DEBE fallar explícitamente (no asumir un valor por defecto). |
| HOM-FR-002 | Por defecto (sin tabla custom), φ DEBE ser la definida en la Sección 3.3 del documento de contexto: `E→A_E, G1→A1, G2→A2, G3→A3, G4→A4, G5→A5`. |
| HOM-FR-003 | `verificar_homomorfismo()` DEBE comprobar `φ(g₁∘g₂) = φ(g₁)∘φ(g₂)` para los 36 pares ordenados de G×G, usando `operacion_G`/`operacion_A` del módulo 001 (no reimplementar la composición aquí). |
| HOM-FR-004 | `kernel()` DEBE devolver `{g ∈ G : φ(g) = A_E}`. |
| HOM-FR-005 | `imagen()` DEBE devolver `{φ(g) : g ∈ G}`. |
| HOM-FR-006 | `es_inyectiva()` DEBE ser equivalente a `len(kernel()) == 1`. |
| HOM-FR-007 | `es_sobreyectiva()` DEBE comparar `imagen()` contra el conjunto completo de `Accion`. |
| HOM-FR-008 | `clases_laterales_kernel()` DEBE agrupar los 6 gestos por el valor de `φ(g)` — cada grupo es una clase lateral de `ker(φ)` en G (consecuencia directa del Primer Teorema de Isomorfismo). |
| HOM-FR-009 | `analisis.py` DEBE, al ejecutarse como script, imprimir: `ker(φ)`, `Im(φ)`, las clases laterales, si φ es mono/epi/isomorfismo, y el resultado de `verificar_homomorfismo()` — sin requerir cámara ni argumentos. |
| HOM-FR-010 | Este módulo NO DEBE importar `cv2`, `mediapipe` ni `subprocess` (hereda NFR-G03). |

## 4. Criterios de aceptación

- **Dado** la tabla φ por defecto, **cuando** se llama `verificar_homomorfismo()`, **entonces** el reporte indica que los 36 pares cumplen la propiedad (SC-G04) — este test es la evidencia ejecutable de la Demostración 2 del documento de contexto (Sección 8: ker(φ)◁G se apoya en que φ es homomorfismo).
- **Dado** la tabla φ por defecto, **cuando** se llama `kernel()`, **entonces** el resultado es `{E}` (ker(φ) trivial en la implementación base, según Sección 3.4 del documento de contexto).
- **Dado** la tabla φ por defecto, **cuando** se llama `es_inyectiva()` y `es_sobreyectiva()`, **entonces** ambas devuelven `True` (φ es isomorfismo en la implementación base, Sección 3.3).
- **Dado** `clases_laterales_kernel()`, **cuando** se cuenta el número de clases, **entonces** coincide con `len(imagen())` — es la verificación operacional del Primer Teorema de Isomorfismo (`G/ker(φ) ≅ Im(φ)`, Demostración 3 del documento de contexto) sin necesidad de construir el isomorfismo `f` explícitamente en código.
- **Dado** una tabla φ custom que mapea dos gestos distintos a la misma acción (p. ej. `G1→A1, G3→A1`), **cuando** se llama `kernel()` y `clases_laterales_kernel()`, **entonces** el kernel deja de ser trivial y aparece una clase lateral con más de un elemento — este es el caso de prueba que ejercita el análisis "no trivial" mencionado como variante enriquecida en la Sección 3.4 del documento de contexto.
- **Dado** el script `analisis.py`, **cuando** se ejecuta con `python -m src.algebra.analisis` en una máquina sin webcam, **entonces** termina exitosamente e imprime el reporte completo (US-5 literal).

## 5. Casos borde

- Tabla φ custom con una clave repetida o faltante → `HOM-FR-001` exige fallo explícito en el constructor, no un `KeyError` tardío al primer `aplicar()`.
- Tabla φ custom que no es función (no aplica: un `dict` de Python garantiza que cada clave tiene un único valor, así que "no función" no es un caso alcanzable — se documenta aquí solo para dejar constancia de que no hace falta validarlo aparte).
- `imagen()` cuando la tabla φ es constante (todos los gestos mapean a `A_E`): `es_sobreyectiva()` debe devolver `False` y `kernel()` debe devolver los 6 elementos de G — caso extremo útil como test adicional de robustez de la lógica de conjuntos.

## 6. No objetivos de este módulo

- No decide *qué acción del sistema operativo* corresponde a cada `Accion` en términos de efecto real (`osascript`/`amixer`) — eso es 007.
- No calcula el isomorfismo `f : G/ker(φ) → Im(φ)` de forma explícita en código; el Primer Teorema de Isomorfismo se verifica *operacionalmente* (mismo cardinal de clases laterales e imagen — ver criterios de aceptación) y se demuestra *formalmente* en el reporte escrito (Sección 8, Demostración 3 del documento de contexto), no en runtime.
