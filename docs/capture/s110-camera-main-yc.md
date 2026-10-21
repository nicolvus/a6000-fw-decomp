# S110 — `Camera::YC`: el motor de imagen de la A6000 (`[CAMERA_MAIN_YC]`)

**Hito de la línea de ingeniería inversa general** (no afecta a la decisión del obturador
electrónico: S51 sigue con A/B/C = NO).

Informe: [analysis/s110_camera_main_yc/yc_engine.md](../../analysis/s110_camera_main_yc/yc_engine.md) ·
Datos: `yc_summary.json`, `func_map.json`, `a7s_diff.json` · Test: `tests/test_s110_camera_main_yc.py`.

## Hallazgo central

`[CAMERA_MAIN_YC]` es el **motor de imagen**: 970 trazas en `0x43ca88f6`–`0x43ccd469`
(4 bloques) que exponen una **API de 8 funciones** y un **despacho de 12 jobs**, y que se
organizan internamente en **141 sub-módulos etiquetados** (los grandes: `SHD` 219, `ITP` 90,
`YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19).

## Qué se ha reconstruido (verificado contra bytes)

1. **API del motor** (8): `api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`,
   `api_YC_SetCapStar` `0x437cfe94`, `api_YC_SetCapTbox` `0x437d88e4`,
   `api_YC_SetSaCamDsp` `0x437ce0cc`/`0x437d77a8`/`0x437d8940`,
   `api_YC_SetVdPreParam` `0x437d0768`/`0x437d5608`/`0x437d9a04`,
   `api_YC_LfnrSetParam` `0x437d8bd4`, `api_YC_DEV_SetCoodinate` `0x437d9d1c`.
2. **12 jobs**: `job_YC_Initialize` `0x438aa574`, `job_YC_ModeManager` `0x4389f29e`,
   `job_YC_SetParam` (15 sitios), `job_YC_SetParamOn` `0x438b7c48`, `job_YC_SetParamOff`
   `0x438b7ba4`, `job_YC_SetParamPrelight` `0x4389b80c`, `job_YC_SetPreParam`
   `0x4388bb54`, `job_YC_SetSaCamDspParam` `0x4388b2c4`, `job_YC_CalcParam` (14 sitios),
   `job_YC_SetCapBoks` `0x4387f4b0`, `job_YC_SetCapStar` `0x438aec84`,
   `job_YC_GetTagPointer` (19 sitios).
3. **Mapa función → trazas**: las 970 cadenas quedan asignadas a **317 funciones** (0 sin
   atribuir) usando el esquema PIC (`destino = literal + (add rX,pc + 4)`) y los prólogos
   Thumb. **Comprobación cruzada con S78**: la cadena `YAP: job_apc_main_stl …` queda en
   `0x438b3ea8` y `job_apc_main_mov` en `0x438b5810`, exactamente las direcciones que S78
   había obtenido con Ghidra.
4. **119 nombres de fichero fuente embebidos** en la zona del módulo: las secuencias
   (`Sequence_Common.cpp` `0x43cb14a1`, `Sequence_Movie.cpp` `0x43cb31f1`,
   `Sequence_MovieSplit.cpp`, `Sequence_SuperSlowMotion.cpp`, `zpd_capture_sequence.cpp`),
   la inicialización (`init_cam_SetCamParam.cpp` `0x43cb40b8`, `SyncLoader.cpp`), el color
   (`yc_clp_common.cpp` `0x43cb81ac`), el MakerNote (`CS_ExifMakerNote*.cpp`) y las etapas
   `Stage_*` (S76).
5. **Diferencial A7S fw3.20**: 0 cadenas con el prefijo (los mismos mensajes existen sin
   etiqueta) y, comparando el texto sin prefijo, **969 de las 970** cadenas de la A6000
   existen también en la A7S. La única traza nueva de la fw3.21 es
   `[CAMERA_MAIN_YC]: HD_SWEEP_HOLD  =%x` (`0x43cbc27c`).

## Abierto / NO VERIFICADO

- El significado de las siglas (SHD, ITP, DCV, OLC, CLP, PFR, ZDL, OAC, OPB, ARC): el
  firmware no las expande.
- No se ha localizado una **tabla de despacho de jobs** (ni absoluta ni PIC).
- El enlace por código entre `api_YC_SetCapBoks/SetCapStar/SetCapTbox` y las etapas
  `Stage_BOKS/STAR/TBOX` (S76) es solo nominal.
- El sentido de `HD_SWEEP_HOLD` (`0x43cbc27c`), en relación con el barrido (S105).
- Nada de esto cambia S51: el motor de imagen no registra nada del obturador.

## Scripts

`analysis/s110_camera_main_yc/extract_yc.py` (cadenas, bloques, ficheros),
`map_functions.py` (atribución a función con el esquema PIC + prólogos Thumb),
`build_summary.py` (sub-módulos, API, jobs, diferencial).
