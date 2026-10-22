# S124 — el bloque de parámetros de exposición/lectura por `drive_mode` (imager) y su diferencial A6000/A7S

> Hito de la **línea de ingeniería inversa general**, con relevance directa para la línea del
> **obturador electrónico**: el parámetro `shut` ("shutter") del bloque de parámetros del imager
> es exactamente donde un obturador mecánico/electrónico tendría que manifestarse.
> Verificación contra los bytes de la A6000 fw3.21 y de la A7S fw3.20; convención
> **vaddr = 0x43541000 + file_offset**. Sin efecto en S51 (A/B/C = NO): este hito **no**
> encuentra un parámetro de obturador electrónico, sino el parámetro de *shutter* ya presente
> en la fw3.20.

## 1. Qué se pregunta

S115 decodificó la traza `[CAM_IMAGER]: SetExps : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d]
[svd:%02x] [shd:%02x] [spl:%02x] [shut:%01x]` (`0x43c93cc2`). ¿De dónde salen esos valores y
cambia la A6000 fw3.21 el bloque respecto a la A7S fw3.20?

## 2. De dónde salen los valores (A6000, lectura del código)

La función que emite la traza es `FUN_436d6f70` (encontrada por la referencia PIC de
`0x43c93cc2` en los sitios `0x436d7242` y `0x436d7280`). Su código:

| lectura | registro/dato | significado |
|---|---|---|
| `ldrh r6, [r1, #4]` | `r1+4` | **PrevDrv** (drive mode anterior) |
| `ldrh r5, [r1]` | `r1+0` | **NowDrv** (drive mode actual) |
| `ldrh r7, [r1, #6]` | `r1+6` | **NextDrv** (drive mode siguiente) |
| `ldrb.w sb, [r1, #9]` | `r1+9` | **`shut`** (un byte) |
| `ldr.w r3, [r4, #0x170]` | contexto +0x170 | `spl` |
| `ldr.w r3, [r4, #0x174]` | contexto +0x174 | `shd` |
| `ldr.w r3, [r4, #0x178]` | contexto +0x178 | `svd` |

Los argumentos se pasan a la llamada de registro así: `r6`→PrevDrv, `r5`→NowDrv, `r7`→NextDrv,
`[sp]`→svd, `[sp+4]`→shd, `[sp+8]`→spl, `[sp+0x18]`→`sb`=**shut**.

→ **`shut` es un byte del bloque de modo** (offset +9), mientras que `svd`/`shd`/`spl` son
tres u32 del **contexto de captura** (+0x170/+0x174/+0x178).

## 3. El conjunto completo de parámetros del modo

Las 5 trazas de `[CAMERA_MAIN_SYNC]` que revelan el bloque son **idénticas** en A6000 y A7S
(texto a texto):

| traza | A6000 | A7S |
|---|---|---|
| `ZAF img_id:%04X, shut:%d, svd:%d, shd:%d, spl:%d, epdsel:%d` | `0x43ca3356` | `0x43ca8e9b` |
| `Imager param error shut:%d, svr_num:%d, VdNum:%d` | `0x43cb11d2` | `0x43cb2bcd` |
| `Imager svd error. shut:%d, svd:%d -> %d` | `0x43cb1217` | `0x43cb2bfe` |
| `shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d` | `0x43cb1253` | `0x43cb2c26` |
| `vfc%d[%d] shut%d->%d(%d) zaf[%d]%d->%d(%d) fr:%d->%d(%d) cmd:%x[%x] img:%x…` | `0x43ca3a50` | `0x43ca936f` |

Es decir, el **bloque de parámetros del imager** es `{shut, svd, shd, spl, sint, gs, epdsel}` y
**existe igual en las dos cámaras**: la fw3.21 no lo cambia, solo cambia quién lo registra y con
qué formato.

## 4. Diferencial de la instrumentación (aquí sí cambia la fw3.21)

