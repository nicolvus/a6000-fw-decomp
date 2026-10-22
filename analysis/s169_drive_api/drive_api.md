# S169 — control positivo del obturador electrónico: la API de **drive** del A6300 y su ausencia total en la A6000

> Hito de la **línea de ingeniería inversa general**, pero con valor directo para la **línea del
> obturador electrónico**. Solo lectura de bytes: `av-cam.bin` de la **A6000 fw3.21**,
> **A7S fw3.20** y **A6300 fw2.01**. Convención: `vaddr = 0x43541000 + file_offset`.
> Regla de referencias: **estricta** (canónica del repo).

## 1. Resumen / veredicto

El **A6300 fw2.01** tiene una **capa de validación de parámetros de cámara** (`LiroSeq`) con
**201 propiedades** nombradas (`CheckSet*`) y **370 comprobaciones** (`LiroSeq ParamCheckErr@%s[campo] cur:%d req:%d`).
Entre esas propiedades están **las del obturador**:

| propiedad (`CheckSet*`) | campo del parámetro | offset en el bloque | sitio |
|---|---|---|---|
| `CheckSetShutDrive` | **`sc_ShutDrive`** | `+0x1dd` | `0x438c51c0` |
| `CheckSetShutDriveMode` | **`uc_ShutDriveMode`** | `+0x1dc` | `0x438c6842` |
| `CheckSetFrontEshutter` | **`front_eshutter`** | `+0x23c` | `0x438c6e1e` |
| `CheckSetSilentShutterMode` | **`SilentShutterMode`** | `+0x264` | `0x438c81da` |
| `CheckSetShutterType` | **`shutterType`** | `+0x268` | `0x438c8b52` |
| `CheckSetShutLowLimit` | `ul_ShutLowLimit` | `+0x248` | `0x438c7ba4` |
| `CheckSetIrisDrive` | `sc_IrisDrive` | `+0x1d1` | `0x438c55a2` |
| `CheckSetIrisDriveMode` | `uc_IrisDriveMode` | `+0x1d0` | `0x438c680e` |
| `CheckSetManualExposureDrive` | `sc_ExposureDrive` | `+0x1ac` | `0x438c5d14` |
| `CheckSetIsoAutoMinShutSpeed` | `isoAutoMinShutSpeedMode` | `+0x28c` | `0x438c8acc` |
| `CheckSetMovieAutoSlowShutMode` | `MovieAutoSlowshutMode` | `+0x250` | `0x438c7efa` |

**En la A6000 fw3.21 y en la A7S fw3.20 NO existe ni una sola** de estas propiedades, ni sus
nombres de campo, ni la capa `ParamCheckErr`: los contadores son **0 / 0 / 1** para
`CheckSet*`, `ParamCheckErr`, `sc_ShutDrive`, `uc_ShutDriveMode`, `shutterType`,
`SilentShutterMode` y `front_eshutter`.

Esto **reforza S135** (que había encontrado el módulo `ElecShutter/` en el HAL del A6300) con
evidencia de **capa de parámetros en runtime**, no solo de configuración: el A6300 **tiene y
valida** un parámetro de tipo de obturador, un modo de obturador silencioso y un obturador
electrónico frontal; la A6000 fw3.21 **no tiene ni el parámetro**.

**No cambia S51 (A=NO, B=NO, C=NO)**: sigue faltando la prueba física.

## 2. Qué es exactamente la familia `CheckSet*`

1. El **nombre de la propiedad** (`CheckSetXxx`) y el **nombre del campo** (`xxx_yyy`) son
   cadenas distintas; el mensaje de traza es `LiroSeq ParamCheckErr@%s[campo] cur:%d req:%d`,
   donde `%s` = la etiqueta de la propiedad y `[campo]` = el nombre del campo.

2. El patrón de código (verificado byte a byte en 3 casos) es:

```
0x438c51ae: ldrsb.w r2, [r0, #0x1dd]   ; valor ACTUAL del campo
0x438c51b2: ldrsb.w r3, [r4, #8]       ; valor SOLICITADO
0x438c51b6: cmp    r2, r3
0x438c51b8: beq    #0x438c51ca
0x438c51ba: ldr    r0, [pc, #0x10]      ; -> mensaje  "LiroSeq ParamCheckErr@%s[sc_ShutDrive] cur:%d req:%d"
0x438c51bc: ldr    r1, [pc, #0x10]      ; -> etiqueta "CheckSetShutDrive"
0x438c51be: add    r0, pc              ; sitio del MENSAJE
0x438c51c0: add    r1, pc              ; sitio de la ETIQUETA
0x438c51c2: pop.w  {r4, r5, r6, lr}
0x438c51c6: b.w    #0x43986518          ; traza
```

   Los tres casos verificados a mano: `sc_ShutDrive` (`+0x1dd`, sitio `0x438c51c0`),
   `front_eshutter` (`+0x23c`, sitio `0x438c6e1e`) y `SilentShutterMode` (`+0x264`, sitio
   `0x438c81da`).

