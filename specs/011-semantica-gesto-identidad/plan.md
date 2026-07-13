# Plan 011 — Semántica del Gesto Identidad

**Depende de:** [spec.md](./spec.md).

## 1. El obstáculo real: el loop de `main.py` no es testeable

SEM-FR-005 pide un test de orquestación, pero hoy **no hay forma de escribirlo**: toda la lógica del pipeline vive dentro de `while True:` en `main()`, entrelazada con `cv2.imshow` y `cv2.waitKey`. Ese es también el motivo por el que el defecto de `spec.md` Sección 1 sobrevivió a 60 tests en verde: 009 es el único módulo sin suite propia, y es justamente donde vive el estado que VIS-FR-003 regula.

La corrección estructural es extraer el cuerpo del loop a una función pura de I/O de video:

```python
@dataclass
class EstadoPipeline:
    """El unico estado mutable de la orquestacion (INT-FR-006, revisado por SEM-FR-001/003)."""
    ultima_accion: Accion | None = None   # None = "sin accion aun" (SEM-FR-003)


def procesar_frame(
    frame_rgb, detector, filtro, estabilizador, homomorfismo, estado: EstadoPipeline
) -> tuple[Gesto, Accion | None]:
    """Un ciclo del pipeline 004 -> 005 -> 006 -> phi -> 007. Sin cv2, sin I/O de ventana:
    testeable con dobles de prueba. Devuelve (gesto_instantaneo, accion_a_mostrar)."""
    landmarks = detector.procesar(frame_rgb)
    if landmarks is None:
        filtro.reset()                                  # INT-FR-003
        gesto_actual = Gesto.E
    else:
        gesto_actual = clasificar_gesto(filtro.aplicar(landmarks))

    gesto_confirmado = estabilizador.actualizar(gesto_actual)   # INT-FR-004
    if gesto_confirmado is not None:
        accion = homomorfismo.aplicar(gesto_confirmado)
        resultado = ejecutar_accion(accion)                     # INT-FR-005 (A_E = no-op)
        if not resultado.exito:
            print(f"[accion] fallo {accion.name}: {resultado.mensaje}")  # ver 013/CNF-FR-011
        if accion != Accion.A_E:                                # <-- SEM-FR-001, el fix
            estado.ultima_accion = accion

    return gesto_actual, estado.ultima_accion
```

`main()` queda como lector de cámara + ventana + tecla `q`, llamando a `procesar_frame()`. Esto además refuerza 009/Sección 1 ("este módulo es intencionalmente delgado"): hoy `main.py` mezcla orquestación con renderizado (ver [013-conformidad-menor](../013-conformidad-menor/spec.md), CNF-FR-003).

## 2. Cambios por archivo

| Archivo | Cambio |
|---|---|
| `src/main.py` | Extraer `procesar_frame()` + `EstadoPipeline`; guardia `if accion != Accion.A_E` (SEM-FR-001); `ultima_accion` inicial `None` (SEM-FR-003). |
| `src/visualizacion/renderer.py` | `dibujar_frame(..., accion: Accion | None, ...)`; si `accion is None` → dibujar `phi(g) = --` (SEM-FR-003). Etiquetar el gesto como en vivo y la acción como última confirmada (SEM-FR-004). |
| `tests/test_orquestacion.py` (nuevo) | Tests de SEM-FR-005 con dobles de prueba para `detector` (devuelve `None` o landmarks de fixture) y `ejecutar_accion` parcheado. |
| `tests/test_renderer.py` | Añadir caso `accion=None` → no lanza excepción (SEM-FR-003). |

## 3. Estrategia de pruebas

El test que faltaba, escrito contra `procesar_frame()` y sin cámara:

```python
def test_confirmacion_de_E_no_borra_la_ultima_accion():
    """SEM-FR-001 / VIS-FR-003: retirar la mano no debe desplazar A1 del overlay."""
    estado = EstadoPipeline()
    detector = DetectorFalso(landmarks=generar_landmark_un_dedo())   # mano con indice arriba
    est = EstabilizadorGesto(frames_estables=10)
    ...
    for _ in range(10):                       # el usuario sostiene G1 -> confirma A1
        _, accion = procesar_frame(FRAME, detector, filtro, est, phi, estado)
    assert accion == Accion.A1

    detector.landmarks = None                 # el usuario retira la mano
    for _ in range(12):                       # mas frames que frames_estables
        _, accion = procesar_frame(FRAME, detector, filtro, est, phi, estado)
    assert accion == Accion.A1                # hoy falla en la iteracion 10: devuelve A_E
```

Este test **debe fallar contra el código actual** antes de aplicar el fix — si pasa a la primera, está mal escrito (no está alcanzando el frame 10 de `E`). Es la prueba de que reproduce el defecto y no otra cosa.

## 4. Riesgo de la corrección

Bajo en lógica, medio en superficie: la extracción de `procesar_frame()` toca el único archivo que **ningún test cubre hoy**, así que la red de seguridad hay que construirla en el mismo cambio (T011-05 antes que T011-01). Hacer el fix de una línea (`if accion != Accion.A_E`) sin la extracción es tentador y funcionaría, pero deja 009 igual de inauditable y el próximo defecto de orquestación volverá a pasar los 60 tests en verde.
