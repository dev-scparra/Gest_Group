# Guion — Video GestGroup (5 minutos)

**Proyecto:** GestGroup — Control por gestos modelado con teoría de grupos
**Curso:** Matemáticas Discretas II · Universidad Nacional de Colombia
**Integrantes:** Yony Sebastian Chaparro Mesa · Sebastian Camilo Parra Siabato · Angel Juaben Inyena Pasuy Muchavisoy

**Estructura y tiempos objetivo (5:00 total):**

| # | Sección | Duración | Acumulado |
|---|---|---|---|
| 1 | Explicación general del problema | 0:40 | 0:40 |
| 2 | Fundamentos matemáticos principales | 1:30 | 2:10 |
| 3 | Diseño de la solución | 1:00 | 3:10 |
| 4 | Ejecución / demostración del proyecto | 1:00 | 4:10 |
| 5 | Resultados obtenidos | 0:35 | 4:45 |
| 6 | Referencias utilizadas | 0:15 | 5:00 |

> Nota de producción: las secciones 3 y 4 pueden grabarse con captura de
> pantalla (código + cámara en vivo); el resto funciona con el presentador a
> cámara o con slides. Los bloques marcados **[PANTALLA]** indican qué mostrar.

---

## 1. Explicación general del problema — 0:00–0:40

**[Presentador a cámara o slide con el título del proyecto]**

> "Los sistemas de control por gestos existen hace años: mueves la mano y el
> computador reacciona. Pero casi siempre se tratan como una caja negra —
> reconocimiento de patrones, sin garantías sobre su comportamiento.
>
> GestGroup nace de una pregunta distinta: ¿qué pasa si modelamos el mapeo
> entre gestos y acciones no como una tabla arbitraria, sino como una
> estructura algebraica formal? Concretamente: los gestos de la mano forman
> un **grupo matemático G**, subgrupo genuino del grupo simétrico S₅; las
> acciones del sistema —subir volumen, pausar, cambiar de pista— forman otro
> grupo **A**; y la función que traduce uno en el otro es un **homomorfismo
> de grupos φ: G → A**.
>
> Eso no es solo una curiosidad matemática: nos permite demostrar
> formalmente propiedades como 'todo gesto produce una acción bien definida'
> o 'dos gestos que el sistema no distingue caen en el mismo bloque
> algebraico', usando los teoremas del curso — kernel, subgrupos normales,
> grupo cociente y el Primer Teorema de Isomorfismo — en vez de solo
> confiar en que 'funciona en la demo'."

---

## 2. Fundamentos matemáticos principales — 0:40–2:10

**[PANTALLA: slide o pizarra con las definiciones; opcionalmente
`docs/demostraciones.md` abierto]**

> "Repasemos rápido las piezas de teoría de grupos que sostienen el
> proyecto.
>
> Primero, un **grupo** es un conjunto con una operación que cumple cuatro
> axiomas: clausura, asociatividad, elemento identidad e inversos. Nuestro
> grupo de gestos G no se definió a mano — se construyó como el subgrupo
> **cíclico genuino de S₅** generado por la permutación
> σ = (1 2 3)(4 5), que tiene orden 6. Es decir:
>
> G = {E, G1, G2, G3, G4, G5} = {σ⁰, σ¹, σ², σ³, σ⁴, σ⁵}
>
> Esto hace a G isomorfo a ℤ/6ℤ: componer Gᵢ con Gⱼ da G₍ᵢ₊ⱼ₎ mod 6.
> Y como es cíclico, es automáticamente abeliano.
>
> Vale la pena mencionar por qué se descartó la primera idea, donde cada
> gesto era su propio inverso: eso es matemáticamente imposible para un
> grupo de 6 elementos, porque obligaría a que el orden del grupo fuera
> una potencia de 2 — y 6 no lo es. Encontrar y corregir esa contradicción
> fue parte del trabajo del proyecto, documentado en la Decisión D1 de
> `docs/demostraciones.md`.
>
> Segundo, el **homomorfismo** φ: G → A es la función que preserva la
> estructura: φ(g₁ ∘ g₂) = φ(g₁) ∘ φ(g₂). De ahí se derivan tres conceptos
> clave que usamos para analizar el sistema:
>
> - El **kernel**, ker(φ) = {g ∈ G : φ(g) = identidad de A} — los gestos
>   que 'no hacen nada'.
> - El hecho de que ese kernel es siempre un **subgrupo normal** de G.
> - Y el **Primer Teorema de Isomorfismo**: G / ker(φ) ≅ Im(φ). En
>   palabras simples, el grupo cociente — que agrupa los gestos que el
>   sistema no distingue entre sí — es estructuralmente idéntico al
>   conjunto de acciones que realmente se ejecutan.
>
> Estas tres piezas — grupo cíclico, homomorfismo y Primer Teorema de
> Isomorfismo — son exactamente lo que verificamos por código más
> adelante, no solo en el papel."

