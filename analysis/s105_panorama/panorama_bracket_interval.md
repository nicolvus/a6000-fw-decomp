# S105 — Los modos de captura especiales: panorámica/barrido (sweep), bracketing e intervalo

**Binario:** `analysis/rea-independent/input/av-cam.bin` (A6000, fw3.21, 11 427 236 B).
**Convención de direcciones:** `vaddr = 0x43541000 + offset_de_fichero`. Todas las direcciones de este
informe son vaddr y se han verificado leyendo bytes (offset = vaddr − `0x43541000`).

**Método:** análisis estático de bytes. Sin ejecutar firmware, sin cámara, sin flasheo, sin `git push`.
El demonio REA compartido (`analysis/rea-independent/run/rea-s104.sock`) **rechazó la conexión**
(`ConnectionRefusedError`, dos intentos) → todo el trabajo se hizo sobre bytes, con un índice propio de
referencias cruzadas (ver §1).

---

## 1. Cómo se referencian las cadenas (hallazgo metodológico previo)

En este blob **las cadenas no se referencian con punteros absolutos**: no existe ni una sola dirección
de cadena almacenada como `u32` en todo el binario (búsqueda exhaustiva sobre los 11,4 MB). El
firmware Thumb usa la forma PC-relativa:

```
ldr  rX, [pc, #imm]     ; 16 bits: 0x48xx..0x4Fxx, Rt = (hw>>8)&7
add  rX, pc             ; 16 bits: 0x4478 + Rd
```

de modo que

```
target = pool_value + (dirección_de_la_instrucción_add + 4)
```

Ejemplo verificado byte a byte:

| instrucción | pool | valor del pool | `add` | destino |
|---|---|---|---|---|
| `0x437e6b5e` `ldr r3,[pc,#0x284]` | `0x437e6de4` | `0x004c44e6` | `0x437e6b6a` (`add r3,pc`) | `0x43cab054` = `'[IMAGING]: [PanoramaSweepStart] Err: 0x%08x : %s:%d'` |

Este mecanismo se usa en el test `tests/test_s105_panorama.py` para re-derivar **cada** referencia
cruzada citada aquí: se lee el par `ldr`/`add`, se recalcula el destino y se compara con la cadena
esperada. Los punteros a *código* (vtables) tampoco existen como direcciones absolutas en el blob, por
lo que la atribución a función se hace por (a) prologo verificado (`push {…,lr}`) y (b) la cadena de
fichero `.cpp` que la propia función cita.

---

## 2. Inventario de cadenas (260 entradas en el JSON)

Conteo de ocurrencias en el binario completo:

| patrón | nº | patrón | nº |
|---|---|---|---|
| `Panorama` | 67 | `MSG_ID_SDF_PANORAMA_CCNR_ENCODE` | 1 |
| `Sweep` | 26 | `MSG_ID_SDF_CCNR_ENCODE` | 1 |
| `Bracket` | **1** | `MSG_ID_SDF_PTM_COUNT` | 1 |
| `Interval` | 10 | `still_cnt_panoramaSweep.cpp` | 1 |
| `INTERVAL` | 4 | `still_cnt_panoramaStitch.cpp` | 1 |
| `PTM` | 59 | `still_seq_panoramaStitch.cpp` | 1 |
| `Ccnr` | 14 | `lc_BracketAF.cpp` | 1 |
| `CCNR` | 10 | `ModulePanoramaCcnrEncode.cpp` | 1 |
| `Tanzaku` | 27 | `ApiPanoramaCcnrEncode.cpp` | 1 |
| `exec_tanzaku` | 2 | `ddl_stitch.cpp` / `ddl_srotate.cpp` | 1 / 1 |

El JSON (`panorama_bracket_interval.json`) lista las **260 cadenas** únicas que contienen `Panorama`,
`Sweep`, `Bracket`, `Interval`/`INTERVAL`, `PTM`, `Ccnr`/`CCNR`, `Tanzaku`/`Tanz` o los nombres de
fichero relevantes, cada una con su vaddr, su offset de fichero, sus sitios de referencia y el
contenedor (función) donde se cita.

### 2.1 Vocabulario de panorámica

Cadenas y función contenedora (todas verificadas con el método de §1):

