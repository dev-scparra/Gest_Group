# Spec 013 — Backlog de Conformidad Menor

**Módulos:** transversal (001, 003, 004, 005, 008, 009).
**Origen:** auditoría de conformidad specs↔código (2026-07-13).
**Severidad:** **BAJA-MEDIA** — ninguno de estos hallazgos rompe la demo por sí solo. Se agrupan en un único spec, en vez de abrir uno por hallazgo, precisamente por la advertencia de fragmentación excesiva de [000-overview](../000-overview/spec.md) Sección 6.

Los tres hallazgos con consecuencia funcional real viven en specs propias: [010](../010-robustez-ejecutor/spec.md) (excepción no controlada), [011](../011-semantica-gesto-identidad/spec.md) (overlay pierde la última acción), [012](../012-clasificador-pulgar-lateralidad/spec.md) (gestos intercambiados con la otra mano).

---

## 1. Requerimientos funcionales

### Grupo A — desviaciones de código respecto a una spec vigente

| ID | Módulo | Requerimiento |
|---|---|---|
| CNF-FR-001 | 002 | **`Homomorfismo.__init__` no cumple HOM-FR-001.** La spec exige que `tabla_phi` tenga "exactamente las 6 claves de `Gesto`", pero el constructor solo comprueba las **faltantes** (`set(Gesto) - set(tabla_phi)`). Una tabla con claves espurias se acepta y **contamina los resultados**: verificado, `Homomorfismo({...6 gestos..., "no_soy_un_gesto": A5, 42: A2})` construye sin error, y `imagen()` devuelve `{A1, A2, A5}` — acciones que ningún gesto produce. DEBE validarse `set(tabla_phi) != set(Gesto)` → `ValueError`, cubriendo claves faltantes **y** sobrantes en una sola comprobación. |
| CNF-FR-002 | 009 | **El manejador de INT-FR-008 deja la app sin salida.** El `except ... continue` del loop salta `cv2.imshow` **y `cv2.waitKey`**: ante una excepción que se repita en cada frame, la ventana se congela y la tecla `q` (INT-FR-007) nunca se procesa — solo queda `Ctrl-C`. Además, 009/spec.md Sección 5 exige que una excepción de 004 haga que "el frame se trate como *sin mano* (`None`) para ese ciclo", no que se descarte el frame entero. DEBE tratarse el frame como "sin mano" y **seguir renderizando y atendiendo el teclado**. Conviene también acotar el `print` del `except` (loguear la primera vez y luego cada N frames) para que un fallo persistente no inunde la consola a 30 líneas/segundo. |
| CNF-FR-003 | 009 / 008 | **`main.py` dibuja el overlay de FPS con `cv2.putText`.** 009/spec.md Sección 1 y Sección 6 son explícitas: "Si aparece lógica de clasificación, algebraica o **de renderizado** dentro de `main.py`, es una señal de que algo se filtró del módulo que le correspondía". El FPS se **mide** en 009 (correcto: SC-G02 lo asigna ahí) pero se **dibuja** en 009 (incorrecto: eso es 008). DEBE moverse el dibujo a `dibujar_frame(..., fps: float)` como nuevo **VIS-FR-007**, dejando a `main.py` solo el cálculo. |
| CNF-FR-004 | 005 | **`FiltroEMA.aplicar()` devuelve su propio estado interno en el primer frame:** `self.x_prev = list(landmarks_raw); return self.x_prev` entrega al llamador un alias de `x_prev`, no una copia. Hoy es inocuo (nadie muta la lista devuelta), pero es un acoplamiento silencioso: cualquier futuro consumidor que ordene o modifique la lista in-place corrompería la historia del filtro sin ningún síntoma cercano a la causa. DEBE devolverse una copia (`return list(self.x_prev)`), consistente con la rama del caso general, que ya construye una lista nueva. |
| CNF-FR-005 | 007 / 009 | **`main.py` descarta el `ResultadoEjecucion`.** ACC-FR-005 dice que el fallo "se reporta, aunque en el MVP no se actúa sobre ese reporte **más allá de loguearlo**" — pero el logueo no existe: `main.py` llama `ejecutar_accion(ultima_accion)` e ignora el valor de retorno. Todo el reporte de errores de 007 (y el de [010](../010-robustez-ejecutor/spec.md)) muere en silencio, y el usuario ve "el gesto se detecta pero no pasa nada" sin ningún diagnóstico. DEBE loguearse `mensaje` cuando `exito` es `False`. |

### Grupo B — specs que hay que corregir (el código tiene razón)

