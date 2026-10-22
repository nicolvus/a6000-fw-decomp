# S127 — `[CAMERA_MAIN_LC]`: el motor de AF de `Camera::LC` (72 trazas)

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)). Sin efecto en S51.

Datos: [`camera_main_lc.json`](camera_main_lc.json) · Test: [`tests/test_s127_camera_main_lc.py`](../../tests/test_s127_camera_main_lc.py)
· Nota de captura: [`docs/capture/s127-camera-main-lc.md`](../../docs/capture/s127-camera-main-lc.md)

## 1. Resumen

- **72 cadenas** con el prefijo `[CAMERA_MAIN_LC]:`, de `0x43c9c6f6` a `0x43ca7e0b`.
- **78 sitios** de referencia PIC (regla estricta) y **37 funciones** emisoras.
- **1 cadena sin referencia**: `0x43c9c779` `[ERROR!!] lc_Movie_DM_AF_Util_getBufferAddr()`.
- El nombre del módulo es **`Camera::LC`** (namespace C++), probado por los nombres RTTI del
  blob: `MarioAfcState` `0x43c9d11a`–`0x43c9d228`, `CPafState` `0x43ca7b17`–`0x43ca7c03`,
  `CCoordControl`/`CPAFCoordControl` `0x43cb60c9`/`0x43cb60e5`. **`LC` no está expandido** en el
  firmware: `[CAMERA_MAIN_LC]` es solo la etiqueta de traza.
- La etiqueta **no cubre todo el módulo**: entre los dos bloques de cadenas hay trazas
  `[CAMERA_MAIN]` del mismo `Camera::LC` (`calibration_fc_pos` `0x43c9c57b`,
  `FOCUS MODE is not AF-A` `0x43c9cd19`, `fc_pos`), estudiadas en S126.
- Reparto medido de las 72 cadenas: **32** en `0x43c9c6f6`–`0x43c9d646` y **40** en
  `0x43ca71fa`–`0x43ca7e0b` (frontera entre `0x43c9d646` y `0x43ca71fa`; el 28/44 anterior era
  erróneo). Los sitios de las primeras 32 se reparten entre las dos regiones de código porque
  tres mensajes los emiten también funciones del bloque *still*: 37 sitios / 22 funciones
  (19 del bloque 1 + 3 del *still*); las 40 restantes tienen 41 sitios / 18 funciones.

## 2. Qué calibra (respuesta medida)

**Ninguna de las 72 trazas es una traza de calibración óptica de lente.** Lo que este bloque
emite es el **estado y los errores del motor de AF**: adquisición de memoria de trabajo del
*DM AF* (`miniRAW`, `resizedY`, `saIf`, `ESRAM/DDR_Bank`, MMU), volcados de *scan/predict*
(`pre position: %d yosoku ; %d yosoku`, `0x43c9ced2`), el resultado ZPD
(`LC_GetZpdResultInfo`, `0x437c1e48`) y los hooks `zpd_HybridMovieAF`
(`0x43ca7d50`/`0x43ca7d7a`). Los únicos parámetros ópticos que aparecen son de lectura:
`F number %d` `0x43c9cf8d`, `fno is %d fno` `0x43c9d05d`, `iris_cur=%d` `0x43ca784c`.

La palabra "calibración" está en el bloque vecino de S126: `calibration_fc_pos` `0x43c9c57b` y
`Calibration start` `0x43c9c6d5`. Esas funciones **llaman a helpers de este bloque**:

| desde (S126) | llamada medida | qué helper de LC |
|---|---|---|
| `0x43738ec0` `calibration_fc_pos…` | `bl 0x4373c7f8` | `lc_Movie_DM_AF_Util_getSaIfAddr` |
| `0x43738ec0` | `bl 0x4373c11c`, `bl 0x43738e14`, `bl 0x43902718` | fuera de las 72 trazas |
| `0x43739488` `Calibration start` | `bl 0x4373c478`, `0x4373c4e4`, `0x4373c558`, `0x4373c8e8` | block 1 |

→ La calibración `fc_pos` **usa** la infraestructura de buffers/MMU del DM AF que este bloque
publica; no hay evidencia de que `[CAMERA_MAIN_LC]` calibre la lente. Se corrige, por tanto, la
premisa del encargo ("la calibración de lente"): el contenido medido es **AF + ZPD + DM AF**.

## 3. Mapa de las 72 trazas por sub-bloque

