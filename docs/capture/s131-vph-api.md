# S131 — `[VPH_API]`: la API de parámetros del subsistema VPH (106 trazas)

**Hito de la línea de ingeniería inversa general** (sin efecto en S51).

Informe: [analysis/s131_vph_api/vph_api.md](../../analysis/s131_vph_api/vph_api.md) ·
Datos: `vph_api.json` · Test: `tests/test_s131_vph_api.py`.

## Qué es

La traza de la **API de parámetros del subsistema VPH** (la tubería de display: OSD, panel,
salida de línea, muteos y ayudas de encuadre). La sintaxis dice qué es cada llamada:

| forma | n | ejemplo |
|---|---|---|
| `<nombre>` (entrada / setter) | 49 | `[VPH_API]<mode>` `0x43ce32e7` |
| `<nombre>_sub` (variante sub) | 42 | `[VPH_API]<mode_sub>` `0x43ce3781` |
| `>nombre<` (salida / getter) | 11 | `[VPH_API]>mode_status<` `0x43ce3d0e` |
| `=x=` (comparación de comando) | 4 | `[VPH_API]=v_command_comp=` `0x43ce374b` |

**60 familias de parámetros**, 106 trazas contiguas `0x43ce32e7`–`0x43ce3dfc`, emitidas por
**48 manejadores** (uno por parámetro, una sola traza cada uno) en dos bloques de código:
`0x4395aab8`–`0x4395b5f4` (39) y `0x4395e1b8`–`0x4395e34c` (9).

## Lo relevante para la línea del obturador

La API incluye el **silenciador del obturador** con 4 trazas: `<shutter_mute_param>`
`0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4` y
`>shutter_mute_status<o/f:%d` `0x43ce3dfc`. Las 4 cadenas `shutter_mute*` **no existen** en la
A7S fw3.20 ni en el A6300 fw2.01, mientras que la traza del silenciador en sí
(`shutter mute on/off`, `[SFRS][PINSEND]`, S118) **sí** está en los tres → la fw3.21 **añade el
parámetro de API**, no el mecanismo. Es el **obturador mecánico** (junto a `yuv_mute` y
`chroma_mute`): **sin efecto en S51**.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| trazas `[VPH_API]` | 106 | 0 | 0 |
| token `VPH` | 134 | 24 | 24 |

El subsistema VPH es mucho mayor en la A6000 fw3.21: no solo se etiqueta, es que **la API
completa no está** en los otros dos firmware.

## Abierto / NO VERIFICADO

- Cómo se referencia la tabla de manejadores (no hay punteros absolutos) y quién la invoca.
- `laxo`, `diceic_arb`, `line_fchr`, `set_eomainsub_inverse` (siglas sin desarrollar).
- Qué hace exactamente `shutter_mute_param` y quién lo consume.
