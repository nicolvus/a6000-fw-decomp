# S106 — `IMAGING_CAP`: el gestor de captura *still* de la A6000

> Milestone S106 de la línea de **ingeniería inversa general** (no es el del obturador
> electrónico). Todos los datos son verificables contra los bytes del
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención de direcciones
> **vaddr = 0x43541000 + file_offset** (verificada empíricamente en hitos anteriores).
> Scripts reproducibles en este mismo directorio.

## 1. Qué es `IMAGING_CAP`

`[IMAGING_CAP]` es el **módulo de trazas del gestor de captura de imagen fija (still)** de la
cámara: el proceso que decide *qué* se dispara, *en qué orden* y *con qué parámetros*, y que
entrega el trabajo a los ejecutores (motor de imagen, SDF, codificador).

- **697 cadenas** con el prefijo `[IMAGING_CAP]`, de `0x43c9b335` a `0x43ccab72`.
- Se reparten en **11 bloques** contiguos (`imaging_cap_blocks.json`):

| bloque | rango | n | contenido dominante |
|---|---|---|---|
| `capturing_flags` | `0x43c9b335`–`0x43c9b3da` | 6 | `EnterCapturing`/`ExitCapturing`/`EnterCapturingLv`/`DisableBBOut` |
| `panorama` | `0x43c9e50f` | 1 | `CameraPanoramaSRotateImage` (detalle en S105) |
| `sacc_mem_rc` | `0x43c9ee77`–`0x43ca120f` | 150 | `RCWrapper`, `SACC_Debug`, `sa_func_NFLASH_*`, `PreProcessRC` |
| `systemsound` | `0x43ca40ca`–`0x43ca40fe` | 2 | sonido del sistema durante la captura |
| `cc` | `0x43ca5eae`–`0x43ca5ece` | 2 | `SACC Open/Close Error` |
| `caif_mknote` | `0x43ca8c6c`–`0x43ca911f` | 14 | `CaifCom::SndEvent`, `CAIF osal_alloc_msgq_id`, `EncryptedMKNote SizeOver` |
| `capmgr_notify` | `0x43ca9842`–`0x43caa908` | 55 | `CapMgr)`, `NotifyCtrl)`, `ImageParam_Capture_Base`, `GetMem_*` |
| `sections` | `0x43caae2d`–`0x43caaf7a` | 6 | `Lock/Unlock ExecSection`, `SectionCtrl) Fatal!` |
| `stage_section_engine` | `0x43cac2b0`–`0x43caead2` | 163 | `CamCore`, `DualRecParamErr`, `dmm`, modos `MODE_CAP*` |
| `alloc` | `0x43cb0b03`–`0x43cb0b1d` | 2 | `Open` de unidad de memoria |
| `develop_stages` | `0x43cc6cd7`–`0x43ccab72` | 296 | `ResizeRotate`, `BdexBase`, `ODL_RES_MSG`, `XDMAC`, `ApolloNrBase` |

**Negativo verificado**: en las 697 cadenas **no aparece ni una vez** `shutter`, `silent`,
`EFCS`, `curtain` ni `mechan` (búsqueda sin distinguir mayúsculas sobre el texto completo).
El gestor de captura no registra nada del obturador → **sin efecto en S51** (A/B/C = NO).

## 2. La arquitectura interna: 83 nombres de fichero fuente embebidos

El firmware lleva incrustados los nombres de los ficheros del subsistema (cadena contigua
`0x43ca8e14`–`0x43cb0cbe`; `scan_source_files.py` → `source_files.json`). Es la forma más
directa de reconstruir la arquitectura real:

