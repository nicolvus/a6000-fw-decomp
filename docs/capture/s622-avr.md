# S622 — `[AVR]`: clase de accesorio LANC-AVR de ACCY

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**2 trazas · 2 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s622_avr/avr.json).

## Qué es

`[AVR]` identifica una clase de accesorio de `ACCY`. [S104](s104-prefixes-a6000.md) documenta `LANC-AVR Attached` y handlers GPIO. Se retira la expansión Audio/Video Rendezvous: la coincidencia con otros símbolos AVR no prueba identidad de subsistema.

## Las 2 trazas (vaddr → texto corto)

```
0x43c25502 [ACCY][DEBUG][AVR] NotifyDetached(%d)
0x43c25528 [ACCY][DEBUG][AVR] NotifyAttached(%d)
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][DEBUG][AVR]` — módulo padre `ACCY` (accesorio) + nivel `DEBUG` + clase de accesorio `AVR`. Longitud total: 18 B (`[ACCY][DEBUG][AVR]`).
- **Notificaciones de conexión**: 2 trazas `DEBUG` — `NotifyAttached(%d)` (conectado) y `NotifyDetached(%d)` (desconectado), ambas con parámetro numérico (`%d`, probablemente ID de dispositivo o handle).
- **Logger dual (patrón S177/S179/S603–S621)**: la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA): nueva con prefijo `[ACCY][DEBUG][AVR]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 18 B (`[ACCY][DEBUG][AVR]`) → fijo (ambas trazas son nivel DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulos `HOUSING` (S610), `SENSER` (S619), `AVOUT` (S621), `AVR` (S622).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][DEBUG][AVR]` | **2** | **0** | **0** |
| núcleos sin prefijo (`NotifyAttached`, `NotifyDetached`) | 0/2 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AccyUmDeviceAvr`, `AVRendezvous*`) | 0 | **6+** | **6+** |
| código equivalente (NO_VERIFICADO - requiere comparación de instrucciones) (AVRendezvous, etc.) | `0x43c25502`… | **sí** | **sí** |

**NO_VERIFICADO:** la equivalencia con `AVRendezvous*` y la duplicación del logger no se deducen de los nombres. El diferencial de cadenas no demuestra equivalencia de código.

**Longitud del prefijo fija:** 18 B (`[ACCY][DEBUG][AVR]`) → fijo (ambas trazas son nivel DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **notificaciones de conexión/desconexión del accesorio AVR**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 2/2 cadenas `[ACCY][DEBUG][AVR]` confirmadas en `0x43c25502`–`0x43c25528`.
- 0/0 en A7S y A6300 para token `[ACCY][DEBUG][AVR]`; 6+ strings AVR relacionadas en A7S/A6300 sin prefijo ACCY.
- Scripts: `analysis/s622_avr/` (pendiente) · Tests: `tests/test_s622_avr.py`.