`n` = cadenas cuyo **primer** sitio cae en el sub-bloque (suma 72; la cadena muerta
`0x43c9c779` se cuenta en el bloque *movie*, su vecino). "Sitios" es el rango de direcciones
`add rX, pc` del sub-bloque.

| sub-bloque | n | rango de cadenas | sitios | funciones | qué se lee |
|---|---:|---|---|---:|---|
| DM AF **movie**: buffers y memoria | 14 | `0x43c9c6f6`–`0x43c9ca37` | `0x4373c7ae`–`0x4373cb4c` | 9 | `[ERROR!!] lc_Movie_DM_AF_Util_getMiniRawAddr()` `0x43c9c6f6`, `ESRAM Acquisition failed` `0x43c9c837`, `[LC] Movie DM AF cannot get miniRAW Stored memhandle` `0x43c9c8ba`, `DDR_Bank Acquisition failed` `0x43c9c9d9` |
| `lc_AF_Scan` | 2 | `0x43c9cb6f`–`0x43c9cb8b` | `0x4373f630`–`0x4373f7e0` | 1 | `LOWCON!!!` `0x43c9cb6f`, `ERROR!!!!! : %d in lc_AF_Scan.cpp` `0x43c9cb8b` |
| volcado **scan/predict** | 7 | `0x43c9ced2`–`0x43c9d03e` | `0x43545f52`–`0x4354612a` | 1 | `pre position: %d yosoku ; %d yosoku ; [%d - %d] repdf : %10.3f use : %derr_est : %10.3f` `0x43c9ced2`, ` DIR [%d] scanless[%d %d] kinbou[%d] partial[%d] direction[%d]` `0x43c9cf3c`, `F number %d` `0x43c9cf8d`, `[df%d] [%10.3f] [%10.3f] [%10.3f]` `0x43c9d00a`, `************` `0x43c9d03e` |
| `lc_HybridAF` | 2 | `0x43c9d05d`–`0x43c9d0d5` | `0x43754e20`–`0x4375536e` | 1 | `fno is %d fno ` `0x43c9d05d`, `scanless manymode is undefined. lc_HybridAF.cpp %d` `0x43c9d0d5` |
| `LC_SendMessage` | 2 | `0x43c9d3df`–`0x43c9d419` | `0x437663e8`–`0x43766408` | 1 | `LC_SendMessage: osal_valloc_msg error!` `0x43c9d3df`, `LC_SendMessage: osal_snd_msg error!` `0x43c9d419` |
| `MS_Writer` | 1 | `0x43c9d45c` | `0x4376bfb6` | 1 | `MS_Writer: disable addr! memmapID: %d` `0x43c9d45c` |
| límites de **housing** | 2 | `0x43c9d498`–`0x43c9d4d4` | `0x4376cd04`–`0x4376cd84` | 2 | `water housing limit size over err %d > %d` `0x43c9d498`, `NG : housing limit is over far limit........` `0x43c9d4d4` |
| errores **OSAL** | 2 | `0x43c9d60c`–`0x43c9d646` | `0x4377710e`–`0x4377803c` | 3 | `osal_ercord error` `0x43c9d60c` (dos funciones), `ERROR !!! MSS_reload osal_err:0x%04x %s : %d` `0x43c9d646` |
| **rlog** del DM AF | 10 | `0x43ca71fa`–`0x43ca743d` | `0x437bbc24`–`0x437bc264` | 6 | `[ERROR!!] local_getLogDataSeqAddr. us_idx: %d, enableLogFieldNum: %d` `0x43ca71fa`, `  LUMI_COEF_CALC! …` `0x43ca72bb`, `watkao1` `0x43ca7372`, `LOG_FIELD_UPDATED! idx: %d` `0x43ca743d` |
| DM AF **still**: buffers y memoria | 10 | `0x43ca7493`–`0x43ca76b0` | `0x437bc4dc`–`0x437bc85e` | 7 | `[ERROR!!] lc_DM_AF_Util_getMiniRawAddr()` `0x43ca7493`, `[ERR] Free st_saWorkRes` `0x43ca7531`, `[LC] Still DM AF cannot get DDR memhandle` `0x43ca755b`, `[NG] MEM_UNIT_TYPE_CAM_RAW_DM_AFWORK` `0x43ca75e8` |
| `LC_GetZpdResultInfo` | 10 | `0x43ca7732`–`0x43ca78b6` | `0x437c1e6e`–`0x437c1f2e` | 1 | `full_count:0x%04x` `0x43ca7732`, `area[60].zpd_flags=%d, area[60].defocus=%d` `0x43ca777c`, `base_defocus=%d` `0x43ca7802`, `LC_GetZpdResultInfo:Error` `0x43ca78b6` |
| control de captura **mlog** | 3 | `0x43ca7a14`–`0x43ca7a94` | `0x437cd19c`–`0x437cd22e` | 1 | `osal_record_pro error! osal_err=%d` `0x43ca7a14`, `osal_capstop error!` `0x43ca7a4a`, `osal_capstart error!` `0x43ca7a94` |
| `zpd_HybridMovieAF` | 7 | `0x43ca7d26`–`0x43ca7e0b` | `0x437cde58`–`0x437ceb92` | 3 | `zpd_HybridMovieAF_reset` `0x43ca7d26`, `zpd_HybridMovieAF Start` `0x43ca7d50`, `zpd_HybridMovieAF End` `0x43ca7d7a`, `buffer[0]=0x%04x`…`buffer[3]` `0x43ca7da2`–`0x43ca7e0b` |

