# G49 — Pixel Shift / High Res Shot / Handheld High Res (DESCARTADO)

Fecha 15-11-2026. Solo estático (SM level 3 + cadenas de `av-cam.bin` y `libObj.so` fw 3.21); sin cámara, sin parche, sin CFW.

## 1. ¿Hay IBIS? No
- `docs/references/sony-ilce-6000-level3-sm.txt`: 0 coincidencias de `STEADY`, `GYRO`, `HALL`, `IMAGE SENSOR`, `SS UNIT`. Único sensor del imager: «CMOS IMAGER» (líneas 1054, 1599, 1725, sin bloque de actuador). Los sensores de la lista de piezas son SE3800 «SENSOR MAGNETIC» (l. 278), SE7750 «SLANT SENSOR» (l. 385; el de orientación, ya medido en la «Nivel digital») y temperaturas del imager (`IMAGER_TEMP1`, l. 502). La única mención «OSS» son objetivos (SELP1650, SEL55210, l. 50-52).
- `av-cam.bin`: 0 cadenas `BodySteady|SSIS|IBIS`. Rutas `[CAMERA_IS]` (0x757da6–0x759426): `IS_LensMount*CB` (callbacks de montura del objetivo), `[STABILIZER][AS]` (0x7591f3), `[EIS]` `rcct_SetStblzPower/GridH` y `GyroAD[p/y]` (0x7592b2–0x759324) = estabilización electrónica de vídeo con giroscopio, que recorta/desplaza en proceso, no mueve el sensor; `IS_LensMountPanoramaGyro` (0x7593a7).
- `libObj.so`: `LensOSSSet/Act` (0xce79ef), `pvt_ActionSetLensOSSMode` (0xcf16da), `pvt_ActionSetFrameLockSteadyShot` (0xcecfb1). `A_AS_GYRO_ADJ/A_AS_HALL_ADJ` (0xbe19d0/0xbe1a18) están en la tabla de comandos de ajuste junto a `S_IRIS_*`/`S_LENS_BARRIER` (0xbe0d70…): ajustes de fábrica por el protocolo del objetivo (lado objetivo). No hay ninguna cadena de actuador de cuerpo.

Conclusión: estabilizador solo en el objetivo (OSS); no hay actuador de sensor. El pixel shift por desplazamiento de sensor es imposible por hardware.

## 2. Vía computacional (varias tomas alineadas y fusionadas)
- MFNR en firmware: `PARAMID_MULTI_FRAME_NR` (libObj 0xd4ad94), `_LEVEL` (0xd4af2a), `pvt_subActionObjectMultiNrProcEvt` (0xd4b31a), `pvt_UpdateProcessMultiNrInfo` (0xd52d90), `MFNR_Lv` (0xcf6958), `mkNoteMultiFrameNR` (0xcc2141). `libObj` solo gestiona parámetros y mensajes; `av-cam` no contiene cadena MFNR (G41 §5). El proceso real es del DSP.
- (a) Alineación: el DSP tiene motion estimation jerárquica: `HME_BaseTar_Addr`/`HME_BaseRef_Addr` (0x7ab1c6/0x7ab23c), `FMT_SRC_REF0_ADDR` (0x74f2de) y el marco de captura `[ContID][FrameID]` (0x7644c8). Registro: sí, pero su precisión sub-píxel y el número de fotogramas NO están verificados (no se decompiló el motor: no hay código ARM, es hardware de DSP). Salida de MFNR: ISO ≤ 25600, JPEG del mismo tamaño que un disparo normal.
- (b) Mayor resolución: el motor fusiona a resolución de sensor. Entrada de captura 6000×4000 (readout completo ≈66,8 ms, ≈15 fps, `docs/capture/imx210-video-readout.md`). Una salida 12000×8000 exigiría tablas de tamaño (`jpegImageSizeX/Y`), búferes del DSP/`dmm` y ruta de codificación JPEG (SDF `ApiEncodeJpeg`) nuevas. Ninguna es un dato del `.dat` que se pueda cambiar: son tamaños fijos del HW de DSP y configuración de descriptores binarios.
- (c) Memoria: DRAM del tipo LPDDR2 (SM l. 809, 2062); capacidad NO verificada en el repo. Cálculo: un fotograma 24 MP YC422 = 6000×4000×2 = 48 MB (RAW 14 b en contenedor de 16 b: 48 MB). Salida a 48 MP YC422 = 192 MB. 4 fotogramas + salida = 4×48+192 = 384 MB, y 6 fotogramas = 480 MB, solo de datos de imagen, sin contar Linux, `av-cam`, vistas ni el pipeline normal.
- Además, con el OLPF y mosaico Bayer sin desplazamiento controlado, la mejora real a mano alzada es modesta (desplazamientos aleatorios), y el readout completo 24 MP son ≈66,8 ms por toma (≈15 fps), con ventana de captura más larga que un disparo único.

## 3. Veredicto
- Sensor shift: DESCARTADO (sin IBIS).
- Computacional en cámara: DESCARTADO. Necesitaría DSP con salida >6000×4000, búferes ≈384–480 MB de imagen y codificador nuevos, no replicables cambiando ficheros del `.dat` sin firmware ejecutándose; el motor MFNR no es parcheable a mayor resolución. NO VERIFICADO: tamaño de DRAM, nº de fotogramas de MFNR, precisión del registro.