---

## 3. Diseño de la solución — 2:10–3:10

**[PANTALLA: diagrama de pipeline / estructura de carpetas `src/`]**

> "La arquitectura tiene cinco capas, en pipeline:
>
> Cámara → MediaPipe → Filtro EMA → Clasificador → φ(g).
>
> OpenCV captura el video; MediaPipe Hands extrae 21 landmarks de la mano
> por frame. Esas coordenadas 'tiemblan' entre frames por ruido de cámara,
> así que antes de clasificar aplicamos un **filtro de media exponencial
> móvil (EMA)**:
>
> x[n] = α · x_raw[n] + (1 − α) · x[n−1]
>
> Es una ecuación en diferencias de primer orden. Su solución homogénea es
> x_h[n] = C·(1−α)ⁿ, y como α está entre 0 y 1, esa componente tiende a
> cero — el filtro es asintóticamente estable, la influencia del ruido
> inicial se olvida exponencialmente. Con α = 0.3 balanceamos suavidad
> contra tiempo de reacción.
>
> El clasificador geométrico decide, a partir de qué dedos están
> levantados, cuál de los seis elementos de G corresponde al frame actual
> — y un estabilizador por debounce evita que un gesto sostenido dispare
> la misma acción en cada frame.
>
> Un detalle de diseño que vale la pena mencionar: la detección del pulgar
> no compara coordenadas fijas en x, porque eso solo funciona para una
> mano. En vez de eso, se orienta por la geometría de la palma —el eje
> meñique→índice— así que **el sistema reconoce los seis gestos
> igual de bien con la mano izquierda o la derecha**.
>
> Por último, el módulo de álgebra implementa φ como una tabla explícita
> Gesto → Acción, y expone funciones para calcular el kernel, la imagen y
> las clases laterales directamente sobre esa tabla — el mismo código que
> corre en producción es el que usamos para verificar las propiedades
> algebraicas."

---

## 4. Ejecución o demostración del proyecto — 3:10–4:10

**[PANTALLA: terminal + ventana de cámara en vivo]**

> "Veámoslo funcionando. Primero, el análisis algebraico puro, sin
> cámara:
>
> ```
> python -m src.algebra.analisis
> ```
>
> [Mostrar la salida en pantalla mientras se narra:]
>
> Esto imprime ker(φ) = {E}, la imagen completa de seis acciones, y
> confirma que φ es inyectiva y sobreyectiva — un isomorfismo — y que la
> propiedad de homomorfismo se cumple sobre los 36 pares posibles de G×G.
>
> Ahora la demo en vivo:
>
> ```
> python -m src.main
> ```
>
> [Grabar la cámara reconociendo gestos en tiempo real, mostrando el
> overlay con el gesto detectado y φ(g):]
>
> - Mano en reposo → E → ninguna acción.
> - Un dedo (índice) → G1 → sube el volumen.
> - Dos dedos → G2 → baja el volumen.
> - Puño cerrado → G3 → pausa o reproduce.
> - Mano abierta → G4 → siguiente pista.
> - Solo el pulgar → G5 → pista anterior.
>
> [Opcional: repetir uno o dos gestos con la mano contraria para mostrar
> que la clasificación no cambia.]
>
> Cada transición que ven en pantalla es literalmente la evaluación de
> φ(g) sobre el gesto que el clasificador acaba de determinar."

