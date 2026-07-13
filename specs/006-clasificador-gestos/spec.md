# Spec 006 — Clasificador de Gestos + Estabilizador

**Módulo:** `src/clasificador/gestos.py`, `src/clasificador/estabilizador.py`
**Depende de:** [005-filtro-ema](../005-filtro-ema/spec.md), [001-grupo-algebraico](../001-grupo-algebraico/spec.md) (usa el enum `Gesto`).
**Consumido por:** [007-ejecutor-acciones](../007-ejecutor-acciones/spec.md) (a través de φ, módulo 002), [008-visualizacion](../008-visualizacion/spec.md).
**Cubre:** US-1, US-3, US-6 de [000-overview](../000-overview/spec.md); SC-G01, SC-G03.

---

## 1. Propósito

Convertir 21 landmarks suavizados en un elemento `g ∈ G` (clasificación geométrica por dedos levantados), y decidir *cuándo* ese gesto está lo bastante sostenido como para considerarse una intención real del usuario (debounce), disparando la confirmación una sola vez por sostenimiento.

Este es el módulo con más superficie de ambigüedad del proyecto — la geometría de la mano es continua, G es discreto — por eso tiene la especificación más detallada de casos borde de todo el pipeline.

## 2. Contrato de interfaz

**Entradas:** `coords: list[tuple[float,float,float]]` (21 landmarks suavizados, salida de 005).

**Salidas:**

```python
def dedos_levantados(coords: list) -> list[bool]:  # [pulgar, indice, medio, anular, menique]

def clasificar_gesto(coords: list) -> Gesto:  # usa el enum Gesto de 001

class EstabilizadorGesto:
    def __init__(self, frames_estables: int = 10): ...
    def actualizar(self, gesto_nuevo: Gesto) -> Gesto | None:
        """None si aún no se confirma; Gesto si se acaba de confirmar (edge, no nivel)."""
```

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| CLA-FR-001 | `dedos_levantados()` DEBE comparar, para índice/medio/anular/meñique, la coordenada `y` de la punta contra la del MCP (punta con `y` menor = levantado, porque `y` crece hacia abajo en la imagen). |
| CLA-FR-002 | Para el pulgar, DEBE comparar la coordenada `x` (no `y`) de la punta contra el MCP — su movimiento natural es lateral (Sección 7.3 del documento de contexto). |
| CLA-FR-003 | `clasificar_gesto()` DEBE mapear los 5 booleanos a exactamente uno de `{G3, G1, G2, G4, G5, E}` según la tabla de la Sección 4.5 del documento de contexto. |
| CLA-FR-004 | Cualquier combinación de dedos que no calce con ninguna de las 5 reglas explícitas DEBE clasificarse como `E`, nunca lanzar excepción ni devolver `None` (FR-005 de la spec original). |
| CLA-FR-005 | `EstabilizadorGesto.actualizar()` DEBE requerir `frames_estables` llamadas consecutivas con el mismo gesto antes de confirmarlo. |
| CLA-FR-006 | Una vez confirmado un gesto, `actualizar()` DEBE devolver `None` en las llamadas subsiguientes mientras el gesto siga siendo el mismo (disparo único, no repetido) — resuelve Q1 de `000-overview`. |
| CLA-FR-007 | Si el gesto cambia (incluso a `E`) y luego vuelve al gesto anterior, el contador y la bandera de disparo DEBEN reiniciarse — permite repetir la misma acción volviendo a pasar por `E` (o por cualquier otro gesto) entremedio. |

## 4. Criterios de aceptación

