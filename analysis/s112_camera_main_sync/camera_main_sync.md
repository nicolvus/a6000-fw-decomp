# S112 — Módulo `[CAMERA_MAIN_SYNC]` (429 trazas)

## Subsistema de sincronización de recursos del sensor

El módulo `[CAMERA_MAIN_SYNC]` gestiona la sincronización y asignación de recursos durante el ciclo de captura del sensor en la cámara Sony A6000 fw3.21. Está compuesto por **429 cadenas de traza** (strings) ubicadas en el rango de direcciones virtuales **0x43c9b409 – 0x43cb5616** (tamaño de rango: ~107 KB en el archivo binario).

### Qué gestiona

El subsistema coordina el acceso a los recursos compartidos por los diferentes subsistemas de la cámara durante la exposición y lectura de imagen. Los principales componentes son:

- **`SyncResMgr`** (55 trazas): Gestor de sincronización de recursos. Proporciona operaciones de bloqueo/desbloqueo, liberación y adquisición de recursos. Se referencia con mensajes como:
  - `SyncResMgr::Lock (%-22s) cnt(%2d)`
  - `SyncResMgr::Unlock (%-22s) cnt (%2d)`
  - `SyncResMgr::Free: CAMDEV(0) ERR:0x%02x cam_core_release error`
  - `SyncResMgr::Free: CAMDEV(1) ERR:0x%02x cam_core_release error`
  - `SyncResMgr::Get: RC_ERR:0x%02x rcct_Acquire RCHV %d error!`
  - `SyncResMgr::Get: RC_ERR:0x%02x rcct_InitHV %d error!`
  - `SyncResMgr::Get: APL_ERR:0x%02x apl_mov_acquire error!`

- **`CAMDEV(0|1)`**: Dos dispositivos de cámara (0 y 1), que representan las instancias de hardware diferenciadas. Los mensajes `Free` y `Get` distinguen entre `CAMDEV(0)` y `CAMDEV(1)`.

- **`FOPD`** (First/Final Overlay Display Processing): Aparece en patrones de registro como `[FOPD]r0:%02X w0:%02X`, formando parte de la entrega de fotogramas.

- **VF/AF sync**: Sincronización de vistafinder y autofocus, mediante mensajes como:
  - `Sync_Kick_IDT`
  - `Sync_Kick_RCH`
  - `Sync_Kick_RCV`

- **Sincronización de lectura** (`Reading synchronization`): Varios mensajes relacionados con el flujo de lectura de imagen:
  - `No Read. cause:no expose`
  - `No Read. cause:clamp, expcnt:%d, clampcnt:%d`
  - `No Read. cause:1st expose with frate changing`
  - `No Read. cause:1st expose`
  - `HS TimeMeasure SyncTask.cpp %dLINE %dusEC_VD_Post SEC_VD_Post`
  - `exp:%d, read:%d, clampinit:%d`
  - `SetSequenceMode img:%d, fratechg:%d, clamp:%d, bb_out:%d cap_`

- **`Dfs_Control`** (11 trazas): Control del DFS (Dynamic Frequency/Frame rate Scaling o similar). Mensajes:
  - `DFS SETTING ERR: Backup_read(BKID_UPM_DEBUG_DISLABLE_DFS_TRAN...`
  - `DFS CMD CLK PRE REQ ERR!:%x`
  - `DFS ID Alloc ERR! DFS:%x DFS_CAM:%x`
  - `DFS F` (corteado)
  - `DVS ID Alloc ERR! :%x`
  - `DVS CB Clear ERR!:%x`
  - `DVS Mem Open ERR!:%x`
  - `DVS SendMsg State ER` (corteado)

- **`DualRec`** / grabación dual: Referenciado a través de `Sync_Cam_Setting` y mensajes de configuración.

- **`APL_ERR`** (17 trazas): Errores del procesador de imagen APL (Auto Picture Library). Mensajes como `APL_ERR:0x%02x apl_mov_set_aic R0ch error!`.

- **`JPEG_Sync`** (13 trazas): Sincronización de encoded/decoded JPEG. Mensajes como `jpeg encode sync next (callback) ERRCODE : %d`.

- **`Wrap` / `!!! BGN Wrap` / `!!! END Wrap`**: Marcadores de sección deWrap-around mode para captura de alta velocidad.

- **`LoadMgr(%X)`** (5 trazas): Gestor de carga de recursos. Mensajes como `LoadMgr(%X) Loader(%d) end`.

