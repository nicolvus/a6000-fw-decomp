# S70 (reconocimiento) — EIS/gyro: estabilización y calibración por lente

**Alcance:** línea de ingeniería inversa **general** de la cámara: subsistema de estabilización
(`CAMERA_IS`), giroscopio y ficheros de calibración IS por lente. **No** es la línea SilentShutter
ni la de la montura (S66). Solo lectura de bytes; nada ejecutado.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

## 1. Mapa del subsistema (VERIFICADO por cadena → función)

| Función | Cadena / log | Dirección de la cadena |
|---|---|---|
| `0x436ea2d0` | `[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB (%x)` | `0x43c98da6` |
| `0x436ea470` | `[CAMERA_IS][DIST]: ERR:MakeDistCorPrm prm=null` | `0x43c98e1d` |
| `0x436ea50c` | `[CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=null` (+`inv1`/`inv2`) | `0x43c98e4d` |
| `0x436ea65c` | `[CAMERA_IS][DIST]: ERR:MakeDistRawAppliTag prm=null` | `0x43c98ef9` |
| `0x436fecbe` | `[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x` | `0x43c9a1f3` |
| `0x436fee80`, `0x4371e4cc` | `[CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x` | `0x43c9a234` |
| `0x436ffab4` | `[CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x` | `0x43c9a26b` |
| `0x43702dac`, `0x43704d90` | `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!` | `0x43c9a2b2` |
| `0x43702dac` | `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!` | `0x43c9a2eb` |
| `0x437046a4` | `[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d` | `0x43c9a324` |
| `0x43705d64` | `[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)` | `0x43c9a3a7` |
| `0x43705dd0` | `[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyro (%x)` | `0x43c9a426` |
| `0x43707152` | **`/mnt/FILE_IS_%04x.dat`** (fichero de calibración IS por lente) | `0x43c9a535` |
| `0x437d0768` | `[CAMERA_MAIN_TC]: GyroStitScl %d %d` (gyro → escala de imagen fija) | `0x43ca7fd4` |
| `0x437d1b30` | `[CAMERA_MAIN_TC]: TC:APL:Err: LmtGyroVect Denom=0 …` | `0x43ca7ffb` |
| `0x43874c50` | `[CAMERA_MAIN_TC]: JudgeBrkGyro %d` | `0x43cb6eea` |
| `0x4354d740` | `EIS_RC1V_SetPower` (rail de alimentación del EIS) | `0x43cb2b9e` |

## 2. Lectura provisional (INFERENCIA)

1. Hay **tres capas** con prefijo propio: `[CAMERA_IS][AS]` (estabilizador "activo" con cola de
   mensajes OSAL y un factor de arranque `upm_get_hcrn_ura`), `[CAMERA_IS][EIS]` (estabilización
   electrónica: alimentación `rcct_SetStblzPower`, rejilla `rcct_SetStblzGridH` y lecturas del
   giroscopio `GyroAD[p],GyroAD[y]`) y `[CAMERA_IS][DIST]` (corrección de distorsión).
2. `IS_LensMountExpStartCB` y `IS_LensMountPanoramaGyro` conectan el EIS con la **montura**: el EIS
   se coordina con el disparo (exp start) y con el barrido panorámico.
3. `/mnt/FILE_IS_%04x.dat` = **datos de calibración del EIS por lente** (el `0x04x` es el ID de
   lente), en la misma convención que `/lens/VX91xx_lensfile.bin` (S66) y `/mnt/Mount_ms_log_%03d.dat`.
4. `GyroStitScl` y `JudgeBrkGyro` operan en la cadena de **time control (TC)**: escalado por el
   movimiento medido y detección de "break" del giroscopio.

## 3. Abierto (NO_VERIFICADO)

- Formato del fichero `/mnt/FILE_IS_%04x.dat` y quién lo escribe (¿la propia cámara al fabricar?).
- Relación entre `GyroAD` (ADC) y las unidades de `GyroStitScl`.
- Qué es exactamente el "AS" (`STABILIZER][AS]`) frente a "EIS".
- Si el EIS de la A6000 compensa con el OSS del objetivo (SteadyShot) y cómo se coordina con
  `LensShdOn`/`PzShdOn` (S66, §sombreado).
- Rail `EIS_RC1V`: qué alimentación exacta es.

## 4. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s70_is.py -q
```
