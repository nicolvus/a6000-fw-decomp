# S107 — `Camera::CamCore` y la pila `ResourceStack`

**Resumen rápido** (≤60 líneas):

- **37 cadenas** con prefijo `[CAMCORE]` en A6000 fw3.21, rango `0x43c905ca → 0x43cebcb2`; **0** en A7S fw3.20 (mismos mensajes sin etiqueta).
- `CamCore` es `Camera::CamCore`, confirmado por RTTI `N6Camera7CamCore8RdcImageE` (0x43c906b6) y `N6Camera7CamCore13SplitRdcImageE` (0x43cb0b94).
- Gestiona: **SGC** (búsqueda SgcTable), **RDC/PFR** (conversión RAW, memoria PFR, ancho >596), **AIF** (extents, DMA config), **MemoryPool** (sin espacio, 11 callsites), **ExlHelper** (conversión CamMode/imager), **DMA Setter** (6 strings de error), **Powersave** (MonPowersave), **corrección de defectos** sensor (setDefectPt).
- La pila **ResourceStack** (4 strings en el bloque `[IMAGING_CAP]` S106, vaddrs `0x43ca10d1 → 0x43ca120f`) gestiona el ciclo acquire/release de recursos durante la captura still. Errores reportados: `CamCore Release`, `rcct_Release`, `Dfe Release`, `GetMemIndex`.
- **Diferencial A6000 vs A7S**: fw3.21 añadió la etiqueta `[CAMCORE]:` a subsistemas existentes; no hay diferencia funcional.
- **Cierre CAM-01 (03-11-2026, medido en bytes):** 33 funciones con traza `[CAMCORE]`, 0 citan un fichero fuente (ninguno). Token `[CAMCORE]`: 37 en A6000, 0 en A7S y 0 en A6300; el texto sin la etiqueta aparece en A7S en 37 de 37 y en A6300 en 34 de 37 (búsqueda exacta de bytes). Dos cadenas `ExlHelper` (`0x43c90f98`, `0x43c90fd5`) no tienen ninguna referencia (`ldr`+`add pc` estricta, literal de 32 bits, rango de 0x40 B); `loadDefectPos` (`0x43cebc99`) se carga desde `0x439cd7aa` (función `0x439cd794`). SGC, el formato interno de `ResourceStack` y el significado de `loadDefectPos` **no son afirmaciones de este informe**. Método: `analysis/camera_closure/`.

**Enlaces:**
- Informe completo: `analysis/s107_camcore/camcore_resources.md`
- Datos estructurados: `analysis/s107_camcore/camcore_resources.json`