- **`EC`** (2 trazas): Errores de la cámara, mensajes como `EC::CapISO Error : ISO %x  MinCap %x`.

- **Register dump patterns** (86 trazas): Formatos de registro hardware como `[CAM0]r0:%02X r1:%02X r2:%02X w0:%02X w1:%02X w2:%02X [CAM1]`, `[DDT]r0:%02X`, `[APL0]r0:%02X ...`, `[IDT]r0:%02X ...`, `[RC0]r0:%02X ...`, `[SRC0]r0:%02X ...`, `[SPC0]r0:%02X ...`, `[VPH]r0:%02X ...`, `[VFX0]r0:%02X ...`, `[VIO]r0:%02X ...`, `[PCP0]r0:%02X ...`, `[ZIMA0]r0:%02X ...`, `[SA0]r0:%02X ...`, `[CPU]r0:%02X ... [DMAC]r0:%02X w0:%02X`. Estos aparecen en trazas de diagnóstico y depuración.

- **`EE(%d) Pin`**, **`RECPin`**, **`PROXYPin`**: Señales de pin de exposición evaluación y proxy.

### Mapa de las 429 trazas por sub-bloque (rangos y vaddrs)

| Sub-bloque | Nº trazas | Rango vaddr (inicio → fin) |
|---|---:|:---|
| SyncResMgr | 55 | 0x43c9b409 → 0x43cb0f3f |
| (vacío/registro) | 86 | 0x43ca2817 → 0x43cb3ec6 |
| DFS_Control | 11 | 0x43ca1781 → 0x43caeed2 |
| APL_Errors | 17 | 0x43cb3600 → 0x43cb3e84 |
| JPEG_Sync | 13 | 0x43ca4b2c → 0x43ca4db7 |
| Sequence_Movie | 9 | 0x43cb32b0 → 0x43cb4064 |
| No Read | 6 | 0x43ca2638 → 0x43ca2765 |
| HS_Main | 5 | 0x43ca2fb8 → 0x43ca3218 |
| VD_Pre | 5 | 0x43ca3975 → 0x43ca3acc |
| DVS | 5 | 0x43caed36 → 0x43caee3b |
| LoadMgr | 5 | 0x43cb385b → 0x43cb394c |
| VD_Sequence | 4 | 0x43ca34bd → 0x43ca518c |
| SendFaceFocus | 4 | 0x43ca51fd → 0x43ca52d9 |
| Clamp | 4 | 0x43cb1329 → 0x43cb139d |
| DMM | 4 | 0x43cb2379 → 0x43cb28fa |
| Format_Strings | 4 | 0x43cb3a29 → 0x43cb3ac5 |
| ... (58 sub-bloques de 1-3 trazas cada uno) | | |

*El sub-bloque vacío (86 trazas) corresponde a patrones de volcado de registros hardware (`[CAMx]`, `[DDT]`, `[APLx]`, `[IDT]`, `[RCx]`, `[SRCx]`, `[SPCx]`, `[VPH]`, `[VFXx]`, `[VIO]`, `[PCPx]`, `[ZIMAx]`, `[SAx]`, `[CPU]`, `[DFE]`, `[EE(%d) Pin]`, `[RECPin]`, `[PROXYPin]`, `[PROXY]`).*

### Funciones que referencian las trazas

El esquema PIC (Position-Independent Code) utilizado en este firmware hace que las cadenas no se apunten con punteros absolutos, sino mediante `ldr rX, [pc, #imm]` seguido de `add rX, pc`, donde el destino es `W + (dirección_del_add + 4)`. Para cada `add` se deben probar todos los `ldr` del mismo registro dentro de una ventana de 4 KB, aceptando solo aquellos cuyo destino cae exactamente al inicio de una cadena.

**Mapa función→traza (completo)**: cruzando las referencias PIC con los prólogos de función
(`push {..,lr}` / `push.w {..,lr}`) se obtienen **430 funciones** que emiten las 429 trazas
(1 407 pares función↔traza). Las que más trazas emiten:

