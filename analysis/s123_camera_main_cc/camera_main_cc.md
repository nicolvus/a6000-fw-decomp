# S123 — el módulo `[CAMERA_MAIN_CC]` (49 trazas): el control de captura

**Hito de la línea de ingeniería inversa general** (A6000 fw3.21). No toca la línea del obturador
electrónico: **0** mensajes de obturador en las 49 trazas.

* Convención de direcciones: `vaddr = 0x43541000 + file_offset` (`analysis/rea-independent/input/av-cam.bin`).
* Regla de referencias: **estricta** (canónica del repo,
  `analysis/s106_imaging_cap/scan_pic_refs_strict.py`; ver
  `analysis/s106_imaging_cap/pic_xref_methodology.md`). Toda cifra de "sitios" de este informe
  usa esa regla, salvo que se diga otra cosa.
* Artefactos: `camera_main_cc.json` (datos consolidados), `cc_strings.json`, `func_map.json`,
  `callgraph.json`, `callers.json`, `source_files.json`, `stage_states.json`, `param_ids.json`,
  `class_registry.json`, `a7s_diff.json`.
* Scripts reproducibles: `scan_cc_strings.py` (cadenas), `map_funcs.py` (mapa función→traza),
  `attr_sources.py` (ficheros fuente), `callgraph.py` (llamadas salientes), `callers.py`
  (llamadas entrantes), `stage_states.py` (byte de estado), `param_ids.py` (ids de parámetro),
  `class_registry.py` (registro de clases), `a7s_diff.py` (diferencial), `find_missing_refs.py`
  (pares PIC anchos), `build_summary.py` (consolida), `disasm.py` (desensamblado puntual).
* Test: `tests/test_s123_camera_main_cc.py` (32 tests, verdes).

---

## 1. Resumen

`[CAMERA_MAIN_CC]` es la familia de trazas de la **clase C++ `CC`** (control de captura) del hilo
principal de la cámara. Contiene **49 cadenas** en la A6000 fw3.21, repartidas en **6 tramos
contiguos** de `.rodata` — **uno por sub-bloque** (§3):

| tramo | rango | n | sub-bloque |
|---|---|---|---|
| 1 | `0x43ca54c8` – `0x43ca5e30` | 21 | control de captura |
| 2 | `0x43ca5f0a` – `0x43ca6158` | 12 | LUT 2D/3D |
| 3 | `0x43ca6470` – `0x43ca6600` | 8 | IE (image effect) |
| 4 | `0x43ca665e` – `0x43ca66a1` | 2 | miniRaw |
| 5 | `0x43ca6805` – `0x43ca686d` | 2 | MakerNote de reproducción raw |
| 6 | `0x43cb4cd3` – `0x43cb4d62` | 4 | CamCore 3D-LUT |

Los tramos están separados por material de otros módulos: entre 1 y 2 hay 92 B con
`[IMAGING_CAP]: SACC Open Error` / `[IMAGING_CAP]: SACC Close Error` (S106); entre 2 y 3, 756 B de
una tabla de caracteres imprimibles; entre 3 y 4, 56 B de datos; entre 4 y 5, 284 B con los
nombres de escena `Neutral` / `Portrait` / `Landscape`; entre 5 y 6, 58 359 B (todo el bloque
`[CAMERA_MAIN_FC]`).

Hallazgos principales (todos contra bytes):

1. **49 trazas**, **47 referenciadas** por la regla PIC estricta (1 sitio cada una) y
   **2 trazas sin referencia estricta** (`GetKDZMode()` `0x43ca5bb7` y `SetMovDevelopParam()`
   `0x43ca5d31`). La regla **ancha** sí encuentra un par candidato para cada una, pero ambos son
   **falsos positivos** comprobados desensamblando (§3.1).
2. **29 funciones** las emiten (límites por prólogo/epílogo Thumb con capstone).
3. El módulo **no es un módulo plano**: son **6 sub-bloques** — control de captura (21 trazas),
   LUT 2D/3D (12), IE / image effect (8), miniRaw (2), MakerNote de reproducción raw (2) y
   CamCore 3D-LUT (4). **Cada sub-bloque es un tramo contiguo propio en `.rodata`** (§1).
4. Los **21 nombres de método** del control de captura son métodos de una **máquina de estados**:
   cada método delega en una **función de etapa** distinta (`0x43aeb2ae`…`0x43aeb640`,
   `0x437a1314`, `0x437a16a4`, `0x4381d4ac`) que escribe un **byte de estado** en el objeto de
   estado (offset `0xb`) y un **sub-paso** (offset `0xa`).
5. La identidad de una captura la forman **6 campos** leídos de una estructura compartida:
   `CapMode@0x1c0`, `ExposureID@0x1b8`, `ContID@0x1bc`, `BDROSeq@0x6ec`, `BDRObase@0x6f4`,
   `FrameID@0x701` (verificado desensamblando cuatro métodos).
6. El prefijo de log `[CAMERA_MAIN_CC]` **corresponde a una clase C++ llamada `CC`**: el registro
   de clases del firmware en `0x43FF8EE4` lista `CC::CcEncryptedTagData`, `CC::CcEncryptedFtTagData`,
   `CC::CcEncryptedNflashTagData` junto a `LC::`, `TC::`, `FC::`, `IM::`, `EC::` — la misma familia
   que los otros submódulos `[CAMERA_MAIN_LC]`, `[CAMERA_MAIN_TC]`, `[CAMERA_MAIN_FC]`,
   `[CAMERA_MAIN_IM]`.
7. **37 llamadas entrantes** desde 22 de las 29 funciones del módulo; los llamadores son
   las **etapas del pipeline de captura** (`Stage_SACC`, `Stage_OPD`, `Stage_MARBLE`,
   `Stage_Adjust`, `Stage_Orientation`, `Stage_Raw`) y las utilidades `CaptureUtility*` — es
   decir, el gestor de captura `[IMAGING_CAP]` (S106) **llama** al control de captura, no al revés.

