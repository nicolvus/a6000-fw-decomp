# S123 — `[CAMERA_MAIN_CC]`: el control de captura (clase `CC`)

**Hito de la línea de ingeniería inversa general** (A6000 fw3.21). No toca la línea del obturador
electrónico: **0** mensajes de obturador en las 49 trazas.
Informe: [analysis/s123_camera_main_cc/camera_main_cc.md](../../analysis/s123_camera_main_cc/camera_main_cc.md) ·
Datos: `analysis/s123_camera_main_cc/camera_main_cc.json` · Test: `tests/test_s123_camera_main_cc.py` (32 tests).

## Hallazgo central

Las **49 trazas `[CAMERA_MAIN_CC]`** son el registro de la **clase C++ `CC`** (control de captura) del
hilo principal de la cámara. **No** es un módulo plano: son **6 sub-bloques**, y **cada uno es un
tramo contiguo propio en `.rodata`** — control de captura (21, `0x43ca54c8`–`0x43ca5e30`), LUT 2D/3D
(12), IE / image effect (8), miniRaw (2), MakerNote de reproducción raw (2) y CamCore 3D-LUT (4,
`0x43cb4cd3`–`0x43cb4d62`). Regla PIC **estricta** (canónica): **47/49** referenciadas (1 sitio cada
una) y **2 huérfanas** (`GetKDZMode()` `0x43ca5bb7`, `SetMovDevelopParam()` `0x43ca5d31`): la regla
ancha les atribuye un par, pero es un **falso positivo** (el `ldr` pertenece a otra función y `r3` se
reescribe antes del `add`; sin puntero absoluto). **29 funciones** las emiten.

## Lo que se ha reconstruido

* **Máquina de estados**: cada uno de los 19 métodos vivos delega en una **función de etapa**
  distinta (`0x43aeb2ae`…`0x43aeb640`, `0x437a1314`, `0x437a16a4`, `0x4381d4ac`) que escribe un
  **byte de estado** (offset `0xb` del objeto) y un **sub-paso** (offset `0xa`). Los diez primeros
  estados (0..9) son **consecutivos y en el orden del pipeline**: `ExtractCaptureData` (0) →
  `CaptureInit` (1) → `SetReadImageParam` (2) → `SetNRParam` (3) → `SetOPDParam` (4) →
  `AfterOPDAfterNR` (5) → `SetDevelopParam` (6) → `SetDualRecParam` (7) → `SetDevDetectDevelopParam`
  (8) → `WriteExifMakernote` (9). **Los ids de parámetro compartidos** que usa son `0x9408`, `0x9409`
  y `0x9410` (`0x437ad618`, tabla de 12 B por id de 16 bits, `0x43ae9226`).
* **Identidad de la captura** (precisa lo que S96 dejó abierto): `CapMode@0x1c0`, `ExposureID@0x1b8`,
  `ContID@0x1bc`, `BDROSeq@0x6ec`, `BDRObase@0x6f4`, `FrameID@0x701` (32/32/32/32/32/8 bits), leídos de
  `Camera::Capture::ImageParam_Capture*` (typeinfo `0x43ff8f24`–`0x43ff8f3c`); `ExtractCaptureData` usa
  otra de 16 B (`ExposureID@0x00`, `ContID@0x04`, `CapMode@0x08`, `FrameID@0x0c`).
* **Clase `CC` confirmada**: el registro de clases de `0x43ff8ee4` lista `CC::CcEncryptedTagData`,
  `CC::CcEncryptedFtTagData`, `CC::CcEncryptedNflashTagData` junto a `LC::`/`TC::`/`FC::`/`IM::`/`EC::` (la
  familia de `[CAMERA_MAIN_LC]`, `[CAMERA_MAIN_TC]`, …), y dos trazas llevan el ámbito `CC::`
  (`CC::WriteMakerNotePlayRaw` `0x43ca6817`).
* **Grafo entrante**: **37 llamadas** desde 22 de las 29 funciones. Los llamadores son las **stages
  del pipeline** (`Stage_SACC.cpp` → `SetSACCParam()`/`WriteSACCMakerNote()`, `Stage_OPD.cpp` →
  `SetOPDParam()`/`AfterOPDAfterNR()`, `Stage_MARBLE.cpp` → `SetNRParam()`/`SetDAEParam()`,
  `Stage_Orientation.cpp` → `SetReadImageParam()`) y las `CaptureUtility*` (`CaptureUtilityModuleAPI.cpp`
  → `CaptureInit()`/`SetReadImageParam()`/`SetReviewDevelopParam()`); la atribución de fichero es
  **INFERENCIA** (3 llamadores sin atribuir o ambiguos). **0 llamadas directas** a `[CAM_DMM]` (S113),
  `[CAM_IMAGER]` (S115) y `[CAMERA_MAIN_YC]` (S110): el enlace es por **tabla de parámetros
  compartida** (`0x43ae9226`, ids `0x9408`/`0x9409`/`0x9410`).

## Diferencial A7S fw3.20 / A6300 fw2.01

**0** cadenas con el prefijo `[CAMERA_MAIN_CC]` en A7S y A6300: **ninguno de los dos modelos tiene
ninguna** familia de prefijos `[CAMERA_MAIN_*]`. Los **47/49 mensajes son idénticos** sin la etiqueta de
módulo; los 2 restantes son **ampliaciones de formato** en la A6000 (`IsSplit Change … uc_proc[%02X]` y
`Create3DLUT … BlkOfs Cr/Cb`). La A7S tiene además `IsSplit Change && (core_sa != CC_PROC_SA) >>>
uc_ret = C_TRUE`, **inexistente** en la A6000.

## Abierto / NO VERIFICADO

* El/los **ficheros fuente** que implementan la clase `CC` (las 29 funciones no referencian ningún
  `.cpp`/`.h`; la atribución por proximidad es INFERENCIA) y el significado de la sigla **`CC`**.
* Rangos reales de `CapMode`/`ContID`/`BDROSeq`/`BDRObase`/`FrameID`; sólo se ha verificado un campo de
  16 bits comparado contra `0x480..0x482` (`0x437a1818`).
* Equivalencia `drive_mode` (imager) ↔ `CapMode` (captura); diferencial **a nivel de función** con
  A7S/A6300 (mismos métodos y misma máquina de estados).