| función | n | primera traza |
|---|---|---|
| `0x4354d740` | 57 | `Sequence Stage Error!` |
| `0x43728dec` | 44 | `SyncResMgr::Free: CAMDEV(0) ERR:0x%02x cam_core_release error` |
| `0x43812848` | 40 | `osal Err: src_id[0x%08x], err[0x%08x]` |
| `0x43812f34` | 35 | `osal Err: src_id[0x%08x], err[0x%08x]` |
| `0x437298e8` | 32 | `SyncResMgr::Free: APL_ERR:0x%02x apl_mov_set_aic R…` |
| `0x4379bb90` | 29 | `SyncResMgr::Free: RC_ERR:0x%02x rcct_SetAicParam R…` |
| `0x43792a0c` | 26 | `int_HS timing error %d/8V->%d/8V` |
| `0x43790b68` | 25 | `HS_Sequence: start delayed %dV #%d => %dV #%d %dus` |
| `0x4354f192` | 24 | `Sequence Stage Error!` |
| `0x4378ec60` | 22 | `[CAM0]r0:%02X r1:%02X r2:%02X w0:%02X …` |

Los scripts de soporte existentes son:
- `analysis/s106_imaging_cap/scan_pic_refs.py` — escáner de referencias a cadenas en toda la imagen (~5 s).
- `analysis/s110_camera_main_yc/map_functions.py` — atribuye cada cadena a su función usando el esquema PIC.

### Ficheros fuente que lo implementan

Los nombres de ficheros `*.cpp* embebidos en las cadenas y referencias incluyen:

- **`SyncResMgr`**: Gestión de bloqueo y liberación de recursos CAMDEV, con funciones de adquisición RC (RC = Resource Container/Handler).
- **`DFS_Control`**: Implementación de la interfaz de control de DFS a través de `Backup_read` y identificadores `BKID_UPM_DEBUG_DISLABLE_DFS_TRAN`.
- **`JPEG_Sync`**: Callbacks de finalización de encode/decode JPEG síncronos.
- **`Wrap`**: Marcadores de inicio/fin de modo de captura envolvente (`!!! BGN Wrap::AsyncUnLock`, `!!! END Wrap::AsyncLock`).
- **`DFS` / `DVS`**: ID allocation, memorización y envío de mensajes de estado.
- **`CamCore`**: `CamCore ParamSetError`, `CamCore Start Error`, `2ndParamSetError`.
- **`External_Storage`**: `ExternalStorageStart() Error`, `ExternalStorageAcquire() Error`, `ExternalStorageRelease() Error`.
- **`LoadMgr`**: `Loader(%X) Unload %s`, `Loader(%X) Reload %s`.
- **`RC_ERR`**, **`RCV`**, **`RCH`**: Manejo de errores y adquisición de recursos de captura (RCV = Resource Container Viewer, RCH = Resource Container Handler).

### Relación con el imager, el DFE, la memoria (DMM) y el gestor de captura (S106)

- **Imager**: Las trazas `Imager Execute %dus`, `Imager param error shut:%d, svr_num:%d, VdNum:%d`, `Imager svd error. shut:%d, svd:%d -> %d` y los patrones de registro `[VPH]`, `[VIO]` relacionan este módulo con el subsistema de imagen. El DFE (Digital Front End) es referenciado mediante `DFCore` y `DFE_ERR` en `SyncResMgr::Release: IMAGER0, DFE_ERR:0x%02x`.

- **DFE (Digital Front End)**: El `SyncResMgr::Release: IMAGER0, DFE_ERR:0x%02x` y `SyncResMgr::Free: IDT_TOP, IDT_ERR(VATR):0x%02x` muestran que el módulo informa errores del DFE y de la tabla IDT (Image Device Table).

- **DMM (Dynamic Memory Manager)**: Las trazas `dmm Free Err: JPGRINGBUF_unit_type[0x%08x], err[%d]`, `dmm Free Err: JPG_INFO_BUF_unit_type[0x%08x], err[%d]` y `dmm AllocNew Err: JPGRINGBUF_unit_type[0x%08x], err[%d]` vinculan al módulo con el gestor de memoria dinámica para asignación de buffers de imagen (JPEG ring buffer, info buffer).

- **Gestor de captura (S106 - `[IMAGING_CAP]`)**: El módulo `[CAMERA_MAIN_SYNC]` es el consumidor principal de los recursos gestionados por el módulo `[IMAGING_CAP]` (S106). Las referencias a `CAM_CORE_ERR`, `rcct_Acquire`, `rcct_Init`, `rcct_Release`, y los patrones `RC_ERR:0x%02x rcct_*` demuestran la dependencia: el sincronizador solicita recursos al gestor de captura y maneja los errores de adquisición/inicialización/liberación. La relación es de **cliente-servidor**: `CAMERA_MAIN_SYNC` pide recursos a `IMAGING_CAP` y reporta estado y fallos.

### Diferencial A6000 vs A7S fw3.20

- En el firmware **A6000 fw3.21**, el módulo **[CAMERA_MAIN_SYNC]** tiene **429 trazas** con el prefijo `CAMERA_MAIN_SYNC]`.
- En el firmware **A7S fw3.20**, **no hay trazas** con el prefijo `CAMERA_MAIN_SYNC]` (0 trazas). Los mismos mensajes de texto (strings idénticos o muy parecidos) existen en el binario de A7S, pero **sin la etiqueta `[CAMERA_MAIN_SYNC]`** previa. Esto significa que la A7S no tiene el subsistema de sincronización de recursos identificado con ese prefijo/etiqueta, aunque la funcionalidad subyacente (bloqueo de recursos, liberación, dump de registros, control DFS, sincronización de JPEG, etc.) está presente bajo otras etiquetas o módulos.

**Conteo de mensajes comunes texto a texto** (verificado byte a byte contra el binario de la
A7S, ignorando los especificadores de formato): **418 de las 429** trazas de la A6000 tienen
un equivalente en la A7S; solo **11** son exclusivas de la A6000 fw3.21:

| vaddr | mensaje |
|---|---|
| `0x43ca2de1` | `CamOutV` |
| `0x43ca35b6` | `CamV` |
| `0x43ca3fe7` | `CONNETCT_COMP err:0x%02x!` |
| `0x43ca4045` | `DISCONNETCT err:0x%02x!` |
| `0x43cb0ded` | `SuperSlowMotion[Buffering] error: IMAGE_FRAME_RATE=%d (enum)` |
| `0x43cb1056` | `Sync_Kick_IDT: overflow %dV #%d => %dV #%d %dus` |
| `0x43cb109a` | `Sync_Kick_IDT: overflow %dV => %dV %dus` |
| `0x43cb10f7` | `Sync_Cam_Setting: DIST_RSLT_NG ConvertPosInvDistortionCorrection error!` |
| `0x43cb13c4` | `Sync_Kick_RCH: overflow %dV #%d => %dV #%d %dus` |
| `0x43cb1408` | `Sync_Kick_RCH: overflow %dV => %dV %dus` |
| `0x43cb55dd` | `EC::CapISO Error : ISO %x  MinCap %x` |

