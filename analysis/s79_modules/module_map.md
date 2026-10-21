# S79 — Mapa de módulos del firmware `av-cam.bin` por prefijos de log (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: la **arquitectura modular** del
`av-cam.bin`, deducida de los prefijos de traza `[MODULO]` que usa el firmware. No es la línea
SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD (`analysis/s73_adj/`), ni ZPD
(`analysis/s75_zpd/`), ni las etapas (`analysis/s76_stages/`), ni los parámetros `apc_*`
(`analysis/s78_apc/`).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `analysis/s79_modules/module_map.json` (tabla completa, A6000 y A7S), `tests/test_s79_modules.py`.

---

## 1. Método (VERIFICADO)

El firmware numera sus trazas con un prefijo entre corchetes al principio de la cadena
(`[CAMERA_MAIN_YC]: …`, `[ADF][ADF][PROC][ERR]…`, `[MOUNT_ERROR]: …`). Extrayendo **todos** los
patrones `[A-Z][A-Z0-9_]{2,}` de las cadenas del blob y contando repeticiones y rango de
direcciones, se obtiene la **tabla de módulos** del firmware:

- **A6000 (fw3.21): 348 prefijos distintos.**
- **A7S (fw3.20): 277 prefijos distintos.**

## 2. La descomposición de `CAMERA_MAIN` (VERIFICADO)

El logger de la aplicación principal (`CAMERA_MAIN`) delega en **8 submódulos**, cada uno con su
propio prefijo (con nº de trazas y rango de cadenas):

| submódulo | trazas | rango de cadenas | contenido (VERIFICADO por las cadenas) |
|---|---|---|---|
| `CAMERA_MAIN_YC` | 970 | `0x43ca88f6`–`0x43ccd469` | **motor de imagen**: `api_YC_CaptureRawReadExecuteClp`, `api_YC_InitCap`, `api_YC_SetCapTbox`, `api_YC_SetSaCamDsp`, `job_YC_*`, `YAP::job_YC_CalcParam` (S78) |
| `CAMERA_MAIN_SYNC` | 429 | `0x43c9b409`–`0x43cb5616` | **gestor de recursos sincronizados**: `SyncResMgr::Lock/Unlock/Free`, `CAMDEV(0)`/`CAMDEV(1)` (los dos núcleos de cámara) |
| `CAMERA_MAIN` | 135 | `0x43c9c57b`–`0x43ccae46` | nivel principal: `calibration_fc_pos`, `agus_debug_dmaf_fc_inf` |
| `CAMERA_MAIN_TC` | 127 | `0x43ca7fd4`–`0x43ccb350` | **giro/calibración temporal**: `GyroStitScl`, `TC:APL:Err: LmtGyroVect`, `calib_r_ave` |
| `CAMERA_MAIN_LC` | 72 | `0x43c9c6f6`–`0x43ca7e0b` | **calibración de lente** (LC): `lc_Movie_DM_AF_Util_getMiniRawAddr/getResizedYAddr/getBufferAddr/getSaIfAddr` |
| `CAMERA_MAIN_CC` | 49 | `0x43ca54c8`–`0x43cb4d62` | **control de captura**: `ExtractCaptureData()`, `CaptureInit()`, `SetReadImageParam()`, `SetNRParam()` con `[CapMode][ExposureID][ContID][BDROSeq]` |
| `CAMERA_MAIN_IM` | 42 | `0x43ca6b32`–`0x43cb5ffa` | **temperatura/ambiente**: `movie thermal diffTemp`, `environmentalTemp`, `paramA%f paramB%f diff:%d` |
| `CAMERA_MAIN_FC` | 9 | `0x43ca6944`–`0x43ca6aec` | **datos de ojo/cara**: `Eye data is invalid, but lc flag is true.` + errores `osal_alloc_timer/set_timer/free_timer` |

**Enlaces con otros hitos (VERIFICADO):** `CAMERA_MAIN_LC` es el sitio donde vive la calibración de
lente y, por tanto, el consumidor de los datos ZPD (S75: `LC_GetZpdResultInfo`,
`area[60].zpd_flags/defocus`); `CAMERA_MAIN_FC` es el que recibe los *datos de ojo* y menciona la
bandera `lc`; `CAMERA_MAIN_TC` es el único que habla del **giro** (conecta con S70/EIS);
`CAMERA_MAIN_CC` es el que reparte `CapMode/ExposureID/ContID/BDROSeq` (conecta con S78: el cálculo
`apc_coring` depende de la secuencia BDRO).

## 3. Las demás familias de módulos (VERIFICADO, ≥40 trazas)

