# S501 — módulo `[STK]` (saliency/tracking, línea general)

## Alcance

Decodificación del módulo `[STK]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01. Las cadenas aparecen como `[TRK]: [STK] ...`, es decir,
submódulo del tracking (`[TRK]`, S71/S111).

## VERIFICADO

- **Volumen de trazas:** A6000 = 76 cadenas `[STK]`; A7S = 76; A6300 = 0
  (eliminado en A6300). Fuente: `strings | grep -c '\[STK\]'` sobre los tres
  `av-cam.bin`. Tras normalizar el salto de línea final quedan 68 cadenas distintas.
- **Inventario REA:** 76 cadenas reconocidas (`analysis/s501_stk/stk_strings.json`,
  rango `0x43cfc7c9`–`0x43cfd8ad`).
- **Referencias de código:** 143 xrefs (`analysis/s501_stk/stk_xrefs.json`); **0 funciones
  contenedoras resueltas** por Ghidra (todas las referencias son Thumb de 2 bytes no
  sembradas como funciones; `analysis/s501_stk/stk_unresolved_xrefs.json`).
- **Subsistemas inferidos de las cadenas (VERIFICADO por texto):**
  - **Saliencia (mapas):** `Saliency`, `Saliency Unexpected Interruption`,
    parámetros `p_yuv422`, `p_saturation_table`, `p_hsv_xyz`, `p_output_color_info`,
    `mode`, `hsv width/height`, `hsv_line_byte_width`, `maps p_hsv_xyz`, `maps width/height`,
    `maps shifted weight[%d]`, `maps previous_max_dist`, `maps hist_on`, `maps p_saliency`,
    `maps p_similarity`.
  - **Similitud de color:** `ColorSimilarity`, `Color Similarity Unexpected Interruption`.
  - **Similitud táctil:** `TouchSimilarity`, `Touch Similarity Unexpected Interruption`.
  - **Cajas (box):** `box p_map`, `p_adj_params`, `p_boxinfo`, `width/height`,
    `max_box_num`, `merge_overlap`, `initial_block_score_threshold`,
    `touch_initial_block_size`, `enlarging_quit_count`, `subsidiary_loop`,
    `subsidiary_score_threshold`, `merge_overlapped_coef`, `remove_border_box_num`,
    `remove_small_area_box`.
  - **Asignación/mensajes:** `Message Alloc Error`, `Stop`.
- **Comparación A6000 vs A7S:** idéntico (76/76 cadenas compartidas; 0 exclusivas
  en cada sentido). A6300 no tiene el módulo (0 cadenas).
  Ver `analysis/s501_stk/stk_compare.json`.

## INFERENCIA

- `[STK]` = submódulo de **saliencia** dentro del tracking de caras/objetos
  (`[TRK]`): calcula mapas de saliencia y similitud (color y táctil) y genera
  cajas de seguimiento. El acrónimo probablemente *Saliency TraCKing*; INFERENCIA.
- Al ser idéntico A6000/A7S y estar ausente en A6300, es un módulo compartido de
  generación A7S/A6000 frente al A6300 (no relacionado con obturador electrónico).

## NO VERIFICADO

- Funciones contenedoras: el código que referencia estas cadenas es Thumb (2 bytes)
  no sembrado en Ghidra; no se resolvieron funciones ni se decompilaron.
- Semántica física de los parámetros (unidades, rangos válidos).
- Relación con los servicios de tracking (`TRK`) y FC-FRC (S71/S111).

## Artefactos

- `analysis/s501_stk/stk_strings.json` (76 cadenas REA)
- `analysis/s501_stk/stk_xrefs.json` (143 xrefs)
- `analysis/s501_stk/stk_unresolved_xrefs.json` (143 xrefs sin función)
- `analysis/s501_stk/stk_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. Funciones no resueltas por
ser Thumb; solo nivel de cadenas y comparación.