| vaddr | cadena | xref | contenedor |
|---|---|---|---|
| `0x43cacf07` | `Stage_Panorama.cpp` | `0x43549042`, `0x437f1204` | `0x43549020`, `0x437f10d4` (IMAGING_CAP) |
| `0x43cacf3f` | `[IMAGING_CAP]: PanoramaSweepStart: err[0x%08x]` | `0x435492b2` | `0x43549020` |
| `0x43cacf9c` | `[IMAGING_CAP]: ApolloSA_Main: err[0x%02x]` | `0x437f1352` | `0x437f10d4` |
| `0x43cad0f4` | `Stage_PanoramaCcnrEncode` | `0x437f179c` | `0x437f1414` |
| `0x43cad10d` | `Stage_InitializeSweepAndSpoolBranch` | `0x437f0980` | `0x437f0838` |
| `0x43caceae` | `[IMAGING_CAP]: UpdateSweepCanvas: err[0x%08x]` | `0x437f0b0e` | `0x437f0a58` |
| `0x43cacedc` | `[IMAGING_CAP]: PanoramaStitch: err[0x%08x]` | `0x437f0c98` | `0x437f0b58` |
| `0x43cab088` | `still_cnt_panoramaSweep.cpp` | `0x437e6b62` (7×) | `0x437e6b3c`, `0x437e6e78`, `0x437e751c` |
| `0x43cab054` | `[IMAGING]: [PanoramaSweepStart] Err: 0x%08x : %s:%d` | `0x437e6b5e` | `0x437e6b3c` |
| `0x43cab0a4` / `0x43cab0db` | `… Jpeg Open / Jpeg Close err: 0x%08x` | `0x437e6d6c` / `0x437e6d8c` | `0x437e6b3c` |
| `0x43cab1d9` | `[IMAGING]: [PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d` | `0x437e711c` | `0x437e6e78` |
| `0x43cab21d` | `[IMAGING]: [PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d` | `0x437e737a` | `0x437e6e78` |
| `0x43cab289` / `0x43cab33a` / `0x43cab374` | `[UpdateSweepCanvas] UnitOpen() / seq_brcEncode() / SWEEP_ERROR` | `0x437e75a0` / `0x437e7ad6` / `0x437e7b46` | `0x437e751c` |
| `0x43cc69fa` | `still_cnt_panoramaStitch.cpp` | `0x438bcffc` (13×) | `0x438bcef8` |
| `0x43cc6a47` / `0x43cc6a8b` / `0x43cc6adb` | `seq_initStitch() / seq_panoramaParallelStitch() / seq_endStitch()` | `0x438bd21e` / `0x438bd28c` / `0x438bd2c0` | `0x438bcef8` |
| `0x43c9e617` | `still_seq_panoramaStitch.cpp` | `0x43780f2a` | `0x43780eb4` |
| `0x43c9e5d0` | `[IMAGING]: [seq_panoramaClippingDecode] cmp_decode Err: 0x%08x : %s:%d` | `0x43780f26` | `0x43780eb4` |
| `0x43ccd5c8` / `0x43ccd5e9` / `0x43ccd5fa` | `PanoramaStripSequence::StripInfo` / `PreProcessResult` / `PreProcessResult::Strip[]` | `0x438f4be4` / `0x438f4caa` / `0x438f4cbe` | `0x438f4bcc` |
| `0x43cc6959` / `0x43cc684d` | `src/stitch/ddl_stitch.cpp` / `src/srotate/ddl_srotate.cpp` | `0x438bc732` / `0x438bc0ba` | `0x438bc720` / `0x438bc0a8` |
| `0x43cad558` / `0x43cad57e` / `0x43cad72d` | `Stage_RchRcv_Resize_PanoramaGmvCoarse` / `…_PanoramaAutoReview` / `…_PanoramaThm` | `0x437f4316` / `0x437f4420` / `0x437f4160` | `0x437f42b8` / `0x437f4378` / `0x437f40c4` |
| `0x43caddc2` / `0x43cae41b` / `0x43cae47c` | `GetImageSizeFromBackup_Panorama` / `ReadBackup_PanoramaJpegStreamSize` / `ReadBackup_PanoramaScnJpegTargetSize` | `0x437f6f40` / `0x437f829a` / `0x437f85e8` | `0x437f6f24` / `0x437f8244` / `0x437f85b8` |
| `0x43c9e50f` | `[IMAGING_CAP]: CameraPanoramaSRotateImage: err[0x%08x]` | `0x437803c0` | `0x437802de` |
| `0x43caa019` | `[IMAGING_CAP]: !!! Can't send Panorama cmd` | `0x437df7ae` | `0x437df646` |

### 2.2 Vocabulario de CCNR

| vaddr | cadena | xref |
|---|---|---|
| `0x43c781ac` | `MSG_ID_SDF_CCNR_ENCODE` | `0x43639822` |
| `0x43c781c3` | `MSG_ID_SDF_CCNR_ENCODE_WITH_MODE` | `0x43639828` |
| `0x43c781e4` | `MSG_ID_SDF_PANORAMA_CCNR_ENCODE` | `0x4363982e` |
| `0x43c78289` | `MSG_ID_SDF_CCNR_RESIZE` | `0x43639858` |
| `0x43c7eefe` | `ModuleOnePassCcnrEncode.cpp` | 113 xrefs (`0x4365c060`…`0x43660bfe`) |
| `0x43c7e8f1` | `ModuleCallbackMgrCcnrEnc.cpp` | `0x4365952a`… |
| `0x43c7b926` | `ModulePanoramaCcnrEncode.cpp` | 46 xrefs (`0x43648066`…`0x4364c57e`) |
| `0x43c7baba` / `0x43c7bbc9` | `WrapAplCcnrTanzakuStart.cpp` / `WrapCamTanzakuStart.cpp` | `0x4364d252`… / `0x4364d4d4`… |
| `0x43c7b19f` | `ExecAplCcnrTanzakuStart` | `0x436433c8` |
| `0x43c7f07d` | `StartTanzaku` | `0x4365e462` (8×) |
| `0x43c7f57a` | `[SDF][INT_ERROR] ExecTanzaku Err!` | `0x43662a68` |
| `0x43c7ef97` | `[SDF][CCNR] Timeout! (...going to whole module RETRY)` | `0x4365eb94` |
| `0x43c7ef1a` / `0x43c7ef6e` | `[CCNR TimeOut] SetPblAifIibNum` / `twai_flg` | `0x4365ea70` / `0x4365eb48` |
| `0x43c7b615` | `[SDF][CCNR_ENCODE] jpegOverLimit (...going to ENCODE RETRY)` | `0x43647c86`… |
| `0x43c7effb` / `0x43c7efcd` | `[CCNR_ENCODE] SDF_RECMODE_STILL_REC` / `SDF_RECMODE_OPAL_DUAL_REC` | `0x43660996` / `0x43660990` |

