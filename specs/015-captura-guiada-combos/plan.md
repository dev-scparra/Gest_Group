# Plan 015 — Captura Guiada de Combos

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/clasificador/
├── gestos.py                # (006, sin cambios)
├── estabilizador.py         # (006, sin cambios; deja de usarse en el flujo de combos)
└── capturador_combo.py      # NUEVO — CapturadorCombo, EstadoCombo, FaseCombo

src/main.py                  # (009) reemplaza estabilizador+combinador por capturador
src/visualizacion/renderer.py # (008) HUD de combo desde EstadoCombo (VIS-FR-009)
config/default.yaml           # combinador.frames_captura/espera/resultado
src/algebra/combinador.py     # ELIMINADO (spec 014, superado por 015)
```

`capturador_combo.py` va en `src/clasificador/`, junto a `estabilizador.py`, no en `src/algebra/`: su responsabilidad es el *timing y estado de captura* de gestos por frame (como el debounce del estabilizador), no el álgebra. Importa `operacion_G` de 001 solo para el cálculo final del par, igual que el estabilizador importa `Gesto`.

## 2. Máquina de estados (núcleo)

Frame-driven y pura: `actualizar(gesto)` avanza un frame. Estados en `FaseCombo`; el conteo por ventana con `collections.Counter`. Transiciones (ver `spec.md` Sección 2):

- INACTIVO: si `gesto==E` → arma. Si armado y `gesto!=E` → arranca CAPTURANDO_G1 (contando ese frame). Si no armado y no-E → se ignora (espera ver E).
- CAPTURANDO_G1/G2: acumula voto; al llegar a `frames_captura`, `ganador = votos.most_common(1)`. Si `ganador==E` → cancela (reset). Si slot 1 → g1, va a ESPERA. Si slot 2 → g2, `compuesto=operacion_G(g1,g2)`, va a RESULTADO con `disparar=compuesto`.
- ESPERA: cuenta `frames_espera`, ignora entrada; luego CAPTURANDO_G2 (votos nuevos).
- RESULTADO: cuenta `frames_resultado`; luego reset (desarmado).

`reset()` desarma (`_armado=False`) para exigir E antes del próximo combo. El `__init__` deja `_armado=True` (primer gesto de la sesión no necesita E previo).

El borde `disparar`: sólo el snapshot del frame que cierra el gesto 2 lleva `disparar != None`; los frames de RESULTADO posteriores lo llevan en `None`. Así 009 ejecuta una sola vez.

## 3. Cambios en `src/main.py` (009)

```python
from src.clasificador.capturador_combo import CapturadorCombo, EstadoCombo

def procesar_frame(frame_rgb, detector, filtro, capturador, homomorfismo, estado):
    landmarks = detector.procesar(frame_rgb)
    gesto_actual = Gesto.E if landmarks is None else clasificar_gesto(filtro.aplicar(landmarks))
    if landmarks is None:
        filtro.reset()
    estado_combo = capturador.actualizar(gesto_actual)     # reemplaza estabilizador+combinador
    if estado_combo.disparar is not None:
        accion = homomorfismo.aplicar(estado_combo.disparar)  # phi(g1 o g2)
        resultado = ejecutar_accion(accion)
        print(f"[combo] {g1} o {g2} = {compuesto} -> {accion.value} [{OK/FALLO}]")
        if accion != Accion.A_E:
            estado.ultima_accion = accion
    return gesto_actual, estado.ultima_accion, estado_combo   # 3-tupla: + estado_combo para 008
```

`procesar_frame` pierde los parámetros `estabilizador`, `combinador` y `ahora` (ya no hay reloj), y gana `capturador`; devuelve una 3-tupla (añade `estado_combo`). `main()` instancia `CapturadorCombo` con los 3 valores de config y pasa `estado_combo` a `dibujar_frame`. El `EstabilizadorGesto` ya no se instancia (el módulo permanece para sus tests).

## 4. Cambios en `config/default.yaml`

```yaml
combinador:
  frames_captura: 20     # ~0.67s a 30 FPS
  frames_espera: 12      # ~0.4s
  frames_resultado: 25   # ~0.83s
```

`cargar_config` sigue exigiendo la clave `combinador` (ahora con las 3 subclaves). La clave `estabilizador` se conserva en config (el módulo sigue existiendo), aunque el flujo de combos no la use.

## 5. Cambios en `src/visualizacion/renderer.py` (008, VIS-FR-009)

`dibujar_frame(..., estado_combo: EstadoCombo | None = None)`. Helper `_dibujar_hud_combo`:
- Panel oscurecido (`cv2.addWeighted`) para legibilidad sobre cualquier fondo.
- Por fase: título, gesto líder + votos, barra de progreso (`_barra_progreso`) con cuenta regresiva en frames y segundos aproximados (usando `fps`), gestos capturados y `g1 o g2 = compuesto` en RESULTADO.
- Se retira la línea simple de combo de 014 (`ResultadoCombinacion`), que este HUD supersede.

## 6. Estrategia de pruebas

- `tests/test_capturador_combo.py` (nuevo): camino feliz con disparo único; votación de mayoría ignora transición; mayoría E cancela; re-armado exige E; primer gesto arranca sin E; cuenta regresiva y líder; espera no consume ni dispara; ventanas configurables; reset desarma. Todos con gestos literales, sin cámara.
- `tests/test_orquestacion.py` (reescrito): combo end-to-end con dobles de prueba (detector falso + `ejecutar_accion` parcheado); disparo único; sin par no hay acción; devuelve `estado_combo`. El filtro de prueba usa `alpha≈0.99` (casi passthrough) para que el cambio de gesto se refleje de inmediato y el test mida el cableado del combo, no la dinámica del EMA.
- `tests/test_renderer.py` (actualizado): HUD en captura enciende píxeles (panel+barra+texto); RESULTADO muestra la composición; INACTIVO no rompe; `estado_combo=None` sigue funcionando.
- `tests/test_config.py` (actualizado): las 3 subclaves `combinador.*` presentes y > 0; falta de `combinador` → error.
- `tests/test_pureza_algebra.py`: sin cambios; `capturador_combo.py` está en `src/clasificador/`, no en `src/algebra/`, así que no aplica (no es capa algebraica pura — usa `operacion_G` pero no es parte del núcleo algebraico).

## 7. Orden de trabajo

1. `capturador_combo.py` + `test_capturador_combo.py` (aislado).
2. `config/default.yaml` + `cargar_config` (mantiene "combinador" requerido).
3. `main.py`: reescribir `procesar_frame` y `main()`; eliminar `combinador.py`.
4. `renderer.py`: HUD + `test_renderer.py`.
5. `test_orquestacion.py` reescrito; `test_config.py` actualizado.
6. Specs (015, y amendar 014/009/008/000) + docs + README.
7. Verificación de campo con cámara (T015): calibrar `frames_captura/espera/resultado`.