**Mensajes compartidos entre *movie* y *still*** (misma cadena, dos emisores): `[LC] MMU param
CloseFree Err (unit_hndl:0x%x)` `0x43c9c7f7` (`0x4373c8ac` + `0x437bc5e2`),
`[NG] MEM_UNIT_TYPE_CAM_RAW_DM_AFWORK_E not expected size. size: %08X` `0x43c9c862`
(`0x4373c958` + `0x437bc800`) y `[LC] MMU param open Err (unit_hndl:0x%x)` `0x43c9c958`
(`0x4373ca16` + `0x437bc6fa`). Por eso las 32 cadenas del primer rango tocan funciones de las
dos regiones.

## 4. Funciones que las referencian (37)

Sitio = dirección del `add rX, pc` (la regla estricta empareja cada `add` con el `ldr` más
cercano del mismo registro; el literal del pool se verificó para los 78 sitios).
"Llamadores" = `bl` directos medidos; vacío = **sin `bl` directo medido**, no prueba de
llamada por puntero.

### 4.1 Bloque 1 (cadenas `0x43c9…`, 19 funciones propias + 3 compartidas)

| función | sitios | cadenas | llamadores `bl` | emite |
|---|---:|---:|---|---|
| `0x43545cd0` | 7 | 7 | `0x4374a93c` | volcado scan/predict (`pre position…`, `DIR…`, `F number`, `df`, `id`, `************`) |
| `0x4373c788` | 1 | 1 | — | `getMiniRawAddr` (movie) |
| `0x4373c7c0` | 1 | 1 | — | `getResizedYAddr` (movie) |
| `0x4373c7f8` | 1 | 1 | — (lo llama `0x43738ec0` vía `bl`) | `getSaIfAddr` (movie) |
| `0x4373c838` | 1 | 1 | — | cierre de MMU (movie) |
| `0x4373c914` | 2 | 2 | — | `ESRAM Acquisition failed`, tamaño `…_E` |
| `0x4373c986` | 1 | 1 | — | memhandle miniRAW (movie) |
| `0x4373c9b0` | 2 | 2 | — | `allocWorkMemAreaBank` + MMU open |
| `0x4373ca58` | 1 | 1 | — | `mmu_start_phys_adrs` cero |
| `0x4373ca9c` | 4 | 3 | — | `DDR_Bank`/`ESRAM_Bank`, tamaño de banco |
| `0x4373f45c` | 3 | 2 | `0x4373fbec`, `0x4373fea0` | `LOWCON!!!` (2 sitios), `ERROR…lc_AF_Scan.cpp` |
| `0x43754be0` | 2 | 2 | `0x4373f51c`, `0x4373f6b6`, `0x4374a938`, `0x4376d830` | `fno is %d fno`, `scanless manymode…` |
| `0x43765ad2` | 2 | 2 | — | `LC_SendMessage` (valloc/snd) |
| `0x4376bf64` | 1 | 1 | — | `MS_Writer: disable addr!` |
| `0x4376cce0` | 1 | 1 | — | housing (water) |
| `0x4376cd44` | 1 | 1 | — | housing (far limit) |
| `0x437770dc` | 1 | 1 | — | `osal_ercord error` |
| `0x437771a0` | 1 | 1 | — | `osal_ercord error` |
| `0x43777fec` | 1 | 1 | — | `MSS_reload` |
| `0x437bc588` | 3 | 3 | — | *still*: `CloseFree`, `Free st_miniRawRes`, `Free st_saWorkRes` |
| `0x437bc694` | 2 | 2 | — | *still*: MMU open + `allocWorkMemArea_ddr` |
| `0x437bc73e` | 5 | 4 | — | *still*: tamaños `MEM_UNIT_TYPE_CAM_RAW_DM_AFWORK(_E)` |

