# S508 — módulo `[GOLFSHOT]` (detección de golpe de golf, línea general)

## Alcance

Decodificación del módulo `[GOLFSHOT]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de cadenas que contienen `GOLFSHOT`:** A6000 = 72; A7S = 72; A6300 = 71.
  Fuente: `strings | grep -c GOLFSHOT`.
- **Inventario REA:** 63 cadenas (`analysis/s508_golfshot/golf_strings.json`), repartidas
  bajo varios prefijos: `[GOLFSHOT]`, `[IMAGING_RSRC]`, `[IMAGING_CAP]`,
  `[CAMERA_MAIN_SYNC]`.
- **Referencias de código:** 62 xrefs (`analysis/s508_golfshot/golf_xrefs.json`); 9 funciones
  contenedoras resueltas (`analysis/s508_golfshot/golf_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** detección de disparo de golf:
  `shot_time_vfc`, `Seq._SndDetEE`, `correctSndDetResult`, `ALOCK_ERR` (BG image),
  `vfc2indx: Shot Timing Transform Error`, `SA_LPF/SA_BGEST/SA_SSP Exec Err`,
  `FREE_ERR: SSP_IMAGE`. Integración con `[CAMERA_MAIN_SYNC]` y `[IMAGING_CAP]`.
- **Comparación:** prácticamente idéntico entre A6000/A7S/A6300 (72/72/71).
  Ver `analysis/s508_golfshot/golf_compare.json`.

## INFERENCIA

- `[GOLFSHOT]` = función de **detección automática de swing de golf** (timing de disparo),
  no relacionada con obturador electrónico.

## NO VERIFICADO

- Algoritmo de detección y parámetros de sonido/imagen.

## Artefactos

- `analysis/s508_golfshot/golf_strings.json` (63 cadenas REA)
- `analysis/s508_golfshot/golf_xrefs.json` (62 xrefs)
- `analysis/s508_golfshot/golf_functions.json` (9 funciones)
- `analysis/s508_golfshot/golf_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