## 2. Qué es `[CAMERA_MAIN_CC]`

### 2.1 El nombre de la clase

`[CAMERA_MAIN_CC]` no es un nombre de fichero: es el **nombre corto de la clase** `CC`
(la familia de clases del firmware es `CC` / `LC` / `TC` / `FC` / `IM` / `EC` / `MakerNote`, y cada
una tiene su propio prefijo de log: `[CAMERA_MAIN_CC]`, `[CAMERA_MAIN_LC]`, `[CAMERA_MAIN_TC]`,
`[CAMERA_MAIN_FC]`, `[CAMERA_MAIN_IM]`, `[CAMERA_MAIN]`).

Prueba 1 — **el registro de clases** (`analysis/s123_camera_main_cc/class_registry.py`):

| ranura | puntero | texto |
|---|---|---|
| `0x43ff8ee4` | `0x43ca923e` | `CC::CcEncryptedTagData` |
| `0x43ff8ee8` | `0x43ca9255` | `CC::CcEncryptedFtTagData` |
| `0x43ff8eec` | `0x43ca926e` | `FC::FcEncryptedTagData` |
| `0x43ff8ef0` | `0x43ca9285` | `LC::LcEncryptedTagData` |
| `0x43ff8ef4` | `0x43ca929c` | `LC::LcEncryptedDebugTagData` |
| `0x43ff8ef8` | `0x43ca92b8` | `TC::TcEncryptedTagData` |
| `0x43ff8efc` | `0x43ca92cf` | `LC::LcEncryptedAmcTagData` |
| `0x43ff8f00` | `0x43ca92e9` | `MakerNote::EncryptedRawDevTagData` |
| `0x43ff8f04` | `0x43ca930b` | `TC::TcAsTagData` |
| `0x43ff8f08` | `0x43ca931b` | `EC::EcAmcTagData` |
| `0x43ff8f0c` | `0x43ca932c` | `CC::CcEncryptedNflashTagData` |
| `0x43ff8f10` | `0x43ca9349` | `LC::LcEncryptedAfData` |
| `0x43ff8f14` | `0x43ca935f` | `IM::ImEncryptedTagData` |

Prueba 2 — **el ámbito de clase en las propias trazas**: `CC::WriteMakerNotePlayRaw` (`0x43ca6817`)
y `CC::SetExtOutputMakerNotePlayRaw` (`0x43ca687f`) llevan el prefijo `CC::` dentro del texto de la
traza; y `CC::set_param_seq_sacc` (`0x43c9eeb1`) aparece como `%s` en
`[IMAGING_CAP]: %s: CC::set_param_seq_sacc error` (`0x43c9ee9e`).

Prueba 3 — **los typeinfo**: la tabla de clases incluye los punteros a los nombres mangled de
`Camera::Imaging::ImageParam` (`0x43ca97d2`), `Camera::Capture::ImageParam_Capture_Share`
(`0x43ca97f0`), `Camera::Capture::ImageParam_Capture` (`0x43ca981c`) y
`Camera::Capture::ImageParam_Capture_Base` (`0x43ca9a16`), referenciados por puntero absoluto en
`0x43ff8f1c`, `0x43ff8f24`, `0x43ff8f30`, `0x43ff8f3c`.

### 2.2 Qué hace: el pipeline de una captura

Los 21 nombres de método son las **etapas del pipeline de captura** (nótese el orden en `.rodata`,
que es el orden de compilación = orden del pipeline):

```
ExtractCaptureData -> CaptureInit -> SetReadImageParam -> SetNRParam -> SetOPDParam
 -> AfterOPDAfterNR -> SetDevelopParam -> SetDevDetectDevelopParam -> DetectYC
 -> SetDualRecParam -> SetDAEParam -> SetBdroIdtData -> SetSACCParam -> SetSACCSaEndParam
 -> WriteExifMakernote -> [GetKDZMode*] -> SetPlayRawDevDetectDevelop
 -> SetPlayRawDevelopParam -> [SetMovDevelopParam*] -> SetReviewDevelopParam
 -> WriteSACCMakerNote
```

(`*` = traza sin código: ver §2.5.)

Es coherente con el pipeline de etapas documentado en S114 (`Stage_Raw`, `Stage_OPD`,
`Stage_MARBLE`, `Stage_Develop`, …) y con la mecánica de la cámara: *read → NR → OPD → develop →
detect develop → YC → dual rec → DAE → BDRO/IDT → SACC → EXIF MakerNote → play raw → review →
SACC MakerNote*.

## 3. Las 49 trazas (dirección, referencia, función)

Referencias PIC = sitio del `add rX,pc` (regla estricta). Función = función que contiene el sitio
(prólogo + epílogo, capstone).