| familia | n | ficheros |
|---|---|---|
| `selector` | 16 | `Capture{AfterEffect,AfterEnc,AfterRead,CorrectRaw,DevEntry,DevExit,Develop,Encode,Exposure,FeatureEffect,Marble,OpdBeforeNR,Prelight,Read,SortJpeg}_Selector.cpp`, `SequenceFilter_Selector.cpp` |
| `utility` | 10 | `CaptureUtility{CamCore,IDT,ImageSize,Imager,ModuleAPI,PreReview,ReadFlow,SDF,StdYc,SyncResource}.cpp` |
| `handler` | 9 | `FunctionMessage/Notify/SetParam`, `EventDispatcher`, `ExecModeHandler`, `ExecReleaseHandler`, `RawDevHandler`, `ReplyHandler`, `SendChannel` |
| `raw_mem` | 6 | `RawMemManager{,_Beforehand,_MemBuffer,_MemPool,_MemRuleLib,_UnitTypeLib}.cpp` |
| `still` | 7 | `still_{cmp_effect,cnt_panoramaSweep,csl_ring_buff,dda_jpg,dda_rc,mem_mgr,seq_enc}.cpp` |
| `stage` | 8 | `Stage_{Common,DevLater,DualRec,Notify,Panorama,Raw,ResizeHV,WaitControl}.cpp` (las 73 etapas están en S76) |
| `bridge` | 7 | `LRBridge`, `Dfs_Control`, `capcon_api_businessif`, `tsk_capcon_sequence`, `tsk_rawdev_sequence`, `CS_Command`, `InternalCapture` |
| `cam` | 6 | `CamMain`, `CamUser`, `CameraBackGround`, `Face`, `HAPI_Filter_TBOX`, `StillInfoAccr` |
| `capture_manager` | 4 | `CaptureManager{,_FunctionIF,_ModeInfo,_ReleaseIF}.cpp` |
| `section` | 4 | `SectionController`, `SectionQueueManager`, `SectionEndFunc`, `S2Handler` |
| `image_param` | 3 | `ImageParamCapture`, `ImageParamCapture_Memory`, `ImageParam_Sync` |
| `caif` | 1 | `CaifCom_Control.cpp` |
| `notify` | 1 | `NotifyController.cpp` |
| `otros` | 1 | `EnumConverter.h` |

## 3. El motor de secciones: tabla de 17 entradas

El despachador de secciones es `FUN_437e534c` (fichero `SectionController.cpp`). Su
pseudocódigo (REA/Ghidra, lectura de bytes) muestra:

1. `FUN_439c5320(local_104, <tabla>, 0x88)` → copia **0x88 = 136 B = 17 × 8 B**;
2. bucle `iVar3` de 0 a `0x10` (**17 entradas**) comparando `local_104[i*2] == param_1`
   (el **id de sección**) y, si coincide, llamando al puntero `local_104[i*2+1]`;
3. el manejador escribe **5 u32 (20 B)** de parámetros (`local_120`…`local_110`) que se copian
   al resultado.

La tabla vive en el blob en **`0x43ff8fb4`** (verificado leyendo 17 pares `<id u32, manejador u32>`):

| id | manejador | fichero `_Selector` referenciado por su código |
|---|---|---|
| `0x00` | `0x437eabfc` | — (sin cadenas referenciadas) |
| `0x01` | `0x437eb144` | — |
| `0x02` | `0x437ea8cc` | `CaptureExposure_Selector.cpp` (`0x43cac1c7`) |
| `0x03` | `0x437eb24c` | `CaptureRead_Selector.cpp` (`0x43cac25e`) |
| `0x04` | `0x437e9d78` | `CaptureAfterRead_Selector.cpp` (`0x43cac11a`) |
| `0x05` | `0x437ea178` | `CaptureDevEntry_Selector.cpp` (`0x43cac157`) |
| `0x06` | `0x437eaa5c` | — |
| `0x07` | `0x437ea034` | `CaptureCorrectRaw_Selector.cpp` (`0x43cac138`) |
| `0x08` | `0x437eaf38` | `CaptureOpdBeforeNR_Selector.cpp` (`0x43cac221`) |
| `0x09` | `0x437ea410` | `CaptureDevelop_Selector.cpp` (`0x43cac190`) |
| `0x0a` | `0x437ead4c` | `CaptureMarble_Selector.cpp` (`0x43cac206`) |
| `0x0b` | `0x437eab64` | `CaptureFeatureEffect_Selector.cpp` (`0x43cac1e4`) |
| `0x0c` | `0x437e9a70` | `CaptureAfterEffect_Selector.cpp` (`0x43cac0dd`) |
| `0x0d` | `0x437ea724` | `CaptureEncode_Selector.cpp` (`0x43cac1ac`) |
| `0x0e` | `0x437e9be8` | `CaptureAfterEnc_Selector.cpp` (`0x43cac0fd`) |
| `0x0f` | `0x437eb470` | `CaptureSortJpeg_Selector.cpp` (`0x43cac277`) |
| `0x10` | `0x437ea2bc` | `CaptureDevExit_Selector.cpp` (`0x43cac174`) |

