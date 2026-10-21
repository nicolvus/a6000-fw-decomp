# S105 — Panorámica/barrido, bracketing e intervalo (modos de captura especiales)

**Firmware:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`) | **Base:** `vaddr = 0x43541000 + offset`

**Veredicto:** los tres modos son radicalmente distintos. La **panorámica** es la única implementada casi
por completo en el firmware; el **bracketing** solo aporta su pieza de AF; el **intervalo** es un
temporizador OSAL con semáforo más una comprobación de PTM en el SDF.

- **Panorámica (sweep)**: `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un campo de
  2 bits del contexto de captura `0x43e9b548` y, en el valor 2, pide la petición **`0x301f`**
  (`movw r0,#0x301f` en `0x437df7a2`; error `"!!! Can't send Panorama cmd"` `0x43caa019`). Cadena:
  `Stage_InitializeSweepAndSpoolBranch` (`0x437f0838`) → `Stage_Panorama::PanoramaSweepStart`
  (`0x43549020`) → `PanoramaSweepStart` (`0x437e6b3c`, `still_cnt_panoramaSweep.cpp`, **abre y cierra el
  encoder JPEG por trama**) → `UpdateSweepCanvas` (`0x437e751c`) → `PanoramaSweepEnd` (`0x437e6e78`,
  `cmp_execStitchPreProcess()` + `cmp_checkFillResidual()`) → `seq_panoramaClippingDecode` (`0x43780eb4`)
  → `PanoramaStitch` (`0x438bcef8`: `seq_initStitch`/`seq_panoramaParallelStitch`/`seq_endStitch`) →
  `PanoramaResize`/`PanoramaResizeEncode`.
- **Sí se capturan N fotogramas y se combinan**: `PanoramaStripSequence::StripInfo` (`0x438f4bcc`) consume
  `PreProcessResult::Strip[]` (`0x43ccd5fa`) y el stitch es **paralelo por tiras**; N no está en el
  firmware (lo decide el userland: WIDE/STD/16:9/360DEG).
- **CCNR**: trabajo del SDF (`MSG_ID_SDF_PANORAMA_CCNR_ENCODE` `0x43c781e4`) ejecutado **por tiras**
  (`Tanzaku`) en el **SPICA** (`exec_tanzaku` `0x43ce29c1`). El motor YC/MARBLE calcula sus parámetros
  **por estilo de captura** (`STL_PANORAMA` `0x43cbdef1`, `STL_APOLLO`, `STL_CAP`) y los cuatro
  coeficientes (`cc_bl48_cb/cr`, `cc_bl14_cb/cr`) son **diferencias p1−p0 entre dos capturas** → reducción
  de ruido por correlación (el acrónimo **no** está expandido; «corner noise reduction» de S101 es
  hipótesis no textual).
- **Bracketing**: la **única** cadena con `Bracket` es `lc_BracketAF.cpp` (`0x43ca79ba`), dos métodos de
  `Camera::LC` (`0x437c74b6`, `0x437c7554`, solo por despacho virtual, `FATAL!` en las líneas 158 y 168).
  **No hay** traza de bracketing de exposición/balance: lo orquesta el userland (`libObj.so`:
  `SequenceSetBracketMode`, `SequenceBracketAF`, `SetBracketForLiro`).
- **Intervalo**: `GetCaptureIntervalResource` (`0x437df338`), semáforo OSAL `CAPTURE_INTERVAL`
  (`stat/sig/wai_sem`, `0x43caa28b`/`0x43caa2c9`/`0x43caa3d3`) y temporizador (`osal_alloc_timer`/
  `osal_set_timer`) con periodo **10000 × N** (`movw r2,#0x2710` en `0x437e0e9a`). El SDF mide el
  intervalo real en PTM (`[SDF] interval(PTM) %ld` `0x43c7a1a5`) y aborta si supera 900 000 unidades
  (`[SDF_ERR] interval_ptm over 10[sec]` `0x43c7a1be`).

**Abierto (NO VERIFICADO):** N de capturas · acrónimo CCNR · unidad del timer OSAL y del PTM · valor del
campo de 2 bits en `+0x265` · clase de `Camera::LC` de las dos funciones de bracketing · peticiones
`0x3005`/`0x301f` del CAM_CMD · algoritmo de `exec_tanzaku`.

**Método:** estático sobre bytes (sin ejecutar firmware, sin cámara, sin flasheo). Las cadenas se
referencian con `ldr [pc]`+`add pc` (no hay punteros absolutos): el test re-deriva cada referencia cruzada.

[Informe](../analysis/s105_panorama/panorama_bracket_interval.md) ·
[JSON](../analysis/s105_panorama/panorama_bracket_interval.json) · Test: `tests/test_s105_panorama.py`