| traza | sub-bloque | ref. PIC | función | texto |
|---|---|---|---|---|
| `0x43ca54c8` | capture-control | `0x4379ecba` | `0x4379ec84` | `ExtractCaptureData()  [CapMode:%d] [ExposureID:%d] [ContID:%d] [FrameID:%d]` |
| `0x43ca552b` | capture-control | `0x4379ed7a` | `0x4379ed34` | `CaptureInit()  …[BDROSeq:%d] [BDRObase:%d] [FrameID:%d]` |
| `0x43ca55a9` | capture-control | `0x4379ee4e` | `0x4379ee04` | `SetReadImageParam()  …` |
| `0x43ca5627` | capture-control | `0x4379ef26` | `0x4379eee0` | `SetNRParam()  …` |
| `0x43ca56a5` | capture-control | `0x4379eff6` | `0x4379efb0` | `SetOPDParam()  …` |
| `0x43ca5723` | capture-control | `0x4379f0c6` | `0x4379f080` | `AfterOPDAfterNR()  …` |
| `0x43ca57a1` | capture-control | `0x4379f196` | `0x4379f150` | `SetDevelopParam()  …` |
| `0x43ca581f` | capture-control | `0x4379f266` | `0x4379f220` | `SetDevDetectDevelopParam()  …` |
| `0x43ca589d` | capture-control | `0x4379f336` | `0x4379f2f0` | `DetectYC()  …` |
| `0x43ca591b` | capture-control | `0x4379f406` | `0x4379f3c0` | `SetDualRecParam()  …` |
| `0x43ca5999` | capture-control | `0x4379f4dc` | `0x4379f498` | `SetDAEParam()  …` |
| `0x43ca5a17` | capture-control | `0x4379f5c6` | `0x4379f586` | `SetBdroIdtData()  …` |
| `0x43ca5a95` | capture-control | `0x4379f65e` | `0x4379f618` | `SetSACCParam()  …` |
| `0x43ca5b13` | capture-control | `0x4379f706` | `0x4379f6ea` | `SetSACCSaEndParam()` (sin campos) |
| `0x43ca5b39` | capture-control | `0x4379f78a` | `0x4379f744` | `WriteExifMakernote()  …` |
| `0x43ca5bb7` | capture-control | **ninguna** | — | `GetKDZMode()  …` **(traza muerta)** |
| `0x43ca5c35` | capture-control | `0x4379f858` | `0x4379f814` | `SetPlayRawDevDetectDevelop  …` |
| `0x43ca5cb3` | capture-control | `0x4379f924` | `0x4379f8e0` | `SetPlayRawDevelopParam()  …` |
| `0x43ca5d31` | capture-control | **ninguna** | — | `SetMovDevelopParam()  …` **(traza muerta)** |
| `0x43ca5daf` | capture-control | `0x4379f9f2` | `0x4379f9ac` | `SetReviewDevelopParam()  …` |
| `0x43ca5e30` | capture-control | `0x4379fb92` | `0x4379fb48` | `WriteSACCMakerNote()  …` |
| `0x43ca5f0a` | lut | `0x437a1bde` | `0x437a1a7e` | `LutMode Change SA %02X <- %02X` |
| `0x43ca5f3b` | lut | `0x437a1bfa` | `0x437a1a7e` | `LutMode Change CAP %02X <- %02X` |
| `0x43ca5f6d` | lut | `0x437a1c16` | `0x437a1a7e` | `LutMode Change MOV/MON %02X <- %02X` |
| `0x43ca5fa3` | lut | `0x437a1c62` | `0x437a1a7e` | `IsSplit Change [%02X] -> [%02X]` |
| `0x43ca5fd5` | lut | `0x437a1cae` | `0x437a1a7e` | `uc_sync = [%02X]` |
| `0x43ca5ff8` | lut | `0x437a1fc2` | `0x437a1d7e` | `Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d BlkOfs Cr:%X, Cb:%X` |
| `0x43ca6049` | lut | `0x437a2002` | `0x437a1d7e` | `Create3DLUT  NullError RefAdr:0x%X BufAdr:0x%X` |
| `0x43ca608a` | lut | `0x437a2344` | `0x437a1d7e` | `Copy3DLUT 0x%X > 0x%X ` |
| `0x43ca60b3` | lut | `0x437a236c` | `0x437a1d7e` | `Copy3DLUT NullError RefAdr:0x%X BufAdr:0x%X` |
| `0x43ca60f1` | lut | `0x437a2404` | `0x437a1d7e` | `Copy2DLUT 0x%X > 0x%X ` |
| `0x43ca611a` | lut | `0x437a242c` | `0x437a1d7e` | `Copy2DLUT NullError RefAdr:0x%X BufAdr:0x%X` |
| `0x43ca6158` | lut | `0x437a2782` | `0x437a24fc` | `LUT Write Cnt:%d ` |
| `0x43ca6470` | ie | `0x437a68d6` | `0x437a6890` | `IE     Error Null Address` |
| `0x43ca649c` | ie | `0x437a691c` | `0x437a6890` | `IE     Error Status[errorCode:   %08x]` |
| `0x43ca64d5` | ie | `0x437a6984` | `0x437a6890` | `IE     Hold SCAN AF etc` |
| `0x43ca64ff` | ie | `0x437a6b60` | `0x437a6890` | `IE     Get   [LightNum:   %2d][MapNum:   %2d][ResAdress:%10lx] ` |
| `0x43ca6551` | ie | `0x437a6b9a` | `0x437a6890` | `IE     Get sync closed NG ` |
| `0x43ca657e` | ie | `0x437a7e1e` | `0x437a7e00` | `IE Invalid Light or Map Number   [num:%2d   ] ` |
| `0x43ca65bf` | ie | `0x437a7f24` | `0x437a7e90` | `IE Set       [LightNum:%2d   ][MapNum:%2d   ] ` |
| `0x43ca6600` | ie | `0x437a8090` | `0x437a7e90` | `IE     Set init NG ` |
| `0x43ca665e` | miniraw | `0x437a9314` | `0x437a8fac` | `CC miniRaw Size Error [width: %3d][height: %3d] ` |
| `0x43ca66a1` | miniraw | `0x437a9422` | `0x437a8fac` | `CC miniRaw norm Size Error [width: %3d][height: %3d] ` |
| `0x43ca6805` | makernote-playraw | `0x437adad0` | `0x437ada6e` | `CC::WriteMakerNotePlayRaw [err %d] [CcTagDaraSize %d] [CC_PLAYRAW_MAKERNOTE SIZE %d] ` |
| `0x43ca686d` | makernote-playraw | `0x437adb48` | `0x437adafe` | `CC::SetExtOutputMakerNotePlayRaw [err %d] [CcTagDaraSize %d] [CC_PLAYRAW_MAKERNOTE SIZE %d] ` |
| `0x43cb4cd3` | camcore-3dlut | `0x4381d2ec` | `0x4381d296` | `CamCore 3D-Lut table Write Start` |
| `0x43cb4d06` | camcore-3dlut | `0x4381d31c` | `0x4381d296` | `CamCore 3D-Lut table Write End` |
| `0x43cb4d37` | camcore-3dlut | `0x4381d336` | `0x4381d296` | `CamCore Change 3D-Lut %X` |
| `0x43cb4d62` | camcore-3dlut | `0x4381d350` | `0x4381d296` | `CamCore GetBaseAddress  %X` |