Sub-operaciones del módulo de panorama (todas en `0x43c7b692`–`0x43c7b926`):
`ExecRcH` `OpenRcAcquire` `CloseIibClose` `OpenRcH` `WaitCallbackJpegTanz` `ExecTanzRcDistCalc`
`CloseJpegClose` `SetInputYcTanz` `CalcAreaInputYcTanz` `MemAllocWorkArea` `WriteToDtable`
`GetTanzNoFromDtable` `CloseVfxEffectTransferClose` `OpenJpegOpen` `WaitCallbackRc` `ExecTanzSrcDistCalc`
`ExecTanzAplStart` `ReadInputYcTanz` `ExecSRotate` `SetColorVfxWorkArea` `ExecJpegReady` `CloseSrcRelease`
`OpenSrcAcquire` `MemFreeWorkArea` `ExecJpegEncode` `OpenTanzCalc` `ExecTanzRcDistCalcForRcH`
`SetVfxEfctStartDmaImgPrmCh3` `CalcInputYcTanz` `OpenVfxEffectTransferOpen` `OpenTanzInitParam`
`WaitCallbackSrc` `ExecTanzaku` `CloseRcRelease` `MakeDevelopResizeTable` `CloseRcH`
`ExecVfxEffectTransferStart`.

### 2.3 Vocabulario de bracketing

| vaddr | cadena | xref | contenedor |
|---|---|---|---|
| `0x43ca79ba` | `lc_BracketAF.cpp` | `0x437c7512`, `0x437c761a`, `0x437c7638` | `0x437c74b6`, `0x437c7554` |
| `0x43c9b47c` | `[IMAGING]: FATAL! %s:%d` | `0x437c750e`… | idem (líneas 158 y 168 del fichero) |

**No existe ninguna otra cadena con `Bracket`** (0 fuera de `lc_BracketAF.cpp`), ni `BRACKET`, ni
`bracket`, ni `Bkt`, ni `ExposureBracketing`. Tampoco hay nombres de modo de disparo en el firmware
(el `drive_mode` de 69 valores es una tabla sin nombres — ver S96).

### 2.4 Vocabulario de intervalo

| vaddr | cadena | xref | contenedor |
|---|---|---|---|
| `0x43ca9f89` | `[IMAGING_CAP]: GetCaptureIntervalResource Error! %x` | `0x437df430` | `0x437df338` |
| `0x43caa28b` | `[IMAGING_CAP]: CapMgr) osal_stat_sem: CAPTURE_INTERVAL err %d` | `0x437e0cf8` | `0x437e0ce8` |
| `0x43caa2c9` | `[IMAGING_CAP]: CapMgr) osal_sig_sem: CAPTURE_INTERVAL err %d` | `0x437e0d1e` | `0x437e0ce8` |
| `0x43caa3d3` | `[IMAGING_CAP]: CapMgr) osal_wai_sem: CAPTURE_INTERVAL err %d` | `0x437e0ff8` | `0x437e0fc0` |
| `0x43caa306` | `[IMAGING_CAP]: CapMgr) FreeCaptureIntervalResource(): err %d` | `0x437e0d7a` | `0x437e0d5a` |
| `0x43caa343` / `0x43caa373` | `osal_alloc_timer: err %x` / `osal_set_timer: err %x` | `0x437e0edc` / `0x437e0f02` | `0x437e0e1c` |
| `0x43caa3a1` | `[IMAGING_CAP]: CapMgr) SetIntervalTimer(): err %d` | `0x437e0f0c` | `0x437e0e1c` |
| `0x43c7a1a5` | `[SDF] interval(PTM) %ld` | `0x4363e862` | `0x4363e7ac` |
| `0x43c7a1be` | `[SDF_ERR] interval_ptm over 10[sec]` | `0x4363e886` | `0x4363e7ac` |
| `0x43c7a3c2` | `ApiPtmCount.cpp` | `0x4363ed0e`… | `0x4363ec80` |
| `0x43c78350` | `MSG_ID_SDF_PTM_COUNT` | `0x43639882` | getter SDF |

---

## 3. Flujo de la panorámica por barrido (sweep)

### 3.1 Disparo de la secuencia

`CaptureManager::CaptureStart` (`0x437df646`, fichero `CaptureManager.cpp`) es el punto donde el modo
selecciona el camino de captura:

```
0x437df6c0  bl   0x4378f9b4        ; devuelve el contexto de captura (objeto 0x43e9b548)
0x437df6c4  ldr  r3, [r0, #8]
0x437df6c6  ldrb.w r5, [r3, #0x265]
0x437df6ca  ubfx r5, r5, #2, #2    ; campo de 2 bits -> 4 sub-flujos
0x437df6ce  cmp  r5, #2
0x437df6d0  beq  0x437df798        ; --> RAMO PANORAMA
0x437df6d2  cmp  r5, #3
0x437df6d4  beq.w 0x437df826
0x437df6d8  cmp  r5, #1
0x437df6da  bne.w 0x437df876        ; --> resto (incluye el camino de intervalo)
```

Ramo panorama (`0x437df798`):

