# S116 — `[SFRS]`: 117 trazas del subsistema

**Hito de la línea de ingeniería inversa general.** Módulo reconstruido solo desde los bytes de
A6000 fw3.21. Sin efecto en la línea del obturador (S51): no hay ningún mensaje de obturador
electrónico en el módulo.

Informe: [analysis/s116_sfrs/sfrs.md](../../analysis/s116_sfrs/sfrs.md) ·
Datos: `sfrs.json`, `strings_raw.json`, `pic_refs_sfrs.json`, `func_map.json` ·
Script: `analysis/s116_sfrs/scan_sfrs.py` · Test: `tests/test_s116_sfrs.py`.

## Hallazgo central

`[SFRS]` es la etiqueta de módulo de **117 cadenas de traza** en `0x43ce7661`–`0x43ceb8c4`
(≈17 KB), emitidas desde **131 puntos** `ldr`+`add` PC-relativo en **52 funciones** de
`0x439a6be8`–`0x439b1cb2`. Las siglas **no se expanden en ningún byte del firmware**: el
informe no las interpreta.

## Los ocho sub-bloques (suman 117)

| sub-bloque | cadenas | primer vaddr | funciones |
|---|---:|---|---:|
| `SUPERSTABLEMOVIE` | 37 | `0x43ceabc3` | 9 |
| `MOTIONSHOTVIDEO` | 25 | `0x43ce99ab` | 11 |
| `EFFECTMOVIEREC` | 23 | `0x43ce9c58` | 7 |
| `PINSEND` | 12 | `0x43ce8cde` | 11 |
| `SET_PATH_STATUS` | 9 | `0x43ce99ed` | 7 |
| `SA` | 6 | `0x43ce9795` | 2 |
| `RC_AIC_TRIGGER` | 3 | `0x43ce7661` | 3 |
| `MULTIPLEXTRIGGER` | 2 | `0x43ceab13` | 2 |

La agrupación es **por subcadena del texto** (regla reproducible en `classify()`), no una
decodificación de comportamiento.

## Evidencia de bytes que sí queda cerrada

- `SETPIN` (`0x439aad92`): `cmp r1,#1` en `0x439aada4` + `bne #0x439aadb2`; el log con
  `movs r1,#0` (`0x439aadb4`) y `movs r2,#0x3a` = **línea 58** solo ocurre en el camino «no
  igual». `add r0,pc` en `0x439aadc2` resuelve a `0x43ce8cde`
  (`[SFRS][DEBUG][SETPIN] YccOut(false): file=%s line=%d`).
- `GETPIN` (`0x439aae20`): `cmp r1,#1` en `0x439aae3c`; log con `movs r2,#0x38` = **línea 56**
  y `add` en `0x439aae4e` → `0x43ce8d2f` (`…[GETPIN] ReqYccAsap(true)…`).
- En ambos, el argumento `file=%s` es **otro literal** (`0x43ce8d13` =
  `SystemCmdAsyncCmdSetPin.cpp`; `0x43ce8d67` = `SystemCmdAsyncGetPin.cpp`), no la cadena
  `[SFRS]`.
- `SUPERSTABLEMOVIE_EXECUTE_PIN_SEND` (`0x43ceb80d`, log en `0x439b1f68`): `dataContent`,
  `dataPlacement`, `dataTransfer` y `scanline` salen de `[r4,#0x3f6]`, `[r4,#0x3f5]`,
  `[r4,#0x3f4]` y `[r4,#0x3ff]` — cuatro campos contiguos del mismo objeto.

## Corrección metodológica

El PC de este firmware se resuelve **sin alinear**: `destino = palabra_literal + (addr_add + 4)`.
La variante alineada cae 2 bytes antes del inicio de la cadena (`0x43ce8cdc` = `'E'`). Además el
`ldr` debe ser el **inmediato anterior del mismo registro** (≤ 0x20 B) y el barrido debe respetar
las fronteras Thumb de 32 bits. Con esas tres reglas: 117/117 cadenas y 131/131 sitios
atribuidos.

## Diferencial A7S fw3.20

151 cadenas `[SFRS]` en A7S, **117 comunes** con la A6000, **0 exclusivas de A6000** y **34
exclusivas de A7S** (comparación texto a texto ignorando especificadores de formato): el
vocabulario `[SFRS]` de la A6000 es un subconjunto estricto del de la A7S. Las 34 de la A7S son
de path (`TransPath*`, `SendOpen/ClosePathCmdToAsyncTask`, `SendComp`), de audio
(`SET_PATH_AUDIO_*`, `AUDIO_*`, `AudioPin*`, `PinSendPathAudio`) y contadores de pines
(`PINCOUNT`, `DEFAULT FREE`).

## Ficheros fuente citados

24 literales `*.cpp` son citados desde el clúster `0x439a0000`–`0x439c0000`, entre ellos
`SystemCmdPinSend.cpp` (`0x43c843ac`, 9 funciones), `ScalarInfraSequenceSa.cpp` (`0x43ce6c15`),
`DrvCallRc.cpp` (`0x43ce76fb`) y `SfrYc.cpp` (`0x43ce73ec`). Solo **12 de las 52 funciones** con
traza pasan un `file=%s`, así que las otras 40 no tienen fichero atribuido.

## Abierto / NO VERIFICADO

- Significado de las siglas `SFRS`, `AIC`, `RC`, `VFX`, `IIB` y de `PINSEND`.
- Tipo y semántica de cada campo (`nowVfc`, `transTime`, `configNum`, `dataContent`…).
- La tabla de líneas de los `.cpp` y si `line=%d` corresponde al fichero de `file=%s`.
- Qué hacen exactamente los modos `EFFECTMOVIEREC`, `MOTIONSHOTVIDEO` y `SUPERSTABLEMOVIE`.
- Nada de esto modifica S51: no aparece ningún mensaje de obturador electrónico.
