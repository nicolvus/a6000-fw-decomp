# S619 — `[SENSER]`: módulo de sensor (sensor de audio/imagen) exclusivo de la A6000 fw3.21

**3 trazas · 3 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s619_senser/` (pendiente) / `.json` (pendiente).

## Qué es

`[SENSER]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 3 mensajes del **módulo senser (sensor de audio/imagen / controlador de sensor)** dentro del módulo ACCY (Accesorio). La sigla **SÍ tiene base textual**: `SENSER` → **SENS**or / **SER**ial / **S**ensor **ER**ror (controlador de sensor, probablemente de audio/micrófono o sensor de imagen). `ACCY` → **ACC**essor**Y** (accesorio).

## Las 3 trazas (vaddr → texto corto)

```
0x43c24f68 [ACCY][ERR][SENSER] unknown block %04X
0x43c24f8f [ACCY][DEBUG][SENSER] Cmd %04X, S1 %02X
0x43c24fb7 [ACCY][ERR][SENSER] unknown command %04X
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][ERR/DEBUG][SENSER]` — módulo padre `ACCY` (accesorio) + nivel `ERR`/`DEBUG` + sub-módulo `SENSER` (sensor). Longitud total variable: 20 B (`[ACCY][ERR][SENSER]`) / 21 B (`[ACCY][DEBUG][SENSER]`).
- **Manejo de errores**: 2 trazas `ERR` — `unknown block %04X` (bloque desconocido) y `unknown command %04X` (comando desconocido).
- **Debug**: 1 traza `DEBUG` — `Cmd %04X, S1 %02X` (comando recibido + estado S1).
- **Logger dual (patrón S177/S179/S603–S618)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ACCY][ERR/DEBUG][SENSER]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijos variables**: 20 B (`[ACCY][ERR][SENSER]`) / 21 B (`[ACCY][DEBUG][SENSER]`) → no fijos (depende del nivel ERR/DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulo `SENSER` (y `HOUSING` en S610).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[SENSER]` con prefijo ACCY | **3** | **0** | **0** |
| núcleos sin prefijo ACCY (`unknown block`, `unknown command`, `Cmd %04X`) | 0/3 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AdfSenserCtrl`, `MCSENSERR`, `Senser`, etc.) | 0 | **20+** (prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>`) | **20+** (prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>`) |
| código equivalente (SenserCtrl, SenserPacket, etc.) | `0x43c24f68`… | **sí** | **sí** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** El controlador de sensor (SenserCtrl, SenserPacket, SenserDiag, etc.) **existe en los tres firmware** (misma funcionalidad: comandos de audio/sensor, SetParam, diagnóstico). Lo propio de la fw3.21 de la A6000 son **las 3 trazas con prefijo `[ACCY][ERR/DEBUG][SENSER]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 usan prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>` para el mismo código SenserCtrl.

**Longitud del prefijo variable:** 20–21 B (`[ACCY][ERR][SENSER]` / `[ACCY][DEBUG][SENSER]`) → no fija (depende del nivel ERR/DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **controlador de sensor (audio/imagen), comandos y errores**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 3/3 cadenas `[ACCY][ERR/DEBUG][SENSER]` confirmadas en `0x43c24f68`–`0x43c24fb7`.
- 0/0 en A7S y A6300 para token `[ACCY][ERR/DEBUG][SENSER]`; 20+ strings senser relacionadas en A7S/A6300 con prefijos distintos.
- Scripts: `analysis/s619_senser/` (pendiente) · Tests: `tests/test_s619_senser.py` (pendiente).