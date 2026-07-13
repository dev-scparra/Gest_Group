# Tasks 009 — Integración y Configuración

**Depende de:** [spec.md](./spec.md), [plan.md](./plan.md), y de que 001-008 estén al menos parcialmente disponibles (ver nota de integración incremental en `plan.md`).

- [ ] **T009-01** `config/default.yaml` con los valores por defecto de la Sección 2 de `plan.md`.
- [ ] **T009-02** `tests/test_config.py`: cargar el YAML real, verificar claves y tipos. Depende de T009-01.
- [ ] **T009-03** `src/main.py`: instanciación de los 5 componentes principales a partir de config (INT-FR-001). Depende de T009-01, y de 003/004/005/006/002 mínimamente implementados.
- [ ] **T009-04** `src/main.py`: loop principal con la rama "sin mano" vs. "con mano" (INT-FR-002/003/004), siguiendo el pseudocódigo de `plan.md` Sección 3. Depende de T009-03.
- [ ] **T009-05** `src/main.py`: disparo de φ + ejecutor cuando `EstabilizadorGesto` confirma (INT-FR-005), manteniendo `ultima_accion` para 008 (INT-FR-006). Depende de T009-04, y de 002/007.
- [ ] **T009-06** `src/main.py`: integrar `dibujar_frame()` (008) y mostrar la ventana con `cv2.imshow`. Depende de T009-05, y de 008.
- [ ] **T009-07** `src/main.py`: salida limpia con tecla `q` + `try/except` por frame (INT-FR-007/008).
- [ ] **T009-08** Checklist de humo end-to-end completo: ejecutar los 6 gestos 20+ veces cada uno, registrar aciertos → **medición real de SC-G01**. Depende de T009-07.
- [ ] **T009-09 [P]** Medir FPS sostenido durante 5 minutos → **SC-G02**. Depende de T009-07.
- [ ] **T009-10 [P]** Medir latencia gesto-estable→acción en ≥20 disparos → **SC-G03**. Depende de T009-07.
- [ ] **T009-11** `README.md`: instalación, permisos de macOS (cámara + Accesibilidad), cómo correr `main.py` y cómo correr `src/algebra/analisis.py` por separado.
- [ ] **T009-12** Ensamblar `docs/reporte_tecnico.pdf` con evidencia de T009-08/09/10 más lo ya documentado en `docs/demostraciones.md` (de 001, 002, 005).

**Definición de hecho:** `pytest tests/test_config.py` en verde; `python src/main.py` corre end-to-end con cámara real, los 6 gestos producen su acción correspondiente, y las 3 mediciones de éxito (SC-G01/02/03) están registradas con números reales, no solo "funcionó en la demo".