```
0x437df7a2  movw r0, #0x301f       ; bytes 43 f2 1f 00 -> peticion 0x301f al CAM_CMD
0x437df7a6  bl   0x437fc310        ; "[CAM_CMD]: Warning! Now rocessing... req[%d]" (0x43caeb10)
0x437df7ac  cbnz r0, 0x437df7d0    ; si falla:
0x437df7ae  ldr  r0, [pc, #0x10c]  ; -> 0x43caa019
0x437df7b6  add  r0, pc            ; "[IMAGING_CAP]: !!! Can't send Panorama cmd"
```

Ramo con `r5 == 1`: `movw r0, #0x3005` (`0x437df6de`, bytes `43 f2 05 00`) y, en error,
`"[IMAGING_CAP]: !!! Can't send DualRec cmd"` (`0x43ca9fef`).

> Lo **VERIFICADO**: la rama de panorama pide `0x301f` y la rama de doble registro pide `0x3005`; el
> nombre del modo está en la cadena de error contigua. Lo **NO VERIFICADO**: el valor numérico de cada
> `r5` (el texto del firmware solo rotula la rama de panorama y la de DualRec).

### 3.2 Cadena de etapas

| # | etapa | función | fichero |
|---|---|---|---|
| 1 | `Stage_InitializeSweepAndSpoolBranch` | `0x437f0838` | `Stage_Panorama.cpp` |
| 2 | `Stage_Panorama::PanoramaSweepStart` | `0x43549020` | `Stage_Panorama.cpp` |
| 3 | `PanoramaSweepStart` (IMAGING) | `0x437e6b3c` | `still_cnt_panoramaSweep.cpp` |
| 4 | `UpdateSweepCanvas` (IMAGING / IMAGING_CAP) | `0x437e751c` / `0x437f0a58` | `still_cnt_panoramaSweep.cpp` / `Stage_Panorama.cpp` |
| 5 | `PanoramaSweepEnd` (IMAGING) | `0x437e6e78` | `still_cnt_panoramaSweep.cpp` |
| 6 | `seq_panoramaClippingDecode` | `0x43780eb4` | `still_seq_panoramaStitch.cpp` |
| 7 | `PanoramaStitch` (IMAGING / IMAGING_CAP) | `0x438bcef8` / `0x437f0b58` | `still_cnt_panoramaStitch.cpp` / `Stage_Panorama.cpp` |
| 8 | `Stage_PanoramaCcnrEncode` | `0x437f1414` | `Stage_Panorama.cpp` |
| 9 | `ApiPanoramaCcnrEncode::ExecMain` (SDF) | `0x4363de9c` | `ApiPanoramaCcnrEncode.cpp` |
| 10 | `ModulePanoramaCcnrEncode` (SDF) | `0x4364801c` (+45 funciones) | `ModulePanoramaCcnrEncode.cpp` |
| 11 | `WrapAplCcnrTanzakuStart` / `WrapCamTanzakuStart` (SDF) | `0x4364d214` / `0x4364d4a8` | `Wrap*.cpp` |
| 12 | `Stage_RchRcv_ResizeFill_PanoramaThm` / `…GmvCoarse` / `…AutoReview` | `0x437f40c4` / `0x437f42b8` / `0x437f4378` | `Stage_Raw.cpp` |

**Detalle de los pasos 3–5** (bytes en `0x437e6b3c`–`0x437e7416`):

* `PanoramaSweepStart` abre y cierra el **codificador JPEG por trama**:
  `bl 0x43afc728` (`0x437e6d64`) y `bl 0x43afc72c` (`0x437e6d84`), con trazas
  `'[IMAGING]: [PanoramaSweepStart] Jpeg Open  err: 0x%08x'` (`0x43cab0a4`) y `… Jpeg Close …`
  (`0x43cab0db`).
* `PanoramaSweepEnd` invoca `cmp_execStitchPreProcess()` (`bl 0x437e65f0` en `0x437e70d2`, traza
  `0x43cab1d9`) y `cmp_checkFillResidual()` (`bl 0x437e6758` en `0x437e734c`, traza `0x43cab21d`): es
  decir, **pre-procesado de stitching** (detección de solape/movimiento) y **comprobación de huecos**
  residuales antes de coser.
* `UpdateSweepCanvas` compone el lienzo con `seq_brcEncode()` (traza `0x43cab33a`) y puede abortar con
  `SWEEP_ERROR Err: 0x%08x, ReqID: 0x%04x` (`0x43cab374`).

**Detalle del paso 7** (`0x438bcef8`): la etapa `PanoramaStitch` del módulo IMAGING
(`still_cnt_panoramaStitch.cpp`) ejecuta tres sub-secuencias —`seq_initStitch()`,
`seq_panoramaParallelStitch()` y `seq_endStitch()`— y llama a la secuencia de stitching
(`bl 0x43780f74` en `0x438bd216`, dentro de `seq_panoramaClippingDecode`, `0x43780eb4`). Los drivers
de bajo nivel son `src/stitch/ddl_stitch.cpp` (`0x438bc720`, citado en `0x438bc732`) y
`src/srotate/ddl_srotate.cpp` (`0x438bc0a8`, citado en `0x438bc0ba`); **ninguno de los dos tiene
llamadores `BL` directos**, es decir, se alcanzan de forma indirecta.

### 3.3 ¿Se capturan N fotogramas y se combinan? — **SÍ**

Prueba directa: `PanoramaStripSequence::StripInfo` (`0x438f4bcc`) opera sobre un resultado de
pre-procesado que es **un array de tiras**:

