# S611 — `[IMAGING_RSRC]`: módulo de recursos de imagen (GOLFSHOT) exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**5 trazas · 5 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s611_imaging_rsrc/imaging_rsrc.json).

## Qué es

`[IMAGING_RSRC]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes del **gestor de recursos de imagen para modo GOLFSHOT** (secuencia de disparo en ráfaga / high-speed shooting). La sigla **SÍ tiene base textual**: `IMAGING_RSRC` → **Imaging Resource** (recursos de imagen); `GOLFSHOT` → nombre interno del modo **ráfaga / high-speed continuous shooting** (modo "golf" = disparo en ráfaga para deportes).

## Las 5 trazas (vaddr → texto corto)

```
0x43ca492f [IMAGING_RSRC]: [GOLFSHOT]SA_LPF Exec[%02d] Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]
0x43ca4984 [IMAGING_RSRC]: [GOLFSHOT]SA_BGEST Exec Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]
0x43ca49d5 [IMAGING_RSRC]: [GOLFSHOT]SA_SSP Exec[%03d] Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]
0x43ca4a2a [IMAGING_RSRC]: [GOLFSHOT] correctSndDetResult(WARNING): Corrected Value is Out of SoundDetBuff
0x43ca4a8a [IMAGING_RSRC]: [GOLFSHOT]vfc2indx: Shot Timing Transform Error
```

## Hallazgos con dirección

- **Doble prefijo**: `[IMAGING_RSRC]: [GOLFSHOT]` — prefijo nuevo `[IMAGING_RSRC]: ` (fw3.21) + prefijo preexistente `[GOLFSHOT]` (A7S/A6300). Longitud total: 29 B (`[IMAGING_RSRC]: [GOLFSHOT]`).
- **Sub-módulos SA (Service Agent)**: 3 agentes SA para pipeline GOLFSHOT:
  - `SA_LPF` (Low-Pass Filter) — filtro paso bajo para imagen
  - `SA_BGEST` (Background Estimation) — estimación de fondo
  - `SA_SSP` (Super-Resolution / Spatial Processing?) — procesamiento espacial/super-resolución
- **Validación de recursos**: `sa_err`, `intfct`, `mbox1` — error codes, interface, mailbox.
- **Sound Detection**: `correctSndDetResult` — corrección de detección de sonido (WARNING si valor fuera de buffer).
- **Timing Transform**: `vfc2indx` — conversión de VFC (Vertical Frame Counter) a índice de disparo; error de transform de timing.
- **Logger dual (patrón S177/S179/S603–S610)**: la fw3.21 **duplica** la traza: nueva con prefijo `[IMAGING_RSRC]: ` + vieja con prefijo `[GOLFSHOT]` vía logger global `0x43902718`.
- **Estructura GOLFSHOT**: en A7S/A6300 existen 70+ trazas `[GOLFSHOT]` + `[ADF]SAN` para secuencia completa (start/stop/analyze, LPF/BGEST/SSP, ALOCK_ERR, FREE_ERR, ADF_START/STOP/ANALYZE, Seq._HSPre/HSEnd/GolfBgest/GolfSsp). La fw3.21 **añade capa `[IMAGING_RSRC]: `** a 5 strings específicas de recursos SA.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[IMAGING_RSRC]` | **5** | **0** | **0** |
| token `[GOLFSHOT]` (mismo núcleo) | **5** (doble prefijo) | **5** | **5** |
| núcleos idénticos (`SA_LPF`, `SA_BGEST`, `SA_SSP`, `correctSndDetResult`, `vfc2indx`) | 5/5 con doble prefijo | **5/5** (prefijo `[GOLFSHOT]`) | **5/5** (prefijo `[GOLFSHOT]`) |
| código equivalente (SA_LPF/BGEST/SSP, vfc2indx) | `0x43ca49xx`… | **sí** | **sí** |

→ **Cambio de *logging*, no de código.** El pipeline GOLFSHOT SA (LPF/BGEST/SSP) **existe igual** en los tres firmware (mismas 5 cadenas núcleo, mismas funciones SA). Lo propio de la fw3.21 de la A6000 son **las 5 trazas con prefijo `[IMAGING_RSRC]: `** y la **duplicación** con logger global (prefijo `[GOLFSHOT]` intacto en A7S/A6300).

**Longitud del prefijo compuesto fija:** 29 B (`[IMAGING_RSRC]: [GOLFSHOT]`) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **recursos SA para pipeline de ráfaga (GOLFSHOT)**, no el obturador per se. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[IMAGING_RSRC]: [GOLFSHOT]...` confirmadas en `0x43ca492f`–`0x43ca4a8a`.
- 5/5 gemelos `[GOLFSHOT]...` confirmados en A7S fw3.20 y A6300 fw2.01 (mismo núcleo).
- 0/0 en A7S y A6300 para token `[IMAGING_RSRC]`.
- Scripts: `analysis/s611_imaging_rsrc/` (pendiente) · Tests: `tests/test_s611_imaging_rsrc.py`.
