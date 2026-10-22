# S124 — el bloque de parámetros de exposición/lectura por `drive_mode` (imager)

**Hito de la línea de ingeniería inversa general**, con relevance directa para la línea del
**obturador electrónico** (el parámetro `shut` del imager).

Informe: [analysis/s124_exposure_params/exposure_params.md](../../analysis/s124_exposure_params/exposure_params.md) ·
Datos: `result.json` · Test: `tests/test_s124_exposure_params.py`.

## Hallazgo central

El bloque de parámetros del imager por modo de lectura es
**`{shut, svd, shd, spl, sint, gs, epdsel}`** y **es el mismo en la A6000 fw3.21 y en la A7S
fw3.20**: las 5 trazas de `[CAMERA_MAIN_SYNC]` que lo revelan coinciden texto a texto. La fw3.21
cambia la *instrumentación*, no los valores.

## Qué se ha verificado (bytes)

1. **De dónde sale cada valor** (función `FUN_436d6f70`, por la referencia PIC de
   `0x43c93cc2`): `PrevDrv` = u16 [r1+4], `NowDrv` = u16 [r1+0], `NextDrv` = u16 [r1+6] y
   **`shut` = byte [r1+9]**; `spl`/`shd`/`svd` son tres u32 del contexto de captura
   (+0x170/+0x174/+0x178).
2. **La fw3.21 reescribe el vocabulario**: `SetExps`/`SetExpsZ`/`SetRead`/`Execute` (con el drive
   mode *anterior*) frente a `Exposure.`/`Change ImagerMode.` (solo Now/Next) en la A7S.
3. **Cambia el layout del contexto**: la rama de modo `0x11` usa `r0+0xfc` en la A6000 frente a
   `r0+0x13c` en la A7S.
4. **Traza nueva en fw3.21**: `[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d` `0x43ca7836` (la
   A7S no la tiene); **retirada**: `b8_shutter_limit` `0x43c9f01c` (solo A7S).

## Por qué NO es un obturador electrónico

`shut` convive con `shutter mute on/off` `0x43c8253b` (el silenciador del obturador
**mecánico**), `shutCycleCount` `0x43cbee6b` y `uc_shut_idx_num` `0x43cc326d`: es el
**índice/contador de obturación** del modo de lectura. La fw3.21 **no** introduce ningún
parámetro de obturador electrónico; el DFE/IMX210 sigue hablando por P2S/DFE0 y CISIF (S56) sin
cambios. **Sin efecto en S51 (A/B/C = NO).**

## Abierto / NO VERIFICADO

- La **tabla de valores por `drive_mode`** (no extraída): sin ella no puede afirmarse si algún
  modo concreto difiere entre A6000 y A7S.
- El significado de `sint` y `gs`.
- Si `zaf_now_shut_cycle` cuenta obturaciones mecánicas o electrónicas.
