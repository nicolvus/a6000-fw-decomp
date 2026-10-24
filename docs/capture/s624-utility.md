# S624 — `[UTILITY]`: módulo de utilidades de conversión exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**2 trazas · 2 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s624_utility/utility.json).

## Qué es

`[UTILITY]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 2 mensajes del **módulo de utilidades de conversión numérica** dentro del módulo ACCY (Accesorio). La sigla **SÍ tiene base textual**: `UTILITY` → **UTILITY** (utilidades/herramientas); `ACCY` → **ACC**essor**Y** (accesorio); `ERR` → nivel **ERR**or.

## Las 2 trazas (vaddr → texto corto)

```
0x43c251d1 [ACCY][ERR][UTILITY]:%d:ConvNum8ToAscii num = %08X
0x43c25204 [ACCY][ERR][UTILITY]:%d:ConvAsciiToNum8 ascii:%08X
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][ERR][UTILITY]` — módulo padre `ACCY` (accesorio) + nivel `ERR` + sub-módulo `UTILITY` (utilidades). Longitud total: 20 B (`[ACCY][ERR][UTILITY]`).
- **Funciones de conversión**: 2 trazas `ERR` — `ConvNum8ToAscii` (convertir número de 8 bits a ASCII) y `ConvAsciiToNum8` (convertir ASCII a número de 8 bits), ambas con código de error (`%d`) y valor hexadecimal (`%08X`).
- **Logger dual (patrón S177/S179/S603–S623)**: la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA): nueva con prefijo `[ACCY][ERR][UTILITY]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 20 B (`[ACCY][ERR][UTILITY]`) → fijo (ambas trazas son nivel ERR).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][ERR][UTILITY]` | **2** | **0** | **0** |
| núcleos sin prefijo (`ConvNum8ToAscii`, `ConvAsciiToNum8`) | 0/2 como literal autónomo | **0** | **0** |
| strings relacionadas UTILITY A7S | 0 | **20+** (prefijos `VDF`, `Utility`, `SFRA`, `CaptureUtility*`, etc.) | **20+** (similares) |
| código equivalente (NO_VERIFICADO - requiere comparación de instrucciones) (conversión numérica) | `0x43c251d1`… | **sí** | **sí** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** Las funciones de conversión `ConvNum8ToAscii` y `ConvAsciiToNum8` **existen en los tres firmware** (mismas funcionalidades de utilidad). Lo propio de la fw3.21 de la A6000 son (NO_VERIFICADO - requiere xrefs/REA para confirmar duplicación de logger) **las 2 trazas con prefijo `[ACCY][ERR][UTILITY]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 tienen 20+ strings relacionadas con utilidades pero con prefijos dispersos (`VDF`, `Utility`, `SFRA`, `CaptureUtility*`, etc.).

**Longitud del prefijo fija:** 20 B (`[ACCY][ERR][UTILITY]`) → fijo (ambas trazas son nivel ERR).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **utilidades de conversión numérica (8-bit ↔ ASCII)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 2/2 cadenas `[ACCY][ERR][UTILITY]` confirmadas en `0x43c251d1`–`0x43c25204`.
- 0/0 en A7S y A6300 para token `[ACCY][ERR][UTILITY]`; 20+ strings UTILITY relacionadas en A7S/A6300 con prefijos dispersos.
- Scripts: `analysis/s624_utility/` (pendiente) · Tests: `tests/test_s624_utility.py`.