3. **Los 201 nombres están vivos** (1 referencia PIC cada uno) y se despachan desde una
   **región contigua** de código `0x438c4ade`–`0x438c8c76` (390 sitios, 603 referencias): es
   un despachador generado por propiedad, en el **orden del bloque de parámetros** (los
   offsets van creciendo: `+0x1ac` → `+0x1d0` → `+0x1dd` → `+0x23c` → `+0x264` → `+0x268`).

4. El prefijo del nombre de campo indica el tipo: `sc_` (byte con signo), `uc_` (byte sin
   signo), `us_`/`ul_` (medio/largo sin signo), sin prefijo (word). **No se desarrolla la sigla
   `sc_`**: no hay expansión en los bytes.

## 3. Differential A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| nombres `CheckSet*` | **0** | **0** | **201** |
| mensajes `LiroSeq ParamCheckErr@%s[...]` | **0** | **0** | **370** |
| apariciones de `LiroSeq` | 2 | 2 | **372** |
| `sc_ShutDrive` | 0 | 0 | **1** |
| `uc_ShutDriveMode` | 0 | 0 | **1** |
| `front_eshutter` | 0 | 0 | **1** |
| `SilentShutterMode` | 0 | 0 | **2** |
| `shutterType` | 0 | 0 | **1** |
| `sc_IrisDrive` / `uc_IrisDriveMode` | 0 / 0 | 0 / 0 | **1 / 1** |
| `sc_ExposureDrive` | 0 | 0 | **1** |
| `ul_ShutLowLimit` | 0 | 0 | **1** |
| `drive_mode` (imager, S134) | **10** | 4 | 6 |

**Matiz importante**: la A6000 **sí** tiene el módulo LiroSeq (2 trazas:
`[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` `0x43ca3b3a` y
`[CAMERA_MAIN]: LiroSequencer cannot read IRIS_DIAL_POS ::: %d` `0x43ccadbf`) y **sí** tiene
`drive_mode` (el del imager de S134) → **no es que la A6000 carezca del subsistema**, es que
**no tiene esta capa de validación de parámetros** y sus parámetros no incluyen los campos de
obturador. La A6000 tampoco tiene `IRIS_DIAL_POS` como parámetro con nombre (`uc_iris_dial_enable`
= 0).

## 4. Salvedad metodológica (heredada de S130 §4)

La comparación mezcla **versión de firmware** y **modelo de cámara**. El A6300 es de otra
generación de plataforma (LIRO/CXD) que la A6000 y la A7S. Por tanto **no** se puede separar
«nuevo en el fw2.01» de «propio de la plataforma del A6300». Lo que **sí** queda establecido es
el dato diferencial: **la A6000 fw3.21 y la A7S fw3.20 no tienen ningún parámetro de
obturador electrónico ni de modo de obturador** en su capa de cámara.

## 5. Qué NO se afirma

- **NO** se afirma que la A6000 sea incapaz de disparar con obturador electrónico: se afirma que
  **su firmware no expone ningún parámetro para ello**.
- **NO** se ha identificado el *fichero fuente* de la capa LiroSeq del A6300 ni el nombre de la
  función que agrupa las 387 comprobaciones (la región `0x438c4ade`–`0x438c8c76` son funciones
  cortas, una por campo).
- **NO** se ha analizado qué valores toman `shutterType`, `SilentShutterMode` o
  `front_eshutter` en runtime ni quién los escribe.
- **NO** se ha seguido la ruta del parámetro `sc_ShutDrive` hasta el driver del obturador.
- **NO** se desarrolla `sc_`/`uc_`/`us_`/`ul_` como siglas.

## 6. Herramientas (reutilizables)

| script | qué hace |
|---|---|
| `analysis/s169_drive_api/scan_all_refs.py` | vuelca el **mapa global de referencias PIC** (regla estricta) de un blob parametrizado → `pic_refs_strict_a6300.json` (**20 001 destinos**) y `pic_refs_strict_a7s.json` (**16 638 destinos**). El mapa de la A6000 ya existía (`analysis/s106_imaging_cap/pic_refs_strict_global.json`, 17 525). |
| `analysis/s169_drive_api/pair_checkset.py` | empareja cada etiqueta `CheckSet*` con su mensaje `ParamCheckErr` usando el mapa (sitios `add` contiguos) → `checkset_pairs.json` (**387 pares** con campo, offset y sitio). |
| `analysis/s168_a6300_rolling/scan_refs.py` | escáner PIC estricto parametrizado (un destino). |
| `analysis/s168_a6300_rolling/find_ref.py` | método inverso de comprobación cruzada. |

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
A6300=firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin
A7S=firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin
.venv/bin/python analysis/s169_drive_api/scan_all_refs.py $A6300 0x43541000 analysis/s169_drive_api/pic_refs_strict_a6300.json
.venv/bin/python analysis/s169_drive_api/scan_all_refs.py $A7S    0x43541000 analysis/s169_drive_api/pic_refs_strict_a7s.json
.venv/bin/python analysis/s169_drive_api/pair_checkset.py analysis/s169_drive_api/pic_refs_strict_a6300.json $A6300 0x43541000 > analysis/s169_drive_api/checkset_pairs.json
.venv/bin/python -m pytest tests/test_s169_drive_api.py -q
```

## 8. Revisión del agente principal

_(vacía)_