- **Dado** landmarks sintéticos donde índice/medio/anular/meñique tienen `y_punta < y_mcp` es falso para todos (todos "abajo"), **cuando** se llama `clasificar_gesto()`, **entonces** el resultado es `Gesto.G3` (puño).
- **Dado** landmarks sintéticos con solo el índice arriba, **entonces** `Gesto.G1`.
- **Dado** landmarks sintéticos con índice y medio arriba (y anular/meñique abajo), **entonces** `Gesto.G2`.
- **Dado** landmarks sintéticos con los 5 dedos arriba (pulgar con `x_punta < x_mcp`), **entonces** `Gesto.G4`.
- **Dado** landmarks sintéticos con solo el pulgar activo, **entonces** `Gesto.G5`.
- **Dado** una combinación ambigua no cubierta (p. ej. solo el meñique arriba), **entonces** `Gesto.E` (CLA-FR-004) — este es un caso de prueba explícito, no un "resto" implícito.
- **Dado** un `EstabilizadorGesto(frames_estables=10)`, **cuando** se llama `actualizar(G1)` 9 veces, **entonces** las 9 llamadas devuelven `None`.
- **Dado** el mismo estabilizador, **cuando** se llama `actualizar(G1)` una décima vez consecutiva, **entonces** esa llamada devuelve `Gesto.G1` (confirmación, borde de subida).
- **Dado** el mismo estabilizador ya confirmado, **cuando** se sigue llamando `actualizar(G1)` (llamadas 11, 12, ...), **entonces** todas devuelven `None` (CLA-FR-006, disparo único).
- **Dado** el estabilizador confirmado en `G1`, **cuando** se llama `actualizar(E)` una vez y luego `actualizar(G1)` 10 veces más, **entonces** vuelve a confirmar `G1` en la décima (CLA-FR-007).

## 5. Casos borde — clasificación geométrica

- **Mano rotada / no de frente a cámara:** la heurística punta-vs-MCP asume una orientación aproximadamente frontal. Con la mano de perfil, la comparación de eje puede volverse ambigua para varios dedos a la vez. **Decisión:** no se corrige geométricamente en el MVP (requeriría normalización 3D con el landmark `z`, fuera de alcance); se documenta como limitación de uso (Sección 11 del documento de contexto) y se acota el caso de prueba de campo a "mano de frente a la cámara".
- **Landmarks con valores en el borde exacto (`y_punta == y_mcp`):** la comparación estricta (`<`) clasifica ese dedo como "no levantado". Es una decisión determinista, no requiere epsilon adicional porque en la práctica MediaPipe rara vez entrega igualdad exacta en floats.
- **Frame sin mano (landmarks `None` desde 005/004):** `clasificar_gesto()` no se llama en absoluto en ese frame — es responsabilidad de 009 (orquestación) tratar "sin mano" como gesto `E` directamente sin invocar este módulo, o invocar `EstabilizadorGesto.actualizar(Gesto.E)` explícitamente. Debe quedar una única convención fijada en 009, no ambigua entre los dos módulos.

## 6. Casos borde — estabilización / debounce

- **Gesto que oscila frame a frame entre dos valores (p. ej. G1, G2, G1, G2... por detección ruidosa cerca del límite):** nunca alcanza `frames_estables` consecutivos de ninguno de los dos, por lo que nunca se confirma nada — comportamiento correcto por diseño (evita disparos espurios), pero es la razón por la que 005 (filtro EMA) debe estar bien calibrado antes de evaluar SC-G01: un α mal elegido puede hacer que gestos válidos nunca se estabilicen.
- **Reinicio del estabilizador al perder y recuperar la mano:** si `EstabilizadorGesto` no se reinicia cuando la mano se pierde y reaparece, el contador podría arrastrar estado de una sesión de gesto anterior no relacionada. **Decisión:** 009 debe llamar `actualizar(Gesto.E)` (o un método `reset()` equivalente, a decidir junto con la implementación) cuando 004 devuelve `None`, análogo a EMA-FR-003 en 005 — mismo patrón de responsabilidad de orquestación.

## 7. No objetivos de este módulo

- No ejecuta ninguna acción de sistema (eso es φ + 007).
- No dibuja nada en pantalla (eso es 008, que sí necesita leer `Gesto` para elegir colores/etiquetas).
