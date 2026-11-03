# S507 — módulo `[VIDENCSTAT]` (estado del codificador de vídeo, línea general)

## Alcance

Decodificación del módulo `[VIDENCSTAT]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 70 cadenas `[VIDENCSTAT]`; A7S = 70; A6300 = 71.
  Fuente: `strings | grep -c '\[VIDENCSTAT\]'`.
- **Inventario REA:** 70 cadenas (`analysis/s507_videncstat/vis_strings.json`).
- **Referencias de código:** 115 xrefs (`analysis/s507_videncstat/vis_xrefs.json`); 32 funciones
  contenedoras resueltas (`analysis/s507_videncstat/vis_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** estado del codificador de vídeo:
  `ExecuteEncPictureNormal/Failure`, `ExecuteEncPicture`, `Notify Final Es`,
  `Use 2nd Latest Index`, protección de tiempo (`can't protect %d[us] restriction`),
  PTS (`[VIDEO INFO] Pts = 0x%08x EndFlug`), `augi,paddingAreaLength`, errores con
  fichero/función/línea/estado.
- **Comparación:** prácticamente idéntico entre A6000/A7S/A6300 (70/70/71).
  Ver `analysis/s507_videncstat/vis_compare.json`.

## INFERENCIA

- `[VIDENCSTAT]` = diagnóstico/estado del **codificador de vídeo** (H.264/AVC), no
  relacionado con obturador electrónico.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- `[VIDENCSTAT]`: 70 cadenas con el token (70 con sitio de carga, 114 sitios) en 32 funciones contenedoras; llamadores directos `bl` 45, punteros literal/PC-relativos/`movw`+`movt` 4/0/0; ficheros fuente citados por esas funciones: `video/enc/avcEncVideoState.cpp`, `video/enc/avcEncVideoStateEncStill.cpp`, `video/enc/avcEncVideoStateIdle.cpp`, `video/enc/avcEncVideoStateNonActive.cpp`; token en A6000/A7S/A6300: 70/70/71; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.

Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.

No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):

- Semántica de los estados internos y de `augi`.

## Artefactos

- `analysis/s507_videncstat/vis_strings.json` (70 cadenas REA)
- `analysis/s507_videncstat/vis_xrefs.json` (115 xrefs)
- `analysis/s507_videncstat/vis_functions.json` (32 funciones)
- `analysis/s507_videncstat/vis_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