### 4.2 Bloque 2 (cadenas `0x43ca…`, 15 funciones propias + 3 compartidas ya listadas = 18)

| función | sitios | cadenas | llamadores `bl` | emite |
|---|---:|---:|---|---|
| `0x437bbbe6` | 1 | 1 | — | `local_getLogDataSeqAddr` |
| `0x437bbc42` | 1 | 1 | — | `local_getLogDataHeadAddr` |
| `0x437bbc72` | 1 | 1 | — | `local_getLogDataMainAddr` |
| `0x437bbea0` | 4 | 4 | — | `LUMI_COEF_CALC`, `ITR_NUM_CALC`, `watkao1`, `END_SYNC_INFO` |
| `0x437bc0ce` | 1 | 1 | — | `DM_AF rlog forward Error!!` |
| `0x437bc21c` | 2 | 2 | — | `LOG_FIELD_NO_EMPTY!`, `LOG_FIELD_UPDATED!` |
| `0x437bc4b8` | 1 | 1 | — | *still*: `getMiniRawAddr` |
| `0x437bc52c` | 1 | 1 | — | *still*: `getSaIfAddr` |
| `0x437bc66a` | 1 | 1 | — | *still*: memhandle DDR |
| `0x437bc84c` | 1 | 1 | — | *still*: `mmu_start_phys_adrs` cero |
| `0x437c1e48` | 10 | 10 | `0x439d9d82` | volcado ZPD (10 líneas) |
| `0x437cd06c` | 3 | 3 | — | `osal_record_pro`/`capstop`/`capstart` |
| `0x437cde1c` | 1 | 1 | `0x437ce2ce` | `zpd_HybridMovieAF_reset` |
| `0x437ce2a0` | 2 | 2 | — | `zpd_HybridMovieAF Start`/`End` |
| `0x437ceae2` | 4 | 4 | — | `buffer[0..3]` |

Detalles de emisión medidos: `lc_HybridAF.cpp %d` recibe la línea **`0x25d`**
(`movw r3,#0x25d` en `0x43755360`) y `fno` se lee de `[ctx+0x202]` en `0x43754e0e`;
`ERROR!!!!! : %d in lc_AF_Scan.cpp` recibe **`0x108b`** (`movw r3,#0x108b` en `0x4373f7d2`);
`LOWCON!!!` se emite tras un contador `> 0xa` (`cmp r2,#0xa` en `0x4373f624` y `0x4373f7ba`).
Cadena de llamadas del AF híbrido: `0x4373f45c` (`lc_AF_Scan`) llama a `0x43754be0` en
`0x4373f51c`/`0x4373f6b6`; a su vez `0x4374a938` llama a `0x43754be0` y el `bl 0x43545cd0`
de `0x4374a93c` viene **inmediatamente después** → el volcado de scan/predict se ejecuta tras
la decisión del AF híbrido.

## 5. Ficheros fuente

Nombres embebidos y verificados leyendo bytes (no son prueba de qué función compiló cada uno):

| fichero | vaddr |
|---|---|
| `Spinal.cpp` | `0x43c9c54f` |
| `lc_AF_Scan.cpp` | `0x43c9cbb0` |
| `lc_wrap_upm.cpp` | `0x43c9d685` |
| `6StillContrastAF/lc_PreReadAF.cpp` | `0x43ca793f` |
| `lc_BracketAF.cpp` | `0x43ca79ba` |
| `Capture/zpd_capture_sequence.cpp` | `0x43cb6145` |
| `Capture/zpd_capture_async_cmd.cpp` | `0x43ccd52b` |

