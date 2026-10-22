# S504 — módulo `[STABILIZER]` (estabilización, línea general)

## Alcance

Decodificación del módulo `[STABILIZER]` (prefijo `[CAMERA_IS][AS]: [STABILIZER][AS]`)
del `av-cam.bin` A6000 fw3.21, comparado con A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de cadenas directas `[STABILIZER]`:** A6000 = 3; A7S = 0; A6300 = 0.
  Fuente: `strings | grep -c STABILIZER`.
- **Inventario REA:** 3 cadenas (`analysis/s504_stabilizer/stab_strings.json`):
  - `[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x`
  - `[CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x`
  - `[CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x`
- **Referencias de código:** 2 xrefs (`analysis/s504_stabilizer/stab_xrefs.json`); 1 función
  contenedora resuelta: `FUN_436fecbc` (`analysis/s504_stabilizer/stab_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** registro/desregistro de callback de
  cola de mensajes síncrona (`osal_reg/unreg_sync_msg_queue_cb`) y obtención del handle
  `upm_get_hcrn_ura`; integración con el subsistema AS (auto? stabilizer) bajo
  `[CAMERA_IS]` (S70/S164).
- **Comparación:** las 3 cadenas son exclusivas de la A6000 frente a A7S/A6300.
  Ver `analysis/s504_stabilizer/stab_compare.json`.

## INFERENCIA

- `[STABILIZER]` es un submódulo mínimo del estabilizador de imagen (AS) dedicado al
  cableado OSAL/UPM; la mayor parte del estabilizador se registra bajo `[CAMERA_IS]`
  y `[AS]` (EIS/gyro, S70). El acrónimo `upm_get_hcrn_ura` sugiere un recurso URA.
- Exclusividad A6000 puede deberse a diferencias de integración OSAL, no a captura.

## NO VERIFICADO

- Significado de `upm_get_hcrn_ura` y del flujo de mensajes.
- Relación con captura/obturador electrónico: sin evidencia.

## Artefactos

- `analysis/s504_stabilizer/stab_strings.json` (3 cadenas REA)
- `analysis/s504_stabilizer/stab_xrefs.json` (2 xrefs)
- `analysis/s504_stabilizer/stab_functions.json` (1 función)
- `analysis/s504_stabilizer/stab_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; evidencia mínima (3 cadenas).