### 3.1 Las 2 trazas sin referencia estricta: falsos positivos de la regla ancha

La regla ancha (probar **todos** los `ldr` del registro en 4 KB) sí produce un par para cada una,
pero en los dos casos el `ldr` pertenece a **otra función** y el registro se reescribe antes del
`add`:

| traza | par ancho | por qué es falso |
|---|---|---|
| `GetKDZMode()` `0x43ca5bb7` | `add r3,pc` `0x4379f406` ← `ldr r3,[pc,#…]` `0x4379ed78` (W=`0x5067ad`, distancia 1678 B) | el `ldr` está en `CaptureInit` (`0x4379ed34`–`0x4379ede8`); el `add` está en `SetDualRecParam` (`0x4379f3c0`–`0x4379f47c`), donde el `ldr` **más cercano** es `0x4379f404` (W=`0x506511`) → destino `0x43ca591b` (`SetDualRecParam`). Entre ambos, `r3` se reescribe **8 veces** (`0x4379f3d2`, `0x4379f3d4`, `0x4379f3da`, `0x4379f3e4`, `0x4379f3ea`, `0x4379f3f0`, `0x4379f3f6`, `0x4379f3fc`) |
| `SetMovDevelopParam()` `0x43ca5d31` | `add r3,pc` `0x4379f924` ← `ldr r3,[pc,#…]` `0x4379f6fe` (W=`0x506409`, distancia 550 B) | el `ldr` está en `SetSACCSaEndParam` (`0x4379f6ea`–`0x4379f730`); el `add` está en `SetPlayRawDevelopParam` (`0x4379f8e0`–`0x4379f992`), donde el `ldr` **más cercano** es `0x4379f922` (W=`0x50638b`) → destino `0x43ca5cb3` (`SetPlayRawDevelopParam`) |

Además, ninguna de las dos tiene **puntero absoluto de 4 B** en los 11,4 MB del blob. Son, por tanto,
**trazas huérfanas**: el texto está en `.rodata` pero ningún código lo referencia.

### 3.2 Las 29 funciones

| función | fin | n trazas | trazas |
|---|---|---|---|
| `0x4379ec84` | `0x4379ed16` | 1 | ExtractCaptureData |
| `0x4379ed34` | `0x4379ede8` | 1 | CaptureInit |
| `0x4379ee04` | `0x4379eec4` | 1 | SetReadImageParam |
| `0x4379eee0` | `0x4379ef94` | 1 | SetNRParam |
| `0x4379efb0` | `0x4379f064` | 1 | SetOPDParam |
| `0x4379f080` | `0x4379f134` | 1 | AfterOPDAfterNR |
| `0x4379f150` | `0x4379f204` | 1 | SetDevelopParam |
| `0x4379f220` | `0x4379f2d4` | 1 | SetDevDetectDevelopParam |
| `0x4379f2f0` | `0x4379f3a6` | 1 | DetectYC |
| `0x4379f3c0` | `0x4379f47c` | 1 | SetDualRecParam |
| `0x4379f498` | `0x4379f568` | 1 | SetDAEParam |
| `0x4379f586` | `0x4379f604` | 1 | SetBdroIdtData |
| `0x4379f618` | `0x4379f6cc` | 1 | SetSACCParam |
| `0x4379f6ea` | `0x4379f730` | 1 | SetSACCSaEndParam |
| `0x4379f744` | `0x4379f7f8` | 1 | WriteExifMakernote |
| `0x4379f814` | `0x4379f8c6` | 1 | SetPlayRawDevDetectDevelop |
| `0x4379f8e0` | `0x4379f992` | 1 | SetPlayRawDevelopParam |
| `0x4379f9ac` | `0x4379fa60` | 1 | SetReviewDevelopParam |
| `0x4379fb48` | `0x4379fc02` | 1 | WriteSACCMakerNote |
| `0x437a1a7e` | `0x437a1ce0` | 5 | LutMode SA/CAP/MOV-MON, IsSplit, uc_sync |
| `0x437a1d7e` | `0x437a24ae` | 6 | Create3DLUT ×2, Copy3DLUT ×2, Copy2DLUT ×2 |
| `0x437a24fc` | `0x437a27b2` | 1 | LUT Write Cnt |
| `0x437a6890` | `0x437a6be4` | 5 | IE Error/Hold/Get ×3 |
| `0x437a7e00` | `0x437a7e3a` | 1 | IE Invalid Light or Map Number |
| `0x437a7e90` | `0x437a80a6` | 2 | IE Set, IE Set init NG |
| `0x437a8fac` | `0x437a9552` | 2 | CC miniRaw ×2 |
| `0x437ada6e` | `0x437adaee` | 1 | CC::WriteMakerNotePlayRaw |
| `0x437adafe` | `0x437adb74` | 1 | CC::SetExtOutputMakerNotePlayRaw |
| `0x4381d296` | `0x4381d386` | 4 | CamCore 3D-Lut ×4 |

## 4. La máquina de estados del control de captura

Cada uno de los 19 métodos vivos delega en una **función de etapa** distinta; la etapa escribe un
**byte de estado** en el objeto de estado (el puntero `[r0+8]`), en el offset `0xb`, y un
**sub-paso** en el offset `0xa`.