* `'PanoramaStripSequence::StripInfo'` — `0x43ccd5c8` (xref `0x438f4be4`)
* `'PreProcessResult'` — `0x43ccd5e9` (xref `0x438f4caa`)
* `'PreProcessResult::Strip[]'` — `0x43ccd5fa` (xref `0x438f4cbe`)

y el stitch es **paralelo por tiras** (`seq_panoramaParallelStitch()`, `0x43cc6a8b`). El resultado es
un mosaico único que después se reescala (`PanoramaResize`: `seq_panoramaResize()`,
`seq_makePanoramaMakerNoteData()`) y se codifica (`PanoramaResizeEncode`:
`seq_bigImageResizeEncode()`).

El **número N** de capturas **no aparece en el firmware**: lo decide el userland
(`libObj.so`: `PanoramaSize (1 : WIDE / 2 : STD / 3 : 16_9 / 4 : 360DEG)`, `PanoramaDirection
(1 : VERTICAL / 2 : HORIZONTAL)`).

---

## 4. El papel de `Ccnr` (reducción de ruido por correlación de cuadros)

### 4.1 Qué es, según los bytes

1. **CCNR es un trabajo del SDF** con mensajes propios: `MSG_ID_SDF_CCNR_ENCODE` (`0x43c781ac`),
   `MSG_ID_SDF_CCNR_ENCODE_WITH_MODE` (`0x43c781c3`), `MSG_ID_SDF_CCNR_RESIZE` (`0x43c78289`) y
   `MSG_ID_SDF_PANORAMA_CCNR_ENCODE` (`0x43c781e4`).
2. **El motor de imagen (YC/MARBLE) calcula los parámetros de CCNR *por estilo de captura*.** Existen
   tres estilos con el mismo bloque `param->ccnr`:
   * `STL_PANORAMA` → `'…MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl48_cb_p1 - param->ccnr.cc_bl48_cb_p0 == 0'`
     (`0x43cbdef1`, xref `0x4389d46e`, función `0x4389d180`), y sus hermanas `cc_bl48_cr`
     (`0x43cbdf54`), `cc_bl14_cb` (`0x43cbdfb7`), `cc_bl14_cr` (`0x43cbe01a`);
   * `STL_APOLLO` (`0x43cbe0e4`, función `0x4389da04`);
   * `STL_CAP` (`0x43cbe2cd`, función `0x4389de06`).
   Los cuatro coeficientes se **expresan como diferencia `p1 − p0` entre dos capturas**: ese es el
   indicio directo de que la corrección se calcula *correlacionando* (o restando) dos fotogramas.
3. **El trabajo se hace por tiras ("tanzaku")**: `OpenTanzInitParam`, `OpenTanzCalc`, `ExecTanzaku`,
   `CalcInputYcTanz`, `SetInputYcTanz`, `ReadInputYcTanz`, `GetTanzNoFromDtable`, `WriteToDtable`,
   `ExecSRotate`, `ExecTanzAplStart`… (tabla completa en §2.2).
4. **La ejecución final la hace el SPICA del acelerador escalar**, con los comandos
   `'exec_tanzaku'` (`0x43ce29c1`) y `'exec_tanzaku_mem2mem'` (`0x43ce29ce`), el marcador
   `'s_callback_exec_tanzaku %08X'` (`0x43ce2942`) y el callback `'CallbackRcct %08X'` (`0x43ce2930`).
   En el SDF, los envoltorios son `WrapSpicaExecOneTanzaku` (`0x43c7feed`),
   `WrapSpicaExecOneTanzakuBase` (`0x43c7c4be`), `WrapSpicaExecOneTanzakuNoWait` (`0x43c7c4dc`) y
   `WrapTanzakuCalc*` (`0x43c7c557`–`0x43c7c5c0`).
5. **Los parámetros viajan también al MakerNote**:
   `'void Camera::YC::job_YC_Set_marble_tanzaku_param_makernote(const Camera::CaptureModuleDataAll*,
   const Camera::APL::APL_MARBLE*)'` (`0x43cbe4a2`) y
   `'[CAMERA_MAIN_YC]: MARBLE: STL\tSet_marble_tanzaku_param_rc main_digitalZoomRatioDenom\t=%x'`
   (`0x43cbdce4`, xref `0x4389c382`).

### 4.2 Qué implica para el pipeline

* En **panorámica** el CCNR se aplica **por tira**, tomando como referencia los datos de la trama
  vecina (`ccnr` en forma `p1 − p0`, `Tanzaku`, `PreProcessResult::Strip[]`), **antes** de coser el
  mosaico. Es decir: **N capturas → N tiras → reducción de ruido correlacionada entre tiras → stitch → JPEG único**.
* En **disparo simple** no hay tiras ni diferencias p0/p1 entre capturas: se usa
  `MSG_ID_SDF_CCNR_ENCODE` / `..._WITH_MODE` sobre una sola imagen, y el motor YC usa el estilo
  `STL_CAP` en lugar de `STL_PANORAMA`.
* El acrónimo **NO está expandido en el firmware**. La hipótesis de S101 («corner noise reduction»)
  **no está respaldada** por los bytes de este hito; lo que sí se puede afirmar es que el bloque
  `ccnr` contiene correcciones de nivel de negro (`bl48`, `bl14`) y de balance de color (`cb`, `cr`)
  **definidas como diferencia entre dos capturas**. Semántica exacta: NO VERIFICADA.

