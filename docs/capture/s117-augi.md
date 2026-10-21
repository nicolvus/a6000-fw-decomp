# S117 — `[AUGI]`: la cabecera de 32 B del bloque de códec

**Hito de la línea general de RE**; cierra lo abierto en S83 §2.8 («Formato exacto de la
cabecera AUGI»); sin efecto en el obturador. Informe:
[analysis/s117_augi/augi.md](../../analysis/s117_augi/augi.md) · Datos: `augi.json`,
`augi_strings_raw.json`, `augi_refs.json` · Test: `tests/test_s117_augi.py`.

## Hallazgo central

`[AUGI]` nombra una **cabecera de 32 B** y las clases que la leen y escriben (`DecExAugiConverter`,
`DecInAudioAugiConverter`, `DecInVideoAugiConverter`, `EncExAugiConverter`): **75 cadenas**,
**86 sitios** PIC, **6 funciones**; la sigla no se expande en el binario.

## La cabecera (copia host, little-endian)

| off | campo | off | campo |
|---:|---|---:|---|
| `+0x00` | `length` (u32) | `+0x14` | `nextPTS` (u32) |
| `+0x04` | `Reserved2` (u16) | `+0x18` | `pic_parameter_set_id` (u8) |
| `+0x06` | flags: `end`/`PS`/`EP`/`DTS` + `Reserved1` | `+0x19` | `num_PPS` (u8) |
| `+0x07` | `Num_AUs` (u8) | `+0x1a` | `seq_parameter_set_id` (5 b) + `num_SPS` (3 b) |
| `+0x08` | `PTS` (u32) | `+0x1b` | `change_PPS`/`change_SPS`/`Reserved4`/`Reffered`/`PictureType` (3 b)/`Reserved3` |
| `+0x0c` | `DTS` (u32) | `+0x1c` | `size_PPS` (u16) |
| `+0x10` | `nextHRDBuffer` (u32) | `+0x1e` | `size_SPS` (u16) |

Evidencia: 14 lecturas del dumper `0x4391ca90` (`0x4391caa0`–`0x4391cbb4`) y escrituras del
escritor `0x435d63a0`; paso **32 B** por `lsls #5` en `0x436163c2` y `0x436150ea`.

## Dos representaciones

En memoria es **little-endian**; en el stream se invierte **cada palabra de 4 B**
(`rev r0,r1` en `0x43a5cb12`, bytes `08 ba 70 47`; bucle `0x435d64e8`–`0x435d6500`), así que
`Num_AUs` (host `+0x07`) queda en `stream[4]` y `+0x18`–`+0x1b` en orden inverso.

## Quién la escribe y quién la lee

- **Escritor de audio**: `0x435d63a0` = `McAvcEncAudioSeqCtrlState::WriteAugi()` (RTTI
  `0x43c4b313`); wrappers `0x43a5cb26`, `0x43a5d182`.
- **Entrada de API**: `0x4360b6f0` = `StrmEngEncCIIf::CodecEventCreateVAUGI(UInt32, const
  UInt32*)` (`0x43c66fbf`). **No** se ha localizado el escritor de vídeo.
- **Lector/dumper**: `0x4391ca90` (25 trazas `[AUGI] … = %d`), desde `0x4391d12e`/`0x4391d136`.

## Tres vistas dec distintas (no son la cabecera)

- `0x43615eac` (`DecEx`) invierte 32 B (`bl 0x43a7e32e`) y lee `length`, `offset`,
  `PTS_DTS_flag`, `AUGI_type`, `num_AUs`, PTS/DTS, `STC_Offset`, `discontinuity_*`.
- `0x4361610c` (`DecInAudio`) y `0x43616200` (`DecInVideo`) leen **directamente**, con
  `pts_33`, `dts`, `stc_offset_33`, `e_ptm`… hasta `+0x2a`; el vídeo añade `offset`, `dts` y
  `e_ptm`, el audio no.

Mezclar vistas da offsets falsos: `+0x04` es `Reserved2` en la cabecera y `offset` en `DecEx`.

## Diferencial A7S y pendientes

- A7S fw3.20: **75 cadenas, 75 comunes, 0 exclusivas en cada sentido**; solo cambia la posición
  (A6000 `0x43c6a28a`–`0x43cd9c8d`, A7S `0x43c6740f`–`0x43cca5a5`).
- NO VERIFICADO: significado de `AUGI`, `PS`, `EP`, `STC`, `HRD` y de los valores de
  `PictureType`/`AUGI_type`/`e_ptm`; qué cuenta `length`; escritor de vídeo; papel de
  `0x43a7e70c`; contenido de SPS/PPS; si A7S usa los mismos offsets (código no comparado).