Los dos manejadores sin nombre propio (`0x00` y `0x01`) sí devuelven un bloque de 20 B
eligiendo el registro según el modo de captura (p. ej. `FUN_437eabfc`: si
`modo-8 < 6` y `+0x1d8 == 0` usa el registro base `+0xb4`; si `+0x1e0 == 7` elige el
registro 10 (`0xa`) o el 13 (`0xd`); si `+0x1e0 == 0x17` el 8; y así hasta el 11 (`0xb`)).
Los nombres `CapturePrelight_Selector.cpp` (`0x43cac241`) y `SequenceFilter_Selector.cpp`
(`0x43cac294`) aparecen referenciados en código **fuera** de la tabla (`0x437eb0b6` y
`0x437eb5f8`…`0x437ebe22`), es decir, en funciones anexas.

**Consecuencia**: la captura still es una **máquina de estados de 17 secciones**; cada
sección tiene un "selector" (`Capture<Etapa>_Selector.cpp`) que resuelve el bloque de
20 B de parámetros con el que se ejecuta esa sección.

## 4. `CapMgr`: la máquina de eventos de la captura

Bloque `capmgr_notify` (`0x43ca9842`–`0x43caa908`) con el prefijo `CapMgr)`:

- `CapMgr) LastDetectionEnd SeqID(%08x) S2on(%d) ExpCnt(%d)` `0x43ca9caa`
- `CapMgr) NotifySyncStart` `0x43ca9cf2`
- `CapMgr) StartRawSequence SeqID(0x%08x)` `0x43ca9dc7`
- `CapMgr) EndRawSequence. CAP_REQ_CANCEL<%d>! spec %x` `0x43ca9e81`
- `CapMgr) CaptureEnd SeqID(0x%08x)` `0x43ca9d55`
- `CapMgr) CheckLastDet SeqID(0x%08x) S2on(%d) ExpCnt(%d) p_img(%d)` `0x43ca9dfd`
- `CapMgr)CaptureCancel_PowerOffDetect() offFactor=%d` `0x43ca9d85`
- `CapMgr) RawMemMgr Wait ReplaceMem<mode:%x><exp_max:%x>` `0x43ca9f43`

El despachador de eventos es `FUN_437ddf4c` (`0x437ddf4c`, 246 B): lee un valor de estado
de la estructura de captura y salta con una **tabla de 16 entradas** en `0x43bc4e08`
(verificada leyendo 16 u32) antes de invocar a `FUN_43787988`.

## 5. El canal CAIF con el codificador

`CaifCom_Control.cpp` (`0x43ca8e14`) + el bloque `caif_mknote` Implementan el envío de
peticiones CAIF al lado del codificador (EN) y la recepción de datos:

- `CaifCom::SndEvent ERROR! Unknown CA Command (%x)` `0x43ca8cf1`
- `ERROR!! CAIF osal_alloc_msgq_id %x` `0x43ca8e58`
- Comandos con dirección explícita: `[EN->CA]CAIF Send Error! CAP_REQ %s:%d` `0x43cca4fb`,
  `[EN->CA]… CAP_SETTING` `0x43cca56c`, `[EN->CA]… CAP_REQ_CLR` `0x43cca5a6`,
  `[CA->EN]CAIF Recieve Error! CAP_START` `0x43cca531`, `[CA->EN]… CAP_DATA` `0x43cca889`,
  `[CA->AVIP]CAP_V_COM Received ERROR! TimeOut` `0x43cca8c3`.

`CAP_*` son **nombres de mensaje del protocolo CAIF** (no estados internos del gestor).

## 6. Modos de adquisición del `CamCore`

`CamCore acquire Error!: %02x[MODE_…]` dan los **8 modos de adquisición**:
`MODE_CAP` (`0x43cada50`), `MODE_CAP_DRP` (`0x43cad970`), `MODE_CAP_PREREVIEW`
(`0x43cad9df`), `MODE_CAP_SNR` (`0x43cadab6`), `MODE_CAP_SNR_PREREVIEW` (`0x43cadb9d`),
`MODE_SNR_BUS_THROUGH` (`0x43cadb22`), `MODE_SNR_BUS_THROUGH_PREREVIEW` (`0x43cadc15`) y
`MODE_CDET(for PreReview)` (`0x43cadc9c`). El fichero `CaptureUtilityCamCore.cpp`
(`0x43cad7ee`) es la fachada hacia esa librería.

## 7. Capa de memoria

- `ImageParamCapture.cpp` (`0x43ca98f4`) + `ImageParamCapture_Memory.cpp` (`0x43ca9a41`):
  `ImageParam_Capture_Base: AddRef %x ref %d : %d remaining.` `0x43ca9842`,
  `: Release …` `0x43ca9986`, `: ALL Released %x %d remaining.` `0x43ca99d0`.