---

## 5. Flujo del bracketing

### 5.1 Lo que hay en el firmware

**Únicamente el AF bracketing**, en el módulo `Camera::LC` (`[CAMERA_MAIN_LC]`), fichero
`lc_BracketAF.cpp` (cadena en `0x43ca79ba`). Dos métodos:

**`0x437c74b6` (158 B)** — máquina de estados por *modo*:

```
0x437c74b6  push {r0, r1, r4, r5, r6, lr}
0x437c74ba  cmp  r3, #0
0x437c74be  ldr  r5, [r0]        ; r5 = this+0 (modo 0/1/2)
0x437c74c0  cmp  r5, #1         ; modo 1
0x437c74c4  cmp  r5, #2         ; modo 2
0x437c74ca  ldrh r6, [r0, #0xa]  ; modo 0: parametro u16 en +0xa
0x437c74cc  bl   0x43af1988
0x437c74d4  bl   0x43adcc34
0x437c74da  str  r3, [r4]       ; estado = 1
0x437c74e4  ldr  r3, [pc, ...]   ; modo 1: ++contador global
0x437c74ee  bl   0x43adcc28
0x437c74f4  bl   0x43adcc22
0x437c74fa  bl   0x43af194e
0x437c7508  movs r3, #2         ; estado = 2
0x437c750e  ldr  r3, [pc, ...]  ; modo desconocido ->
0x437c7512  ldr  r4, [pc, ...]  ; "lc_BracketAF.cpp" (0x43ca79ba)
0x437c7526  ldr  r0, [pc, ...]  ; "[IMAGING]: FATAL! %s:%d" (0x43c9b47c)
```

**`0x437c7554` (344 B)** — máquina de estados por *disparo*:

* si `this+0xc == 0` → salida inmediata;
* `this+0` discrimina 0/1/2; el estado 1 recorre un `tbb` sobre `this+0x10` con **5 sub-estados**
  (0..4) y llama `0x4373e0e8`, `0x436ecaa8`, `0x43adaac6`, `0x436f7354`;
* el estado inválido aborta con `FATAL!` **línea 168** (`0xa8`).

Ambos métodos **no tienen ningún llamador directo** (búsqueda exhaustiva de `BL` sobre los 206 360
pares de llamada del binario): se invocan por **despacho virtual**, coherente con que sean métodos de
una clase de `Camera::LC`. La identidad de la clase es NO VERIFICADA (el blob no contiene vtables con
direcciones absolutas).

### 5.2 Lo que NO está en el firmware

* **Cero** cadenas con `Bracket` fuera de `lc_BracketAF.cpp`; cero `BRACKET`, `bracket`, `Bkt`,
  `ExposureBracketing`, `ContinuousShot`.
* No hay tabla de nombres de modo de disparo (el `drive_mode` de 69 valores es una tabla sin nombres,
  ver S96).

Por tanto **el modo de bracketing de exposición/balance de blancos se orquesta en el userland**:
`libObj.so` contiene `CamUser::SequenceSetBracketMode` (`SequenceSetBracketModeE`),
`CamUser::SequenceSyncBracketReset` (`SeqSyncBracketReset)`), `CamUser::SequenceBracketAF`
(`SequenceBracketAFE`), los mensajes al firmware `SetBracketForLiro` y `SetBracketStateClearForLiro`
(«NON SUPPORTED MsgID»), y los eventos `pvt_ActionSetBracketModeEvt`,
`pvt_ActionObjectBracketCountEvt`, `pvt_ExeResetBracketCount`. El firmware aporta el AF bracketing;
el resto son N peticiones de captura ordinarias con distinto EV/WB.

---

## 6. Flujo del disparo por intervalo

### 6.1 Lado del gestor de captura (IMAGING_CAP)

| pieza | vaddr | evidencia |
|---|---|---|
| `GetCaptureIntervalResource` | `0x437df338` | `'[IMAGING_CAP]: GetCaptureIntervalResource Error! %x'` `0x43ca9f89` (xref `0x437df430`) |
| `FreeCaptureIntervalResource` | `0x437e0d5a` | `'…FreeCaptureIntervalResource(): err %d'` `0x43caa306` (xref `0x437e0d7a`) |
| semáforo `CAPTURE_INTERVAL` | `0x437e0ce8` | `osal_stat_sem` `0x43caa28b` (xref `0x437e0cf8`), `osal_sig_sem` `0x43caa2c9` (xref `0x437e0d1e`), `osal_wai_sem` `0x43caa3d3` (xref `0x437e0ff8`, función `0x437e0fc0`) |
| temporizador de intervalo | `0x437e0e1c` | `osal_alloc_timer` `0x43caa343` (xref `0x437e0edc`), `osal_set_timer` `0x43caa373` (xref `0x437e0f02`), `SetIntervalTimer(): err %d` `0x43caa3a1` (xref `0x437e0f0c`) |

Cálculo del periodo (bytes en `0x437e0e9a`–`0x437e0eac`):

```
0x437e0e9a  movw r2, #0x2710      ; bytes 42 f2 10 72  -> 10000
0x437e0e9e  str  r6, [r5]
0x437e0ea8  mul  r2, r2, sb       ; periodo = 10000 * N   (sb = byte del recurso de intervalo)
0x437e0eac  bl   0x437e0bb4       ; osal_set_timer(handle, r1, periodo, r3=2, ...)
```