| método | función de etapa | byte de estado (`0xb`) | sub-paso (`0xa`) |
|---|---|---|---|
| `ExtractCaptureData()` | `0x43aeb2ae` | `0` | `0` |
| `CaptureInit()` | `0x43aeb2ec` | `1` | `0` |
| `SetReadImageParam()` | `0x43aeb324` | `2` | `0` |
| `SetNRParam()` | `0x43aeb358` | `3` | `0` |
| `SetOPDParam()` | `0x43aeb3a6` | `4` | `0` |
| `AfterOPDAfterNR()` | `0x43aeb3f8` | `5` | `0` |
| `SetDevelopParam()` | `0x437a1314` | `6` | — |
| `SetDualRecParam()` | `0x43aeb50e` | `7` | — |
| `SetDevDetectDevelopParam()` | `0x43aeb472` | `8` | `0` |
| `WriteExifMakernote()` | `0x43aeb5a6` | `9` | `0` |
| `SetReviewDevelopParam()` | `0x43aeb606` | `0xb` (11) | — |
| `SetPlayRawDevDetectDevelop` | `0x43aeb5ca` | `8` | `0` |
| `SetPlayRawDevelopParam()` | `0x43aeb5e8` | `6` | `0` |
| `SetSACCParam()` | `0x43aeb568` | `6` | — |
| `SetDAEParam()` | `0x43aeb564` (`b.w 0x4381d4ac`) | — | — |
| `DetectYC()` | `0x43aeb4ca` | `0` | — |
| `SetBdroIdtData()` | — (solo registro) | — | — |
| `SetSACCSaEndParam()` | — (solo registro) | — | — |
| `WriteSACCMakerNote()` | `0x437a16a4` | — | — |

Evidencia (extracto desensamblado de `0x43aeb3a6`, etapa de `SetOPDParam`):

```
0x43aeb3a6  ldr   r3, [r0, #8]
0x43aeb3a8  movs  r2, #4
0x43aeb3ae  strb  r2, [r3, #0xb]      ; estado = 4
0x43aeb3b2  bl    0x437a1818
0x43aeb3b6  strb  r0, [r5, #0xa]      ; sub-paso = <valor de 0x437a1818>
```

Los diez primeros (0..9) son **consecutivos y en el orden del pipeline**; `SetReviewDevelopParam`
usa `0xb` = 11 y los métodos "alternativos" (play raw, DAE, SACC) **reutilizan** valores ya
existentes, por lo que el byte funciona como *id de operación actual*, no como identificador único
de método.

## 5. Qué parametriza: la identidad de la captura

Los **18** métodos con formato de 6 campos (de los 19 vivos; `SetSACCSaEndParam()` no imprime campos)
leen la identidad de una estructura compartida (objeto pasado en `r1`), verificado desensamblando
`CaptureInit` (`0x4379ed34`), `SetReadImageParam` (`0x4379ee04`), `SetDevelopParam` (`0x4379f150`)
y `WriteSACCMakerNote` (`0x4379fb48`):

| campo | offset | tamaño | evidencia |
|---|---|---|---|
| `CapMode` | `0x1c0` | 32 bits | `ldr.w r3,[r1,#0x1c0]` → `[sp]` |
| `ExposureID` | `0x1b8` | 32 bits | `ldr.w r3,[r1,#0x1b8]` → `[sp,#4]` |
| `ContID` | `0x1bc` | 32 bits | `ldr.w r3,[r1,#0x1bc]` → `[sp,#8]` |
| `BDROSeq` | `0x6ec` | 32 bits | `ldr.w r3,[r1,#0x6ec]` → `[sp,#0xc]` |
| `BDRObase` | `0x6f4` | 32 bits | `ldr.w r3,[r1,#0x6f4]` → `[sp,#0x10]` |
| `FrameID` | `0x701` | 8 bits | `ldrb.w r3,[r1,#0x701]` → `[sp,#0x14]` |

`ExtractCaptureData()` (`0x4379ec84`) usa **otra** estructura de 16 bytes, con los mismos campos
en otro orden:

| campo | offset |
|---|---|
| `ExposureID` | `0x00` |
| `ContID` | `0x04` |
| `CapMode` | `0x08` |
| `FrameID` | `0x0c` |

Esto confirma y **precisa** lo que S96 dejó abierto: la identidad de una captura son cinco campos
(`CapMode`, `ExposureID`, `ContID`, `FrameID`, `BDROSeq`) más `BDRObase`, y **`CapMode`/`ExposureID`/
`ContID` son 32 bits** (no bytes).

### 5.1 El canal de parámetros compartidos

Además de leerlos directamente de la estructura, el módulo usa la **tabla de parámetros compartida**
a través de `0x43ae9226(tabla, id, &salida)`, que busca un registro de **12 bytes** por id de 16
bits:

```
0x43ae922e  movs  r3, #0xc
0x43ae9230  mla   r3, r3, r4, r0        ; registro = base + 12*i
0x43ae9234  ldrb  r6, [r3, #5]
0x43ae9236  ldrb  r5, [r3, #4]
0x43ae9238  orr   r5, r5, r6, lsl #8    ; id de 16 bits
0x43ae923c  cmp   r5, r1                ; == id buscado
```

El módulo usa los ids **`0x9408`, `0x9409`, `0x9410`** (helper `0x437ad618`, que los copia a
`[r3+4]` y `[r3+8]` de su estructura de recursos); el id `0x9400` lo usa el motor de captura
(`Stage_Raw`). Este es el **canal de estado compartido** entre el control de captura, el motor de
imagen (S110), el gestor de captura (S106) y el DMM (S113).

### 5.2 Rango de `CapMode`

El helper `0x437a1818` (devuelve el sub-paso) clasifica por un campo de 16 bits en el offset `0x14`:

```
0x437a1826  ldrh  r2, [r3, #0x14]
0x437a1828  sub.w r2, r2, #0x480
0x437a182c  subs  r2, #2
0x437a182e  uxth  r2, r2
0x437a1830  cmp   r2, #2
0x437a1832  bls   0x437a18b4           ; <=> campo en 0x480..0x482
```

→ un campo de 16 bits se compara contra `0x480..0x482`; es **INFERENCIA** (no verificada) que ese
campo sea `CapMode` (el rango `0x480` no aparece en ninguna traza).