`lc_HybridAF.cpp` no existe como cadena independiente: solo aparece **dentro** de mensajes
(`scanless manymode is undefined. lc_HybridAF.cpp %d` `0x43c9d0d5`; `NOT_DETECT … lc_HybridAF.cpp %d`
`0x43c9d07e`), y `lc_Movie_DM_AF_Util`/`lc_DM_AF_Util` son prefijos de nombre de función, no
ficheros. Otros literales del módulo: `LC_MovieAF Sta/End` `0x43c9c55d`/`0x43c9c56c`,
`LC_near_1st` `0x43c9cc64`, `LC_move_peak` `0x43c9cc70`, `LC_EXTRAFILE` `0x43c9d51e`,
`LC_Com:%2X` `0x43c9d636`, `LC_DEPTH_MAP_LOG` `0x43ca71e9`, `LC_req_pipi` `0x43ca79cb`,
`/mnt/lc_mslog_%04x.dat` `0x43ca7a7d`.

## 6. Relación con ZPD (S75) y AF híbrido

- **Volcado del resultado ZPD**: `LC_GetZpdResultInfo` es la función `0x437c1e48`
  (prólogo `push {r0,r1,r2,r4,r5,r6,r7,lr}`, 10 sitios de traza `0x437c1e6e`–`0x437c1f2e`).
  La llama `0x439d9d82` (`bl`). Tiene un gate que carga el byte de flags
  (`ldrb.w r3,[rX,#0xc0]` en `0x437c1e5a`), prueba el bit 1 (`tst.w r3,#2` en `0x437c1e5e`) y
  salta al error con `beq` en `0x437c1e64`; si no pasa, emite
  `LC_GetZpdResultInfo:Error` `0x43ca78b6`.
- **Layout leído** (corregido; `full_count` viene del **primer argumento**, `r7`, no de `[r4]`):

| offset | campo | traza |
|---|---|---|
| `[r4]+0x00` | `buffer_user_id` | `buffer_user_id=%04x` `0x43ca7756` |
| `+0x3c4` / `+0x3c8` | `zpd_flags` / `defocus` | `area[60].zpd_flags=%d, area[60].defocus=%d` `0x43ca777c` |
| `+0x3cc` / `+0x3d0` | `selected_ym` / `selected_contrast` | `area[60].selected_ym=%d, area[60].selected_contrast=%d` `0x43ca77b9` |
| `+0xce4` | `base_defocus` | `base_defocus=%d` `0x43ca7802` |
| `+0xce8` | `zaf_now_shut_cycle` | `zaf_now_shut_cycle=%d` `0x43ca7824` |
| `+0xcec` | `iris_cur` | `iris_cur=%d` `0x43ca784c` |
| `+0xcf0` | `select_area` (byte) | `select_area=0x%02x` `0x43ca786a` |
| `+0xcf1` | `mario_use_ng_flag` (byte) | `mario_use_ng_flag=%d` `0x43ca788f` |

  Lecturas de campo en `0x437c1e7a` (base), `1e8c` (`+0x3c4`), `1e98`, `1ea6`, `1eb2`,
  `1ec0`, `1ed4`, `1ee8`, `1efc`, `1f10` (las dos últimas con `ldrb.w`, offsets `0xcf0`/`0xcf1`).
- **Puente ZPD → AF híbrido**: `NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable.
  lc_HybridAF.cpp %d` `0x43c9d07e` (S126) lo emite `0x43754be0` (`lc_HybridAF`), la misma
  función que decide el `scanless manymode` (`0x43c9d0d5`). Es el enlace ya documentado en
  [`s75_zpd/zpd_subsystem.md`](../s75_zpd/zpd_subsystem.md).
- **Hooks de vídeo**: `zpd_HybridMovieAF_reset` `0x437cde1c` (llamada desde `0x437ce2ce`),
  `zpd_HybridMovieAF Start/End` `0x437ce2a0` (`0x437ce2c4`/`0x437ce560`) y el volcado
  `buffer[0..3]` `0x437ceae2`; no se ha medido `bl` directo a estas dos últimas.

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| cadenas con `[CAMERA_MAIN_LC]` | 72 | **0** | **0** |
| mensajes interiores idénticos como cadena independiente | 72/72 | **0/72** | **0/72** |

La etiqueta es **nueva en la fw3.21**. En A7S/A6300 los conceptos existen sin etiqueta y con
otra redacción: A7S tiene `lc_HybridAF.cpp` (1), `lc_PreReadAF.cpp` (1), `lc_BracketAF.cpp` (1),
`fc_pos` (3), `MarioAfc` (9) y `zpd_` (1, `LC_GetZpdResultInfo`); el A6300 tiene
`LC_GetZpdResultInfo` (2), `zpd_` (10), `MarioAfc` (10), `fc_pos` (1) y `lc_BracketAF.cpp` (1).
No existen en A7S `zpd_HybridMovieAF`, `LOWCON`, `watkao`, `lc_AF_Scan.cpp`, `kinbou`,
`yosoku`, `scanless`, `lc_DM_AF_Util`, `lc_Movie_DM_AF_Util`,
`MEM_UNIT_TYPE_CAM_RAW_DM_AFWORK` ni `lc_wrap_upm.cpp`.