`0x437e0bb4` es un envoltorio que llama a `0x43561244` (mecanismo genérico de llamada por descriptor,
el mismo que usan las llamadas OSAL). El temporizador se arma con **múltiplos de 10000 unidades**
(unidades de timer OSAL: 1 ms → 10 s). La unidad exacta es NO VERIFICADA.

`CaptureEnd` (`0x437de2a4` / `0x437de308`, traza `'[IMAGING_CAP]: CapMgr) CaptureEnd SeqID(0x%08x)'`
`0x43ca9d55`) es quien llama a `SetIntervalTimer` (`0x437e0dfc`), es decir, **al terminar cada disparo
se rearma el temporizador para el siguiente**.

### 6.2 Lado del SDF (control por PTM)

`SDF::CheckPtmInterval` (`0x4363e7ac`):

```
0x4363e862  ldr  r0, [pc, #0xf0]   ; pool 0x4363e954
0x4363e870  add  r0, pc            ; -> 0x43c7a1a5  '[SDF] interval(PTM) %ld\n'
0x4363e872  mov  r2, sl            ; intervalo medido (64 bits sl:fp)
0x4363e87a  ldr  r2, [pc, #0xc0]   ; pool 0x4363e93c = 900000  (limite, 64 bits)
0x4363e87e  cmp  r2, sl
0x4363e880  sbcs r1, r3, fp
0x4363e884  bhs  0x4363e930        ; limite >= intervalo -> OK
0x4363e886  ldr  r0, [pc, #0xd0]   ; -> 0x43c7a1be  '[SDF_ERR] interval_ptm over 10[sec]\n'
```

Es decir: el SDF **mide el intervalo real en unidades PTM** y aborta si supera el límite de
**900 000** unidades, con un mensaje que lo expresa como «10[sec]». Si la unidad PTM fuese 1/90 000 s,
900 000 unidades serían exactamente 10 s (INFERENCIA, no verificada).

La cuenta de PTM la lleva `ApiPtmCount` (`ApiPtmCount.cpp` `0x43c7a3c2`, funciones `0x4363ec80`,
`0x4363edf8`, `0x4363ef52`, `0x4363efe0`) con las operaciones `WaitImcResponse` (`0x43c7a051`),
`SendMessageImc` (`0x43c7a02d`) y `CheckPtmMax` (`0x43c7a76e`); el mensaje asociado es
`MSG_ID_SDF_PTM_COUNT` (`0x43c78350`).

---

## 7. Diferencias con el disparo simple

| | disparo simple | panorámica/sweep | bracketing | intervalo |
|---|---|---|---|---|
| disparador de modo | rama `r5 == 1` (`req 0x3005`) | rama `r5 == 2` (`req 0x301f`, `0x437df7a2`) | **no hay rama propia en el firmware** | rama resto → `GetCaptureIntervalResource` (`0x437df338`) |
| disparos | 1 | **N** (tiras) | N (los decide el userland) | N (repetidos por timer) |
| mecanismo deHilera | — | `UpdateSweepCanvas` / `seq_brcEncode()` | — | temporizador OSAL + semáforo `CAPTURE_INTERVAL` |
| post-proceso de imagen | `MSG_ID_SDF_CCNR_ENCODE(_WITH_MODE)` | `MSG_ID_SDF_PANORAMA_CCNR_ENCODE`, `ModulePanoramaCcnrEncode`, `exec_tanzaku` (SPICA) | — | — |
| stitching | no | `PanoramaStitch` (`seq_initStitch`/`seq_panoramaParallelStitch`/`seq_endStitch`), `PanoramaResize`, `PanoramaResizeEncode` | no | no |
| estilo del motor YC | `STL_CAP` | `STL_PANORAMA` (params `ccnr` en forma `p1−p0`) | — | — |
| AF | flujo normal | `fc_feature_panorama.cpp` (módulo FC, `0x43cf07bd`) | `lc_BracketAF.cpp` (`0x437c74b6`, `0x437c7554`) | flujo normal |
| control temporal | — | barrido del usuario | — | PTM: `interval(PTM)` (`0x43c7a1a5`), `interval_ptm over 10[sec]` (`0x43c7a1be`) |

---

## 8. Enlaces con hitos previos

* **S96** (`analysis/s96_modes/capture_modes.md`) ya citaba `MSG_ID_SDF_PANORAMA_CCNR_ENCODE`
  (`0x43c781e4`), `PanoramaSweepStart` (`0x43cab054`), `lc_BracketAF.cpp` (`0x43ca79ba`) y
  `[SDF] interval(PTM) %ld` (`0x43c7a1a5`): **las direcciones coinciden**; este hito explica *qué*
  hacen.
* **S101** (`analysis/s101_sdf/sdf_module.md`, `docs/capture/s101-sdf.md`): el panorama, el CCNR y el
  PTM viven **dentro del SDF** (módulo `[SDF]`, `0x43c7785b`–`0x43c806f9`). S101 atribuyó el CCNR a
  «corner noise reduction»: es una **hipótesis no textual** que este hito **no confirma**.
* **S82** (`analysis/s82_autoframing/autoframing_stages.md`): las etapas de panorama usan el mismo
  esquema `Stage_*` (`Stage_Panorama.cpp`, `Stage_Raw.cpp`).
* **S84** (`analysis/s84_sa_api/sa_api_catalogue.md`): la ejecución del CCNR por tiras **no** es una
  familia `sa_func_*`; es el **SPICA** del acelerador escalar (`exec_tanzaku`, `0x43ce29c1`).