## 6. Ficheros fuente

**Dato verificado**: ninguna de las 29 funciones del módulo referencia un nombre de fichero
`.cpp`/`.h` (0 referencias en `0x4379ec84`–`0x437adb74` y `0x4381d296`–`0x4381d386`); el módulo
solo emite trazas de información, no de error con fichero/línea.

Lo que sí se puede atribuir, por **orden de código** (la referencia al nombre de fichero más
cercana por delante y por detrás del sitio de llamada — INFERENCIA de unidad de traducción):

| fichero | vaddr del **nombre** | sitios de **código** que lo referencian |
|---|---|---|
| `SyncYCOut.cpp` | `0x43ca4de4` | `0x4379b40a`, `0x4379b450` (justo antes del bloque CC) |
| `Stage_SACC.cpp` | `0x43c9f18a` | `0x43782464` — **llama a `SetSACCParam()` y `WriteSACCMakerNote()`** |
| `CaptureUtilityCommon.cpp` | `0x43c9f285` | `0x43782c20`, `0x43782e44` |
| `CaptureUtilityExifMkNote.cpp` | `0x43c9f505` | `0x43783e34` |
| `Stage_Raw.cpp` | `0x43cad1e2` | `0x437f247c`…`0x437f2978` — llama a `WriteExifMakernote()` |
| `Stage_ResizeHV.cpp` | `0x43cad6ea` | `0x437f480c` |
| `CaptureUtilityCamCore.cpp` | `0x43cad7ee` | `0x437f5554`, `0x437f55a0`, `0x437f5690`, `0x437f5a04` |
| `CaptureUtilityImager.cpp` | `0x43cae2f6` | `0x437f8104` |
| `CaptureUtilityModuleAPI.cpp` | `0x43cae4b7` | `0x437f87b2`, `0x437f8ddc` — llama a `CaptureInit()`, `SetReadImageParam()`, `SetReviewDevelopParam()` |
| `CaptureUtilityPreReview.cpp` | `0x43cae53b` | `0x437f9068`, `0x437f918c` — llama a `SetDualRecParam()` |
| `CaptureUtilitySDF.cpp` | `0x43cae774` | `0x437f9fde`…`0x437faab4` |
| `CaptureUtilityStdYc.cpp` | `0x43cae822` | `0x437fac18`, `0x437fae50` |
| `ImageParamCapture.cpp` | `0x43ca98f4` | `0x437dcee8`, `0x437dcfc8` (justo después del bloque CC) |
| `CaptureManager.cpp` | `0x43ca9c97` | `0x437ddeda`…`0x437df2be` |
| `NotifyController.cpp` | `0x43caa4f6` | `0x437e11c4`…`0x437e14f8` |
| `Stage_Adjust.cpp` | `0x43cc6cc6` | `0x438bd764` — llama a `DetectYC()` |
| `Stage_MARBLE.cpp` | `0x43cc956d` | `0x438cb068` — llama a `SetDAEParam()` y `SetNRParam()` |
| `Stage_OPD.cpp` | `0x43cc9785` | `0x438cbb70`, `0x438cbc94` — llama a `SetOPDParam()` y `AfterOPDAfterNR()` |
| `Stage_Orientation.cpp` | `0x43cc97b4` | `0x438cbe30`…`0x438cc0a0` — llama a `SetReadImageParam()` |

**NO VERIFICADO**: el/los ficheros fuente que *implementan* la clase `CC` (ver §10).

## 7. Grafo de llamadas

### 7.1 Saliente (qué llama el control de captura)

Los **19** métodos vivos del control de captura delegan el registro en la **misma función**
`0x4379ebd8`, que formatea el texto (`vsnprintf`, `0x439c5004`, envuelto por `0x43902718`) y lo
publica en una cola OSAL a través de las tablas virtuales `0x435612d0`/`0x435612ec`/`0x43561308`.
Los tres métodos del bloque LUT usan un registrador **distinto**, `0x437a19d0` (`0x437a1a7e`,
`0x437a1d7e`, `0x437a24fc`).

Las llamadas de trabajo de cada método (una función de etapa por método) están en §4.

### 7.2 Entrante (quién llama al control de captura) — 37 llamadas

