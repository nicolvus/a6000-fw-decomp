# S120 — `[IDT_OPD]`: la segunda instancia del módulo IDT (mapas de imagen)

> Informe completo: [`analysis/s120_idt_opd/idt_opd.md`](../../analysis/s120_idt_opd/idt_opd.md) ·
> datos: [`analysis/s120_idt_opd/idt_opd.json`](../../analysis/s120_idt_opd/idt_opd.json) ·
> tests: [`tests/test_s120_idt_opd.py`](../../tests/test_s120_idt_opd.py)

## Qué es

`[IDT_OPD]` es el **prefijo de traza de la instancia "OPD" del módulo IDT** (el que calcula
los mapas de imagen que consume el imager). En la fw3.21 de la A6000 hay **274 trazas**
`[IDT_OPD]`, todas en un bloque contiguo de cadenas (`0x43cf11f9`–`0x43cf5810`), y **cada
una va seguida de su gemelo `[IDT]`** (274 parejas exactas).

## Hallazgos

- **No es una sigla inventada**: `IDT_OPD` es un **recurso** del `SyncResMgr`
  (`RESOURCE_IDT_OPD`, `0x43c9c461`) y una **tarea/comando**
  (`IDT_OPD_TOP_Sync_OPDAcquire`, `IDT_OPD_TOP_Sync_SetFOPD`).
- **La duplicación es de instrumentación, no de código**: las mismas funciones emiten las dos
  variantes (135 funciones contienen ambas). Verificado a mano en `0x439f85d4` y `0x439ee7e8`:
  la cadena `[IDT_OPD]: …` va al emisor de mensaje estructurado (`0x439f80b8` / `0x439ec5b0`,
  registro de 0x9a B) y la `[IDT]: …` al `printf` de consola (`0x436ce4cc`).
- **Estructuras de bloque verificadas** (desensamblando):
  - bloque **IE** (`IE_CCinit`, `0x439e80c8`): 19 campos — `tar_num`(+0x00), `isSpectRef`(+0x0c),
    `isMapOut`(+0x0d), `refmap`(+0x10), `r/g/b val.high|low`(+0x16…+0x24), `ie_miniraw`(+0x54),
    `ie_offset`(+0x58), `ie_imgwidth/height/addnum/aspect`(+0x5c…+0x62), `ie_out`(+0x70),
    `imgmap`(+0x74), `backImgData`(+0x78).
  - bloque **MAP** (`0x439ee7e8`): 18 campos — `miniraw`(+0x0c), `offset`(+0x10),
    `imgwidth/height/addnum/aspect`(+0x14…+0x1a), `x_size/y_size/x.sel/y.sel/x.span/y.span`
    (+0x28…+0x30), `shade_map`(+0x38), `4cmap`(+0x3c), `histmap`(+0x40), `summap`(+0x44),
    `out_opd_cc`(+0x48), `out_opd_ec`(+0x4c), `input`(+0x54).
  - los **18 punteros** del volcado `0x439f85d4` viven en `0x43f41b30`, `0x43f41cbc`,
    `0x43f418a8` y 5 globales sueltos (`msain0/1`, `msaout`, `mapRC_in`, `refmap`).
- **Relaciones**: el `IMAGING_CAP` (S106) dispara el `KickFOPD` (`0x43cadd2d/60/8f`); el
  `SyncResMgr` (S112) reparte `RESOURCE_IDT_OPD` (`0x43c9c2fc`, `0x43cb0f3e`); el
  `CAMERA_MAIN_LC` consume el **miniRAW** (`0x43c9c8ba`); el IDT corre en **HS3@CPU0**
  (`0x43ca12f6`). **El driver del imager (S115) no nombra el IDT**: la relación es por puntero.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| trazas `[IDT_OPD]` | **274** | **0** | **0** |
| trazas `[IDT]` | 298 | 306 | 382 |
| `RESOURCE_IDT_OPD` | sí | sí | sí |
| mensajes comunes (texto sin prefijo) | — | **270 de 274** | 270 de 274 |

→ la A7S y la A6300 **tienen la instancia OPD** (recurso y comandos) pero **no la etiquetan**;
la A6000 fw3.21 solo añade la doble instrumentación. 4 mensajes son reformulaciones
(`Sync rate`, `det:xs:…`, `test`, `test2`); 36 mensajes son propios de la A7S (16 de ellos
`PBL … ERROR. R0./W0./W1./W2.` por canal).

## Abierto

Qué hace la instancia OPD frente a la "IDT" normal; layout completo del bloque LC (0x60 B) y
del array `waku` (0x8c B); formato/tamaño en bytes de cada mapa; quién consume finalmente los
mapas (el DFE, por puntero); significado de `tar_num`, `isSpectRef`, `isMapOut`, `msain0/1`,
`msaout`, `kido_th`, `ratio_wak`, `sel_hist/sel_sum`, `gle`, `SGC`.

Tests: `.venv/bin/python -m pytest tests/test_s120_idt_opd.py -q`