* **S78** (`analysis/s78_apc/yc_apc_params.md`): el bloque `ccnr` del MARBLE es un conjunto de
  parámetros **distinto** de los `apc_*`, y además depende del **estilo de captura**
  (`STL_PANORAMA` / `STL_APOLLO` / `STL_CAP`).
* **S97** (`analysis/s97_encsync/encoder_sync.json`): no aporta a estos tres modos (son de vídeo).
* **S71** (`analysis/s71_frc/frc_subsystem.md`): el módulo FC tiene `FC/Feature/fc_feature_panorama.cpp`
  (`0x43cf07bd`) con `ExecApiStartPanoramaDetection` (`0x439d771c`), `CancelPanoramaSearch`
  (`0x439d724c`) y `ExecApiCancelPanorama` (`0x439d75c6`): la **detección de caras durante la
  panorámica** es del lado FC, no del modo de captura.

---

## 9. Lo que queda sin resolver

1. **Número de capturas N** por barrido: no está en `av-cam.bin` (lo decide el userland:
   `PanoramaSize WIDE/STD/16:9/360DEG`).
2. **Significado del acrónimo CCNR**: el firmware no lo expande; la hipótesis «corner noise reduction»
   de S101 no está respaldada; lo demostrable es que `ccnr` contiene correcciones `bl48`/`bl14` ×
   `cb`/`cr` expresadas como **diferencia entre dos capturas**.
3. **Unidad del temporizador OSAL** (el periodo es `10000 × N`): si la unidad es 1 ms serían 10 s en
   múltiplos.
4. **Unidad del contador PTM**: el límite es 900 000 unidades y el mensaje dice «10[sec]».
5. **Valor numérico del campo de 2 bits** en `+0x265` del contexto de captura `0x43e9b548` (solo se
   puede etiquetar la rama de panorama y la de DualRec por su cadena de error contigua).
6. **Identidad de la clase** de `Camera::LC` a la que pertenecen `0x437c74b6` y `0x437c7554`
   (despacho virtual; el blob no tiene vtables con direcciones absolutas).
7. **Significado de los identificadores de petición** `0x3005` (DualRec) y `0x301f` (panorama) en la
   tabla del `CAM_CMD`.
8. **Algoritmo exacto** que ejecuta el SPICA en `exec_tanzaku` y qué entrada usa (tira propia vs. tira
   vecina).
9. **Relación entre el `ContID` de S96** y el número de tomas de los tres modos: no localizada.

---

## 10. Inventario por palabra clave y diferencial con la A7S fw3.20

Anexo reproducible: `scan_keyword_inventory.py` → `keyword_inventory.json` (el script se
**autovalida**: comprueba cada cadena curada contra los bytes y aborta si una dirección no
contiene el texto esperado; las 5 entradas `MARBLE:` y la dirección `0x43c9ebb4` se corrigieron
al integrarlo).

Conteo de cadenas que contienen cada palabra clave (A6000 fw3.21 frente a A7S fw3.20):

| palabra clave | A6000 | A7S | lectura |
|---|---|---|---|
| `panorama` | 96 (92 distintas) | 89 (85) | fw3.21 añade 7 trazas de panorámica (p. ej. `IS_LensMountPanoramaGyro` `0x43c9a426`, `REQ_PANORAMA_EE` `0x43ca13ff`) |
| `sweep` | 29 | 24 | fw3.21 añade 5 trazas de barrido |
| `stitch` | 45 | 43 | motor de costura casi idéntico |
| `interval` | 16 | 18 | **la A7S tiene 2 trazas más** de intervalo |
| `bracket` | 1 | 1 | **una sola** en ambas: `lc_BracketAF.cpp` `0x43ca79ba` → el bracketing no se implementa con ese nombre en el firmware |

Negativo destacado (contado sobre los bytes crudos, no sobre las cadenas): la subcadena
`Bracket` aparece **1 vez** en el binario de la A6000 y 1 en la A7S; la subcadena `bracket` en
minúsculas, **0 veces** en ambos. El bracketing de exposición no está en `av-cam.bin`: lo
orquesta el userland y llega a la cámara como `drive_mode`/`ContID`/`BDROSeq` (S96).

Estructuras de control verificadas en ambos firmwares (bytes idénticos en el mapeo):

- `tbb` de `SWEEP_DIRECTION`: `0x437f6f38` (A6000) / `0x438271da` (A7S) → 4 entradas.
- `tbb` de `SWEEP_LENGTH`: `0x437f6f68` (A6000) / `0x438271f8` (A7S) → 4 entradas.
- Límite del intervalo: constante `0x000DBBA0` (900 000 PTM) en `0x4363e93c` (A6000) y
  `0x4365a668` (A7S).

---

## 11. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s105_panorama.py -q
.venv/bin/python analysis/s105_panorama/scan_keyword_inventory.py   # anexo §10
```

El test verifica, contra bytes: (a) que cada cadena citada existe en `vaddr − 0x43541000` con el
texto exacto; (b) los recuentos de las 26+ patrones y los del anexo §10; (c) que cada sitio de
referencia citado resuelve a la cadena esperada mediante el mecanismo `ldr [pc]` + `add pc`; y
(d) que las direcciones de código citadas no son relleno (`0x00`/`0xFF`) y empiezan por un
prólogo Thumb válido.
