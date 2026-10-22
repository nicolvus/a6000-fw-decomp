# S603 — `[CAMERA_DSP_APL]`: el driver APL de cámara (DSP) — etiqueta nueva de la fw3.21

**18 trazas · 22 sitios (regla PIC estricta) · ~6 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s603_camera_dsp_apl/` (pendiente) / `.json` (pendiente).

## Qué es

`[CAMERA_DSP_APL]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 18 mensajes del **driver APL (Application) de la cámara/DSP** que gestiona memoria eSRAM/DDR, direcciones DMA para bloques de procesamiento de imagen (TAR, ME, MBL, HME, REF), y control del bloque IIB (Image Input Block). La sigla **SÍ tiene base textual**: `APL` → **A**pplication **P**rocessing **L**ayer / **A**PL driver; `DSP` → **D**igital **S**ignal **P**rocessing; `CAMERA` → submódulo de cámara. `CAMERA_DSP_APL` no se expande en ninguna cadena (NO VERIF.).

## Las 18 trazas (vaddr → texto corto; sitio y función en análisis pendiente)

```
0x43c901da [Error] cannot free reference memory
0x43c90211 [Error] MemOpen (%X)
0x43c90238 [Error] sapl_mov_stop - TIMEOUT
0x43c9026a [Error] sapl_SetDmaAddrTar - MEMORY_TARGET
0x43c902a7 [Error] sapl_SetDmaAddrMEOut - MEMORY_MEPRIVATE
0x43c902e9 [Error] sapl_SetDmaAddrMEOut - MEMORY_MEPRIVATE 4K2K CORE1
0x43c90336 [Error] sapl_SetDmaAddrOut - FMT_SRC_REF0_ADDR is NULL
0x43c9037f [Error] sapl_SetDmaAddrMBLOut - MEMORY_MARBLEOUT
0x43c903c2 [Error] sapl_SetDmaAddrMBLOut - MEMORY_MEPRIVATE 4K2K CORE1
0x43c90410 [Error] sapl_SetDmaAddrOut - HME_COPY_SRC_ADDR is NULL
0x43c90459 [Error] sapl_SetDmaAddrParamBuffer - MEMORY_ESRAM
0x43c904af [Error] APL Small eSRAM Alloc (%X)
0x43c904e4 [Error] APL LGR eSRAM Alloc (%X)
0x43c90517 [Error] APL Small eSRAM Free (%X)
0x43c9054b [Error] APL LgrDl eSRAM Free (%X)
0x43c9057f [Error] APL Base DDR Free (%X)
0x43c905b0 [Error] APL TAR DDR Free (%X)
0x43c905e0 [APL Driver] IIB stop Timeout No=%x, IIB_STT=%x
```

## Hallazgos con dirección

- **Función principal de error**: `FUN_436bd784` (0x436bd784, 162 B) — logger común que emite todas las trazas `[CAMERA_DSP_APL]` con módulo propio (id no determinado aún), nivel ERROR (10), y formato `(nivel, flag, fmt, …)`. Llamada desde 14+ sitios en `FUN_436be5ac`, `FUN_436bd830`, `FUN_43a2ff90`, etc.
- **Función de setup APL**: `FUN_436be5ac` (0x436be5ac, 1424 B) — función mayor que configura parámetros DMA, validaciones de memoria, y emite 10+ trazas `[CAMERA_DSP_APL]` vía `FUN_436bd784` + logger global `FUN_43902770`.
- **Función de stop IIB**: `FUN_43a2ff90` (0x43a2ff90, 130 B) — bucle de parada del bloque IIB con timeout 200 iteraciones; emite traza `sapl_mov_stop - TIMEOUT` vía `FUN_43a2fee8` (wrapper) + logger global.
- **Logger global dual**: igual que S177/S179, la fw3.21 **duplica** la traza: la nueva (logger de módulo `FUN_436bd784`/`FUN_43a2fee8`) y la antigua (`bl 0x43902770` → string original SIN prefijo). Ejemplo: en `FUN_436be5ac` offset `0x436be60c` carga string `0x43c90211` (`[CAMERA_DSP_APL]: [Error] MemOpen (%X)`) y en `0x436be612` llama `0x43902770` con `0x43c90223` (string original `[Error] MemOpen (%X)` sin prefijo).
- **Estructuras de datos**: arrays indexados por `iVar1` (instancia APL, 0/1) con stride `0x38` y `0x44`; campos en offsets `+0x14` (DMA addr), `+0x1c`, `+0x20`, `+0x24`, `+0x28`, `+0x2c`, `+0x30`, `+0x34`.
- **Funciones `sapl_*`**: `sapl_mov_stop`, `sapl_SetDmaAddrTar`, `sapl_SetDmaAddrMEOut`, `sapl_SetDmaAddrOut`, `sapl_SetDmaAddrMBLOut`, `sapl_SetDmaAddrParamBuffer` — API del driver SAPL (Sony APL) para control de DMA y memoria.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAMERA_DSP_APL]` | **18** | **0** | **0** |
| núcleo sin prefijo (`[Error] sapl_*`, `[Error] APL *`, `[APL Driver] IIB...`) | 0/18 como literal autónomo | **18/18** (idénticos) | **18/18** (idénticos) |
| prefijos alternativos `[APL_ADDR]`, `[APL_SIZE]` | **0** | **12+** | **12+** |
| gemelo exacto en `vaddr+N` | **sí, longitud variable** (prefijo 21–24 B) | — | — |
| código equivalente (`sapl_*`, `FUN_436be5ac` homólogo) | `0x436bd784`… | `0x4375bxxx`… | `0x437f5xxx`… |

→ **Cambio de *logging*, no de código.** El driver APL/SAPL **existe igual** en los tres firmware (mismas 18 cadenas núcleo, mismas funciones `sapl_*`, misma estructura de datos stride `0x38`/`0x44`). Lo propio de la fw3.21 de la A6000 son **las trazas con prefijo `[CAMERA_DSP_APL]`** y la **eliminación de los prefijos `[APL_ADDR]`/`[APL_SIZE]`** que sí tienen A7S/A6300. La fw3.21 **duplica** la traza (nueva con logger de módulo + vieja con logger global `0x43902770`), salvo en `FUN_43a2ff90` donde solo usa logger propio `FUN_43a2fee8`.

**Longitud del prefijo no fija:** 21 B (`[CAMERA_DSP_APL]: [Error] `), 24 B (`[CAMERA_DSP_APL]: [APL Driver] `) → se ajusta al nivel/mensaje, igual que S177 (16 B) y S179 (14 B).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **memoria y DMA para el pipeline de imagen (APL/SAPL)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 22/22 pares PIC verificados a mano (pool, `destino = literal + (add+4)`, sin reuso de registro).
- Scripts: `analysis/s603_camera_dsp_apl/` (pendiente) · Tests: `tests/test_s603_camera_dsp_apl.py` (pendiente).