- `RawMemManager*.cpp` (`0x43caa6bd`–`0x43caadb9`): `MemPool`, `MemBuffer`, `MemRuleLib`,
  `UnitTypeLib`; trazas `CapMgr) RawMemMgr Wait ReplaceMem<mode:%x><exp_max:%x>` `0x43ca9f43`,
  `ShareMem_StlRaw8` `0x43ca9b12`, `CapMgr) Error! UseRaw_DualRec was called too many.`
  `0x43caa044`, `CapMgr) Error! FreeRaw_DualRec was called too many.` `0x43caa086`.
- Familia de unidades de memoria: `GetMem_2ndRaw` `0x43ca9ad5`, `GetMem_YcCor` `0x43ca9b52`,
  `GetMem_MainYc` `0x43ca9c1d`, `GetMem_RawCor` `0x43ca9c5a`, `AllocMem_Raw_Snr` `0x43ca9a5e`.
- DMM (gestor de memoria dinámico): `SetDmmInfo) FATAL! overwrite: id 0x%x handle 0x%x, type 0x%x`
  `0x43ca9bd1`.

## 8. Puentes hacia el resto del sistema

- **SDF** (S103): `CaptureUtilitySDF.cpp` (`0x43cae774`) → el gestor de captura pide
  **33 `MSG_ID_SDF_*`** al ejecutor de trabajos still.
- **Etapas de procesado**: 8 `Stage_*.cpp` en esta zona (el catálogo completo de 73 etapas
  está en S76).
- **Panorámica/barrido**: `still_cnt_panoramaSweep.cpp` (`0x43cab088`) (detalle en S105).

## 9. Cómo se referencian las cadenas (esquema PIC) — método reproducible

En este firmware **no hay punteros absolutos** a las cadenas: el *pool* de literales guarda
un **desplazamiento** y el código lo materializa con

```
ldr  rX, [pc, #inm]      ; W = valor del pool
add  rX, pc              ; destino = W + (dirección_del_add + 4)
```

Verificado con dos casos independientes:

| ldr | pool | W | add | destino |
|---|---|---|---|---|
| `0x437284da` `ldr r3,[pc,#0x2c]` | `0x43728508` | `0x572e4f` | `0x437284e2` | `0x43c9b335` = `[IMAGING_CAP]: EnterCapturing %d` |
| `0x437f5b4a` `ldr.w r3,[pc,#0x954]` | `0x437f64a0` | `0x4b7dea` | `0x437f5b4e` | `0x43cad93c` = `[IMAGING_CAP]: Raw Addr[%08x],Size[%08x],Offset[%x]` |

`scan_pic_refs.py` implementa el cálculo para toda la imagen (`pic_refs.json`):

- **5 560** destinos distintos caen en la zona de cadenas del módulo (barrido con el rango
  restringido a `0x43c90000`–`0x43cd0000`; el barrido de toda la imagen da 73 336);
- **695 de las 697** cadenas de `IMAGING_CAP` tienen referencia confirmada (regla con
  *kill analysis*, ver [`pic_xref_methodology.md`](pic_xref_methodology.md));
- las **2** sin referencia son `0x43ca9b12`
  (`[IMAGING_CAP]: ShareMem_StlRaw8 Err: unit_type[0x%08x], err[%d]`) y `0x43cc839c`
  (`[IMAGING_CAP]: Rch_Rcv_Zima_Base Err: Func[0x%08x]`): **ni** referencia PIC **ni** puntero
  absoluto de 4 B en los 11,4 MB → cadenas muertas que el enlazador conservó.

> **Corrección (hito S110) y rectificación (S118)**: la primera versión del escáner emparejaba
> cada `add rX,pc` con el `ldr` **más cercano** del mismo registro (694/697). Una segunda
> versión probaba **todos** los `ldr` del registro en 4 KB (696/697), pero esa regla **inventa**
> referencias: los dos sitios que añadía son falsos (el `add` de `0x43785d18` materializa
> `[IMAGING_CAP]: PreProcessRC: Release_RC error` `0x43ca03e0`, y el de `0x438c1340`
> `[IMAGING_CAP]: …` `0x43cc7979`, no las cadenas que se les atribuía). La **kill analysis**
> (descartar el par si alguien vuelve a escribir el registro entre `ldr` y `add`) da
> **695/697**. La metodología y la calibración están en
> [`pic_xref_methodology.md`](pic_xref_methodology.md).

