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

## NO VERIFICADO

- Semántica de los códigos de error internos.

## Artefactos

- `analysis/s511_int_error/ie_strings.json` (53 cadenas REA)
- `analysis/s511_int_error/ie_xrefs.json` (1368 xrefs)
- `analysis/s511_int_error/ie_functions.json` (275 funciones)
- `analysis/s511_int_error/ie_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. Macro genérico, no módulo aislado.
