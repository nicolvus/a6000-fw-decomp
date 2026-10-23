# S625 — `[ADR]`: campo de dirección dentro de una traza CAM_UTIL_SENS

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**1 traza · 1 sitio (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s625_adr/adr.json).

## Qué es

`[ADR]` es un campo de dirección dentro de una traza de `CAM_UTIL_SENS`, no un módulo independiente. [S104](s104-prefixes-a6000.md) ya distinguía este campo; su presencia no demuestra una funcionalidad nueva.

## La traza (vaddr → texto corto)

```
0x43cce3fa [CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x
```

## Hallazgos con dirección

- **Prefijo compuesto**: `[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x` — módulo `CAM_UTIL_SENS` (Camera Utility Sensor) reporta número de archivo, dirección y tamaño. Longitud del token `[ADR]` dentro del mensaje: 5 B (`[ADR]`).
- **Estructura de datos**: reporta `FILE_NUM` (número de archivo), `ADR` (dirección), `SIZE` (tamaño) — típico de logging de operaciones de archivo/memoria.
- **Logger dual (patrón S177/S179/S603–S624)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo compuesto**: el token `[ADR]` aparece dentro de un mensaje mayor, no como prefijo standalone.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ADR]` standalone | **0** | **0** | **0** |
| token `[ADR]` dentro de mensaje `CAM_UTIL_SENS` | **1** | **0** | **0** |
| strings relacionadas A7S (`ADR` suelto) | 0 | **50+** (`[ADF]...Adr`, `StartAdr`, `StopAdr`, `dataAdr`, `buffAdr`, etc.) | **50+** (similares) |
| código equivalente (CAM_UTIL_SENS) | `0x43cce3fa`… | **parcial** | **parcial** |

→ **Token *nuevo* en traza, código preexistente.** El token `[ADR]` dentro de mensajes de `CAM_UTIL_SENS` **no existe en A7S/A6300** (usan `Adr`, `adrs`, `Adr` sueltos sin brackets). Lo propio de la fw3.21 de la A6000 es **la traza con token `[ADR]` explícito** dentro del mensaje de `CAM_UTIL_SENS`. La fw3.21 **duplica** la traza (nueva con logger de módulo + vieja con logger global `0x43902718`).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **logging de direcciones de archivo/memoria**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 1/1 cadena `[ADR]` dentro de `[CAM_UTIL_SENS]` confirmada en `0x43cce3fa`.
- 0/0 en A7S y A6300 para token `[ADR]` standalone o dentro de `CAM_UTIL_SENS`; 50+ strings `Adr`/`adr`/`ADR` sueltas en A7S/A6300.
- Scripts: `analysis/s625_adr/` (pendiente) · Tests: `tests/test_s625_adr.py`.
