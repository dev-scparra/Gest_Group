# Plan 013 — Backlog de Conformidad Menor

**Depende de:** [spec.md](./spec.md).

## 1. Orden de aplicación

Estos cambios son independientes entre sí **salvo** por el archivo que tocan. Dos de ellos (CNF-FR-003, CNF-FR-005) caen dentro de `main.py`, que [011](../011-semantica-gesto-identidad/spec.md) reestructura con `procesar_frame()`. **Aplicar 011 primero** y estos después, o se resuelve el mismo conflicto dos veces.

Los del Grupo B (correcciones de spec, sin código) y CNF-FR-012 (docstring) se pueden hacer en cualquier momento: no tocan comportamiento y no colisionan con nada.

## 2. Notas de implementación

**CNF-FR-001** — una comprobación reemplaza a la actual y cubre los dos casos:

```python
if set(tabla_phi) != set(Gesto):
    faltantes = set(Gesto) - set(tabla_phi)
    sobrantes = set(tabla_phi) - set(Gesto)
    raise ValueError(
        f"tabla_phi debe tener exactamente las 6 claves de Gesto "
        f"(faltan: {faltantes or 'ninguna'}; sobran: {sobrantes or 'ninguna'})"
    )
```

**CNF-FR-002** — el arreglo consiste en mover el `try` para que **envuelva solo el pipeline**, dejando el render y el teclado siempre en el camino principal:

```python
try:
    gesto_actual, accion = procesar_frame(frame_rgb, ...)   # 011
except Exception as exc:
    _log_acotado(f"Error no anticipado en el frame, se trata como 'sin mano': {exc}")
    gesto_actual, accion = Gesto.E, estado.ultima_accion    # 009/Sec.5: como "sin mano"

dibujar_frame(frame_bgr, detector.landmarks_para_dibujo(), gesto_actual, accion, filtro.alpha, fps)
cv2.imshow("GestGroup", frame_bgr)
if cv2.waitKey(1) & 0xFF == ord("q"):                       # INT-FR-007: siempre alcanzable
    break
```

`_log_acotado` imprime la primera ocurrencia y luego una de cada N (p. ej. 30) para no inundar la consola a 30 líneas/segundo con un fallo persistente.

**CNF-FR-010** — el test de pureza usa `ast`, no `import`: importar el módulo para inspeccionar sus imports sería circular y además ejecutaría el código bajo prueba.

```python
PROHIBIDOS = {"cv2", "mediapipe", "subprocess"}

def test_capa_algebraica_es_pura():
    """NFR-G03 / HOM-FR-010: src/algebra no puede depender de I/O ni de vision."""
    for archivo in Path("src/algebra").glob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                modulos = {a.name.split(".")[0] for a in nodo.names}
            elif isinstance(nodo, ast.ImportFrom):
                modulos = {(nodo.module or "").split(".")[0]}
            else:
                continue
            assert not (modulos & PROHIBIDOS), f"{archivo.name} importa {modulos & PROHIBIDOS}"
```

Verificación de que el test sirve: añadir `import cv2` a `src/algebra/analisis.py`, correr `pytest`, comprobar que **falla**, y revertir. Un test de invariante que nunca se vio fallar no es un test, es decoración.

**CNF-FR-011** — las constantes van en sus módulos respectivos, no en uno nuevo:

```python
# grupo_gestos.py
ELEMENTOS_G: frozenset[Gesto] = frozenset(Gesto)
IDENTIDAD_G: Gesto = Gesto.E
```

## 3. Estrategia de pruebas

| Requerimiento | Test |
|---|---|
| CNF-FR-001 | `test_tabla_con_clave_espuria_falla_en_constructor` → `pytest.raises(ValueError)`. |
| CNF-FR-002 | `test_excepcion_en_pipeline_no_impide_salir` — `procesar_frame` parcheado con `side_effect=RuntimeError`; verificar que el loop sigue llamando a `dibujar_frame`/`waitKey`. Encaja en `tests/test_orquestacion.py` (creado por 011). |
| CNF-FR-003 | Verificación estática: `grep -rn "putText" src/main.py` sin resultados. Los tests de 008 cubren el nuevo parámetro `fps`. |
| CNF-FR-004 | `test_primer_frame_devuelve_copia_no_el_estado_interno` — mutar la lista devuelta y comprobar que `filtro.x_prev` no cambia. |
| CNF-FR-010 | `test_capa_algebraica_es_pura` (arriba), en `tests/test_pureza_algebra.py`. |
| CNF-FR-012, Grupo B | Sin test: son docstrings y specs. Se verifican leyéndolos. |

## 4. Riesgo

Bajo en todos los ítems. El único con superficie real es CNF-FR-002, que reordena el `try/except` del loop principal — el mismo bloque que 011 reestructura. De ahí la dependencia de orden de la Sección 1.
