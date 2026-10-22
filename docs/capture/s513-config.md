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

## NO VERIFICADO

- Semántica de cada área y su consumidor.

## Artefactos

- `analysis/s513_config/cfg_strings.json` (47 cadenas REA)
- `analysis/s513_config/cfg_xrefs.json` (48 xrefs)
- `analysis/s513_config/cfg_functions.json` (1 función)
- `analysis/s513_config/cfg_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
