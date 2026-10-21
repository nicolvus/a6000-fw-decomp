# S110 — `Camera::YC`: el motor de imagen de la A6000 (`[CAMERA_MAIN_YC]`, 970 trazas)

> Hito de la **línea de ingeniería inversa general** (no afecta a la decisión del obturador
> electrónico: S51 sigue con A/B/C = NO). Todos los datos son verificables contra los bytes
> del `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención de direcciones
> **vaddr = 0x43541000 + file_offset**.
> Scripts reproducibles en este directorio.

## 1. Qué es `[CAMERA_MAIN_YC]`

Es el **motor de imagen**: el módulo que calcula los parámetros del disparo (sombreado,
ruido, balance, coordenadas) y los entrega al sensor y al acelerador escalar. 970 cadenas
en `0x43ca88f6`–`0x43ccd469`, repartidas en **4 bloques**:

| bloque | rango | n | contenido |
|---|---|---|---|
| `api` | `0x43ca88f6`–`0x43ca8c49` | 17 | la API pública del motor (`api_YC_*`) |
| `imagen` | `0x43cb79ea`–`0x43cbe577` | 430 | OLC, CLP, MARBLE, DCV, PFR, OAC, OPB… |
| `parametros` | `0x43cbf241`–`0x43cc56af` | 361 | SHD, YAP, NR, MODE, jobs |
| `sombra_nf` | `0x43ccb48e`–`0x43ccd469` | 162 | SHD (continuación), KKNR, COMP |

El motor se organiza en **jobs** (unidades de trabajo) y expone una **API** propia; el
nombre del job aparece en la propia traza, de modo que cada cadena de job identifica el
código que la emite.

## 2. La API del motor: 8 funciones `api_YC_*`

| API | función que la referencia | qué hace (según su propia traza) |
|---|---|---|
| `api_YC_InitCap` | `0x437cf5f0` (y `0x437d885c`) | inicializa el motor para una captura (`job_YC_GetTagPointer error`) |
| `api_YC_SetCapBoks` | `0x437d8c88` | fija los parámetros BOKS de la captura (etapa `Stage_BOKS`) |
| `api_YC_SetCapStar` | `0x437cfe94` (y `0x437d8ce4`) | fija los parámetros STAR (etapa `Stage_STAR`) |
| `api_YC_SetCapTbox` | `0x437d88e4` | fija los parámetros TBOX (etapa `Stage_TBOX`) |
| `api_YC_SetSaCamDsp` | `0x437ce0cc`, `0x437d77a8`, `0x437d8940` | abre/cierra el DSP de la cámara en el SA (`Open error`/`Close error`) |
| `api_YC_SetVdPreParam` | `0x437d0768`, `0x437d5608`, `0x437d9a04` | escribe parámetros en el VD previo (previsualización) |
| `api_YC_LfnrSetParam` | `0x437d8bd4` | parámetros de reducción de ruido de línea (LFNR) |
| `api_YC_DEV_SetCoodinate` | `0x437d9d1c` | fija las coordenadas de desarrollo (el nombre está escrito así en el firmware: "Coodinate") |

Cada API está respaldada por un fichero fuente propio en el firmware (ver §5).

## 3. Los 12 jobs del motor

`job_YC_*` (nombre exacto del firmware). La función que referencia el nombre es la que
Ejecuta el job:

| job | funciones que lo nombran | lectura |
|---|---|---|
| `job_YC_Initialize` | `0x438aa574`, `0x438aa65c` | arranque del motor |
| `job_YC_ModeManager` | `0x4389f29e` | conmutación de modo |
| `job_YC_SetParam` | 15 sitios (`0x4388c910`…) | **el job central**: calcula/escribe los parámetros |
| `job_YC_SetParamOn` | `0x438b7c48`, `0x438ebe28` | parámetros al activar (previsualización) |
| `job_YC_SetParamOff` | `0x438aa574`, `0x438b7ba4` | parámetros al desactivar |
| `job_YC_SetParamPrelight` | `0x4389b80c` | parámetros en *prelight* (antes del disparo) |
| `job_YC_SetPreParam` | `0x4388bb54`, `0x4388c698`, `0x4388c910` | parámetros previos |
| `job_YC_SetSaCamDspParam` | `0x4388b2c4`, `0x4388c180`, `0x4388c420`… | parámetros del DSP en el SA |
| `job_YC_CalcParam` | 14 sitios (`0x4388a514`…) | cálculo de parámetros |
| `job_YC_SetCapBoks` | `0x4387f4b0` | parámetros BOKS de la captura |
| `job_YC_SetCapStar` | `0x438aec84` | parámetros STAR de la captura |
| `job_YC_GetTagPointer` | 19 sitios (`0x437ce0cc`…) | acceso al *tag pointer* (MakerNote) |

**Método (validado contra S78):** la atribución cadena→función se hace con el esquema PIC
(`destino = literal_del_pool + (add rX,pc + 4)`) y el inicio de función se detecta por los
prólogos Thumb `push {..,lr}` (0xb5xx con bit de LR) y `push.w {..,lr}` (0xE92D + 2ª mitad
con bit 14). Con ese método, la cadena `YAP: job_apc_main_stl …` (`0x43cc4ff9`) queda
asignada a `0x438b3ea8` y `YAP: job_apc_main_mov …` (`0x43cc50fb`) a `0x438b5810` — exactamente
las direcciones que S78 había obtenido con Ghidra. Es una comprobación cruzada entre dos
hitos y dos motores distintos.

Además del motor de YC, S78 ya localizó los jobs de parámetros `apc_*` (`job_apc_main_stl`
`0x438b3ea8`, `job_apc_main_mov` `0x438b5810`, `job_apc_gain_stl`, etc.) y los 50 parámetros
`apc_*` en 7 módulos: nada de eso se repite aquí.

## 4. Sub-módulos: la etiqueta que sigue al prefijo

Cada traza de YC lleva una etiqueta de sub-módulo tras `[CAMERA_MAIN_YC]: `. Los principales
(con su número de trazas y de funciones que las referencian):

| sub-módulo | n | funciones | rango | contenido |
|---|---|---|---|---|
| `SHD` | 219 | 38 | `0x43cc0204`–`0x43ccd393` | **sombreado** (S96: tabla `tbb` de 69 drive_mode → 14 ShdMode) |
| `ITP` | 90 | 32 | `0x43cbb12f`–`0x43cbd243` | bloque de 90 trazas entre YAP y DCV |
| `YAP` | 79 | 34 | `0x43cbb726`–`0x43cc50fb` | **YAP**: los parámetros `apc_*` (S78) |
| `DCV` | 42 | 10 | `0x43cb9aea`–`0x43cba901` | bloque DCV |
| `OLC` | 37 | 12 | `0x43cb822b`–`0x43cb92ae` | bloque OLC |
| `NR` | 36 | 19 | `0x43cbb09c`–`0x43ccc255` | reducción de ruido |
| `CLP` | 29 | 27 | `0x43cb81be`–`0x43cbae6e` | `yc_clp_common.cpp` |
| `MARBLE` | 24 | 9 | `0x43cb7cdb`–`0x43cbe440` | motor de desarrollo (S105: coeficientes `ccnr` por estilo) |
| `KKNR` | 22 | 6 | `0x43ccc2ca`–`0x43ccc6f1` | reducción de ruido de kernel (`Stage_KKNR`) |
| `PFR` | 19 | 26 | `0x43cbbbc5`–`0x43cbc18c` | *partial fixed range* (S107: memoria PFR de CamCore) |
| `OPB` / `OAC` | 10 / 10 | 7 / 4 | — | bloques menores |
| `ZDL` | 8 | 5 | `0x43cc5340`–`0x43cc5518` | — |
| `SPICA` | 5 | 6 | `0x43cc3555`–`0x43cc3a45` | enlace con el SPICA (S84) |
| `COMP` / `NOT` | 6 / 6 | 2 / 4 | `0x43ccb5e6`–`0x43ccb6fe` | — |

En total **141 etiquetas distintas** (el recuento fino está en `yc_summary.json`); las
siglas (SHD, ITP, DCV, OLC, CLP, PFR, ZDL…) **no están expandidas en el firmware**: cualquier
desarrollo concreto es hipótesis NO VERIFICADA.

## 5. Los ficheros fuente del área (119 nombres embebidos)

`source_files.json` lista los 119 nombres `*.cpp/*.h` embebidos entre `0x43ca8e14` y
`0x43ccab00`. Los propios del motor de imagen son:

- **Secuencias**: `Sequence_Common.cpp` `0x43cb14a1`, `Sequence_Movie.cpp` `0x43cb31f1`,
  `Sequence_MovieSplit.cpp` `0x43cb334d`, `Sequence_SuperSlowMotion.cpp` `0x43cb34ac`,
  `Sequence_HSRecGolfshot.cpp` `0x43cb2245`, `zpd_capture_sequence.cpp` `0x43cb614d`.
- **Inicialización**: `init_cam_SetCamParam.cpp` `0x43cb40b8`,
  `init_cam_SetCamParam_Util.cpp` `0x43cb4229`, `SyncLoader.cpp` `0x43cb397a`.
- **Color y desarrollo**: `yc_clp_common.cpp` `0x43cb81ac`, `still_dda_rc.cpp` `0x43cab9a6`,
  `still_cmp_effect.cpp` `0x43caafcb`, `ddl_srotate.cpp` `0x43cc6859`, `ddl_stitch.cpp`
  `0x43cc6964`, `still_cnt_panoramaStitch.cpp` `0x43cc69fa`.
- **MakerNote**: `CS_ExifMakerNote.cpp` `0x43cc56dc`, `CS_ExifMakerNote_dslr.cpp` `0x43cc56f1`.
- **Parámetros de imagen**: `ImageParamCapture_SyncBranch.cpp` `0x43cc6779`,
  `ImageParam_SpecialSeq.cpp` `0x43cc67c9`, `EnumConverter.h` `0x43cb0bbf` y `0x43cc6769`.
- **Etapas** (S76): `Stage_Apollo.cpp`, `Stage_BDRO.cpp`, `Stage_BOKS.cpp`, `Stage_Decomp.cpp`,
  `Stage_Develop.cpp`, `Stage_KKNR.cpp`, `Stage_MARBLE.cpp`, `Stage_OPD.cpp`,
  `Stage_Orientation.cpp`, `Stage_Adjust.cpp`, `Stage_SoftFocus.cpp`, `Stage_StillDate.cpp`,
  `Stage_TBOX.cpp`, `Stage_AutoFraming.cpp`, `Stage_CaComm.cpp`, `Stage_CameraHAPI.cpp`,
  `Stage_FaceDetect.cpp`.

El resto (`CaptureManager*.cpp`, `SectionController.cpp`, `RawMemManager*.cpp`, los 16
`Capture*_Selector.cpp`…) pertenecen al gestor de captura (S106) y comparten zona de cadenas.

## 6. Mapa función → trazas

`func_map.json` asigna cada cadena a la función que la referencia: **304 funciones** con
**1 756 pares** (función, cadena) y **958 de las 968 cadenas** cubiertas (las 970 del informe
son *ocurrencias* del prefijo, no cadenas distintas). *El recuento de sitios depende de la
regla: ver [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md).* Ejemplos:

| función | n trazas | primera traza |
|---|---|---|
| `0x437cf5f0` | 1 | `[CAMERA_MAIN_YC]: api_YC_InitCap: job_YC_GetTagPointer error: 0x%x` |
| `0x437d8c88` | 2 | `[CAMERA_MAIN_YC]: api_YC_SetCapBoks: 0x%x` |
| `0x438aa574` | 6 | `[CAMERA_MAIN_YC]: SHD::job_YC_SetParam (CAP): msq_sel_b  = 0x%x` |
| `0x438b3ea8` | 5 | `[CAMERA_MAIN_YC]: YAP: job_apc_main_stl main_digitalZoomRatioDenom=%x` (S78) |
| `0x438b5810` | 1 | `[CAMERA_MAIN_YC]: YAP: job_apc_main_mov digitalZoomRatioDenom=%x` (S78) |

La traza `SHD::job_YC_SetParam (CAP): msq_sel_b  = 0x%x` muestra que el job de parámetros
del sombreado se nombra a sí mismo **`SHD::job_YC_SetParam (CAP)`**: es el mismo job
`job_YC_SetParam` aplicado al bloque de sombreado en modo captura (`CAP`).

### 6.1 Diez cadenas sin referencia

Estas 10 trazas **no** tienen ninguna referencia en la imagen: ni por el esquema PIC ni como
puntero absoluto de 4 B (búsqueda exhaustiva sobre los 11,4 MB):

| vaddr | texto |
|---|---|
| `0x43ca88f6` | `[CAMERA_MAIN_YC]: ---api_YC_CaptureRawReadExecuteClp---` |
| `0x43ca8af8` | `[CAMERA_MAIN_YC]: api_YC_SetCapLaxo: 0x%x` |
| `0x43cbb0e4` | `[CAMERA_MAIN_YC]: NR:` |
| `0x43cbe537` | `[CAMERA_MAIN_YC]: End:osal_capstop Ret=%d` |
| `0x43cc3d9c` | `[CAMERA_MAIN_YC]: STAR::job_YC_SetCapStar: Open star error` |
| `0x43cc435b` | `[CAMERA_MAIN_YC]: YAP::job_YC_SetParamOff: GetDevYap error: 0x%p` |
| `0x43cc5340` | `[CAMERA_MAIN_YC]: ZDL::job_YC_Initialize: GetHeadZdl error` |
| `0x43ccd278` | `[CAMERA_MAIN_YC]: ShiftQsrfShd (Split): color invalid: %x` |
| `0x43ccd2ec` | `[CAMERA_MAIN_YC]: CalcSensShdCoef (CamHead): %x %x` |
| `0x43ccd439` | `[CAMERA_MAIN_YC]: CalcLim28OnOff: ApiIdx = 0x%x` |

Son cadenas **muertas** que el enlazador conservó (algunas son mensajes de error completos,
como `ZDL::job_YC_Initialize: GetHeadZdl error`): el código que las usaba ya no está en esta
fw3.21, pero los *format strings* quedaron en el blob. Con la regla de *kill analysis* la
lista baja a **2** (`0x43ca88f6` y `0x43ca8af8`); las 8 restantes sí tienen referencia
confirmada, pero por el criterio *ancho* (que también produce falsos positivos) — quedan como
"referencia probable" hasta verificarlas a mano.

> **Corrección de método (rectificada tras S118):** la primera versión del escáner PIC
> emparejaba cada `add rX,pc` con el `ldr` más cercano del registro; la segunda probaba
> **todos** los `ldr` del registro en 4 KB. La segunda regla **inventa** referencias (en
> `[SFRA]` dio 186 puntos donde la verificación manual encuentra 118). La regla correcta es la
> **kill analysis** (`analysis/s106_imaging_cap/scan_pic_refs_v2.py`): descartar el par si
> alguien vuelve a escribir el registro entre `ldr` y `add`. Con ella, las 968 cadenas de YC
> dan **958** referencias (las 970 del informe son *ocurrencias* del prefijo, no cadenas
> distintas) y el mapa función→traza baja de 332 a **304** funciones. La metodología
> completa, con la calibración de S118, está en
> [`analysis/s106_imaging_cap/pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md).
> La atribución cadena→función se valida contra S78 (Ghidra): `job_apc_main_stl` →
> `0x438b3ea8` y `job_apc_main_mov` → `0x438b5810`, sin cambios.

## 7. Diferencial con la A7S fw3.20

- La A7S fw3.20 tiene **0** cadenas con el prefijo `[CAMERA_MAIN_YC]`: los mismos mensajes
  existen **sin etiqueta** (`YAP: job_YC_RawDevMakerNote_Yap_apc_init` en `0x43cb9e32`,
  `MARBLE: MOV <MBL_MOV_Image_Mod> ul_rc_zo` en `0x43cb717b`).
- Comparando el texto **sin el prefijo** cadena a cadena: **969 de las 970** cadenas de la
  A6000 existen también en la A7S. La **única** traza nueva de la fw3.21 es
  `[CAMERA_MAIN_YC]: HD_SWEEP_HOLD  =%x` (`0x43cbc27c`).
  → el motor de imagen es **funcionalmente el mismo** en A6000 fw3.21 y A7S fw3.20; la
  diferencia es la instrumentación (la etiqueta de módulo) y esa única traza de *sweep hold*.

## 8. Verificaciones hechas (trazabilidad)

| afirmación | cómo se comprueba |
|---|---|
| 970 cadenas, 4 bloques | `extract_yc.py` cuenta las ocurrencias del prefijo y segmenta por huecos |
| 958/968 referenciadas (kill analysis) | `func_map.json` + búsqueda de punteros absolutos |
| 304 funciones con la regla de kill analysis | `map_functions.py` (PIC + prólogos Thumb) |
| 8 `api_YC_*`, 12 `job_YC_*` | `build_summary.py` sobre el mapa función→cadenas |
| 141 sub-módulos | etiqueta tras el prefijo, contada sobre las 970 cadenas |
| 119 ficheros fuente | `extract_yc.py` busca `*.cpp`/`*.h` en el rango del módulo |
| 969/970 comunes con la A7S | comparación texto a texto contra el blob de la A7S (`a7s_diff.json`) |
| `job_apc_main_stl` → `0x438b3ea8` | comprobación cruzada con S78 (Ghidra) |

## 9. NO VERIFICADO / abierto

- El **significado de las siglas** SHD, ITP, DCV, OLC, CLP, PFR, ZDL, OAC, OPB, ARC: el
  firmware solo usa las siglas.
- La **tabla de despacho de jobs**: no se ha localizado una tabla de punteros a los 12 jobs
  (ni absolutos ni con el esquema PIC); los jobs parece invocarse directamente.
- La **relación exacta** entre `api_YC_SetCapBoks/SetCapStar/SetCapTbox` y las etapas
  `Stage_BOKS`/`Stage_STAR`/`Stage_TBOX` (S76): la correlación de nombres es evidente, pero
  el enlace por código no está verificado.
- El significado de la traza nueva `HD_SWEEP_HOLD` (`0x43cbc27c`) y su relación con el
  barrido de panorámica (S105).
- Nada de esto **afecta a S51**: el motor de imagen no registra nada del obturador.

## 10. Relación con los demás hitos

- **S78**: los 50 parámetros `apc_*` y los jobs `job_apc_*` viven en el sub-módulo `YAP`.
- **S96**: la tabla de sombreado (`SHD::GetShdMode`, 69 → 14 modos) está en el sub-módulo `SHD`.
- **S105**: `MARBLE` calcula los coeficientes `ccnr` por estilo de captura; `ddl_stitch.cpp` y
  `still_cnt_panoramaStitch.cpp` viven en esta misma zona.
- **S107**: `PFR` es la memoria que `CamCore` reserva y libera.
- **S84**: `SPICA` es el enlace con el acelerador de procesado.
- **S106**: el gestor de captura (`IMAGING_CAP`) es quien llama a esta API.

## 11. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 970 cadenas con vaddr/offset/texto |
| `blocks.json` | los 4 bloques con sus tokens |
| `func_map.json` | mapa función → cadenas (317 funciones) |
| `yc_summary.json` | sub-módulos, API, jobs y diferencial |
| `source_files.json` | los 119 ficheros fuente embebidos del área |
| `a7s_diff.json` | diferencial A6000 vs A7S fw3.20 |
| `extract_yc.py`, `map_functions.py`, `build_summary.py` | scripts de extracción (reproducibles) |
