# S509 — módulo `[WSX]` (BSFS / sistema de archivos binario, línea general)

## Alcance

Decodificación del módulo `[WSX]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 59 cadenas `[WSX]`; A7S = 59; A6300 = 59.
  Fuente: `strings | grep -c '\[WSX\]'`.
- **Inventario REA:** 59 cadenas (`analysis/s509_wsx/ws_strings.json`).
- **Referencias de código:** 60 xrefs (`analysis/s509_wsx/ws_xrefs.json`); 28 funciones
  contenedoras resueltas (`analysis/s509_wsx/ws_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** BSFS (binary search file system):
  `BSFS INIT/CLOSE/SEARCH`, `BSF SEARCH: Start/End`, `BSSt`, `BsfsWSXClear/Close`,
  `GET/SEND LOG`, `MSG RECEIVE`, errores de fichero/función/línea.
- **Comparación:** idéntico en las tres (59/59/59). Ver `analysis/s509_wsx/ws_compare.json`.

## INFERENCIA

- `[WSX]` = subsistema de **búsqueda/lectura de datos en archivos binarios** (BSFS),
  no relacionado con obturador electrónico.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- `[WSX]`: 59 cadenas con el token (59 con sitio de carga, 64 sitios) en 29 funciones contenedoras; llamadores directos `bl` 29, punteros literal/PC-relativos/`movw`+`movt` 0/0/0; ficheros fuente citados por esas funciones: `nalSepTop/nalSepApp.cpp`; token en A6000/A7S/A6300: 59/59/59; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.

Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.

No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):

- Estructura del BSFS y su uso por otros módulos.

## Artefactos

- `analysis/s509_wsx/ws_strings.json` (59 cadenas REA)
- `analysis/s509_wsx/ws_xrefs.json` (60 xrefs)
- `analysis/s509_wsx/ws_functions.json` (28 funciones)
- `analysis/s509_wsx/ws_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
