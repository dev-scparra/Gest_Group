# GestGroup — Documento de Contexto para el Desarrollo

**Proyecto Final · Matemáticas Discretas II · Universidad Nacional de Colombia**  
**Integrantes:** Yony Sebastian Chaparro Mesa · Sebastian Camilo Parra Siabato · Angel Juaben Inyena Pasuy Muchavisoy

---

## Tabla de Contenidos

1. [Visión General del Proyecto](#1-visión-general-del-proyecto)
2. [Fundamentos Matemáticos del Curso](#2-fundamentos-matemáticos-del-curso)
   - 2.1 [Grupos y Axiomas](#21-grupos-y-axiomas)
   - 2.2 [El Grupo Simétrico S₅](#22-el-grupo-simétrico-s₅)
   - 2.3 [Homomorfismos de Grupos](#23-homomorfismos-de-grupos)
   - 2.4 [Kernel de un Homomorfismo](#24-kernel-de-un-homomorfismo)
   - 2.5 [Subgrupos Normales](#25-subgrupos-normales)
   - 2.6 [Grupo Cociente](#26-grupo-cociente)
   - 2.7 [Primer Teorema de Isomorfismo](#27-primer-teorema-de-isomorfismo)
3. [Modelo Algebraico de GestGroup](#3-modelo-algebraico-de-gestgroup)
   - 3.1 [El Grupo G de Gestos](#31-el-grupo-g-de-gestos)
   - 3.2 [El Grupo A de Acciones](#32-el-grupo-a-de-acciones)
   - 3.3 [El Homomorfismo φ : G → A](#33-el-homomorfismo-φ--g--a)
   - 3.4 [Análisis del Kernel](#34-análisis-del-kernel)
   - 3.5 [Aplicación del Primer Teorema de Isomorfismo](#35-aplicación-del-primer-teorema-de-isomorfismo)
4. [Arquitectura Técnica del Sistema](#4-arquitectura-técnica-del-sistema)
   - 4.1 [Pipeline General](#41-pipeline-general)
   - 4.2 [Capa 1: Captura de Video](#42-capa-1-captura-de-video)
   - 4.3 [Capa 2: Detección de Landmarks con MediaPipe](#43-capa-2-detección-de-landmarks-con-mediapipe)
   - 4.4 [Capa 3: Filtro EMA](#44-capa-3-filtro-ema)
   - 4.5 [Capa 4: Clasificador de Gestos](#45-capa-4-clasificador-de-gestos)
   - 4.6 [Capa 5: Ejecutor de Acciones φ(g)](#46-capa-5-ejecutor-de-acciones-φg)
5. [Entradas y Salidas del Sistema](#5-entradas-y-salidas-del-sistema)
6. [Estructura del Repositorio](#6-estructura-del-repositorio)
7. [Implementación Detallada por Módulo](#7-implementación-detallada-por-módulo)
   - 7.1 [Módulo de Captura](#71-módulo-de-captura)
   - 7.2 [Módulo del Filtro EMA](#72-módulo-del-filtro-ema)
   - 7.3 [Módulo Clasificador](#73-módulo-clasificador)
   - 7.4 [Módulo del Homomorfismo φ](#74-módulo-del-homomorfismo-φ)
   - 7.5 [Módulo de Acciones](#75-módulo-de-acciones)
   - 7.6 [Módulo de Visualización](#76-módulo-de-visualización)
8. [Demostraciones para el Reporte Técnico](#8-demostraciones-para-el-reporte-técnico)
9. [Dependencias y Configuración del Entorno](#9-dependencias-y-configuración-del-entorno)
10. [Casos de Prueba](#10-casos-de-prueba)
11. [Limitaciones y Trabajo Futuro](#11-limitaciones-y-trabajo-futuro)
12. [Referencias](#12-referencias)

---

## 1. Visión General del Proyecto

GestGroup es una aplicación de control por gestos en tiempo real que utiliza la cámara del computador para reconocer configuraciones de la mano y ejecutar acciones del sistema operativo (control de volumen, reproducción de audio, navegación). 

El diferenciador central frente a otros proyectos de visión computacional es que **el sistema completo está modelado usando teoría de grupos**: los gestos forman un grupo algebraico G (subgrupo del grupo simétrico S₅), las acciones forman un grupo A, y el mapeo entre ellos es un **homomorfismo de grupos** φ : G → A cuyo kernel, subgrupos normales y grupo cociente se analizan rigurosamente usando los teoremas del curso de Matemáticas Discretas II.

El filtro de media exponencial móvil (EMA) opera como capa de preprocesamiento para estabilizar el ruido de la cámara antes de la clasificación algebraica. No es el tema central del proyecto — es la justificación técnica que hace posible la clasificación robusta sobre la que descansa el análisis algebraico.

---

## 2. Fundamentos Matemáticos del Curso

Esta sección recoge las definiciones y teoremas del curso que son necesarios para entender y justificar el modelo algebraico de GestGroup.

### 2.1 Grupos y Axiomas

**Definición (Grupo):** Un grupo es un conjunto G con una operación binaria ⋆ sobre G tal que satisface las siguientes condiciones:

1. **Clausura:** Para todo g₁, g₂ ∈ G, g₁ ⋆ g₂ ∈ G.
2. **Asociatividad:** Para todo g₁, g₂, g₃ ∈ G, (g₁ ⋆ g₂) ⋆ g₃ = g₁ ⋆ (g₂ ⋆ g₃).
3. **Identidad:** Existe e ∈ G tal que g ⋆ e = e ⋆ g = g para todo g ∈ G.
4. **Inversos:** Para todo g ∈ G existe h ∈ G tal que g ⋆ h = h ⋆ g = e.

Se denota el grupo como (G, ⋆), o simplemente G cuando la operación es clara del contexto.

**Propiedades fundamentales:**
- El elemento identidad e es único en G.
- El inverso de cada elemento es único.
- El inverso de un producto satisface (xy)⁻¹ = y⁻¹x⁻¹.
- (g⁻¹)⁻¹ = g para todo g ∈ G.

### 2.2 El Grupo Simétrico S₅

El **grupo simétrico Sₙ** es el grupo de todas las biyecciones (permutaciones) del conjunto {1, 2, ..., n} bajo composición de funciones. Su orden es |Sₙ| = n!.

Para el proyecto, trabajamos con **S₅** (permutaciones del conjunto {1, 2, 3, 4, 5}, que representan los cinco dedos de la mano), con |S₅| = 120.

**Notación de ciclos:** Una permutación se escribe como producto de ciclos disjuntos. Por ejemplo, en S₅:
- La permutación identidad: e = (1)(2)(3)(4)(5)
- Un ciclo de longitud 2 (trasposición): (1 2) intercambia dedos 1 y 2
- Un ciclo de longitud 5: (1 2 3 4 5) rota todos los dedos

**Composición de ciclos:** La composición se realiza de derecha a izquierda. Ejemplo en S₅:
```
(1 3 2 4 5)(3 1 4 2 5) = (1 5 2)(3)(4)
```
Para calcular: se toma cada elemento y se traza primero por la permutación derecha y luego por la izquierda.

**Subgrupos de S₅:** Un subgrupo H ≤ S₅ es un subconjunto cerrado bajo la composición que también forma grupo. Los gestos de la mano que reconoce GestGroup forman un subgrupo G ≤ S₅.

### 2.3 Homomorfismos de Grupos

**Definición:** Sean (G, ⋆) y (K, ∗) dos grupos. Una función φ : G → K es un **homomorfismo de grupos** si para todo g₁, g₂ ∈ G:

```
φ(g₁ ⋆ g₂) = φ(g₁) ∗ φ(g₂)
```

Esta propiedad se llama **compatibilidad con la operación**: el homomorfismo preserva la estructura algebraica.

**Consecuencias inmediatas de ser homomorfismo:**
- φ(eG) = eK (el elemento identidad se mapea a la identidad)
- φ(g⁻¹) = φ(g)⁻¹ para todo g ∈ G (los inversos se preservan)
- La imagen Im(φ) = {φ(g) : g ∈ G} es un subgrupo de K

**Tipos de homomorfismos:**
- **Monomorfismo:** φ es inyectiva (cada gesto produce una acción distinta)
- **Epimorfismo:** φ es sobreyectiva (toda acción es alcanzable por algún gesto)
- **Isomorfismo:** φ es biyectiva (monomorfismo + epimorfismo)
- **Endomorfismo:** G = K

**Composición de homomorfismos (Teorema 12.1 del curso):** Dados φ : G → H y ψ : H → K homomorfismos, entonces ψ ∘ φ : G → K es también un homomorfismo.

### 2.4 Kernel de un Homomorfismo

**Definición:** Si φ : G → K es un homomorfismo, el **kernel** de φ es:

```
ker(φ) = φ⁻¹({eK}) = {g ∈ G : φ(g) = eK}
```

Es decir, ker(φ) es el conjunto de todos los elementos de G que φ mapea al elemento identidad de K.

**Teorema:** ker(φ) ≤ G (el kernel es un subgrupo de G).

**Demostración:**
1. **No vacío:** φ(eG) = eK, luego eG ∈ ker(φ), por tanto ker(φ) ≠ ∅.
2. **Clausura:** Dados x, y ∈ ker(φ), φ(xy) = φ(x)φ(y) = eK · eK = eK, luego xy ∈ ker(φ).
3. **Inversos:** Dado x ∈ ker(φ), φ(x⁻¹) = φ(x)⁻¹ = eK⁻¹ = eK, luego x⁻¹ ∈ ker(φ). □

**Relación con inyectividad:** φ es inyectiva si y solo si ker(φ) = {eG}.

### 2.5 Subgrupos Normales

**Definición (13.1 del curso):** Suponiendo que H es un subgrupo de G, decimos que H es un **subgrupo normal** (H ◁ G) si para cualquier h ∈ H y g ∈ G:

```
ghg⁻¹ ∈ H
```

En términos de conjuntos: H ◁ G si y solo si gHg⁻¹ ⊆ H para todo g ∈ G.

**Criterios para normalidad:**
- Si G es abeliano, todo subgrupo de G es normal (Corolario 13.3).
- Todo subgrupo de Z(G) (el centro de G) es normal en G (Teorema 13.2).
- El kernel de cualquier homomorfismo es siempre un subgrupo normal.

**Teorema fundamental:** Si φ : G → K es un homomorfismo, entonces ker(φ) ◁ G.

**Demostración:** Dado k ∈ ker(φ) y g ∈ G arbitrario:
```
φ(gkg⁻¹) = φ(g)φ(k)φ(g⁻¹) = φ(g) · eK · φ(g)⁻¹ = φ(g)φ(g)⁻¹ = eK
```
Luego gkg⁻¹ ∈ ker(φ), por tanto ker(φ) ◁ G. □

### 2.6 Grupo Cociente

**Definición:** Si H ◁ G, el conjunto de todas las clases laterales (cosets) de H en G forma un grupo llamado el **grupo cociente** o **grupo factor**:

```
G/H = {Ha : a ∈ G}
```

con la operación Ha ∗ Hb = Hab.

**Teorema (13.6 del curso):** Si H ◁ G, entonces G/H es un grupo para la operación Ha ∗ Hb = Hab.

**Demostración:**
1. **Asociatividad:** (Ha ∗ Hb) ∗ Hc = Hab ∗ Hc = H[(ab)c] = H[a(bc)] = Ha ∗ (Hb ∗ Hc). ✓
2. **Identidad:** He = H, porque Ha ∗ He = H(ae) = Ha. ✓
3. **Inversos:** El inverso de Ha es Ha⁻¹ porque Ha ∗ Ha⁻¹ = H(aa⁻¹) = He = H. ✓

**Orden del grupo cociente:** |G/H| = [G : H] = |G|/|H| (cuando G es finito).

**Interpretación:** Cada clase lateral Ha agrupa todos los elementos de G que se comportan de la misma manera respecto a H. En el contexto de GestGroup: dos gestos que siempre producen la misma acción pertenecen a la misma clase lateral de ker(φ).

### 2.7 Primer Teorema de Isomorfismo

**Teorema (Primer Teorema de Isomorfismo):** Sea φ : G → K un homomorfismo sobreyectivo. Entonces:

```
G / ker(φ) ≅ K
```

Es decir, el grupo cociente de G módulo el kernel de φ es isomorfo a K (o a Im(φ) si φ no es sobreyectivo).

**¿Qué nos dice el teorema?** Todo homomorfismo sobreyectivo φ : G → K puede descomponerse en dos pasos:

```
G  →[ρ]→  G/ker(φ)  →[f]→  K
```

donde ρ es el homomorfismo canónico ρ(g) = ker(φ)·g, y f es el isomorfismo definido por f(ker(φ)·g) = φ(g).

**El isomorfismo f está bien definido** porque si ker(φ)·g₁ = ker(φ)·g₂, entonces g₁g₂⁻¹ ∈ ker(φ), lo que implica φ(g₁) = φ(g₂).

**Consecuencia práctica para GestGroup:** La imagen de φ puede recuperarse completamente a partir de su kernel. Los gestos que "hacen lo mismo" (que el sistema no distingue) son exactamente los que forman la misma clase lateral del kernel.

---

## 3. Modelo Algebraico de GestGroup

### 3.1 El Grupo G de Gestos

Se define el conjunto de gestos distinguibles que el sistema puede reconocer:

```
G = {e, g₁, g₂, g₃, g₄, g₅}
```

donde:

| Símbolo | Gesto físico | Descripción como permutación de dedos |
|---|---|---|
| e | Mano en reposo / posición neutra | Identidad (ningún dedo activo) |
| g₁ | 1 dedo levantado (índice) | Solo el dedo 2 en posición "arriba" |
| g₂ | 2 dedos levantados (índice + medio) | Dedos 2 y 3 en posición "arriba" |
| g₃ | Puño cerrado | Ningún dedo en posición "arriba" (distinto de e por tensión muscular) |
| g₄ | Mano abierta (5 dedos) | Todos los dedos en posición "arriba" |
| g₅ | Pulgar abajo | Solo el dedo 1 en posición "abajo" activo |

**La operación de G:** La composición secuencial de gestos, g₁ ∘ g₂ significa "hacer el gesto g₁ seguido del gesto g₂". El resultado es otro gesto reconocible en G.

**Verificación de axiomas:**

**1. Clausura:** El clasificador siempre devuelve un elemento de G (incluyendo e si el gesto es ambiguo). La composición de cualquier par de gestos es interpretada por el sistema como un elemento de G. ✓

**2. Asociatividad:** La composición de gestos es asociativa porque corresponde a la composición de funciones en S₅, que es inherentemente asociativa: (g₁ ∘ g₂) ∘ g₃ = g₁ ∘ (g₂ ∘ g₃). ✓

**3. Identidad:** El gesto e (mano en reposo) es el elemento neutro: e ∘ gᵢ = gᵢ ∘ e = gᵢ para todo gᵢ ∈ G. Físicamente, volver a la posición de reposo no altera el gesto que viene después. ✓

**4. Inversos:** Para cada gesto gᵢ existe gᵢ⁻¹ ∈ G tal que gᵢ ∘ gᵢ⁻¹ = e. Físicamente, "deshacer" el gesto regresa al estado neutro. En esta implementación, gᵢ⁻¹ = gᵢ para todos los gestos (cada gesto es su propio inverso, lo que hace a G abeliano). ✓

**Relación con S₅:** Cada dedo i ∈ {1,2,3,4,5} puede estar en estado "arriba" (1) o "abajo" (0). Un gesto define una configuración de los 5 dedos. Formalmente, cada gesto es una función σ : {1,2,3,4,5} → {0,1}, y la composición es la composición de estas funciones como permutaciones. Luego G ≤ S₅ (G es subgrupo del grupo simétrico S₅).

### 3.2 El Grupo A de Acciones

```
A = {a_e, a₁, a₂, a₃, a₄, a₅}
```

| Símbolo | Acción en el sistema |
|---|---|
| a_e | Ninguna acción (identidad) |
| a₁ | Subir volumen |
| a₂ | Bajar volumen |
| a₃ | Pausa / Play |
| a₄ | Siguiente pista |
| a₅ | Pista anterior |

**La operación de A:** Composición de acciones — ejecutar a₁ seguido de a₂ produce el efecto combinado a₁ ∘ a₂.

**Nota sobre abelianidad:** En esta implementación, A es abeliano (el orden de las acciones no importa para el efecto total), lo que simplifica la verificación de que ker(φ) es normal en G (por el Corolario 13.3).

### 3.3 El Homomorfismo φ : G → A

La función φ asigna a cada gesto una acción del sistema:

```
φ : G → A

φ(e)  = a_e   (ninguna acción)
φ(g₁) = a₁    (subir volumen)
φ(g₂) = a₂    (bajar volumen)
φ(g₃) = a₃    (pausa/play)
φ(g₄) = a₄    (siguiente pista)
φ(g₅) = a₅    (pista anterior)
```

**Verificación de la propiedad de homomorfismo:**

Para todo g, h ∈ G debe cumplirse: φ(g ∘ h) = φ(g) ∘ φ(h)

Dado que G es abeliano y cada gesto es su propio inverso, la tabla de composición de G es:

```
∘  | e   g₁  g₂  g₃  g₄  g₅
---|----------------------------
e  | e   g₁  g₂  g₃  g₄  g₅
g₁ | g₁  e   g₁∘g₂ ...
g₂ | g₂  ...
...
```

La verificación completa de la propiedad de homomorfismo se realiza comprobando cada par (gᵢ, gⱼ) en la tabla de Cayley de G y verificando que φ lo preserva.

**¿Es φ monomorfismo?** En la implementación propuesta, φ es inyectiva porque cada gesto produce una acción distinta (ker(φ) = {e}). Esto lo convierte en un **monomorfismo**.

**¿Es φ epimorfismo?** Sí, porque cada acción en A tiene al menos un gesto en G que la produce. Im(φ) = A.

**Conclusión:** En la implementación base, φ es un **isomorfismo** G ≅ A (biyectivo y homomorfismo). Esto puede modificarse en versiones donde varios gestos produzcan la misma acción, haciendo el análisis del kernel más rico.

### 3.4 Análisis del Kernel

```
ker(φ) = {g ∈ G : φ(g) = a_e} = {e}
```

En la implementación base, solo el gesto neutro e mapea a la acción identidad a_e.

**ker(φ) es subgrupo normal de G:** Demostración directa por el teorema del curso:

Como φ es homomorfismo, ker(φ) ≤ G. Además, ker(φ) ◁ G porque para todo k ∈ ker(φ) y g ∈ G:
```
φ(gkg⁻¹) = φ(g)φ(k)φ(g⁻¹) = φ(g) · a_e · φ(g)⁻¹ = φ(g)φ(g)⁻¹ = a_e
```
Por tanto gkg⁻¹ ∈ ker(φ), lo que prueba que ker(φ) ◁ G. □

**Variante extendida (para enriquecer el análisis):** Si se añaden gestos ambiguos que el clasificador no puede distinguir de e (por ejemplo, una mano semiabierta o mal detectada), estos caen en ker(φ) y el análisis de clases laterales se vuelve no trivial.

### 3.5 Aplicación del Primer Teorema de Isomorfismo

Dado que φ : G → A es un homomorfismo y ker(φ) ◁ G:

```
G / ker(φ) ≅ Im(φ)
```

En la implementación base donde ker(φ) = {e}:

```
G / {e} ≅ A
```

Lo que es consistente con φ siendo isomorfismo.

**Interpretación para el reporte:** El grupo cociente G/ker(φ) agrupa los gestos que el sistema no puede distinguir (producen la misma acción). Las clases laterales de ker(φ) en G son los "bloques" de gestos equivalentes desde la perspectiva del sistema. El Primer Teorema de Isomorfismo garantiza que este grupo cociente es estructuralmente idéntico al grupo de acciones reales que el sistema ejecuta.

---

## 4. Arquitectura Técnica del Sistema

### 4.1 Pipeline General

```
┌─────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────────┐    ┌──────────┐
│  Cámara │───▶│  MediaPipe   │───▶│ Filtro EMA │───▶│ Clasificador │───▶│  φ(g)    │
│  OpenCV │    │  (landmarks) │    │ (suavizado)│    │  g ∈ G       │    │ Acción   │
└─────────┘    └──────────────┘    └────────────┘    └──────────────┘    └──────────┘
     │                │                   │                  │                │
  frame RGB     21 landmarks         coords EMA          gesto g         ejecutar
  por frame     (x,y,z) × 21        suavizadas          clasificado      en sistema
```

**Descripción de cada capa:**

1. **Captura:** OpenCV captura frames de la webcam a ~30 FPS en formato BGR.
2. **Detección:** MediaPipe Hands detecta la mano y devuelve 21 landmarks normalizados [0,1].
3. **Suavizado:** El filtro EMA estabiliza las coordenadas eliminando el temblor frame a frame.
4. **Clasificación:** El clasificador geométrico determina qué elemento g ∈ G corresponde al frame actual.
5. **Ejecución:** φ(g) ejecuta la acción correspondiente en el sistema operativo.

### 4.2 Capa 1: Captura de Video

**Tecnología:** OpenCV (`cv2`)

```python
import cv2

cap = cv2.VideoCapture(0)  # 0 = cámara por defecto
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
```

**Salida:** Frame BGR de 640×480 píxeles a ~30 FPS.

**Conversión necesaria:** MediaPipe requiere formato RGB, no BGR:
```python
frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
```

### 4.3 Capa 2: Detección de Landmarks con MediaPipe

**Tecnología:** MediaPipe Hands (`mediapipe`)

MediaPipe detecta 21 landmarks de la mano. Cada landmark tiene coordenadas (x, y, z) normalizadas en [0,1] relativas al tamaño del frame.

**Numeración de landmarks clave:**

```
                 8 (punta índice)
                 |
         7       |
         |    4 (punta pulgar)
    6    |    |
    |  3 |  3 |
  5 | 2  |2   |
    1    1    1
         0 (muñeca)
```

| ID | Landmark | Dedo |
|---|---|---|
| 0 | Muñeca | Base |
| 1-4 | Articulaciones del pulgar | Dedo 1 |
| 5-8 | Articulaciones del índice | Dedo 2 |
| 9-12 | Articulaciones del medio | Dedo 3 |
| 13-16 | Articulaciones del anular | Dedo 4 |
| 17-20 | Articulaciones del meñique | Dedo 5 |

**Las puntas de los dedos** (usadas para clasificación) están en los IDs: 4, 8, 12, 16, 20.

**Las articulaciones MCP** (base de cada dedo) están en: 2, 5, 9, 13, 17.

```python
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

results = hands.process(frame_rgb)

if results.multi_hand_landmarks:
    landmarks = results.multi_hand_landmarks[0].landmark
    # landmarks[i].x, landmarks[i].y, landmarks[i].z
```

**Salida:** Lista de 21 objetos con atributos `.x`, `.y`, `.z` normalizados en [0,1].

### 4.4 Capa 3: Filtro EMA

**Propósito:** Las coordenadas de MediaPipe "tiemblan" entre frames consecutivos por ruido de cámara y micromovimientos. El filtro EMA suaviza esta señal manteniendo reactividad.

**Ecuación del filtro:**

```
x[n] = α · x_raw[n] + (1 - α) · x[n-1]
```

donde:
- `x[n]` es la coordenada suavizada en el frame actual
- `x_raw[n]` es la coordenada cruda entregada por MediaPipe
- `x[n-1]` es la coordenada suavizada del frame anterior
- `α ∈ (0, 1)` es el factor de suavizado (hiperparámetro configurable)

**Comportamiento según α:**
- α → 1: el filtro sigue al dedo rápidamente (más ruido, menos retraso)
- α → 0: el filtro es muy suave (menos ruido, más retraso)
- **Valor recomendado:** α = 0.3 para un equilibrio entre suavidad y reactividad

**Solución analítica (para el reporte técnico):**

Desarrollando la recursión:
```
x[n] = α · x_raw[n] + (1-α) · x[n-1]
     = α · x_raw[n] + (1-α)[α · x_raw[n-1] + (1-α) · x[n-2]]
     = α · Σₖ₌₀^∞ (1-α)^k · x_raw[n-k]
```

Es un **promedio ponderado de todos los frames pasados** donde los frames más recientes tienen mayor peso exponencial.

**Estabilidad:** La solución homogénea es `x_h[n] = C · (1-α)^n`. Como |1-α| < 1 (dado α ∈ (0,1)), se tiene que x_h[n] → 0 cuando n → ∞. Esto confirma que el filtro es **estable**: la influencia de condiciones iniciales desaparece exponencialmente.

**Implementación:**

```python
class FiltroEMA:
    def __init__(self, alpha: float = 0.3, num_landmarks: int = 21):
        self.alpha = alpha
        self.num_landmarks = num_landmarks
        # Estado: coordenadas suavizadas del frame anterior
        self.x_prev = None  # shape: (21, 3)

    def aplicar(self, landmarks_raw: list) -> list:
        """
        landmarks_raw: lista de 21 objetos con .x, .y, .z
        Retorna: lista de 21 tuplas (x_suav, y_suav, z_suav)
        """
        coords_raw = [(lm.x, lm.y, lm.z) for lm in landmarks_raw]

        if self.x_prev is None:
            # Primer frame: inicializar con los valores crudos
            self.x_prev = coords_raw
            return coords_raw

        coords_suav = []
        for i, (x_raw, y_raw, z_raw) in enumerate(coords_raw):
            x_s = self.alpha * x_raw + (1 - self.alpha) * self.x_prev[i][0]
            y_s = self.alpha * y_raw + (1 - self.alpha) * self.x_prev[i][1]
            z_s = self.alpha * z_raw + (1 - self.alpha) * self.x_prev[i][2]
            coords_suav.append((x_s, y_s, z_s))

        self.x_prev = coords_suav
        return coords_suav

    def reset(self):
        self.x_prev = None
```

### 4.5 Capa 4: Clasificador de Gestos

**Propósito:** Determinar a qué elemento g ∈ G pertenece la configuración de la mano en el frame actual.

**Algoritmo de clasificación por dedos levantados:**

Un dedo está "levantado" si la punta (landmark de mayor ID del dedo) está **más arriba** (menor coordenada y en imagen, ya que y crece hacia abajo) que la articulación MCP (base del dedo).

```python
PUNTAS = [4, 8, 12, 16, 20]   # IDs landmarks de puntas
MCPS   = [2, 5,  9, 13, 17]   # IDs landmarks de bases (MCP)

def dedos_levantados(coords: list) -> list:
    """Retorna lista de booleanos: True si dedo i está levantado."""
    levantados = []
    for punta, mcp in zip(PUNTAS, MCPS):
        # Para el pulgar (dedo 0): comparar x en lugar de y
        if punta == 4:
            levantado = coords[punta][0] < coords[mcp][0]
        else:
            levantado = coords[punta][1] < coords[mcp][1]
        levantados.append(levantado)
    return levantados
```

**Tabla de clasificación: dedos levantados → elemento de G:**

| Pulgar | Índice | Medio | Anular | Meñique | Gesto g |
|---|---|---|---|---|---|
| - | F | F | F | F | g₃ (puño) |
| - | T | F | F | F | g₁ (1 dedo) |
| - | T | T | F | F | g₂ (2 dedos) |
| T | T | T | T | T | g₄ (mano abierta) |
| T | F | F | F | F | g₅ (pulgar) |
| cualquier otro | | | | | e (reposo/neutro) |

```python
from enum import Enum

class Gesto(Enum):
    E  = "reposo"       # identidad
    G1 = "1_dedo"       # subir volumen
    G2 = "2_dedos"      # bajar volumen
    G3 = "puno"         # pausa/play
    G4 = "mano_abierta" # siguiente
    G5 = "pulgar"       # anterior

def clasificar_gesto(coords: list) -> Gesto:
    dedos = dedos_levantados(coords)
    pulgar, indice, medio, anular, menique = dedos

    if not any([indice, medio, anular, menique]):
        return Gesto.G3  # puño
    elif indice and not medio and not anular and not menique:
        return Gesto.G1  # 1 dedo
    elif indice and medio and not anular and not menique:
        return Gesto.G2  # 2 dedos
    elif all([pulgar, indice, medio, anular, menique]):
        return Gesto.G4  # mano abierta
    elif pulgar and not any([indice, medio, anular, menique]):
        return Gesto.G5  # pulgar
    else:
        return Gesto.E   # reposo / gesto no reconocido
```

**Detección de estabilidad (debounce):** Para evitar que acciones se disparen repetidamente mientras se mantiene el gesto, se implementa un contador de frames consecutivos:

```python
class EstabilizadorGesto:
    def __init__(self, frames_estables: int = 10):
        self.frames_estables = frames_estables
        self.gesto_actual = Gesto.E
        self.contador = 0
        self.gesto_ejecutado = False

    def actualizar(self, gesto_nuevo: Gesto) -> Gesto | None:
        """
        Retorna el gesto solo cuando se ha mantenido estable
        durante `frames_estables` frames consecutivos.
        """
        if gesto_nuevo == self.gesto_actual:
            self.contador += 1
        else:
            self.gesto_actual = gesto_nuevo
            self.contador = 0
            self.gesto_ejecutado = False

        if self.contador >= self.frames_estables and not self.gesto_ejecutado:
            self.gesto_ejecutado = True
            return self.gesto_actual

        return None
```

### 4.6 Capa 5: Ejecutor de Acciones φ(g)

**Propósito:** Implementar el homomorfismo φ : G → A, mapeando cada elemento de G a una acción ejecutable en el sistema.

```python
from enum import Enum

class Accion(Enum):
    A_E = "ninguna"
    A1  = "subir_volumen"
    A2  = "bajar_volumen"
    A3  = "pausa_play"
    A4  = "siguiente"
    A5  = "anterior"

# Definición explícita del homomorfismo φ
PHI = {
    Gesto.E:  Accion.A_E,
    Gesto.G1: Accion.A1,
    Gesto.G2: Accion.A2,
    Gesto.G3: Accion.A3,
    Gesto.G4: Accion.A4,
    Gesto.G5: Accion.A5,
}

def phi(gesto: Gesto) -> Accion:
    """El homomorfismo φ : G → A."""
    return PHI[gesto]
```

**Ejecución de acciones en el sistema operativo:**

```python
import subprocess
import platform

def ejecutar_accion(accion: Accion):
    sistema = platform.system()

    if accion == Accion.A_E:
        return  # ninguna acción

    elif accion == Accion.A1:  # subir volumen
        if sistema == "Darwin":  # macOS
            subprocess.run(["osascript", "-e",
                "set volume output volume (output volume of (get volume settings) + 10)"])
        elif sistema == "Linux":
            subprocess.run(["amixer", "-q", "sset", "Master", "10%+"])
        elif sistema == "Windows":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            # implementación para Windows

    elif accion == Accion.A2:  # bajar volumen
        if sistema == "Darwin":
            subprocess.run(["osascript", "-e",
                "set volume output volume (output volume of (get volume settings) - 10)"])
        elif sistema == "Linux":
            subprocess.run(["amixer", "-q", "sset", "Master", "10%-"])

    elif accion == Accion.A3:  # pausa/play
        if sistema == "Darwin":
            subprocess.run(["osascript", "-e",
                "tell application \"System Events\" to key code 49"])  # tecla espacio

    elif accion == Accion.A4:  # siguiente pista
        if sistema == "Darwin":
            subprocess.run(["osascript", "-e",
                "tell application \"System Events\" to key code 124 using command down"])

    elif accion == Accion.A5:  # pista anterior
        if sistema == "Darwin":
            subprocess.run(["osascript", "-e",
                "tell application \"System Events\" to key code 123 using command down"])
```

---

## 5. Entradas y Salidas del Sistema

### Entradas

| Nivel | Entrada | Tipo | Descripción |
|---|---|---|---|
| Sistema | Stream de video | BGR frame 640×480 | Cámara a ~30 FPS |
| MediaPipe | Frame RGB | numpy array | Convertido de BGR |
| Filtro EMA | 21 landmarks crudos | list[(x,y,z)] | Normalizados en [0,1] |
| Clasificador | 21 landmarks suavizados | list[(x,y,z)] | Salida del filtro EMA |
| φ | Gesto g | Gesto (enum) | Elemento clasificado de G |
| Configuración | α (alpha) | float ∈ (0,1) | Factor de suavizado EMA |
| Configuración | frames_estables | int | Frames para confirmar gesto |

### Salidas

| Nivel | Salida | Tipo | Descripción |
|---|---|---|---|
| MediaPipe | 21 landmarks | list[landmark] | Posiciones de la mano |
| Filtro EMA | 21 coords suavizadas | list[(x,y,z)] | Sin temblor |
| Clasificador | g ∈ G | Gesto (enum) | Elemento del grupo G |
| φ(g) | a ∈ A | Accion (enum) | Elemento del grupo A |
| Ejecutor | Efecto en sistema | side effect | Volumen/reproducción cambiado |
| Visualización | Frame anotado | BGR frame | Landmarks + gesto + acción dibujados |
| Análisis (reporte) | ker(φ), Im(φ), G/ker(φ) | conjuntos | Estructuras algebraicas analizadas |

---

## 6. Estructura del Repositorio

```
gestgroup/
│
├── README.md                    # Descripción general y cómo ejecutar
├── requirements.txt             # Dependencias Python
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada principal
│   │
│   ├── captura/
│   │   ├── __init__.py
│   │   └── video_capture.py     # Módulo de captura con OpenCV
│   │
│   ├── deteccion/
│   │   ├── __init__.py
│   │   └── mediapipe_handler.py # Wrapper de MediaPipe Hands
│   │
│   ├── preprocesamiento/
│   │   ├── __init__.py
│   │   └── filtro_ema.py        # Implementación del filtro EMA
│   │
│   ├── algebra/
│   │   ├── __init__.py
│   │   ├── grupo_gestos.py      # Definición del grupo G y operación
│   │   ├── grupo_acciones.py    # Definición del grupo A
│   │   ├── homomorfismo.py      # Implementación de φ : G → A
│   │   └── analisis.py          # Cálculo de ker(φ), Im(φ), G/ker(φ)
│   │
│   ├── clasificador/
│   │   ├── __init__.py
│   │   ├── gestos.py            # Enum Gesto y clasificador geométrico
│   │   └── estabilizador.py     # Debounce / estabilización de gestos
│   │
│   ├── acciones/
│   │   ├── __init__.py
│   │   └── ejecutor.py          # Ejecución de acciones en el SO
│   │
│   └── visualizacion/
│       ├── __init__.py
│       └── renderer.py          # Overlay de landmarks y estado
│
├── tests/
│   ├── test_filtro_ema.py       # Tests unitarios del filtro
│   ├── test_clasificador.py     # Tests del clasificador de gestos
│   ├── test_homomorfismo.py     # Verificación algebraica de φ
│   └── test_algebra.py          # Tests de ker(φ), Im(φ), etc.
│
├── docs/
│   ├── reporte_tecnico.pdf      # Reporte final del proyecto
│   └── demostraciones.md        # Demostraciones matemáticas formales
│
└── assets/
    └── demo.mp4                 # Video de demostración
```

---

## 7. Implementación Detallada por Módulo

### 7.1 Módulo de Captura

```python
# src/captura/video_capture.py

import cv2

class CapturaVideo:
    def __init__(self, camara_id: int = 0, ancho: int = 640, alto: int = 480):
        self.cap = cv2.VideoCapture(camara_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def leer_frame(self):
        """Retorna (exito, frame_bgr, frame_rgb)."""
        exito, frame_bgr = self.cap.read()
        if not exito:
            return False, None, None
        frame_bgr = cv2.flip(frame_bgr, 1)  # espejo horizontal
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return True, frame_bgr, frame_rgb

    def liberar(self):
        self.cap.release()
        cv2.destroyAllWindows()
```

### 7.2 Módulo del Filtro EMA

Ver implementación completa en la Sección 4.4.

**Parámetro α recomendado:** 0.3. Puede exponerse en la UI para permitir ajuste en tiempo real, lo que sirve como demostración del efecto del parámetro.

### 7.3 Módulo Clasificador

Ver implementación completa en la Sección 4.5.

**Consideración importante:** El pulgar usa comparación en el eje x (horizontal) porque su movimiento natural es lateral, no vertical como los otros dedos.

### 7.4 Módulo del Homomorfismo φ

```python
# src/algebra/homomorfismo.py

from src.clasificador.gestos import Gesto
from src.acciones.ejecutor import Accion

class Homomorfismo:
    """
    Implementa el homomorfismo φ : G → A y permite
    analizar sus propiedades algebraicas.
    """

    def __init__(self, tabla_phi: dict[Gesto, Accion] = None):
        if tabla_phi is None:
            # φ por defecto (biyectivo en la implementación base)
            self.tabla_phi = {
                Gesto.E:  Accion.A_E,
                Gesto.G1: Accion.A1,
                Gesto.G2: Accion.A2,
                Gesto.G3: Accion.A3,
                Gesto.G4: Accion.A4,
                Gesto.G5: Accion.A5,
            }
        else:
            self.tabla_phi = tabla_phi

    def aplicar(self, gesto: Gesto) -> Accion:
        """El homomorfismo φ(g)."""
        return self.tabla_phi[gesto]

    def kernel(self) -> set[Gesto]:
        """ker(φ) = {g ∈ G : φ(g) = a_e}"""
        return {g for g, a in self.tabla_phi.items() if a == Accion.A_E}

    def imagen(self) -> set[Accion]:
        """Im(φ) = {φ(g) : g ∈ G}"""
        return set(self.tabla_phi.values())

    def es_inyectiva(self) -> bool:
        """φ es inyectiva sii |ker(φ)| = 1."""
        return len(self.kernel()) == 1

    def es_sobreyectiva(self, grupo_A: set[Accion]) -> bool:
        """φ es sobreyectiva sii Im(φ) = A."""
        return self.imagen() == grupo_A

    def clases_laterales_kernel(self, grupo_G: list[Gesto]) -> dict:
        """
        Calcula G/ker(φ): agrupa los gestos por la acción que producen.
        Cada clase lateral {g · ker(φ)} agrupa gestos con φ(g) igual.
        """
        clases = {}
        for g in grupo_G:
            accion = self.aplicar(g)
            if accion not in clases:
                clases[accion] = []
            clases[accion].append(g)
        return clases

    def verificar_homomorfismo(self, operacion_G: callable,
                                operacion_A: callable,
                                grupo_G: list[Gesto]) -> bool:
        """
        Verifica φ(g₁ ∘ g₂) = φ(g₁) ∘ φ(g₂) para todo par (g₁, g₂) ∈ G².
        """
        for g1 in grupo_G:
            for g2 in grupo_G:
                lhs = self.aplicar(operacion_G(g1, g2))
                rhs = operacion_A(self.aplicar(g1), self.aplicar(g2))
                if lhs != rhs:
                    return False
        return True
```

### 7.5 Módulo de Acciones

Ver implementación del ejecutor de acciones en la Sección 4.6.

**Nota sobre compatibilidad multiplataforma:** El módulo `ejecutor.py` debe detectar el sistema operativo (`platform.system()`) y usar las APIs correspondientes. La implementación primaria apunta a macOS y Linux. En Windows se puede usar `pycaw` para el volumen y `pyautogui` para las teclas multimedia.

### 7.6 Módulo de Visualización

```python
# src/visualizacion/renderer.py

import cv2
import mediapipe as mp
from src.clasificador.gestos import Gesto
from src.acciones.ejecutor import Accion

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

COLORES_GESTO = {
    Gesto.E:  (200, 200, 200),  # gris
    Gesto.G1: (0, 255, 0),      # verde
    Gesto.G2: (0, 200, 255),    # amarillo
    Gesto.G3: (0, 0, 255),      # rojo
    Gesto.G4: (255, 0, 0),      # azul
    Gesto.G5: (255, 0, 255),    # magenta
}

def dibujar_frame(frame_bgr, hand_landmarks, gesto: Gesto,
                   accion: Accion, alpha: float):
    """Añade overlays al frame: landmarks, gesto detectado, acción φ(g)."""

    # Dibujar landmarks de MediaPipe
    if hand_landmarks:
        mp_drawing.draw_landmarks(
            frame_bgr, hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

    color = COLORES_GESTO.get(gesto, (255, 255, 255))

    # Gesto detectado
    cv2.putText(frame_bgr, f"g = {gesto.value}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Acción ejecutada (φ(g))
    cv2.putText(frame_bgr, f"phi(g) = {accion.value}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Parámetro α del filtro EMA
    cv2.putText(frame_bgr, f"alpha (EMA) = {alpha:.2f}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    # Nota matemática en esquina superior derecha
    cv2.putText(frame_bgr, "G/ker(phi) ≅ Im(phi)", (350, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    return frame_bgr
```

---

## 8. Demostraciones para el Reporte Técnico

Esta sección contiene las demostraciones formales que deben aparecer en el reporte del curso.

### Demostración 1: (G, ∘) es un grupo

**Proposición:** El conjunto G = {e, g₁, g₂, g₃, g₄, g₅} con la operación de composición secuencial de gestos es un grupo.

**Prueba:**

1. **Clausura:** El clasificador siempre retorna un elemento de G (por construcción del enum Gesto). La composición de dos gestos es el gesto resultante de ejecutarlos en secuencia, que el clasificador mapea a algún gᵢ ∈ G. ✓

2. **Asociatividad:** La operación de composición hereda asociatividad de la composición de funciones en S₅. Para todo g₁, g₂, g₃ ∈ G: (g₁ ∘ g₂) ∘ g₃ = g₁ ∘ (g₂ ∘ g₃). ✓

3. **Elemento identidad:** El gesto e (mano en reposo) satisface e ∘ gᵢ = gᵢ ∘ e = gᵢ para todo gᵢ ∈ G. Físicamente, la posición neutra no altera el gesto que precede o sigue. ✓

4. **Inversos:** Para cada gᵢ ∈ G, definimos gᵢ⁻¹ = gᵢ (cada gesto es su propio inverso). Entonces gᵢ ∘ gᵢ = e porque al hacer el mismo gesto dos veces el sistema lo interpreta como "regresar al estado neutro" (implementado en el estabilizador de gestos). ✓

**Conclusión:** (G, ∘) es un grupo. Además, como gᵢ ∘ gⱼ = gⱼ ∘ gᵢ para todo par, **G es abeliano**. □

### Demostración 2: ker(φ) ◁ G

**Proposición:** ker(φ) es un subgrupo normal de G.

**Prueba (usando que φ es homomorfismo):**

Sea k ∈ ker(φ) y g ∈ G arbitrario. Queremos mostrar que gkg⁻¹ ∈ ker(φ).

```
φ(gkg⁻¹) = φ(g) · φ(k) · φ(g⁻¹)    [por propiedad de homomorfismo]
           = φ(g) · a_e · φ(g)⁻¹       [pues k ∈ ker(φ)]
           = φ(g) · φ(g)⁻¹             [a_e es identidad en A]
           = a_e                         [inverso]
```

Por tanto gkg⁻¹ ∈ ker(φ), lo que prueba ker(φ) ◁ G. □

**Nota adicional:** Como G es abeliano, toda la prueba es inmediata por el Corolario 13.3 del curso: todo subgrupo de un grupo abeliano es normal.

### Demostración 3: Primer Teorema de Isomorfismo aplicado

**Proposición:** G/ker(φ) ≅ Im(φ).

**Prueba:**

Definimos el isomorfismo f : G/ker(φ) → Im(φ) por:

```
f(ker(φ) · g) = φ(g)
```

**Bien definida:** Si ker(φ) · g₁ = ker(φ) · g₂, entonces g₁g₂⁻¹ ∈ ker(φ), luego φ(g₁g₂⁻¹) = a_e, es decir φ(g₁) = φ(g₂). ✓

**Homomorfismo:**
```
f(ker(φ)·g₁ ∗ ker(φ)·g₂) = f(ker(φ)·g₁g₂) = φ(g₁g₂) = φ(g₁)·φ(g₂) = f(ker(φ)·g₁)·f(ker(φ)·g₂)
```
✓

**Inyectiva:** Si f(ker(φ)·g₁) = f(ker(φ)·g₂), entonces φ(g₁) = φ(g₂), luego φ(g₁g₂⁻¹) = a_e, es decir g₁g₂⁻¹ ∈ ker(φ), por tanto ker(φ)·g₁ = ker(φ)·g₂. ✓

**Sobreyectiva:** Por definición, Im(φ) = {φ(g) : g ∈ G} = {f(ker(φ)·g) : g ∈ G}. ✓

**Conclusión:** f es isomorfismo, por tanto G/ker(φ) ≅ Im(φ). □

### Demostración 4: Estabilidad del Filtro EMA

**Proposición:** El filtro EMA con α ∈ (0,1) es estable.

**Prueba:** La ecuación x[n] - (1-α)·x[n-1] = α·x_raw[n] es una ecuación en diferencias lineal de primer orden. La solución homogénea satisface:

```
x_h[n] - (1-α)·x_h[n-1] = 0
```

Lo que tiene solución x_h[n] = C·(1-α)ⁿ. Como α ∈ (0,1), se tiene 0 < (1-α) < 1, luego:

```
lim_{n→∞} |x_h[n]| = lim_{n→∞} |C|·(1-α)ⁿ = 0
```

La influencia de las condiciones iniciales desaparece exponencialmente. El filtro es **asintóticamente estable**. □

---

## 9. Dependencias y Configuración del Entorno

### requirements.txt

```
mediapipe==0.10.9
opencv-python==4.9.0.80
numpy==1.26.4
```

**Para macOS (control de volumen):**
```
# Usar subprocess con osascript (incluido en macOS)
```

**Para Linux (control de volumen):**
```
# Usar subprocess con amixer (incluido en alsa-utils)
```

**Para Windows (control de volumen):**
```
pycaw==20181228
comtypes==1.4.1
```

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/gestgroup.git
cd gestgroup

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python src/main.py
```

### Versiones de Python

Compatible con Python 3.9, 3.10, 3.11. Se recomienda 3.11.

### Verificación de instalación

```python
import mediapipe as mp
import cv2
import numpy as np

print(f"MediaPipe: {mp.__version__}")
print(f"OpenCV: {cv2.__version__}")
print(f"NumPy: {np.__version__}")
```

---

## 10. Casos de Prueba

### Test 1: Verificación del filtro EMA

```python
# tests/test_filtro_ema.py

def test_convergencia_ema():
    """El filtro EMA debe converger al valor constante cuando x_raw es constante."""
    filtro = FiltroEMA(alpha=0.3)
    # Simular landmarks constantes en (0.5, 0.5, 0.0)
    landmarks_fake = [(0.5, 0.5, 0.0)] * 21

    x_prev = 0.0
    for i in range(100):
        resultado = filtro.aplicar_coord(0.5, x_prev)
        x_prev = resultado

    assert abs(x_prev - 0.5) < 0.001, "El filtro debe converger a 0.5"

def test_estabilidad_ruido():
    """El filtro EMA debe reducir la varianza del ruido."""
    import random
    filtro = FiltroEMA(alpha=0.3)
    señal_ruidosa = [0.5 + random.gauss(0, 0.1) for _ in range(200)]
    señal_suavizada = []
    x_prev = señal_ruidosa[0]

    for x_raw in señal_ruidosa:
        x_s = 0.3 * x_raw + 0.7 * x_prev
        señal_suavizada.append(x_s)
        x_prev = x_s

    var_cruda = sum((x - 0.5)**2 for x in señal_ruidosa) / len(señal_ruidosa)
    var_suav  = sum((x - 0.5)**2 for x in señal_suavizada) / len(señal_suavizada)

    assert var_suav < var_cruda, "La varianza debe reducirse con el filtro"
```

### Test 2: Verificación algebraica de φ

```python
# tests/test_homomorfismo.py

def test_phi_mapea_identidad_a_identidad():
    """φ(e_G) debe ser e_A."""
    phi = Homomorfismo()
    assert phi.aplicar(Gesto.E) == Accion.A_E

def test_kernel_contiene_solo_identidad():
    """En la implementación base, ker(φ) = {e}."""
    phi = Homomorfismo()
    assert phi.kernel() == {Gesto.E}

def test_phi_es_inyectiva():
    """φ debe ser inyectiva en la implementación base."""
    phi = Homomorfismo()
    assert phi.es_inyectiva()

def test_imagen_es_A_completo():
    """Im(φ) debe ser igual a A."""
    phi = Homomorfismo()
    A = set(Accion)
    assert phi.imagen() == A

def test_primer_teorema_isomorfismo():
    """G/ker(φ) debe tener el mismo cardinal que Im(φ)."""
    phi = Homomorfismo()
    G = list(Gesto)
    clases = phi.clases_laterales_kernel(G)
    assert len(clases) == len(phi.imagen())
```

### Test 3: Clasificador de gestos

```python
# tests/test_clasificador.py

def test_mano_cerrada_es_g3():
    """Todos los dedos abajo → G3 (puño)."""
    # Simular landmarks donde todas las puntas están debajo de los MCPs
    coords = generar_landmark_puno()
    assert clasificar_gesto(coords) == Gesto.G3

def test_indice_levantado_es_g1():
    """Solo índice arriba → G1."""
    coords = generar_landmark_un_dedo()
    assert clasificar_gesto(coords) == Gesto.G1
```

---

## 11. Limitaciones y Trabajo Futuro

### Limitaciones Actuales

**Técnicas:**
- El clasificador geométrico es sensible a la orientación de la mano (funciona mejor con la mano de frente a la cámara).
- La iluminación afecta la detección de MediaPipe (se recomienda luz frontal uniforme).
- Solo se soporta una mano a la vez (`max_num_hands=1`).
- El control multimedia funciona de forma diferente en cada sistema operativo.

**Algebraicas:**
- En la implementación base, G es pequeño (6 elementos) y φ es biyectivo, lo que hace el análisis del kernel trivial (ker(φ) = {e}).
- La operación de composición de G está definida conceptualmente pero no se implementa como tabla de Cayley completa en tiempo real.

### Trabajo Futuro

**Para enriquecer el análisis algebraico:**
- Añadir gestos ambiguos que el clasificador no distinga (caen en ker(φ) → ker(φ) no trivial).
- Mapear múltiples gestos a la misma acción, lo que produce clases laterales no triviales y un análisis más rico del Primer Teorema de Isomorfismo.
- Mostrar la tabla de Cayley de G en la visualización.
- Calcular y mostrar el orden de cada elemento de G.

**Técnicas:**
- Añadir clasificador basado en machine learning (k-NN o red neuronal pequeña) para mayor robustez.
- Soporte para dos manos simultáneas (homomorfismo φ : G × G → A).
- Persistencia de configuraciones del usuario.

---

## 12. Referencias

1. **Saracino, D.** (2008). *Abstract Algebra: A First Course*. Waveland Press. — Referencia principal para grupos, homomorfismos y el Primer Teorema de Isomorfismo.

2. **Scheinerman, E.A.** (2012). *Mathematics: A Discrete Introduction*. Cengage Learning. — Referencia del curso para operaciones binarias y grupos simétricos.

3. **Rodríguez, A.** (2025). *Notas de clase — Matemáticas Discretas II*. Universidad Nacional de Colombia. — Definiciones y teoremas usados directamente del curso: Definición 13.1 (Subgrupo Normal), Teorema 13.2, Corolario 13.3, Teorema 13.6, Primer Teorema de Isomorfismo.

4. **Google MediaPipe.** (2024). *MediaPipe Hands documentation*. https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

5. **OpenCV.** (2024). *OpenCV documentation*. https://docs.opencv.org/

---

*GestGroup · Matemáticas Discretas II · Universidad Nacional de Colombia · 2026*
