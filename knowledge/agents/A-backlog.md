# Backlog del Agente A — Sensor y driver: A7S (IMX235) vs A6000 (IMX210)

Sesiones asignadas: S200–S299. Un tema = una sesión. Estado: TODO | DOING | DONE <hash> | BLOCKED <causa>.

Referencia base: S57 (IMX210 ID1–8 / ShutMode / SSB / SyncMode / XPI) y S58 (AE productor, matriz IMX235, emulación A7S, diferencias Silent 0x4c/0x4d/0x4e/0x4f). S169: A7S y A6000 tienen 0/0 `CheckSet*` de LiroSeq → la A7S implementa el silent shutter por otra vía (drive mode, tabla de timings o mensaje a Liro).

## Ítems

- [x] S201 DONE — Comparación de registros A7S↔A6000 por subsistema (11 filas: 4 idénticos, 7 distintos, 0 ausentes en A6000) + vía de Silent de la A7S (drive mode tipo==2 → 0x4e/0x4f, selector 0x43826d58, sin LiroSeq/ForLiro). Informe docs/capture/s201-imx210-imx235-registers.md; JSON analysis/s201_imx210_imx235_registers/compare.json; tests test_s200 + test_s201 (14 verdes).
- [x] S202 DONE — Tiempos de lectura/exposición en profundidad: svd/shd/spl (IMX210 ID3-ID8) vs columnas modo IMX235 (0x4e/0x4f), fórmula svd (0x4381106c), contador VD, lectura 4176 líneas ≈ 66,8 ms, fin de integración. Informe docs/capture/s202-imx210-imx235-timing.md; JSON analysis/s202_imx210_imx235_timing/timing.json; test test_s202 (4 verdes).
- [x] S203 DONE (incorporada en S201) — Cómo implementa la A7S el silent shutter sin CheckSet*: drive mode (tipo==2 → 0x4e/0x4f) + tabla de timings; sin LiroSeq (0/0) ni ForLiro (rechazado).
- [x] S204 DONE — Clasificación final resumida + veredicto sobre qué falta en la A6000 (docs/capture/s204-clasificacion-final.md). Ciclo cerrado: S51 sin cambios (A=NO, B=NO, C=NO).

## Ítems derivados (pendientes, se añaden al backlog futuro)

- [ ] (derivado) Datasheet IMX210/IMX235 o traza pasiva CIS0+XPI+VD para demostrar fin de integración (requiere autorización física; ver physical-test-plan.md P0–P2/P7).
- [ ] S201 TODO — Comparación de registros A7S↔A6000 no cubierta por S57/D.5: tabla por subsistema (ID1–8, ID0x100/0x101, sombra P2S, SIF sync, vectores 0x43fe995c vs A7S 0x43fee370/0x43fee598). Clasificación idéntico / distinto / ausente en A6000.
- [ ] S202 TODO — Tiempos de lectura/exposición: svd/shd/spl (IMX210) vs columnas modo de lectura IMX235 (0x4e/0x4f); fórmula svd, contador VD, unidades; fim de integración (no hay reescritura al final). Tabla comparativa.
- [ ] S203 TODO — Cómo implementa la A7S el silent shutter sin `CheckSet*` (S169): drive mode (ShutMode 0/1), tabla de timings (matriz 0x43fee598) y mensaje a Liro (si existe). Identificar la vía concreta.
- [ ] S204 TODO — Clasificación final de todas las diferencias: idéntico, distinto, ausente en A6000; cierre con tabla resumen y veredicto sobre qué falta en la A6000.

## Ítems derivados (se añaden al agotar)

(none yet)
