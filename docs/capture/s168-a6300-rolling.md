# S168 — control positivo del «rolling shutter» del A6300: la cadena es **muerta**

> Hito de la **línea de ingeniería inversa general** (control positivo para la línea del
> obturador electrónico). Solo bytes: `av-cam.bin` de la A6000 fw3.21, la A7S fw3.20 y el
> A6300 fw2.01. Convención: `vaddr = 0x43541000 + file_offset`.

## Veredicto

**La cadena `position num in rolling is strange %d` del A6300 fw2.01 (`0x43d9fe03`) no la
referencia NINGÚN código**: es una **cadena muerta** en `.rodata`. Por tanto **no** demuestra
que el A6300 fw2.01 implemente compensación de *rolling shutter*.

La única cadena viva de su entorno es `position num in vd is strange %d` (`0x43d9fde2`), y el
código que la emite (`0x4372914c`) es un **cálculo de ancho en bits del número de posición del
VD** con control de rango (`(1<<n)-1 <= 0xFE`; si no cabe, avisa y fuerza 8 bits).

## Método (reutilizable)

Tres herramientas parametrizadas en `analysis/s168_a6300_rolling/`:

| script | qué hace |
|---|---|
| `scan_refs.py` | réplica de la **regla estricta** canónica (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) con *blob* y *base* como parámetros |
| `find_ref.py` | **método inverso independiente**: `add_addr = destino − W − 4`, comprobando el `add rD,pc` y el `ldr` más cercano |
| `alive_map.py` | mapa vivo/muerto de una banda de `.rodata` (refs PIC + punteros absolutos + pares `movw`/`movt`) |

**Controles:** en la A6000, `Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)` (`0x43c7751a`, S166)
→ **1** referencia (`ldr 0x43636ce2` + `add 0x43636ce6`); en el A6300,
`position num in vd is strange %d` → **1** referencia (`ldr 0x43729164` + `add 0x43729166`).

## Evidencia

| cadena (A6300 fw2.01) | dirección | refs PIC | puntero abs. | `movw/movt` |
|---|---|---|---|---|
| `[BL]Wait_BL_ASYNC_RCV (%+hd)` | `0x43d9fdc5` | 1 | 0 | 0 |
| `position num in vd is strange %d` | `0x43d9fde2` | **1** | 0 | 0 |
| `position num in rolling is strange %d` | `0x43d9fe03` | **0** | 0 | 0 |
| `this vsync command has another command` | `0x43d9fe29` | 1 | 0 | 0 |
| `ASYNC BL COMMAND BANISH ! Mount_FcZm_BLComm.cpp %d` | `0x43d9fe50` | 1 | 0 | 0 |

4 de 5 cadenas de la banda `0x43d9fd80`–`0x43d9fe80` están referenciadas; **exactamente una —
la del *rolling*— no**. La cadena tampoco aparece en ningún otro fichero del paquete del A6300
(solo en `av-cam.bin`).

## Diferencial

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `position num in rolling is strange %d` | 0 | 0 | **1** (`0x43d9fe03`) |
| refs de código de esa cadena | — | — | **0 (muerta)** |
| `position num in` / `strange %d` | 0 / 0 | 0 / 0 | **2 / 2** |

## Excepciones de `roll` (no son *rolling shutter*)

Tres casos reales en la A6000, que **no** son el concepto *rolling shutter*:
`SetDistRoll` `0x43c7b1f3` (1/1/1), `SetRoll` `0x43c7fc61` (1/1/1) y
`RollAD,%d,%d,%d,%d,%d,%d,%d,%d` `0x43c9ae2e` (**1/0/0**, propio de la fw3.21 de la A6000).
`SetRoll`/`SetDistRoll` son **comandos de la API RC** (junto a `SetStblzPower`, `SetDistItp`,
`SetHoldX/Y`, `SetSync`, `SetMirror`); `RollAD` imprime 9 valores AD leídos de un global
(`0x437212b8`). Su análisis detallado está en el hito **S169**.

## Corrección que impone sobre S164

La revisión de S164 afirmaba que «el concepto de *rolling shutter* **existe en el A6300**». Eso
**queda matizado**: la cadena existe, pero **está muerta** → no prueba la existencia del
concepto en ese firmware. **No cambia S51** (A=NO, B=NO, C=NO) ni S135 (control positivo del
subsistema `ElecShutter/` en el HAL del A6300, que es independiente de esta cadena); de hecho
**debilita** un argumento potencial.

Informe: [analysis/s168_a6300_rolling/rolling.md](../../analysis/s168_a6300_rolling/rolling.md) ·
test: `tests/test_s168_a6300_rolling.py` (16 tests).
