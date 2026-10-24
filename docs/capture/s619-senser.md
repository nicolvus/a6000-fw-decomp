# S619 — `[SENSER]`: interfaz SENSER de servicio/accesorios exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**3 trazas · 3 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s619_senser/senser.json).

## Qué es

`[SENSER]` aparece en mensajes de comandos bajo `ACCY`. Las cadenas no demuestran que sea un sensor de audio o imagen ni permiten expandir la sigla. Esa interpretación histórica se retira; el contrato de servicio requiere seguir las llamadas.

## Las 3 trazas (vaddr → texto corto)

```
0x43c24f10 [ACCY][ERR][SENSER] unknown block %04X
0x43c24f37 [ACCY][DEBUG][SENSER] Cmd %04X, S1 %02X
0x43c24f5f [ACCY][ERR][SENSER] unknown command %04X
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][ERR/DEBUG][SENSER]` — módulo padre `ACCY` (accesorio) + nivel `ERR`/`DEBUG` + sub-módulo `SENSER` (sensor). Longitud total variable: 19 B (`[ACCY][ERR][SENSER]`) / 21 B (`[ACCY][DEBUG][SENSER]`).
- **Manejo de errores**: 2 trazas `ERR` — `unknown block %04X` (bloque desconocido) y `unknown command %04X` (comando desconocido).
- **Debug**: 1 traza `DEBUG` — `Cmd %04X, S1 %02X` (comando recibido + estado S1).
- **Logger dual (patrón S177/S179/S603–S618)**: la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA): nueva con prefijo `[ACCY][ERR/DEBUG][SENSER]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijos variables**: 19 B (`[ACCY][ERR][SENSER]`) / 21 B (`[ACCY][DEBUG][SENSER]`) → no fijos (depende del nivel ERR/DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulo `SENSER` (y `HOUSING` en S610).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[SENSER]` con prefijo ACCY | **3** | **0** | **0** |
| núcleos sin prefijo ACCY (`unknown block`, `unknown command`, `Cmd %04X`) | 0/3 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AdfSenserCtrl`, `MCSENSERR`, `Senser`, etc.) | 0 | **20+** (prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>`) | **20+** (prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>`) |
| código equivalente (NO_VERIFICADO - requiere comparación de instrucciones) (SenserCtrl, SenserPacket, etc.) | `0x43c24f10`… | **sí** | **sí** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** El controlador de sensor (SenserCtrl, SenserPacket, SenserDiag, etc.) **existe** (NO_VERIFICADO - requiere análisis de A7S/A6300) en los tres firmware (misma funcionalidad: comandos de audio/sensor, SetParam, diagnóstico). Lo propio de la fw3.21 de la A6000 son (NO_VERIFICADO - requiere xrefs/REA para confirmar duplicación de logger) **las 3 trazas con prefijo `[ACCY][ERR/DEBUG][SENSER]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 usan prefijos `[ADF][ADJ]`, `[SYS_SENSER_CA_PUTS]`, `<SACC_Debug>` para el mismo código SenserCtrl.

**Longitud del prefijo variable:** 20–21 B (`[ACCY][ERR][SENSER]` / `[ACCY][DEBUG][SENSER]`) → no fija (depende del nivel ERR/DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **controlador de sensor (audio/imagen), comandos y errores**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 3/3 cadenas `[ACCY][ERR/DEBUG][SENSER]` confirmadas en `0x43c24f10`–`0x43c24f5f`.
- 0/0 en A7S y A6300 para token `[ACCY][ERR/DEBUG][SENSER]`; 20+ strings senser relacionadas en A7S/A6300 con prefijos distintos.
- Scripts: `analysis/s619_senser/` (pendiente) · Tests: `tests/test_s619_senser.py`.
