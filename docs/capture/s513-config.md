# S513 — módulo `[CONFIG]` (volcado de configuración, línea general)

## Alcance

Decodificación del módulo `[CONFIG]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 47 cadenas `[CONFIG]`; A7S = 47; A6300 = 47.
  Fuente: `strings | grep -c '\[CONFIG\]'`.
- **Inventario REA:** 47 cadenas (`analysis/s513_config/cfg_strings.json`).
- **Referencias de código:** 48 xrefs (`analysis/s513_config/cfg_xrefs.json`); 1 función
  contenedora resuelta (`analysis/s513_config/cfg_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** volcado de áreas de trabajo:
  `code_work_area`, `eSRAM_work_area`, `DRAM_work_area`, `bin_buffer_address`,
  y sus tamaños.
- **Comparación:** idéntica (47/47/47). Ver `analysis/s513_config/cfg_compare.json`.

## INFERENCIA

- `[CONFIG]` = módulo de **volcado de configuración de memoria** (áreas de trabajo),
  no relacionado con obturador electrónico.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- `[CONFIG]`: 47 cadenas con el token (47 con sitio de carga, 47 sitios) en 1 funciones contenedoras; llamadores directos `bl` 2, punteros literal/PC-relativos/`movw`+`movt` 0/0/0; ficheros fuente citados por esas funciones: ninguno; token en A6000/A7S/A6300: 47/47/47; alcance `bl` ≤ 3 al obturador: ninguna de las 7 funciones de obturador conocidas.

Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.

No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):

- Semántica de cada área y su consumidor.

## Artefactos

- `analysis/s513_config/cfg_strings.json` (47 cadenas REA)
- `analysis/s513_config/cfg_xrefs.json` (48 xrefs)
- `analysis/s513_config/cfg_functions.json` (1 función)
- `analysis/s513_config/cfg_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
