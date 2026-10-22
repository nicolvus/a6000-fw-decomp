# Backlog del Agente A — Sensor y driver: A7S (IMX235) vs A6000 (IMX210)

Sesiones asignadas: S200–S299. Un tema = una sesión. Estado: TODO | DOING | DONE <hash> | BLOCKED <causa>.

Referencia base: S57 (IMX210 ID1–8 / ShutMode / SSB / SyncMode / XPI) y S58 (AE productor, matriz IMX235, emulación A7S, diferencias Silent 0x4c/0x4d/0x4e/0x4f). S169: A7S y A6000 tienen 0/0 `CheckSet*` de LiroSeq → la A7S implementa el silent shutter por otra vía (drive mode, tabla de timings o mensaje a Liro).

## Ítems hechos

- [x] S200 DONE — Setup: backlog, contradiction-audit de S57/S58/S169 (vigentes), encuesta de cobertura, definición del alcance (registros y tiempos no cubiertos; una tabla por subsistema).
- [x] S201 DONE — Comparación de registros A7S↔A6000 por subsistema (11 filas: 4 idénticos, 7 distintos, 0 ausentes en A6000) + vía de Silent de la A7S (drive mode tipo==2 → 0x4e/0x4f, selector 0x43826d58, sin LiroSeq/ForLiro). Informe docs/capture/s201-imx210-imx235-registers.md; JSON analysis/s201_imx210_imx235_registers/compare.json; tests test_s200 + test_s201 (14 verdes).
- [x] S202 DONE — Tiempos de lectura/exposición en profundidad: svd/shd/spl (IMX210 ID3-ID8) vs columnas modo IMX235 (0x4e/0x4f), fórmula svd (0x4381106c), contador VD, lectura 4176 líneas ≈ 66,8 ms, fin de integración. Informe docs/capture/s202-imx210-imx235-timing.md; JSON analysis/s202_imx210_imx235_timing/timing.json; test test_s202 (4 verdes).
- [x] S203 DONE (incorporada en S201) — Cómo implementa la A7S el silent shutter sin CheckSet*: drive mode (tipo==2 → 0x4e/0x4f) + tabla de timings; sin LiroSeq (0/0) ni ForLiro (rechazado).
- [x] S204 DONE — Clasificación final resumida + veredicto sobre qué falta en la A6000 (docs/capture/s204-clasificacion-final.md). Ciclo cerrado: S51 sin cambios (A=NO, B=NO, C=NO).
- [x] S205 DONE — Escritor de `S[0]` (selector de fila IMX210) y origen del bloque de modo `G+0x224` (`0x43eb07fc`). Análisis de bytes (REA daemon no terminó el autoanálisis en tiempo; se usó Capstone/bytes como respaldo, verificando lo decisivo contra instrucciones). Hallazgos: `0x43843a44` es función de staging real (copia 4 bancos de 16 B desde `origen+0x2c` a `destino+0x64`); 0 slots GOT apuntan a S; 0 stores absolutos a S; escritor de `S[0]` NO_VERIFICADO (S se pasa por puntero en registro). Informe docs/capture/s205-imager-s0-writer.md; tests test_s205 (6 verdes).
- [ ] S206 DOING — Tabla completa de los 119 registros sombra IMX210 (S56 rec_map) vs los 35 registros matriz IMX235 (S57), dirección por dirección y función por función; clasificación idéntico / distinto / ausente en A6000 por subsistema (modo, tiempo, exposición, lectura, P2S, SIF).
- [ ] S207 TODO — ¿La A7S/IMX235 tiene algún registro o mecanismo de fin de integración o segunda cortina electrónica que falte al IMX210? Barrido de bytes en la matriz IMX235 y código A7S buscando registros de fin/exposición no presentes en la tabla IMX210.
- [x] S208 DONE — Transporte P2S y formato de trama A6000 vs A7S: idénticos (cabecera 0x81, dirección 16 bit, dato 8 bit, trama 81|len|81|AH AL|datos; sin byte extra en A7S, S56-16). Clasificación IDÉNTICO. Informe docs/capture/s208-p2s-transport.md; JSON analysis/s208_p2s_transport/p2s_transport.json; tests (9 verdes, 52 totales S200-S208).

## Ítems derivados (bloqueados por cámara/autorización)

- [ ] (derivado) Datasheet IMX210/IMX235 o traza pasiva CIS0+XPI+VD para demostrar fin de integración (requiere autorización física; ver physical-test-plan.md P0–P2/P7). Anotado en knowledge/agents/NEEDS-HUMAN.md.