### Estado de verificación

- **NO VERIFICADO / abierto**: el significado de los identificadores de sincronismo
  (`Sync_Kick_IDT`, `Sync_Kick_RCH`, `Sync_Kick_RCV`), de la abreviaturas `HS`/`VD` y del
  contador `%d/8V` (posición en octavos de vertical).

### Revisión del agente principal (correcciones aplicadas)

1. **Extracción de las cadenas**: el borrador tomaba las direcciones **un byte después** del
   inicio real (se saltaba el `[` de `[CAMERA_MAIN_SYNC]`) y guardaba el texto **sin cortar en
   el NUL**, de modo que cada "cadena" incluía las siguientes. Reextraídas: rango real
   `0x43c9b409`–`0x43cb5616` (no `0x43c9b40a`–`0x43cb5617`).
2. **Sub-bloques**: el borrador anunciaba 147 (JSON) y 63 (informe); con los datos corregidos
   son **101** etiquetas distintas (la mayor, sin etiqueta, 160; `SyncResMgr` 55; `APL_ERR` 17;
   `jpeg` 13; `DFS` 11; `Sequence_Movie` 9).
3. **Mapa función→traza**: estaba declarado como pendiente; ahora está **completo** (430
   funciones, 1 407 pares) y se incluye en el JSON.
4. **Diferencial A7S**: el borrador dejaba los marcadores `XXX`/`YYY` sin números; verificados
   byte a byte: **418/429** mensajes comunes y **11** exclusivos de la A6000 (tabla arriba).
5. Se añade `reextract.py` (reextracción + mapa + diferencial) como script reproducible.

---

## Referencias y ficheros relacionados

- **Firmware analizado**: `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B, vaddr = 0x43541000 + file_offset)
- **JSON estructurado**: `camera_main_sync.json`
- **Scripts de extracción**: `analysis/s106_imaging_cap/scan_pic_refs.py`, `analysis/s110_camera_main_yc/map_functions.py`
- **Hitos previos**: S31 (CAMERA_MAIN_SYNC/DFECore línea del obturador), S37/S38 (DMM), S89 (mapas IDT/IDT_OPD), S106 ([IMAGING_CAP] + ResourceStack), S107 ([CAMCORE]), S108 ([CAMERA_SA]), S109 ([CDIAG]), S110 ([CAMERA_MAIN_YC]), S111 ([TRK])