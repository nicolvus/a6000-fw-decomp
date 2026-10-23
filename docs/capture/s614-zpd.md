# S614 — `[ZPD]`: módulo ZPD (Phase Detection AF) exclusivo de la A6000 fw3.21

**5 trazas · 5 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s614_zpd/` (pendiente) / `.json` (pendiente).

## Qué es

`[ZPD]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes del **módulo ZPD (Zone Phase Detection / Phase Detection AF)** que gestiona la secuencia de acoplamiento de lente, carga de datos DRA (Defect Reduction Algorithm?), y carga de datos de lente desde la lente o desde el cuerpo. La sigla **SÍ tiene base textual**: `ZPD` → **Z**one **P**hase **D**etection / **Z** **P**hase **D**etection AF (enfoque automático por detección de fase zonal).

## Las 5 trazas (vaddr → texto corto)

```
0x43ccf2d7 [ZPD]: lens attach sequence end.
0x43ccf2f8 [ZPD]: load dra data.
0x43ccf31f [ZPD]: load lens data from lens.
0x43ccf340 [ZPD]: load lens data from body.
0x43ccf361 [ZPD]: load:%s
```

## Hallazgos con dirección

- **Secuencia de acoplamiento**: `lens attach sequence end` — finalización de la secuencia de acoplamiento de lente (comunicación montura-cuerpo).
- **Carga de datos DRA**: `load dra data` — carga de datos DRA (Defect Reduction Algorithm / algoritmo de reducción de defectos) para corrección de píxeles defectuosos.
- **Carga de datos de lente**: dos fuentes — `from lens` (desde la lente, EEPROM de la lente) y `from body` (desde el cuerpo, caché local).
- **Carga genérica**: `load:%s` — función genérica de carga con nombre de recurso como parámetro.
- **Logger dual (patrón S177/S179/S603–S613)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ZPD]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo simple**: 5 B (`[ZPD]: `) → uno de los prefijos más cortos de la serie (S605: 7 B, S606: 10 B, S607: 10 B, S608: 10 B, S610: 21 B, S611: 27 B, S612: 25 B, S613: 16 B).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ZPD]` | **5** | **0** | **0** |
| núcleo sin prefijo (`lens attach sequence end`, `load dra data`, `load lens data from lens/body`, `load:%s`) | 0/5 como literal autónomo | **0** | **0** |
| strings ZPD relacionadas A7S | 0 | **30+** (sin prefijo, `[Err]`, `ZpdPre`, `StartZpdPre`, `ZPD FLASH`, etc.) | **50+** |
| código equivalente (ZPD, DRA, carga lente) | `0x43ccf2d7`… | **sí, sin prefijo** | **sí, sin prefijo** |

→ **Módulo *nuevo* en traza, código preexistente.** El subsistema ZPD (Phase Detection AF, DRA, carga de datos de lente) **existe en los tres firmware** (misma funcionalidad: secuencia de acoplamiento, DRA, carga de datos de lente desde lente/cuerpo). Lo propio de la fw3.21 de la A6000 son **las 5 trazas con prefijo `[ZPD]: `**. En A7S/A6300 el subsistema ZPD existe (70+ strings ZPD relacionadas) pero **sin prefijo unificado `[ZPD]: `** — usan prefijos dispersos (`[Err]`, `StartZpdPre`, `ZpdPre`, `ZPD FLASH`, `ZPD_SRAM`, etc.). La fw3.21 **unifica** bajo `[ZPD]: ` y **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global `0x43902718`).

**Longitud del prefijo fija:** 5 B (`[ZPD]: `) → el más corto de la serie.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **AF por detección de fase y carga de datos de lente/DRA**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[ZPD]: ` confirmadas en `0x43ccf2d7`–`0x43ccf361`.
- 0/0 en A7S y A6300 para token `[ZPD]`; 30+/50+ strings ZPD relacionadas en A7S/A6300 (sin prefijo unificado).
- Scripts: `analysis/s614_zpd/` (pendiente) · Tests: `tests/test_s614_zpd.py` (pendiente).