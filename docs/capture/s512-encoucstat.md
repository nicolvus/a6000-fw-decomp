# S512 — módulo `[ENCOUCSTAT]` (estado del codificador (couc), línea general)

## Alcance

Decodificación del módulo `[ENCOUCSTAT]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 49 cadenas `[ENCOUCSTAT]`; A7S = 54; A6300 = 68.
  Fuente: `strings | grep -c '\[ENCOUCSTAT\]'`.
- **Inventario REA:** 49 cadenas (`analysis/s512_encoucstat/enc_strings.json`).
- **Referencias de código:** 95 xrefs (`analysis/s512_encoucstat/enc_xrefs.json`); 29 funciones
  contenedoras resueltas (`analysis/s512_encoucstat/enc_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** estado del codificador (couc):
  `AVC_ENC_VIDEO_ERR_{STATE,MEMORY,PARAM,INDEX,SA_TIMEOUT}`, `ES Overflow!!`,
  `MSG SET/SEND ERROR`. Errores con fichero/función/línea.
- **Comparación:** A6000 tiene menos trazas que A7S/A6300 (49 vs 54/68).
  Ver `analysis/s512_encoucstat/enc_compare.json`.

## INFERENCIA

- `[ENCOUCSTAT]` = diagnóstico del **codificador de vídeo (couc)**, variante del
  estado del encoder (S507), no relacionado con obturador electrónico.

## NO VERIFICADO

- Semántica de los errores internos.

## Artefactos

- `analysis/s512_encoucstat/enc_strings.json` (49 cadenas REA)
- `analysis/s512_encoucstat/enc_xrefs.json` (95 xrefs)
- `analysis/s512_encoucstat/enc_functions.json` (29 funciones)
- `analysis/s512_encoucstat/enc_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución.
