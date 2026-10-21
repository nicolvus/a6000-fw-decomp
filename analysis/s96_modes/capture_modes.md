# S96 — Modos de captura: `drive_mode`, `CapMode` y la tabla de 69 → 14 ShdMode

**Alcance:** línea de ingeniería inversa **general** de la cámara: cómo se nombran y se propagan los
**modos de captura** en la A6000 fw3.21 (el `drive_mode` del imager, el `CapMode` del gestor de
captura y la tabla que los cruza con el perfil de sombreado). No es la línea SilentShutter, ni la
montura (S66 —aunque enlaza con su tabla de sombreado—), ni el AF, ni ADJ_CMD, ni ZPD, ni `apc_*`,
ni ZIT, ni ADF, ni el API del SA, ni el visor, ni las caras, ni el wireless, ni el almacenamiento,
ni la reproducción, ni el IDT, ni AutoFraming.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s96_modes.py`.

---

## 1. Los dos niveles de "modo" (VERIFICADO)

### 1.1 `drive_mode` — el modo del **imager** (0..0x44 = 69 valores)

Lo usa el driver del sensor (`CAM_IMAGER`/`DFECore`):

| traza | dirección |
|---|---|
| `[CAM_IMAGER]: Invalid SetExposure Error!! [drive_mode:%2d]` | `0x43c9397a` |
| `[CAM_IMAGER]: Invalid Execute Error!! [drive_mode:%2d]` | `0x43c93a6c` |
| `[CAM_IMAGER]: Invalid SetRead Error!! [drive_mode:%2d]` | `0x43c93d30` |
| `[CAM_IMAGER]: GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]` | `0x43c94a9f` |
| `[CAM_IMAGER]: Invalid GetModeParam Error!! [drive_mode:%02x]` | `0x43c94aff` |
| `[DFECore]: eyePtn:%d is unusable in driveMode:%d.` | `0x43c92bde` |
| `GetPrelightImagerDriveMode` | `0x43cae26b` |
| `[IMAGING_CAP]: getDriveModeSizeRatio Error!(%x) max %x, cur %x` | `0x43cae2b7` |
| `[CAM_IMAGER]: Execute(0) [NowDriveMode:%2d] [SIFSyncCode:%02x]` | `0x43c93aa3` |

→ el `drive_mode` **sincroniza el imager con el resto del sistema** (`SIFSyncCode`, `GetTransModeState`
de un modo a otro) y **condiciona el tamaño de lectura** (`getDriveModeSizeRatio`). El patrón de
"patrón de ojos" (`eyePtn`) depende de él.

### 1.2 `CapMode` / `ExposureID` / `ContID` / `FrameID` / `BDROSeq` — el modo de la **captura**

Lo usa el gestor `CAMERA_MAIN_CC` (S79/S82):

| función | traza | dirección |
|---|---|---|
| `ExtractCaptureData()` | `[CapMode:%d] [ExposureID:%d] [ContID:%d] [FrameID:%d]` | `0x43ca54c8` |
| `CaptureInit()` | `[CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d]` | `0x43ca552b` |
| `SetReadImageParam()` | ídem | `0x43ca55a9` |
| `SetNRParam()` | ídem | `0x43ca5627` |
| `SetOPDParam()` | ídem | `0x43ca56a5` |

→ la identidad de una captura la definen **cinco campos**: el modo (`CapMode`), el identificador de
exposición (`ExposureID`), el de **continuidad** (`ContID`, p. ej. ráfaga/bracketing), el de fotograma
(`FrameID`) y la **secuencia BDRO** (`BDROSeq`, el "bilateral DRO" que el motor YC usa para el
cálculo de parámetros, S78/S89).

## 2. La tabla que cruza modo de captura y perfil de sombreado (VERIFICADO, de S66)

`SHD::GetShdMode` (`0x438ef40e`) recibe el `drive_mode` y lo traduce con una **tabla de saltos
`tbb` de 69 bytes** en `0x438ef418`:

```
0x438ef40e  push {r0, r1, r4, lr}
0x438ef410  cmp  r3, #0x44        ; drive_mode 0..0x44 (69 modos)
0x438ef412  bhi  0x438ef492      ; -> "unknown drive_mode"
0x438ef414  tbb  [pc, r3]        ; tabla en 0x438ef418
```

Los 69 modos se reducen a **14 valores de ShdMode** (`0x00`–`0x0D` y `0x0F`; falta `0x0E`), con
reparto `0x02`→20 modos, `0x00`→10, `0x01`→8, `0x0A`→7, `0x08`→4, `0x03`→4 y el resto 1–3.
INFERENCIA: el sombreado se selecciona cruzando **modo de captura × modelo de lente**.

## 3. Los modos concretos que se nombran en el firmware (VERIFICADO)

| modo | evidencia | dirección |
|---|---|---|
| foto | `SDF_RECMODE_STILL_REC` | `0x43c7effb` |
| vídeo | `REQ_MOVIE_REC` / `REPLY_MOVIE_REC` | `0x43ca13be` / `0x43ca15b6` |
| ráfaga | `BURST_CNT`, `Burst_` | `0x43cb4bfe`, `0x43ccaf9b` |
| panorámica | `MSG_ID_SDF_PANORAMA_CCNR_ENCODE`, `ApiPanoramaCcnrEncode.cpp`, `ModulePanoramaCcnrEncode.cpp` | `0x43c781e4`, `0x43c79fd2`, `0x43c7b926` |
| barrido (sweep) | `[IMAGING]: [PanoramaSweepStart] …`, `still_cnt_panoramaSweep.cpp` | `0x43cab054`, `0x43cab088` |
| bracketing | `lc_BracketAF.cpp` | `0x43ca79ba` |
| intervalo | `[SDF] interval(PTM) %ld`, `[SDF_ERR] interval_ptm over 10[sec]` | `0x43c7a1a5` |
| golf | `[ADF][DBGCMD]SoundAnalyzer StartGolfShot` … (S88) | `0x43c2b143` |

## 4. Abierto (NO_VERIFICADO)

- La **tabla de 69 valores de `drive_mode` con su nombre**: no hay una tabla de nombres en el blob
  (los nombres de modo aparecen en el userland, no en `av-cam.bin`).
- El rango real de `CapMode` y de `ContID` (cuántos valores toma cada uno).
- Cómo se calcula `BDROSeq` y qué valores tiene.
- La tabla de "69 → 14" completa (la tiene `analysis/s66/out/shd_modes_a6000.txt`; no se reproduce aquí).
- La equivalencia entre `drive_mode` (imager) y `CapMode` (captura).

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s96_modes.py -q
```
