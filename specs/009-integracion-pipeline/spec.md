# Spec 009 — Integración y Configuración

**Módulo:** `src/main.py`, `config/default.yaml`
**Depende de:** todos los módulos 001-008.
**Cubre:** el resto de US-1..US-7 de [000-overview](../000-overview/spec.md) en su forma end-to-end; SC-G02, SC-G03 (medición); resuelve Q4.

---

## 1. Propósito

Cablear el pipeline completo en un loop único, cargar configuración externa, y ser el único lugar del proyecto que decide *cuándo* se llaman los `reset()` de 005 y 006 al perder/recuperar la mano — decisiones que esos módulos dejaron explícitamente delegadas aquí (ver EMA-FR-003 y la Sección 6 de 006/spec.md).

Este módulo es intencionalmente delgado: no contiene lógica de negocio propia, solo orquestación. Si aparece lógica de clasificación, algebraica o de renderizado dentro de `main.py`, es una señal de que algo se filtró del módulo que le correspondía.

## 2. Contrato de interfaz

**Entradas:** `config/default.yaml` (α, `frames_estables`, `camara_id`, resolución, umbrales de MediaPipe).

**Salidas:** ninguna programática — es el punto de entrada del proceso (`python -m src.main`).

> **Corrección (013/CNF-FR-008):** esta spec decía `python src/main.py`, que **no funciona**: `main.py` usa imports absolutos (`from src.acciones.ejecutor import ...`) y falla al ejecutarse como script suelto. La forma correcta es `python -m src.main`, como documenta el README.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| INT-FR-001 | DEBE cargar `config/default.yaml` al arrancar y usar sus valores para instanciar `CapturaVideo` (003), `DetectorManos` (004), `FiltroEMA` (005), `EstabilizadorGesto` (006) — resuelve Q4 (config al inicio, sin hot-reload obligatorio en el MVP). |
| INT-FR-002 | DEBE implementar el loop principal en el orden: 003 → 004 → (si mano detectada) 005 → 006 → φ (002) → 007 → 008; (si no hay mano) → reset de 005/006 → 008 con gesto `E`. |
| INT-FR-003 | Cuando 004 devuelve `None` (sin mano) en un frame donde el frame anterior sí tenía mano, DEBE llamar `FiltroEMA.reset()` (005) — implementa EMA-FR-003. |
| INT-FR-004 | Cuando 004 devuelve `None`, DEBE alimentar `Gesto.E` a `EstabilizadorGesto.actualizar()` (006) en vez de omitir la llamada — implementa la convención que 006/spec.md Sección 6 dejó pendiente de fijar aquí. |
| INT-FR-005 | Cuando `EstabilizadorGesto.actualizar()` devuelve un `Gesto` no-`None` (confirmación), DEBE calcular `φ(g)` (002) y llamar `ejecutar_accion()` (007) exactamente una vez. |
| INT-FR-006 (revisado por [011](../011-semantica-gesto-identidad/spec.md), SEM-FR-001) | DEBE mantener el valor de "última acción confirmada" a través de frames (para pasarlo a 008, VIS-FR-003) — es el único estado mutable que vive en `main.py` en vez de en un módulo dedicado, precisamente porque es un artefacto de la orquestación, no del dominio de ningún módulo individual. **Solo se actualiza cuando `φ(g) != A_E`**: `A_E` es un no-op (ACC-FR-004), no un disparo real, y confirmar `E` —que es lo que ocurre a los `frames_estables` frames de retirar la mano— no debe desplazar del overlay a la última acción que sí tuvo efecto. Su valor inicial es `None` ("aún no hay acción"), distinguible de `A_E` ("ninguna"). |
| INT-FR-007 | DEBE permitir salida limpia con una tecla (p. ej. `q`), llamando `CapturaVideo.liberar()` (003) antes de terminar el proceso. |
| INT-FR-008 (precisado por [013](../013-conformidad-menor/spec.md), CNF-FR-002) | DEBE capturar y loguear (sin propagar) cualquier excepción no anticipada de un frame individual, para que un fallo puntual no termine la sesión completa (NFR-G02 aplicado al loop principal). El manejador **NO puede saltarse `cv2.imshow` ni `cv2.waitKey`**: si lo hace, una excepción que se repita en todos los frames congela la ventana y la tecla `q` (INT-FR-007) deja de procesarse, quedando solo `Ctrl-C`. El frame se trata como "sin mano" (Sección 5) y el render y el teclado siguen ocurriendo. El logueo DEBE estar acotado (primera ocurrencia + 1 de cada N), o un fallo persistente inunda la consola a ~30 líneas/segundo. |
| INT-FR-009 (añadido por 013, CNF-FR-005) | DEBE loguear el `mensaje` de `ResultadoEjecucion` cuando `ejecutar_accion()` devuelve `exito=False`. ACC-FR-005 dice que el fallo "se reporta, aunque en el MVP no se actúa sobre ese reporte **más allá de loguearlo**" — pero el logueo no existía: `main.py` descartaba el valor de retorno, así que todo el reporte de errores de 007 moría en silencio y el usuario veía "el gesto se detecta pero no pasa nada" sin diagnóstico. |

## 4. Criterios de aceptación

- **Dado** el pipeline corriendo con cámara real, **cuando** el usuario sostiene `g₁` por `frames_estables` frames, **entonces** se observa el efecto de `A1` (subir volumen) y el overlay lo refleja (US-1, US-2 end-to-end).
- **Dado** el pipeline corriendo, **cuando** el usuario retira la mano del cuadro y la vuelve a poner, **entonces** no hay salto ni confirmación espuria causada por estado arrastrado de antes de perder la mano (INT-FR-003/004, US-6).
- **Dado** `config/default.yaml` con `alpha: 0.1` en vez de `0.3`, **cuando** se reinicia la app, **entonces** el comportamiento de suavizado observable cambia (más lento a converger) — confirma que INT-FR-001 realmente conecta la config con 005, no un valor hardcodeado ignorando el archivo.
- **Dado** el pipeline corriendo durante 5 minutos, **cuando** se mide el FPS sostenido, **entonces** es ≥15 (SC-G02, medido aquí porque es el único módulo que ve el pipeline completo).

## 5. Casos borde

- `config/default.yaml` ausente o mal formado: DEBE fallar rápido y explícito al arrancar (no a mitad de sesión) — un error de configuración es preferible detectarlo antes de abrir la cámara.
- Excepción dentro de 004 (MediaPipe) en un frame específico: capturada por INT-FR-008, el frame se trata como "sin mano" (`None`) para ese ciclo, el loop continúa.
- Combinación simultánea de "cámara desconectada" (003 devuelve `(False,None,None)`) DEBE terminar el loop de forma controlada (no es lo mismo que "sin mano", que sí es un estado transitorio esperado) — INT-FR-002 debe distinguir explícitamente estos dos casos.

## 6. No objetivos de este módulo

- No implementa lógica de ningún módulo 001-008 — solo los invoca en el orden correcto.
- No decide el valor por defecto de α ni `frames_estables` (esos valores son propiedad de 005/006 respectivamente); solo los lee de config y los pasa.