---

## 5. Resultados obtenidos — 4:10–4:45

**[PANTALLA: salida de `pytest` o slide con los números]**

> "El proyecto queda respaldado por 86 tests automatizados, todos
> deterministas y sin depender de cámara ni hardware real —la capa
> algebraica se prueba de forma pura, y captura, detección y ejecución de
> acciones se prueban con mocks.
>
> Matemáticamente, se verificó computacionalmente que:
>
> - (G, ∘) cumple los cuatro axiomas de grupo sobre las 216 ternas
>   posibles.
> - φ es homomorfismo sobre los 36 pares de G × G.
> - ker(φ) = {E}, es normal en G, y G/ker(φ) tiene exactamente 6 clases
>   laterales — el mismo cardinal que Im(φ), confirmando el Primer
>   Teorema de Isomorfismo en este caso concreto.
> - El filtro EMA converge al valor de entrada con error menor a 1e-6 tras
>   200 iteraciones, y reduce la varianza frente a una señal con ruido
>   gaussiano.
>
> Una auditoría posterior de conformidad entre especificación y código
> —documentada en las specs 010 a 013— encontró y corrigió tres defectos
> que habían sobrevivido a la primera versión de la suite, todos por la
> misma causa: el test asumía el mismo camino feliz que el código. Esa
> auditoría es en sí misma parte del resultado: no basta con tests en
> verde, hay que preguntarse qué caso NO están cubriendo."

---

## 6. Referencias utilizadas — 4:45–5:00

**[PANTALLA: slide de créditos/bibliografía]**

> "Este trabajo se apoya en:
>
> - Saracino, *Abstract Algebra: A First Course*, para grupos,
>   homomorfismos y el Primer Teorema de Isomorfismo.
> - Scheinerman, *Mathematics: A Discrete Introduction*, para operaciones
>   binarias y grupos simétricos.
> - Las notas de clase de Matemáticas Discretas II, de donde vienen las
>   definiciones y teoremas 13.1 a 13.6 que citamos en las demostraciones.
> - Y la documentación oficial de MediaPipe Hands y OpenCV para la capa de
>   visión por computador.
>
> Todo el código, las specs y las demostraciones formales están en el
> repositorio. Gracias por ver GestGroup."

**[Fin — logo/nombre del proyecto en pantalla]**

---

## Notas para grabación

- **Recursos a preparar antes de grabar:** cámara con buena luz frontal
  (ver limitaciones en `GestGroup_Contexto_Desarrollo.md`, Sección 11);
  permisos de macOS de Cámara y Accesibilidad concedidos de antemano (ver
  `README.md`); terminal con fuente grande y tema de alto contraste para
  legibilidad en video.
- **Comandos a tener listos en el historial de la terminal**, en este
  orden: `python -m src.algebra.analisis`, `python -m src.main`,
  `pytest tests/ -v` (o `-q` para una salida más corta en pantalla).
- Si el tiempo aprieta, la sección 2 (fundamentos) es la más comprimible:
  puede omitirse la explicación de por qué se descartó el modelo
  "autoinverso" y dejar solo la definición de G, φ, kernel y el Primer
  Teorema de Isomorfismo.
- Si sobra tiempo, la sección 4 (demo) es la más expandible: mostrar los
  seis gestos con ambas manos, o mostrar `python -m scripts.smoke_vision`
  imprimiendo lateralidad + gesto + los 5 booleanos de dedos en tiempo
  real.
