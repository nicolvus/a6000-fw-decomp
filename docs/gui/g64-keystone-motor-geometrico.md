# G64 — Keystone Compensation: ¿hay motor geométrico con malla? (15-11-2026)

Resultado: **PARCIAL**. Sin CFW, sin cámara, sin tocar `scripts/gui/harness/`. Estático sobre `av-cam.bin` 3.21 (REA, sesión propia ya cerrada). No se escribió parche: falta verificar el último eslabón (§3).

## 1. Dónde está la compensación de distorsión (VERIFICADO por cadenas y xrefs)
- Cadena SDF: `ExecRcctSetDistParamCalc`, `ExecRcctDistCorrectionCalc(Rotate)`, `SetDistItp`, `SetDistPower`, `SetDistRoll`, `ModuleDistCorrectionH/V`, `SdfDistParamReader/Writer`, mensajes `MSG_ID_SDF_DIST_ENCODE/RESIZE`. Ruta de captura: `rcct_DistCorrectionH/V_dataset_main` (`[IMAGING_CAP]`); Live View/sync: `job_RCH/RCV_dataset_main` (`[CAMERA_MAIN_SYNC]`, xrefs `0x43799350`/`0x437997f4`), con variante `NODIST`. Es decir, se aplica a foto y a la cadena de vista (a: ambos; el detalle por modo de Live View no se midió).
- Motor hardware: `rcct_SetDistParam` (envoltorio `0x439414dc`), `rcct_DistCorrectionH` (`0x43941570`), `rcct_SetStblzGridH` (`0x43941814`), `rcct_RcNormalizeDistParam`, `rcct_NormalizeDistParamLR`; despachan por método virtual a un driver RC (`0x439443a8`, `0x439447ac`).

## 2. Formato de los datos (a)
- Parámetro de aplicación (`0x437992f8`, hacia `rcct_SetDistParam`): bloque de 13 palabras (`param_2[0..0xc]`, la 12.ª es modo); coeficientes, no malla. Interpretación de cada palabra: NO_VERIFICADO.
- Capa EIS/DIST de `[CAMERA_IS]` (`MakeDistCorPrm` `0x436ea470` → `0x437000dc`): produce **dos rejillas de 11×11 int16** (bucle `0x79 = 121`, paso `0xb`, copias en `+0xec` y `+0x1de` del bloque EIS `0x4371f64c`), a partir de 9 puntos de muestreo por eje y los datos de la lente; el valor por defecto de `0x43adc2fc` fija un lienzo de 16000×12000 y rejilla 4000×3000. `MakeDistRawAppliTag` escribe esa corrección en el RAW. Esto es una **malla 2D de desplazamientos** (VERIFICADO en la generación; la mitad EIS: `rcct_SetStblzGridH` recibe `(param_1+7)>>3`, un tamaño, no el puntero de la malla).
- (c) EIS: `0x4371e078` suma desplazamientos X/Y por eje con límites (`+0x28/+0x2a`), sin rotación vista; panorama (gyro por montura) y Clear Image Zoom (escala) no se analizaron.

## 3. Lo que falta para decidir
Falta confirmar que el motor RC (`0x43945504` para `SetStblzGridH`, `0x439447ac` para `DistCorrectionH`) **consume** la rejilla 11×11 en la imagen (y no solo la guarda en el tag RAW), y qué fuente de datos puede sustituirse con ajuste ≠ 0 (`param_5` de `0x437000dc`). Hasta entonces no se puede afirmar ni que un trapecio sea expresable ni que no. Un trapecio sí cabe en una rejilla 11×11 (bilineal); no cabe en un polinomio radial.

## 4. Pendientes
KEYSTONE-1 en `docs/PENDIENTES.md`.