| módulo | trazas | rango |
|---|---|---|
| `ADF` | 1231 | `0x43c26366`–`0x43c37a62` |
| `IMAGING_CAP` | 697 | `0x43c9b335`–`0x43ccab72` |
| `SDF` | 477 | `0x43c7785b`–`0x43c806f9` |
| `CAM_IMAGER` | 371 | `0x43c92f71`–`0x43cfafd9` |
| `IDT` | 298 | `0x43ca2939`–`0x43cfc2cb` |
| `IDT_OPD` | 274 | `0x43cf11f9`–`0x43cf57f1` |
| `CDIAG` | 270 | `0x43c3b0d4`–`0x43c3e86a` |
| `VDF` | 243 | `0x43c813fc`–`0x43c8d525` |
| `CAMERA_SA` | 231 | `0x43cc5286`–`0x43cef0d8` |
| `TRK` | 216 | `0x43cebceb`–`0x43cfe31c` |
| `VEF` | 149 | `0x43c8c26a`–`0x43c8f2e1` |
| `MOUNT_DEBUG` / `MOUNT_ERROR` | 132 / 80 | `0x43c9648d`–`0x43c9a10f` / `0x43c95659`–`0x43c9a1b9` (S66) |
| `SFRS` / `SFRA` | 117 / 100 | `0x43ce7661`–`0x43ceb8c4` / `0x43ce5a16`–`0x43ce7723` |
| `VPH_API` | 106 | `0x43ce32e7`–`0x43ce3dfc` |
| `ACCY` | 106 | `0x43c24cac`–`0x43c26319` |
| `DBGCMD` | 102 | `0x43c2a443`–`0x43c2b315` |
| `STK` | 76 | `0x43cfc7c9`–`0x43cfd8ad` (tracking/saliency) |
| `FACE` | 70 | `0x43c32a3b`–`0x43cfbfc3` |
| `VIDENCSTAT` | 70 | `0x43cd67bb`–`0x43cd7e31` |
| `CLK_CTRL` | 66 | `0x43c3a1df`–`0x43c3b09c` |
| `GOLFSHOT` | 65 | `0x43ca492f`–`0x43cb3ec5` |
| `WSX` | 59 | `0x43ce415f`–`0x43ce490c` |
| `CTRLCORE` | 55 | `0x43c3b82d`–`0x43cdb492` |
| `CAM_DMM` | 54 | `0x43cce6ae`–`0x43ccf1c3` |
| `SAD` | 45 | `0x43ce546b`–`0x43ce59c1` |
| `CAM_FUNC_MGR` | 43 | `0x43ca12af`–`0x43cb02f1` |
| `APL` | 42 | `0x43cebde1`–`0x43cec4fe` |
| `PNL` | 41 | `0x43c76138`–`0x43c7782c` (panel/display; S73) |

## 4. Diferencial A6000 (fw3.21) vs A7S (fw3.20) (VERIFICADO)

- La A6000 tiene **348** prefijos y la A7S **277** (71 menos).
- Prefijos **exclusivos de la A6000** (83 en total): entre los relevantes,
  `CAMERA_MAIN`, `CAMERA_MAIN_CC`, `CAMERA_MAIN_FC`, `CAMERA_MAIN_IM`, `CAMERA_MAIN_LC`,
  `CAMERA_MAIN_SYNC`, `CAMERA_MAIN_TC`, `CAMERA_MAIN_YC`, `CAMERA_IS`, `CAMERA_ADJ`,
  `CAMERA_DETECT_FC`, `CAMERA_DEVICE`, `CAMERA_DSP_APL`, `ACCY`, `ADC_DEBUG`, `AVOUT`, `ADR`,
  `AVR`, `BKID`, `CAMCORE`.
- Prefijos **exclusivos de la A7S** (12): `APL_ADDR`, `APL_ESR`, `APL_PARM`, `APL_REF`, `APL_SIZE`,
  `APL_TAR`, `APL_UPDT`, `CDCTCUBENCTABLE`, `NLAP`, `PIN`, `PINCOUNT`, `TCUB`.

INFERENCIA: la fw3.21 de A6000 reorganiza la traza en submódulos `CAMERA_MAIN_*` muy explícitos
(la A7S los tiene repartidos) y elimina el bloque de diagnóstico de `APL` por submódulos
(`APL_PARM`/`APL_ESR`/…) que sí existe en la fw3.20.

## 5. Abierto (NO_VERIFICADO)

- Qué significan exactamente las siglas `ADF`, `IDT`, `VDF`, `VEF`, `SFRS`/`SFRA`, `WSX`, `GOLFSHOT`,
  `ACCY`, `AUGI`, `SAD`, `APL` (no deducibles solo del prefijo).
- Correspondencia entre prefijo de log y *tarea* real (hilo/módulo) del OSAL.
- Qué módulos de la lista existen también en la fw3.20 con otro nombre (posible renombrado).
- Los 83 prefijos exclusivos de A6000 más allá de los 20 listados.

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s79_modules.py -q
```