## 10. Diferencial con la A7S fw3.20

`scan_a7s_diff.py` (`imaging_cap_a7s_diff.json`):

- **A6000 fw3.21**: 697 cadenas con el prefijo `[IMAGING_CAP]`.
- **A7S fw3.20**: **0** cadenas con ese prefijo. Las mismas mensagens existen, pero **sin
  etiqueta de módulo**: `CapMgr) LastDetectionEnd SeqID(%08x) S2on(%d) ExpCnt(%d)` en
  `0x43cae3b3`, `SectionCtrl) Fatal! Invalid sequence id:%x seq:%x` en `0x43caefd1`,
  `EnterCapturing %d` en `0x43ca1ed8`, `CapMgr) StartRawSequence SeqID(0x%08x)` en
  `0x43cae47d`.
  → **la fw3.21 de la A6000 añade la etiqueta `[IMAGING_CAP]:` a este subsistema**; no es
  una diferencia funcional del gestor, sino de instrumentación.
- Los **16 `*_Selector.cpp`** están presentes en A6000, A7S y A6300: la estructura de
  secciones es común a toda la familia.

## 11. Verificaciones hechas (trazabilidad)

| afirmación | cómo se comprueba |
|---|---|
| 697 cadenas, rango `0x43c9b335`–`0x43ccab72` | `scan_a7s_diff.py` cuenta las ocurrencias del prefijo |
| tabla de 17 secciones en `0x43ff8fb4` | lectura directa de 17 pares u32 |
| 16 nombres `_Selector.cpp` | búsqueda de bytes + referencias PIC por manejador |
| 83 ficheros fuente | `scan_source_files.py` sobre `0x43ca8000`–`0x43cb1000` |
| 694/697 referenciadas | `scan_pic_refs.py` (reproduce el esquema `literal + PC`) |
| 3 cadenas sin referencia | ausencia de puntero absoluto y de destino PIC |
| 0 menciones de obturador | búsqueda case-insensitive en las 697 cadenas |
| A7S sin prefijo | recuento sobre `firmware/extracted/a7s-fw320/.../av-cam.bin` |

## 12. NO VERIFICADO / abierto

- Los **nombres de las 17 secciones**: solo 14 manejadores referencian el nombre de su
  `*_Selector.cpp`; los ids `0x00`, `0x01` y `0x06` no lo hacen (y hay 2 nombres de selector
  —`CapturePrelight`, `SequenceFilter`— referenciados fuera de la tabla). La asignación
  id↔etapa completa queda abierta.
- El **significado** de los 20 B que devuelve cada manejador (5 u32) y de los campos del
  contexto de captura que lo eligen (`+0x1d8`, `+0x1e0`, `+0x4b70`, `+0x54a5`, `+0x54a8`).
- El **formato binario** de los mensajes CAIF y de los `MSG_ID_SDF_*`; el papel exacto de
  `MODE_CDET` y de `MODE_SNR_BUS_THROUGH*`.
- Por qué 3 cadenas quedaron sin referencia (¿código eliminado en fw3.21?).
- Nada de esto **afecta a S51**: el gestor de captura no menciona el obturador.

## 13. Relación con los demás hitos

- **S103 (SDF)**: el ejecutor de trabajos still al que este gestor envía 33 `MSG_ID_SDF_*`.
- **S105 (panorámica/barrido/bracketing/intervalo)**: `still_cnt_panoramaSweep.cpp` y
  `CapturePanoramaSRotateImage` están en este subsistema.
- **S76 (etapas)**: los 8 `Stage_*.cpp` de esta zona son parte de las 73 etapas catalogadas.
- **S84 (API del motor de imagen)**: las llamadas `sa_func_*` de este gestor.
- **S51 (obturador electrónico)**: **sin efecto**; A/B/C = NO.

## 14. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 697 cadenas con vaddr/offset/texto |
| `imaging_cap_blocks.json` | los 11 bloques con histograma de tokens |
| `section_handlers.json` | las 17 entradas y las cadenas que referencia cada manejador |
| `source_files.json` | los 83 ficheros fuente embebidos, agrupados |
| `pic_refs.json` | destinos de las referencias PIC de toda la imagen |
| `imaging_cap_a7s_diff.json` | diferencial A6000 / A7S fw3.20 / A6300 fw2.01 |
| `scan_pic_refs.py`, `scan_section_handlers.py`, `scan_source_files.py`, `scan_a7s_diff.py` | scripts de extracción (reproducibles) |
