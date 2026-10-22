# S169 — control positivo del obturador electrónico: la API de **drive** del A6300

> Hito de la **línea de RE general** con valor directo para la **línea del obturador electrónico**.
> Solo bytes: `av-cam.bin` de la A6000 fw3.21, la A7S fw3.20 y el A6300 fw2.01.

## Veredicto

El **A6300 fw2.01** tiene una **capa de validación de parámetros de cámara** (`LiroSeq`) con
**201 propiedades** (`CheckSet*`) y **370 comprobaciones** (`LiroSeq ParamCheckErr@%s[campo] cur:%d req:%d`).
Entre ellas hay **parámetros de obturador**, con su nombre de campo y su offset en el bloque de
parámetros:

| propiedad | campo | offset | sitio |
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

**La A6000 fw3.21 y la A7S fw3.20 tienen 0 de todo eso**: `CheckSet*` **0/0/201**,
`ParamCheckErr` **0/0/370**, `sc_ShutDrive` **0/0/1**, `front_eshutter` **0/0/1**,
`SilentShutterMode` **0/0/2**, `shutterType` **0/0/1**.

Es decir: **no falta la traza, falta el parámetro**. Esto **reforza S135** (que encontró el
módulo `ElecShutter/` en el HAL del A6300) con evidencia de **capa de parámetros en runtime**.

## Patrón de código (verificado a mano)

```
0x438c51ae: ldrsb.w r2, [r0, #0x1dd]   ; valor ACTUAL del campo
0x438c51b2: ldrsb.w r3, [r4, #8]       ; valor SOLICITADO
0x438c51b6: cmp    r2, r3
0x438c51b8: beq    #0x438c51ca
0x438c51ba: ldr    r0, [pc, #0x10]      ; -> "LiroSeq ParamCheckErr@%s[sc_ShutDrive] cur:%d req:%d"
0x438c51bc: ldr    r1, [pc, #0x10]      ; -> "CheckSetShutDrive"
0x438c51be: add    r0, pc              ; sitio del MENSAJE
0x438c51c0: add    r1, pc              ; sitio de la ETIQUETA
0x438c51c2: pop.w  {r4, r5, r6, lr}
0x438c51c6: b.w    #0x43986518          ; traza
```

## Matiz

La A6000 **sí** tiene el módulo LiroSeq (2 trazas: `[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d`
`0x43ca3b3a`, `[CAMERA_MAIN]: LiroSequencer cannot read IRIS_DIAL_POS ::: %d` `0x43ccadbf`) y
**sí** tiene `drive_mode` (el del imager de S134, 10 apariciones) → **no** le falta el
subsistema: le falta **esta capa de validación de parámetros**, y sus parámetros no incluyen
los campos de obturador.

**Salvedad** (heredada de S130 §4): la comparación mezcla versión de firmware y modelo (el A6300
es de otra generación de plataforma, LIRO/CXD). No se puede separar «nuevo en el fw2.01» de
«propio de la plataforma».

## Efecto en S51

**Ninguno**: **S51 sigue A=NO, B=NO, C=NO**. El hallazgo dice que la **fw3.21 de la A6000 no
expone ningún parámetro de obturador electrónico**, no que su hardware sea incapaz. La ausencia
estática no demuestra incapacidad del hardware: sigue faltando la prueba física.

## Herramientas

| script | qué hace |
|---|---|
| `analysis/s169_drive_api/scan_all_refs.py` | mapa global de referencias PIC (regla estricta) de un blob parametrizado → `pic_refs_strict_a6300.json` (**20 001** destinos) y `pic_refs_strict_a7s.json` (**16 638**); el de la A6000 ya existía (17 525). |
| `analysis/s169_drive_api/pair_checkset.py` | empareja cada `CheckSet*` con su mensaje `ParamCheckErr` → `checkset_pairs.json` (**387 pares** con campo, offset y sitio). |

Informe: [analysis/s169_drive_api/drive_api.md](../analysis/s169_drive_api/drive_api.md) ·
test: `tests/test_s169_drive_api.py` (32 tests).
