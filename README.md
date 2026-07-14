# GestGroup

Control por gestos en tiempo real modelado con teoría de grupos: los gestos
forman un grupo `G ≤ S₅`, las acciones del sistema forman un grupo `A`, y el
mapeo entre ambos es un homomorfismo `φ : G → A` cuyo kernel, imagen y grupo
cociente se analizan y verifican automáticamente (ver `docs/demostraciones.md`).

Proyecto de Matemáticas Discretas II — Universidad Nacional de Colombia.
Integrantes: Yony Sebastian Chaparro Mesa, Sebastian Camilo Parra Siabato,
Angel Juaben Inyena Pasuy Muchavisoy.

Especificaciones detalladas por módulo en [`specs/`](specs/), empezando por
[`specs/000-overview/spec.md`](specs/000-overview/spec.md).

## Instalación

Requiere **Python 3.11** (MediaPipe 0.10.9 no soporta versiones más nuevas).

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Permisos de macOS (obligatorios antes de la demo)

- **Cámara:** la primera vez que se ejecuta `main.py`, macOS pedirá permiso
  de cámara para la app/terminal que ejecuta Python. Concédelo en
  **Preferencias del Sistema → Privacidad y Seguridad → Cámara**.
- **Accesibilidad:** las acciones de pausa/play y cambio de pista usan
  `osascript ... System Events` (simulación de teclas), lo que requiere
  permiso de **Preferencias del Sistema → Privacidad y Seguridad →
  Accesibilidad** para la terminal/IDE/intérprete de Python. Sin este
  permiso, esos comandos fallan silenciosamente o interrumpen la demo
  pidiendo el permiso de forma interactiva — verificarlo **antes** de
  presentar, no durante.

### Windows y Linux

- **Windows:** paridad completa de las 5 acciones vía simulación de teclas
  multimedia (`ctypes.windll.user32.keybd_event`) — sin dependencias
  adicionales.
- **Linux:** soporte de segundo nivel, solo control de volumen vía `amixer`
  (paquete `alsa-utils`).

## Ejecutar

```bash
python -m src.main
```

Salir con la tecla `q`. La configuración (α del filtro EMA, frames estables
del debounce, resolución/FPS de cámara, umbrales de MediaPipe) se carga desde
[`config/default.yaml`](config/default.yaml).

### Gestos reconocidos

Funciona **con cualquiera de las dos manos**, de frente a la cámara. La detección del
pulgar (de la que dependen `G3`, `G4` y `G5`) se orienta por la geometría de la palma
—el eje meñique→índice— y no por una comparación de `x` con signo fijo, que solo sería
válida para una mano y con la otra intercambiaría `G3` y `G5`. Ver
[`specs/012`](specs/012-clasificador-pulgar-lateralidad/spec.md), Decisión D2.

| Gesto | Descripción | Acción `φ(g)` |
|---|---|---|
| `E` | Mano en reposo / gesto no reconocido | Ninguna acción |
| `G1` | Índice levantado | Subir volumen |
| `G2` | Índice + medio levantados | Bajar volumen |
| `G3` | Puño cerrado (pulgar abajo) | Pausa / Play |
| `G4` | Mano abierta (5 dedos) | Siguiente pista |
| `G5` | Solo el pulgar extendido | Pista anterior |

La tabla de clasificación es la de
[`specs/012`, Sección 5](specs/012-clasificador-pulgar-lateralidad/spec.md), que
reemplaza a la de la Sección 4.5 del documento de contexto: aquella declaraba el
pulgar como indiferente en la fila del puño, lo que hacía de `G5` un caso particular
de `G3` y dejaba a `G5` inalcanzable.

### Comprobar la detección sin lanzar acciones

```bash
python -m scripts.smoke_vision
```

Muestra la ventana con los landmarks e imprime, una vez por segundo, la mano detectada
(`Left`/`Right`), el gesto clasificado y los 5 booleanos de dedos. Útil para verificar
que **los 6 gestos se clasifican igual con las dos manos** antes de una demo.

### Análisis algebraico sin cámara

```bash
python -m src.algebra.analisis
```

Imprime `ker(φ)`, `Im(φ)`, las clases laterales de `G/ker(φ)`, si `φ` es
mono/epi/isomorfismo, y la verificación de la propiedad de homomorfismo sobre
los 36 pares de `G×G`. Es el artefacto de evidencia para el reporte técnico
(ver `docs/demostraciones.md`).

## Tests

```bash
pytest tests/ -v
```

86 tests, todos deterministas y sin necesidad de cámara/hardware real (capa
algebraica pura + mocks para captura/detección/ejecución de acciones).

Las specs [010](specs/010-robustez-ejecutor/spec.md)–[013](specs/013-conformidad-menor/spec.md)
documentan una auditoría de conformidad specs↔código y las correcciones que salieron
de ella. Los tres defectos con consecuencia funcional real habían sobrevivido a 60
tests en verde, en los tres casos por el mismo motivo: **el test modelaba el camino
feliz con la misma suposición que el código**. La suite añade ahora un test de
orquestación (009 no tenía), fixtures de mano para ambas lateralidades, y un test que
falla si alguien importa `cv2` dentro de `src/algebra/`.

## Estructura del repositorio

```
config/default.yaml       # alpha, frames_estables, camara, umbrales mediapipe
src/
├── main.py                    # punto de entrada — orquestacion del pipeline
├── algebra/                   # 001/002 — grupos G y A, homomorfismo φ, analisis
├── captura/                   # 003 — OpenCV
├── deteccion/                 # 004 — MediaPipe Hands
├── preprocesamiento/          # 005 — filtro EMA
├── clasificador/              # 006 — clasificacion geometrica + debounce
├── acciones/                  # 007 — ejecutor de acciones (macOS/Linux/Windows)
└── visualizacion/             # 008 — overlay de video
scripts/derivar_cayley.py # deriva la tabla de Cayley de G desde S5 (trazabilidad)
tests/                    # 60 tests, un archivo por modulo
docs/demostraciones.md    # demostraciones formales + evidencia ejecutable
specs/                    # spec.md / plan.md / tasks.md por modulo
```

## Notas sobre el modelo algebraico

`G` no se modela como "6 elementos donde cada uno es su propio inverso"
(la formulación original resulta matemáticamente imposible para `|G|=6` — ver
`docs/demostraciones.md`, Decisión D1). En su lugar, `G` es el subgrupo
cíclico genuino de `S₅` generado por `σ=(1 2 3)(4 5)` (orden 6), isomorfo a
`ℤ/6ℤ`. La tabla de Cayley se deriva por composición real de permutaciones en
`scripts/derivar_cayley.py`, no se transcribe a mano.

autorizo que claude controle mi mente