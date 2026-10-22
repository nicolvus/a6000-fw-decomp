# S502 — módulo `[EIS]` (estabilización electrónica, línea general)

## Alcance

Decodificación del módulo `[EIS]` (prefijo `[CAMERA_IS][EIS]`) del `av-cam.bin` A6000
fw3.21, comparado con A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas directas `[EIS]`:** A6000 = 4 cadenas REA (`0x43c9a2b2`–`0x43c9a352`);
  cadenas que contienen `EIS` en el binario: A6000 = 6, A7S = 3, A6300 = 3.
- **Inventario REA:** 4 cadenas (`analysis/s502_eis/eis_strings.json`):
  - `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!`
  - `[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!`
  - `[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d`
  - `[CAMERA_IS][EIS]: %x, %d, %d`
- **Referencias de código:** 5 xrefs (`analysis/s502_eis/eis_xrefs.json`); 3 funciones
  contenedoras resueltas (`FUN_43702dac`, `FUN_437046a4`, `FUN_43704d90`)
  (`analysis/s502_eis/eis_functions.json`).
- **Subsistemas inferidos (VERIFICADO por texto):** control de potencia del estabilizador
  (`rcct_SetStblzPower`), rejilla horizontal (`rcct_SetStblzGridH`), lectura del giroscopio
  (`GyroAD[p/y]`). El módulo vive bajo `[CAMERA_IS]` (estabilización IS/EIS, S70/S164).
- **Comparación:** A6000 tiene 6 cadenas con `EIS` frente a 3 en A7S/A6300 (diferencia
  cuantitativa; las 4 directas `[CAMERA_IS][EIS]` son exclusivas de la A6000 en esta muestra).
  Ver `analysis/s502_eis/eis_compare.json`.

## INFERENCIA

- `[EIS]` es un submódulo pequeño de `[CAMERA_IS]` dedicado al control de potencia/rejilla
  del estabilizador y a la lectura del giroscopio; la mayor parte de la estabilización
  se registra bajo otras etiquetas (`[CAMERA_IS]`, `[STABILIZER]`).
- La diferencia 6 vs 3 sugiere que la A6000 amplía el diagnóstico del EIS frente a A7S/A6300,
  sin relación evidente con el obturador electrónico.

## NO VERIFICADO

- Significado de los parámetros (`%x, %d, %d`) y de `rcct_SetStblzGridH`.
- Relación con captura y con los modos de obturador.
- Si las 3 cadenas adicionales de A7S/A6300 son el mismo subsistema con distinto prefijo.

## Artefactos

- `analysis/s502_eis/eis_strings.json` (4 cadenas REA)
- `analysis/s502_eis/eis_xrefs.json` (5 xrefs)
- `analysis/s502_eis/eis_functions.json` (3 funciones)
- `analysis/s502_eis/eis_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. Módulo pequeño, evidencia limitada.