| ID | Módulo | Requerimiento |
|---|---|---|
| CNF-FR-006 | 004 | **DET-FR-002 es falso tal como está escrito:** exige "21 tuplas `(x,y,z)` normalizadas en `[0,1]`". El `z` de MediaPipe **no** está en `[0,1]`: es profundidad relativa a la muñeca, con signo (negativo = más cerca de la cámara). El código hace lo correcto (pasa el valor tal cual, sin validar ni recortar); es la spec la que miente. DEBE reescribirse: `x`, `y` normalizados a `[0,1]` respecto al ancho/alto de la imagen; `z` es profundidad relativa con signo, misma escala que `x`, **sin garantía de rango**. Relevante porque 005/spec.md Sección 5 razona sobre "landmarks fuera de `[0,1]`" apoyándose en esta afirmación errónea. |
| CNF-FR-007 | 008 | **VIS-FR-005 pide la anotación `G/ker(phi) ≅ Im(phi)`**, pero el código dibuja `G/ker(phi) = Im(phi)` (con `=`, no `≅`). No es un descuido: las fuentes Hershey de OpenCV (`cv2.FONT_HERSHEY_SIMPLEX`) no tienen glifo para `≅` y lo renderizarían como `?`. La desviación es correcta; DEBE documentarse en VIS-FR-005 en vez de dejar la spec pidiendo algo que OpenCV no puede dibujar. (Si se quiere el símbolo real, la única vía es componer el texto con PIL/FreeType y volcarlo al frame — desproporcionado para una anotación decorativa; se descarta explícitamente.) |
| CNF-FR-008 | 009 | **009/spec.md Sección 2 dice que el punto de entrada es `python src/main.py`**, y el docstring de `src/main.py` repite lo mismo. Ambos son incorrectos: `main.py` usa imports absolutos (`from src.acciones.ejecutor import ...`), que fallan al ejecutarlo como script suelto. La forma correcta es `python -m src.main`, como ya documenta el README (corregido en `d3481f1`). DEBEN alinearse la spec 009 y el docstring de `main.py` con el README. |
| CNF-FR-009 | 003 | **CAP-FR-001 dice "a la resolución y FPS configurados"**, pero el FPS está fijo en `30` dentro de `video_capture.py` y `config/default.yaml` no tiene clave `fps` (INT-FR-001 tampoco la lista). O bien se añade `camara.fps` a la config y se pasa al constructor, o bien CAP-FR-001 se reescribe como "a la resolución configurada y a 30 FPS fijos". **Recomendación: lo segundo** — nadie pidió FPS variable, y añadir una perilla de config sin caso de uso es superficie gratuita. |

### Grupo C — cobertura de test que falta para requisitos ya escritos

| ID | Módulo | Requerimiento |
|---|---|---|
| CNF-FR-010 | 001 / 002 | **NFR-G03 y HOM-FR-010 no tienen test que los haga cumplir.** Ambos son MUST con ID propio ("este módulo NO DEBE importar `cv2`, `mediapipe` ni `subprocess`") y hoy se cumplen **por suerte**: nada impide que un `import cv2` se cuele mañana en `src/algebra/` y la suite siga en verde. DEBE añadirse un test que recorra los `.py` de `src/algebra/` y falle si alguno importa `cv2`, `mediapipe` o `subprocess` (vía `ast.parse`, sin ejecutar los módulos). Es el único requerimiento de la capa algebraica —la que el curso va a evaluar— sin respaldo ejecutable. |
| CNF-FR-011 | 001 | **ALG-FR-008 ("ambos grupos DEBEN quedar disponibles como constantes importables") se cumple a medias.** Existen `Gesto`, `Accion`, `CAYLEY_G`, `CAYLEY_A`, pero no hay constantes para el **conjunto de elementos** ni para la **identidad**: cada consumidor las reconstruye ad hoc (`set(Gesto)`, `Gesto.E`), incluida `verificar_axiomas_grupo`, que las recibe por parámetro en cada llamada. DEBEN exponerse `ELEMENTOS_G`/`IDENTIDAD_G` y `ELEMENTOS_A`/`IDENTIDAD_A`, de modo que "el grupo" sea un objeto importable y no una convención repetida en cada sitio. |
| CNF-FR-012 | 001 | **El docstring de `verificacion.py` afirma algo falso:** *"No se duplica la lógica entre `grupo_gestos.py` y `grupo_acciones.py`: **ambos delegan** en `verificar_axiomas_grupo()`"*. Ninguno de los dos módulos importa ni llama a `verificar_axiomas_grupo` — el único consumidor es `tests/test_verificacion.py`. La función **sí** es genérica y reusable (ALG-FR-005 se cumple), pero la frase describe una colaboración que no existe y engaña a quien lea el módulo. DEBE corregirse el docstring para decir lo que realmente pasa: es una utilidad de verificación que G y A **pueden** usar y que la suite aplica a ambos. |

## 2. Criterios de aceptación

- **Dado** `Homomorfismo({...los 6 gestos..., "clave_espuria": Accion.A5})`, **cuando** se construye, **entonces** lanza `ValueError` (CNF-FR-001) — hoy construye sin queja e `imagen()` incluye `A5`.
- **Dado** el loop con una excepción que se repite en todos los frames, **cuando** el usuario pulsa `q`, **entonces** la app sale limpiamente (CNF-FR-002) — hoy la ventana está congelada y `waitKey` nunca corre.
- **Dado** un `grep -rn "putText" src/main.py`, **cuando** se ejecuta, **entonces** no devuelve resultados (CNF-FR-003).
- **Dado** un archivo `src/algebra/*.py` al que se le añada `import cv2`, **cuando** se corre `pytest`, **entonces** la suite **falla** (CNF-FR-010) — hoy pasa en verde.
- **Dado** `python -m src.main`, **cuando** se ejecuta, **entonces** arranca; y ni la spec 009 ni el docstring de `main.py` siguen recomendando `python src/main.py` (CNF-FR-008).

## 3. No objetivos

- No se rediseña ninguna interfaz pública más allá de lo que cada CNF-FR pide.
- CNF-FR-003 y CNF-FR-005 tocan el mismo archivo que [011](../011-semantica-gesto-identidad/spec.md) (`main.py`, función `procesar_frame()`): conviene aplicarlos **después** de 011 para no resolver conflictos dos veces. Ver `tasks.md`.