| método llamado | nº | llamadores (sitio → función) | bloque de código del llamador (INFERENCIA) |
|---|---|---|---|
| `SetSACCParam` `0x4379f618` | 1 | `0x4378258a` → `0x43782464` | `Stage_SACC.cpp` (ref. `0x43782464`) |
| `WriteSACCMakerNote` `0x4379fb48` | 1 | `0x4378286a` → `0x43782464` | `Stage_SACC.cpp` (ref. `0x43782464`) |
| `CaptureInit` `0x4379ed34` | 3 | `0x437f8880`, `0x437f8976` → `0x437f87b2`/`0x437f88f2`; `0x43afff4c` → `0x43affede` | `CaptureUtilityModuleAPI.cpp` (ref. `0x437f87b2`) / sin atribuir |
| `SetReadImageParam` `0x4379ee04` | 2 | `0x437f8d78` → `0x437f8be0`; `0x438cc9aa` → `0x438cc7a0` | `CaptureUtilityModuleAPI.cpp` (refs `0x437f87b2`–`0x437f8ddc`) / `Stage_Orientation.cpp` (refs `0x438cbe30`–`0x438cc0a0`) |
| `SetNRParam` `0x4379eee0` | 1 | `0x438cb4b8` → `0x438cb300` | `Stage_MARBLE.cpp` (ref. `0x438cb068`) |
| `SetOPDParam` `0x4379efb0` | 2 | `0x438cbba8` → `0x438cbb70`; `0x438cbcd8` → `0x438cbc94` | `Stage_OPD.cpp` (refs `0x438cbb70`, `0x438cbc94`) |
| `AfterOPDAfterNR` `0x4379f080` | 1 | `0x438cbd6e` → `0x438cbc94` | `Stage_OPD.cpp` (ref. `0x438cbc94`) |
| `SetDevelopParam` `0x4379f150` | 2 | `0x43b000fa` → `0x43b000ce`; `0x43b1d55a` → `0x43b1d52e` | sin atribuir |
| `SetDevDetectDevelopParam` `0x4379f220` | 1 | `0x43b00066` → `0x43b00000` | sin atribuir |
| `DetectYC` `0x4379f2f0` | 1 | `0x438bd74a` → `0x438bd6b8` | entre `still_cnt_panoramaStitch.cpp` (`0x438bcef8`) y `Stage_Adjust.cpp` (`0x438bd764`) — **ambiguo** |
| `SetDualRecParam` `0x4379f3c0` | 1 | `0x437f8ee2` → `0x437f8eba` | entre `CaptureUtilityModuleAPI.cpp` (`0x437f8ddc`) y `CaptureUtilityPreReview.cpp` (`0x437f9068`) — **ambiguo** |
| `SetDAEParam` `0x4379f498` | 1 | `0x438cb490` → `0x438cb300` | `Stage_MARBLE.cpp` (ref. `0x438cb068`) |
| `WriteExifMakernote` `0x4379f744` | 2 | `0x437f44a4` → `0x437f4378`; `0x43afff56` → `0x43affede` | entre `Stage_Raw.cpp` (`0x437f2978`) y `Stage_ResizeHV.cpp` (`0x437f480c`) — **ambiguo** / sin atribuir |
| `SetPlayRawDevDetectDevelop` `0x4379f814` | 1 | `0x43b00070` → `0x43b00000` | sin atribuir |
| `SetPlayRawDevelopParam` `0x4379f8e0` | 1 | `0x43b00182` → `0x43b000ce` | sin atribuir |
| `SetReviewDevelopParam` `0x4379f9ac` | 1 | `0x437f8daa` → `0x437f8be0` | `CaptureUtilityModuleAPI.cpp` (refs `0x437f87b2`–`0x437f8ddc`) |
| `ExtractCaptureData` `0x4379ec84` | 1 | `0x43afa144` → `0x43afa0ce` | sin atribuir |
| `LUT Write Cnt` `0x437a24fc` | 1 | `0x43aeb66a` → `0x43aeb654` | — |
| `IE` (grupo) `0x437a6890` | 1 | `0x43aebe96` → `0x43aebe44` | — |
| `IE Invalid…` `0x437a7e00` | 2 | `0x437a7ede`, `0x437a7ef2` → `0x437a7e90` | interno |
| `IE Set` `0x437a7e90` | 3 | `0x43aebe64` → `0x43aebe44`; `0x43aebece` → `0x43aebea2`; `0x43aebf04` → `0x43aebee4` | — |
| `CC miniRaw` `0x437a8fac` | 7 | `0x437a9628`…`0x437a9802` → `0x437a95d2`…`0x437a97e2` | interno |

**Lectura**: el control de captura es un **servidor** de parámetros de captura para las *stages* del
pipeline (`[IMAGING_CAP]`, S106) y para las utilidades `CaptureUtility*`; **no** llama al gestor de
captura, al motor de imagen, al imager ni al DMM (0 llamadas directas a las funciones de esos
módulos; ver §8).

## 8. Relación con los módulos ya documentados

| módulo (hito) | relación con `[CAMERA_MAIN_CC]` | evidencia |
|---|---|---|
| **Gestor de captura `[IMAGING_CAP]`** (S106) | **el gestor llama al control**, no al revés: `Stage_SACC.cpp` (`0x43782464`) llama a `SetSACCParam()` (`0x4378258a`) y a `WriteSACCMakerNote()` (`0x4378286a`); el texto `CC::set_param_seq_sacc` (`0x43c9eeb1`) aparece en `[IMAGING_CAP]: %s: CC::set_param_seq_sacc error` (`0x43c9ee9e`) | verificado |
| **Motor de imagen `[CAMERA_MAIN_YC]`** (S110) | **estado compartido**, sin llamada directa: el CC lee/escribe la tabla de parámetros compartidos `Camera::Imaging::ImageParam` / `Camera::Capture::ImageParam_Capture*` (typeinfo en `0x43ff8f1c`–`0x43ff8f3c`) mediante `0x43ae9226`; además el CC mantiene LUTs 3D que el motor consume (`LutMode Change CAP`) | parcial: typeinfo + tabla de parámetros verificados; el flujo exacto NO VERIFICADO |
| **Imager `[CAM_IMAGER]`** (S115) | **estado compartido**, sin llamada directa: `CaptureUtilityImager.cpp` (`0x43cae2f6`, ref. de código `0x437f8104`) es el puente; el `drive_mode` del imager (S96) y el `CapMode` del CC son campos distintos del mismo `ImageParam` | NO VERIFICADO el nexo exacto |
| **DMM `[CAM_DMM]`** (S113) | **relación lejana**: **0** llamadas desde las 29 funciones del CC a las 25 funciones del DMM (`0x439011d8`…`0x43903d5c`, `analysis/s113_cam_dmm/func_map.json`); la memoria la pide el gestor de captura (S106), no el CC | verificado (0 intersección de destinos `bl`) |
| **Motor de 17 secciones / `Stage_*`** (S114) | **es el consumidor directo**: las *stages* `Stage_SACC.cpp` (`0x43782464`), `Stage_OPD.cpp` (`0x438cbb70`, `0x438cbc94`), `Stage_MARBLE.cpp` (`0x438cb068`) y `Stage_Orientation.cpp` (`0x438cbe30`–`0x438cc0a0`) llaman a los métodos del CC | verificado (37 llamadas) |
| **CamCore** (S107) | el CC escribe la **tabla 3D-LUT del CamCore** (`0x4381d296`, 4 trazas) | verificado |

