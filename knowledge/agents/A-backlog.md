# Backlog del Agente A — Sensor y driver: A7S (IMX235) vs A6000 (IMX210)

Sesiones asignadas: S200–S299. Un tema = una sesión. Estado: TODO | DOING | DONE <hash> | BLOCKED <causa>.

Referencia base: S57 (IMX210 ID1–8 / ShutMode / SSB / SyncMode / XPI) y S58 (AE productor, matriz IMX235, emulación A7S, diferencias Silent 0x4c/0x4d/0x4e/0x4f). S169: A7S y A6000 tienen 0/0 `CheckSet*` de LiroSeq → la A7S implementa el silent shutter por otra vía (drive mode, tabla de timings o mensaje a Liro).

## Ítems hechos

- [x] S200 DONE — Setup: backlog, contradiction-audit de S57/S58/S169 (vigentes), encuesta de cobertura, definición del alcance (registros y tiempos no cubiertos; una tabla por subsistema).
- [x] S201 DONE — Comparación de registros A7S↔A6000 por subsistema (11 filas: 4 idénticos, 7 distintos, 0 ausentes en A6000) + vía de Silent de la A7S (drive mode tipo==2 → 0x4e/0x4f, selector 0x43826d58, sin LiroSeq/ForLiro). Informe docs/capture/s201-imx210-imx235-registers.md; JSON analysis/s201_imx210_imx235_registers/compare.json; tests test_s200 + test_s201 (14 verdes).
- [x] S202 DONE — Tiempos de lectura/exposición en profundidad: svd/shd/spl (IMX210 ID3-ID8) vs columnas modo IMX235 (0x4e/0x4f), fórmula svd (0x4381106c), contador VD, lectura 4176 líneas ≈ 66,8 ms, fin de integración. Informe docs/capture/s202-imx210-imx235-timing.md; JSON analysis/s202_imx210_imx235_timing/timing.json; test test_s202 (4 verdes).
- [x] S203 DONE (incorporada en S201) — Cómo implementa la A7S el silent shutter sin CheckSet*: drive mode (tipo==2 → 0x4e/0x4f) + tabla de timings; sin LiroSeq (0/0) ni ForLiro (rechazado).
- [x] S204 DONE — Clasificación final resumida + veredicto sobre qué falta en la A6000 (docs/capture/s204-clasificacion-final.md). Ciclo cerrado: S51 sin cambios (A=NO, B=NO, C=NO).
- [x] S205 — [Contrato recuperado el 25-10-2026](../../docs/capture/s205-imager-s0-writer.md): slot GOT `0x44020c9c → S=0x43eb35d0`; quinto argumento de `0x43843a44`. `0x43843a5e` escribe `S[0]=u8(*(ctx+0x20)+1)`. Para selector 3 copia cuatro filas de 16 B desde `G+0x224+0x2c+16*i` a `S+0x64+16*i`. El negativo antiguo solo cubría un rango GOT que excluía el slot real. Productores anteriores del selector y efecto eléctrico siguen abiertos.
- [x] S206 — Publicada la [tabla de 119 entradas](../../docs/capture/s206-imx210-imx235-full-table.md) y su verificador en `analysis/s206_imx210_imx235_full_table/`. La clasificación por dirección no resuelve la equivalencia funcional de los 112 registros restantes.
- [x] S207 — Publicado el [barrido de cadenas y matriz](../../docs/capture/s207-imx235-end-of-integration.md). El negativo textual no demuestra ausencia de fin de integración ni identidad funcional entre sensores.
- [ ] S206/S207 — Resolver correspondencia funcional y mecanismo de fin de integración. NO_VERIFICADO: los informes publicados no cierran esta pregunta.
- [x] S208 DONE — Transporte P2S y formato de trama A6000 vs A7S: idénticos (cabecera 0x81, dirección 16 bit, dato 8 bit, trama 81|len|81|AH AL|datos; sin byte extra en A7S, S56-16). Clasificación IDÉNTICO. Informe docs/capture/s208-p2s-transport.md; JSON analysis/s208_p2s_transport/p2s_transport.json; tests (9 verdes, 52 totales S200-S208).

## Ítems derivados

- [ ] Buscar documentación técnica IMX210/IMX235 que permita interpretar los registros. Es trabajo documental; no requiere cámara.
- [ ] Traza pasiva CIS0+XPI+VD para observar fin de integración: diferida hasta terminar la ingeniería inversa necesaria. Ver [NEEDS-HUMAN](NEEDS-HUMAN.md).