**Matiz sobre `************`** `0x43c9d03e`: no es una cadena independiente en A7S/A6300 (el
recuento 0/72 se mantiene); allí las secuencias de asteriscos aparecen solo como cola o relleno
de otras cadenas (`[SFRS][FUNC]********************FUNCCMD_SETRECSTATE…`,
`**********************pre_time : %ld now_time : %ld…`), no como traza LC reutilizada.

## 8. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 72 cadenas / 78 sitios / 37 funciones | `scan_s127.py` sobre el mapa global estricto; recuento en `func_map.txt` |
| los 78 sitios son `add rX, pc` que resuelven a la cadena | test: decodifica el `ldr` más cercano, lee el literal del pool y comprueba `W + (site+4) == vaddr` |
| las cadenas están en su vaddr | test: compara los bytes (y el NUL final) de las 72 |
| atribución sitio→función | prólogo Thumb (`push {…,lr}` / `push.w`), corregido a mano en `0x4373c7f8` (el `bl` de `0x43738fe0` lo confirma) |
| layout ZPD | desensamblado de `0x437c1e48` (10 lecturas de campo + el gate de `+0xc0`, 10 sitios) |
| llamadores | `scan_callers.py` (búsqueda de `bl` a direcciones concretas) |
| diferencial | recuento de prefijo e interior exacto en los tres `av-cam.bin` |

## 9. NO VERIFICADO / abierto

- `LC` no está expandido; `CPaf`, `Mario`, `Gpma`, `MaInToOut`, `watkao`, `kinbou`, `yosoku`,
  `mario_use_ng_flag` tampoco. Solo `Camera::LC` está probado por RTTI.
- No se ha identificado el fichero fuente de los helpers `lc_Movie_DM_AF_Util`/`lc_DM_AF_Util`
  ni de `0x43545cd0`, `0x43765ad2`, `0x4376bf64`, `0x4376cce0`, `0x4376cd44`, `0x437770dc`,
  `0x437771a0`, `0x43777fec`, `0x437cd06c`, `0x437cde1c`, `0x437ce2a0`, `0x437ceae2`.
- Que no haya `bl` directo **no** prueba llamada por puntero: solo "sin `bl` directo medido".
- Se desconoce la semántica de `watkao1`, `kinbou`, `yosoku`, `scanless manymode`, `mario_use_ng_flag`
  y de los campos `zpd_flags`/`select_area`; se citan por su traza, no por su significado.
- No se ha medido qué consumidor lee `buffer[0..3]` ni el destino de `LC_SendMessage`.
- El bloque no emite trazas de calibración óptica; si la calibración de lente existe en otro
  sitio, este hito no la cubre.

## 10. Revisión del agente principal

_(vacía)_

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (22 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 72 apariciones del token `[CAMERA_MAIN_LC]` entre `0x43c9c6f6` y
   `0x43ca7e0b`; **78 sitios PIC** (regla estricta) en **37 funciones** y **1 cadena muerta**
   (`0x43c9c779`) — coherente con la metodología canónica.
2. **`LC_GetZpdResultInfo`**: la cadena está en `0x43ca78c8` y la **función** en `0x437c1e48`
   (prólogo Thumb `0xb5f7` = `push {r4-r7,lr}`) → ambas direcciones del informe son correctas
   (cadena y código).
3. **El módulo no calibra la lente**: el subagente lo demuestra por el contenido de las trazas
   (AF, ZPD y DM AF) y por el RTTI de `Camera::LC`; es una **corrección de la premisa del hito**
   (yo lo lancé como «calibración de lente») → **aceptada y documentada**: la sigla `LC` se deja
   **sin desarrollar**.
4. **Diferencial**: 0 prefijos y **0/72** mensajes interiores coincidentes en la A7S y el A6300 →
   el módulo es material **propio de la A6000 fw3.21** (con la salvedad de versión/modelo
   documentada en S130 §4).
5. **Sin efecto en S51**: nada en el módulo toca la línea del obturador.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