**Cero llamadas directas** desde el CC a los módulos ya documentados: la intersección de los 79
destinos `bl`/`blx` de las 29 funciones del CC con los conjuntos de funciones de `[CAM_DMM]` (25,
S113), `[CAM_IMAGER]` (94, S115) y `[CAMERA_MAIN_YC]` (332, S110) es **vacía** en los tres casos.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| cadenas con el prefijo `[CAMERA_MAIN_CC]` | **49** | **0** | **0** |
| Prefijos `[CAMERA_MAIN_*]` en todo el blob | 8 (135+49+9+42+72+429+127+970 = 1833) | **0** | **0** |
| mensajes de la A6000 presentes en el otro modelo (sin prefijo) | 49 | **47** | **47** |
| mensajes *extendidos* en la A6000 | — | `IsSplit Change [%02X] -> [%02X] uc_proc[%02X]` (`0x7844f4`) | `IsSplit Change [%02X] -> [%02X] uc_proc[%02X]` (`0x895189`) |
| | | `Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d` (`0x784571`) | `Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d` (`0x895206`) |

* La **A7S y la A6300 no tienen ninguna familia de prefijos `[CAMERA_MAIN_*]`**: sus
  equivalentes (`ExtractCaptureData() …`, `CaptureInit() …`, `SACC Open Error`, …) existen
  **sin etiqueta de módulo**. En la A6000 la A7S además tiene la cadena de comentario
  `IsSplit Change && (core_sa != CC_PROC_SA) >>> uc_ret = C_TRUE` (`0x784522`), **inexistente** en la
  A6000 (0 coincidencias de `CC_PROC`, `core_sa`, `uc_proc`).
* Los **47 mensajes comunes** son texto a texto idénticos; las 2 diferencias son **ampliaciones de
  formato** en la A6000 (el campo `uc_proc[%02X]` y los campos `BlkOfs Cr/Cb`).
* Las **direcciones** no son comparables (base distinta por modelo); el diferencial de **funciones**
  (mismo número de métodos y misma máquina de estados) es **NO VERIFICADO**.

## 10. NO VERIFICADO / abierto

1. **El/los ficheros fuente que implementan la clase `CC`.** Ninguna de las 29 funciones referencia
   un `.cpp`/`.h`; la atribución por proximidad (§6) es INFERENCIA.
2. **El significado de la sigla `CC`.** El firmware no la expande; el registro de clases sólo dice
   `CC::CcEncryptedTagData`, `CC::CcEncryptedFtTagData`, `CC::CcEncryptedNflashTagData`
   (`CC` + `Cc` + `Encrypted` + `Tag`/`Ft`/`Nflash` + `Tag`/`Data`).
3. **Qué son exactamente `LightNum`/`MapNum`** (sub-bloque IE): los números de LUT de efecto
   (imagen) que se registran y se leen; la fuente del recurso está en `IE Get … [ResAdress:%10lx]`.
4. **El rango real de `CapMode`, `ContID`, `BDROSeq`, `BDRObase` y `FrameID`**: sólo se ha
   verificado el offset y el tamaño de los campos y el rango `0x480..0x482` de un campo de 16 bits
   sin identificar (§5.2).
5. **La equivalencia `drive_mode` (imager) ↔ `CapMode` (captura)**: no verificada; el CC y el
   imager no se llaman directamente.
6. **Las 2 trazas huérfanas** `GetKDZMode()` y `SetMovDevelopParam()`: no se sabe si corresponden a
   métodos nunca compilados o a código muerto (el texto sí está en `.rodata`).
7. **El contenido de la LUT 3D y su consumidor**: el CC la escribe (`Create3DLUT`, `Copy3DLUT`) y
   el CamCore la consume (`CamCore Change 3D-Lut`), pero el flujo completo no está reconstruido.
8. **El diferencial a nivel de función A7S/A6300** (mismos métodos, mismas etapas).

## 11. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (32 tests del hito + comprobaciones a mano):**

1. **Recuento**: 49 apariciones del token `[CAMERA_MAIN_CC]` en el blob; **47** con referencia
   estricta (1 sitio cada una) en **29 funciones** emisoras; las 2 huérfanas son
   `GetKDZMode()` `0x43ca5bb7` y `SetMovDevelopParam()` `0x43ca5d31`, y el informe demuestra que
   su par "ancho" es un **falso positivo** → coherente con la metodología canónica
   (`analysis/s106_imaging_cap/pic_xref_methodology.md`).
2. **Nombres de la clase `CC`**: verificados en los bytes — `CcEncryptedTagData` `0x43ca9242`,
   `CcEncryptedFtTagData` `0x43ca9259`, `ImageParam_Capture` `0x43ca9802`. *Matiz*: las
   direcciones `0x43ff8ee4`/`0x43ff8f24` que cita el informe son **tablas de punteros**
   (vptrs), no las cadenas de nombre; estas están en la zona de `.rodata` indicada arriba. La
   atribución de la clase `CC` a esos punteros es coherente con lo que describe el informe.
3. **Ficheros y métodos citados, verificados**: `Stage_SACC.cpp` `0x43c9f18a`,
   `Stage_OPD.cpp` `0x43cc9785`, `SetSACCParam` `0x43ca5aa7`, `WriteSACCMakerNote` `0x43ca5e42`,
   `SetOPDParam` `0x43ca56b7`, `AfterOPDAfterNR` `0x43ca5735`, `LutMode Change SA` `0x43ca5f0a`,
   `IE     Error Null Address` `0x43ca6470`, `CamCore 3D-Lut table Write Start` `0x43cb4cd3`.
4. **Diferencial**: A7S fw3.20 y A6300 fw2.01 tienen **0** cadenas con el prefijo (ninguno de
   los dos modelos tiene familia `[CAMERA_MAIN_*]`) y **47/49** mensajes idénticos sin
   etiqueta → encaja con el mapa de etiquetado de S128 (los `[CAMERA_MAIN_*]` son de la fw3.21
   de la A6000).

**Nota**: el informe ya traía una sección "Revisión del agente principal" (vacía, como se le
pidió); esta es la real.
