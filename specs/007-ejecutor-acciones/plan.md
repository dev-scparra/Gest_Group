# Plan 007 — Ejecutor de Acciones

**Depende de:** [spec.md](./spec.md).

## 1. Ubicación en el repositorio

```
src/acciones/
├── __init__.py
└── ejecutor.py   # ejecutar_accion(), ResultadoEjecucion, backends por SO
```

## 2. Dependencias técnicas

`subprocess` y `platform` (librería estándar). Sin dependencias de terceros en macOS/Linux. Windows quedaría detrás de `pycaw`/`comtypes` si se implementara (fuera de alcance, ver `requirements.txt` de 009 — se listan como comentario, no como dependencia instalada).

## 3. Notas de implementación

Implementación directa de la Sección 4.6 del documento de contexto, con dos adiciones respecto al esbozo original:

- `ResultadoEjecucion` (dataclass con `exito: bool`, `mensaje: str | None`) envolviendo cada `subprocess.run(..., capture_output=True)` — el esbozo original no capturaba ni interpretaba el resultado del `subprocess.run`.
- Separación clara por función interna: `_ejecutar_macos(accion)`, `_ejecutar_linux(accion)`, `_ejecutar_windows(accion)`, seleccionadas por `platform.system()` en `ejecutar_accion()` — así el test unitario puede parchear `platform.system` y probar cada rama sin depender del SO real donde corre la suite.

## 4. Estrategia de pruebas

- `tests/test_ejecutor.py`: con `unittest.mock.patch` sobre `subprocess.run` y `platform.system`:
  - `Accion.A_E` → no se llama `subprocess.run` (ACC-FR-004).
  - Mock de éxito (`returncode=0`) para cada una de las 5 acciones en macOS → se arma el comando `osascript` esperado (verificar los argumentos exactos pasados, no solo que se llamó).
  - Mock de fallo (`returncode≠0`) → `ResultadoEjecucion.exito == False`.
  - `platform.system()` mockeado a `"Windows"` → comportamiento documentado en ACC-FR-006.
- **Sin test automatizado que verifique el efecto real en el SO** (subir volumen de verdad) — eso es, por naturaleza, un checklist manual (ver `tasks.md`), igual que en 003.

## 5. Riesgo técnico — permisos de macOS

`osascript "tell application System Events to key code ..."` requiere que la aplicación que ejecuta el proceso Python (Terminal, iTerm, VS Code, o el intérprete mismo) tenga permiso en **Preferencias del Sistema → Privacidad y Seguridad → Accesibilidad**. Sin este permiso, los comandos de teclado (pausa/play, siguiente, anterior) fallan silenciosamente o piden permiso la primera vez de forma interactiva (lo cual puede interrumpir una demo en vivo si no se concedió de antemano). **Acción requerida antes de cualquier demo:** verificar el permiso manualmente, documentarlo en el README como paso de instalación obligatorio, no opcional.
