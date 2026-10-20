# S52/R2 — IMX235 frente a IMX210

## B2 — Unicorn offline reproducible

Ejecutar `~/.venvs/re/bin/python -I work/codex/s52/emulate_setexposure.py`. Emula el dispatcher de ShutMode sobre una copia privada; detiene en la primera llamada saliente. Los 30 casos están en `s52_shutmode_emulation.json`.

| modo | IMX235: byte final, frontera | IMX210: byte final, frontera | instrucciones diferenciales |
|---:|---|---|---|
| 0 | `cfg+4=00`; `436f2d10` | `cfg+2=40`; `436d6f50` | `436f424c..5a`; `436d70d0..de` |
| 1 | `04`; `436f2cf4` | `c4`; `436d6f34` | `436f425c..72`; `436d70e0..fe` |
| 2 | error `438f7114` | `94`, copias `param+8/+14`; `436d6f34` | `436f42fc`; `436d7114..54` |
| 3 | `14`; `4355de98` | `d4`; `4355faf0` | `436f4290..b8`; `436d7114..78` |
| 4 | `40`; `436f2d10` | `c0`; `436d6f50` | `436f42c4..ec`; `436d71a0..bc` |

Los tres SHR dan el mismo patrón hasta la frontera. Esto prueba buffers y selección de aplicador, no efecto eléctrico. B5 termina en dichas llamadas; sus contratos deben recuperarse para afirmar cola, empaquetado o MMIO.

## B4 — modos y campos

`436f3928` recorre 69 filas, elige columna y copia a punteros de campo. `s52_sensor_register_trace.csv` enumera los 48 campos distintos de columnas 0/12/13, lector y valores. Sin consumidor posterior tipado, todos quedan **NO VERIFICADO** como geometría, lectura, SHR, sincronía o cortina.

IMX210: `0x0b` y `0x2f` son modos completos conocidos 6000×4000; no existe matriz de registros equivalente. Ninguno de sus 13 modos es `0x4e/0x4f`: se descarta reutilización como código existente, no una implementación nueva.

| hipótesis | estado | evidencia / incógnita |
|---|---|---|
| H52-5: ShutMode 0 IMX210 termina integración electrónicamente | NO VERIFICADO | rama/buffer existen; falta datasheet o traza pasiva |
| H52-7: modo completo permite foto silenciosa A6000 como código existente | DESCARTADO | no `4e/4f`, ni ruta Silent/política |