| elemento | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| traza de exposición | `[CAM_IMAGER]: SetExps : [PrevDrv][NowDrv][NextDrv][svd][shd][spl][shut]` `0x43c93cc2` | `[IMAGING]: Exposure. [NowDriveMode][NextDriveMode][svd][shd][spl][shut]` `0x43c9c942` |
| traza de cambio de modo | `[CAM_IMAGER]: SetExpsZ: …[svrz][shrz][splz][epd][epdsel]` `0x43c939b5` | `[IMAGING]: Change ImagerMode. [NowDriveMode][NextDriveMode][svd][shd][spl][shd]` `0x43c9c8d9` |
| traza de lectura | `[CAM_IMAGER]: SetRead : …[AGainCont_EC][AGainCont][AGainDrv]` `0x43c93fcb` | — (mismo bloque, otro formato) |
| **nuevo en fw3.21** | **`[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d` `0x43ca7836`** | — |
| **retirado en fw3.21** | — | `b8_shutter_limit` `0x43c9f01c` (sensor B8, no presente en la A6000) |
| estructura del contexto | `r0+0xfc` (rama de modo 0x11) | `r0+0x13c` (rama de modo 0x11) |
| rama especial | `cmp r3,#0x11` → `FUN_436d9f70` | `cmp r3,#0x11` → `FUN_436f5db8` |

Lectura: **la fw3.21 (i) reescribe el vocabulario de trazas del imager** (añade el drive mode
*anterior* y separa `SetExps`/`SetRead`/`Execute`), **(ii) cambia el layout del contexto de
captura** (el offset de la sub-estructura pasa de `+0x13c` a `+0xfc`) y **(iii) añade una traza
nueva en el módulo de calibración de lente**: `zaf_now_shut_cycle=%d`, que cuenta los ciclos de
obturación. El **conjunto de parámetros** (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`, `epdsel`)
y sus valores **son los mismos**.

## 5. Qué es `shut` (y por qué NO es un obturador electrónico)

- La cadena hermana `shutter mute on/off` (`0x43c8253b`) y `[SFRS][PINSEND] shutter mute thru`
  (`0x43ce955e` / A7S `0x43ce0d29`) hablan del **silenciador del obturador mecánico** (el
  sonido de la cortina), no de un obturador electrónico.
- `shut` convive con `shutCycleCount` (`0x43cbee6b`) y `uc_shut_idx_num`
  (`[CAMERA_MAIN_YC]: SHD::job_YC_Initialize: uc_shut_idx_num = 0x%x` `0x43cc326d`): es el
  **índice/contador de obturación** del modo de lectura, no un selector de mecanismo.
- En el lado del obturador electrónico (S51–S61) no aparece ningún campo nuevo con este
  nombre: el DFE/IMX210 sigue hablando por P2S/DFE0 y CISIF (S56), sin cambios en fw3.21.

**Conclusión para la línea del obturador:** la fw3.21 **no** introduce ningún parámetro de
obturador electrónico en el bloque de parámetros del imager; lo que sí añade es instrumentación
(ciclo de obturación) y un cambio de layout del contexto.

## 6. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| offsets +0/+4/+6/+9 del bloque de modo | desensamblado de `FUN_436d6f70` (`ldrh r5,[r1]`, `ldrh r6,[r1,#4]`, `ldrh r7,[r1,#6]`, `ldrb.w sb,[r1,#9]`) |
| `shut` = byte +9, `svd/shd/spl` = u32 del contexto | argumentos de la llamada de registro en `0x436d7242`–`0x436d7282` |
| 5 trazas del bloque idénticas en A6000 y A7S | comparación texto a texto sobre ambos blobs |
| `zaf_now_shut_cycle` solo en la A6000 | búsqueda del literal en los dos blobs |
| `b8_shutter_limit` solo en la A7S | ídem |
| cambio de layout `+0x13c` → `+0xfc` | desensamblado de la rama `cmp r3,#0x11` en ambos blobs |

## 7. NO VERIFICADO / abierto

- **La tabla de valores por `drive_mode`**: no se ha extraído (la referencia a la tabla del
  bloque de modo no es un puntero absoluto y no se ha localizado todavía). Sin ella **no** se
  puede afirmar si algún modo concreto difiere entre A6000 y A7S.
- El significado de `sint` y `gs` (parámetros del mismo bloque).
- Si `zaf_now_shut_cycle` cuenta obturaciones mecánicas o electrónicas (NO VERIFICADO).
- Nada de esto **modifica** S51 (A/B/C = NO).

## 8. Ficheros de este hito

| fichero | contenido |
|---|---|
| `compare_params.py` | compara la función de exposición entre A6000 y A7S (sitios PIC + desensamblado) |
| `result.json` | resultado de la comparación (sitios, funciones, secuencias de instrucciones) |
