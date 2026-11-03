# S511 — subetiqueta `[INT_ERROR]` (errores internos del SDF, línea general)

## Alcance

Decodificación de la subetiqueta `[INT_ERROR]` (aparece como `[SDF][INT_ERROR]`)
del `av-cam.bin` A6000 fw3.21, comparada con A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 53 cadenas `[INT_ERROR]`; A7S = 53; A6300 = 53.
  Fuente: `strings | grep -c '\[INT_ERROR\]'`.
- **Inventario REA:** 53 cadenas (`analysis/s511_int_error/ie_strings.json`).
- **Referencias de código:** 1368 xrefs (`analysis/s511_int_error/ie_xrefs.json`); 275 funciones
  contenedoras resueltas (`analysis/s511_int_error/ie_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** macro de error interno del SDF:
  `IntErrCode`, `SetCamMemList Err!`, `SetCamEncType Err!`, `ExecCamCoreDevelopStart Err!`,
  `inExtentList`, `outStreamObj`, `outExtentList`, `limitDMAcycle`, `inputArbitration`,
  etc.
- **Comparación:** idéntica (53/53/53). Ver `analysis/s511_int_error/ie_compare.json`.

## INFERENCIA

- `[INT_ERROR]` es un **macro de diagnóstico genérico** del SDF (S103), no un módulo
  independiente; su gran número de xrefs (1368) refleja su uso generalizado.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- `[INT_ERROR]`: 53 cadenas con el token (53 con sitio de carga, 1368 sitios) en 277 funciones contenedoras; llamadores directos `bl` 545, punteros literal/PC-relativos/`movw`+`movt` 6/0/0; ficheros fuente citados por esas funciones: `ApiDistResizeApl.cpp`, `ApiPanoramaCcnrEncode.cpp`, `ApiPtmCount.cpp`, `ApiYcPinNoBase.cpp`, `ModuleDecodeJpeg.cpp`, `ModuleDecodeJpegBase.cpp`, `ModuleDecodeJpegRss.cpp`, `ModuleDecodeJpegSimple.cpp`, `ModuleDistBase.cpp`, `ModuleEncodeJpegBase.cpp`, `ModuleJpegSort.cpp`, `ModuleOnePassBase.cpp`, `ModuleOnePassCcnrEncode.cpp`, `ModuleOnePassDevelopResize.cpp`, `ModuleOnePassScnBase.cpp`, `ModuleOnePassScnEncode.cpp`, `ModuleOnePassScnEncodeWithThm.cpp`, `ModuleOnePassScnResize.cpp`, `ModuleOnePassSplitEncode.cpp`, `ModulePanoramaCcnrEncode.cpp`, `ModuleResizeRotateNoMem.cpp`, `ModuleSpica.cpp`, `WrapAplCcnrTanzakuStart.cpp`, `WrapCamTanzakuStart.cpp`, `WrapJpegSort.cpp`, `WrapJpegTanzEncode.cpp`, `WrapJpegTanzReady.cpp`, `WrapPrcStart.cpp`, `WrapRcBase.cpp`, `WrapRcctAcquire.cpp`, `WrapRcctDistCorrectionCalc.cpp`, `WrapRcctDistCorrectionCalcRotate.cpp`, `WrapRcctDistCorrectionH.cpp`, `WrapRcctDistCorrectionV.cpp`, `WrapRcctHoldV.cpp`, `WrapRcctInitH.cpp`, `WrapRcctInitHV.cpp`, `WrapRcctInitV.cpp`, `WrapRcctRcNormalizeDistParam.cpp`, `WrapRcctRelease.cpp`, `WrapRcctResizeH.cpp`, `WrapRcctSetAicParam.cpp`, `WrapRcctSetDistParam.cpp`, `WrapRcctSetDistParamBase.cpp`, `WrapRcctSetDistParamCalc.cpp`, `WrapRcctSetStblzGridH.cpp`, `WrapRcctSetStblzParamV.cpp`, `WrapRcctSetStblzPower.cpp`, `WrapRcctSetStblzVectorH.cpp`, `WrapRcrtCopyBase.cpp`, `WrapRcrtResizeBase.cpp`, `WrapRcrtResizeOverSpec.cpp`, `WrapSaCalcBase.cpp`, `WrapSrotateStart.cpp`, `WrapVfxEffectTransferClose.cpp`, `WrapVfxEffectTransferOpen.cpp`, `WrapVfxEffectTransferStart.cpp`, `WrapVfxEffectTransferStartNoWaitCb.cpp`, `WrapVfxSimpleTransferClose.cpp`, `WrapVfxSimpleTransferOpen.cpp`, `WrapVfxSimpleTransferStart.cpp`; token en A6000/A7S/A6300: 53/53/53; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.

Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.

No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):

- Semántica de los códigos de error internos.

## Artefactos

- `analysis/s511_int_error/ie_strings.json` (53 cadenas REA)
- `analysis/s511_int_error/ie_xrefs.json` (1368 xrefs)
- `analysis/s511_int_error/ie_functions.json` (275 funciones)
- `analysis/s511_int_error/ie_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. Macro genérico, no módulo aislado.
