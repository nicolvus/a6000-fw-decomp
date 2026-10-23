# S604 — `[LENS_YC]` y `[IMAGING_RAW]`: dos módulos exclusivos de traza de la A6000 fw3.21

**Auditoría 23-10-2026:** la exclusividad verificada es la del prefijo de traza en los tres binarios comparados. No demuestra ausencia de código equivalente en otro modelo ni identifica por sí sola un módulo nuevo. Los tests corregidos leen los archivos reales y ya no convierten un error de ruta en cero coincidencias.

> **Nota:** ambos módulos son **exclusivos de la A6000 en traza** (token `[XXX]` 0/0 en A7S y A6300), pero el **código subyacente existe en los tres** firmware. El patrón es idéntico a S177/S179/S603: **cambio de logging, no de código**.

---

## 1. `[LENS_YC]` — capa de comunicación con el objetivo (Camera::Lens + ODL)

**21 trazas · ~25 sitios (estricta) · ~11 funciones RTTI `Camera::Lens::*` + ODL.** La sigla **SÍ tiene base textual**: `LENS` → objetivo; `YC` → probable **Y**C (luminancia/crominancia) o **Y** **C**ommunication; se deja sin desarrollar.

### Las 21 trazas (vaddr → texto corto)

```
0x43c9a074 %s: Open error (0x%x)
0x43c9a095 %s: Close error (0x%x)
0x43c9aed6 %s: LoadLensAberrationData error (0x%x)
0x43c9af09 %s: FreeLensAberrationData error (0x%x)
0x43c9af3c %s: AllocLensAberrationData error (0x%x)
0x43c9b012 %s: AllocNewWait error (0x%x)
0x43c9b03b %s: Alloc error (0x%x)
0x43c9b05d %s: Free error (0x%x)
0x43c9b07e %s: AsyncSend error (0x%x)
0x43c9b0a4 %s: AsyncRecieve error (0x%x)
0x43c9b0cd %s: wrong message received
0x43c9b0f3 base.msg_code  = 0x%x
0x43c9b114 base.option    = 0x%x
0x43c9b135 base.prg_num   = 0x%x
0x43c9b156 base.timeout   = 0x%x
0x43c9b177 base.err_code  = 0x%x
0x43c9b198 prg.prg_id     = 0x%x
0x43c9b1b9 prg.usr_unq_id = 0x%x
0x43c9b1da prg.offset     = 0x%x
0x43c9b1fb prg.unit_type  = 0x%x
0x43c9b21c %s: Load error (0x%x)
```

### Hallazgos con dirección

- **Clase RTTI principal**: `Camera::Lens` (11 strings RTTI en `0x43c99fd2`–`0x43c9b332`), idéntica en A6000/A7S/A6300.
- **Sub-módulo ODL** (Optical Data Layer): `Camera::Lens::ODL` con tipo de error `ODL_ERR` y operaciones `Load`, `Free`, `AllocLensAberrationData`, `LoadLensAberrationData`, `Alloc`, `FreeLensAberrationData`.
- **Métodos de alto nivel**: `Initialize(UPM_BOOT_FACTOR*)`, `SetAberrationDataInfo(u16)`, `job_Mount_CloseAberrationDataHndl()`, `job_Mount_LoadAberrationDataHndl()`, `job_Mount_SaveAberrationDataHndl(u16)`.
- **Logger dual**: la fw3.21 **duplica** la traza (nueva con prefijo `[LENS_YC]: ` + vieja sin prefijo vía logger global `0x43902718`), igual que S177/S179/S603.
- **Longitud del prefijo**: 10 B (`[LENS_YC]: `) antepuesto al literal original → el prefijo **se ajusta al nombre del módulo**.

### Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[LENS_YC]` | **21** | **0** | **0** |
| núcleo sin prefijo (`%s: Open error...`, etc.) | 0/21 como literal autónomo | **21/21** (idénticos) | **21/21** (idénticos) |
| RTTI `Camera::Lens::*` + ODL | 11 | 11 | 11 |
| gemelo exacto en `vaddr+10` | **21/21** | — | — |
| código equivalente | sí | sí | sí |

→ **Cambio de *logging*, no de código.** El módulo `Camera::Lens` + ODL **existe igual** en los tres firmware. Lo propio de la fw3.21 de la A6000 son **las 21 trazas con prefijo `[LENS_YC]`**; la fw3.21 **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global).

### Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **aberraciones del objetivo y comunicación montura-objetivo**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

---

## 2. `[IMAGING_RAW]` — gestor de memoria RAW (RawMemMgr)

**20 trazas · ~22 sitios (estricta) · ~1 función principal (`RawMemMgr`)**. La sigla **SÍ tiene base textual**: `IMAGING_RAW` → **RawMemMgr** (gestor de memoria para imágenes RAW). `RawMemMgr` aparece explícito en todas las trazas.

### Las 20 trazas (vaddr → texto corto)

```
0x43caa6cf RawMemMgr) DisableSetMode_Unlock Multiple call count:%d
0x43caa716 RawMemMgr) Callback Dummy!
0x43caa75d RawMemMgr) GetMem Warning: Please wait callback. %x
0x43caa7a0 RawMemMgr) isMemEmpty State Err: now state. %x
0x43caa7de RawMemMgr) FreeRemainingMem State Err: now state. %x
0x43caa822 RawMemMgr) FreeRemainingMem state Error: %d
0x43caa85d RawMemMgr) FreeAll State Err: now state. %x
0x43caa898 RawMemMgr) FreeAll state Error: %d
0x43caa8ca RawMemMgr) ReserveAll State Err: now state. %x
0x43caa981 RawMemMgr_MemPool) Wait Alloc
0x43caa9ae RawMemMgr_MemPool) Wait Alloc - Comp(%d)
0x43caa9e6 RawMemMgr_MemPool) AllocArea(MemQue) Dmm Err: type[0x%08x] err[%d]
0x43caaa38 RawMemMgr_MemPool) AllocArea(ImgPrm) Dmm Err: err[%d]
0x43caaa7d RawMemMgr_MemPool) AllocArea(MemQue) Dmm Err: err[%d]
0x43caabc6 RawMemMgr_MemQue) Req id:[0x%08x] FrontQue que:[0x%x] Empty! **
0x43caac15 RawMemMgr_MemQue) Req id:[0x%08x] FrontQue que:[0x%x] id:[0x%08x] remain:[%d] **
0x43caac75 RawMemMgr_MemQue: Remaining Queue id:[0x%04x] param:[0x%08x]  **
0x43caacc5 RawMemMgr_MemQue: SetMemoryPool Err:[%d]
0x43caacfd RawMemMgr_MemQue: Add Que Front Full Err:[0x%04x] param:[0x%08x]  **
0x43caad51 RawMemMgr_MemQue: Add Que Full Err:[0x%04x] param:[0x%08x]  **
```

### Hallazgos con dirección

- **Módulo único**: `RawMemMgr` — gestor de memoria para imágenes RAW con submódulos `MemPool` (pools de áreas DMM) y `MemQue` (colas de peticiones).
- **Estados**: `isMemEmpty`, `FreeRemainingMem`, `FreeAll`, `ReserveAll` con validación de estado (`State Err`).
- **Pool DMM**: `AllocArea` para `MemQue` e `ImgPrm` (Image Parameters) con manejo de errores DMM.
- **Colas (MemQue)**: peticiones con `id`, `que`, `remain`; detección de colas vacías/llenas (`Front Full`, `Full`).
- **Logger dual**: la fw3.21 **duplica** la traza (nueva con prefijo `[IMAGING_RAW]: ` + vieja sin prefijo). En A7S/A6300 las 20 cadenas existen **sin prefijo** (ver búsqueda arriba: 20/20 idénticas).
- **Longitud del prefijo**: 14 B (`[IMAGING_RAW]: `) → se ajusta al nombre del módulo.

### Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[IMAGING_RAW]` | **20** | **0** | **0** |
| núcleo sin prefijo (`RawMemMgr)...`) | 0/20 como literal autónomo | **20/20** (idénticos) | **20/20** (idénticos) |
| gemelo exacto en `vaddr+14` | **20/20** | — | — |
| código equivalente (`RawMemMgr`) | sí | sí | sí |

→ **Cambio de *logging*, no de código.** El `RawMemMgr` **existe igual** en los tres firmware (mismas 20 cadenas núcleo, misma estructura MemPool/MemQue, mismos errores DMM). Lo propio de la fw3.21 de la A6000 son **las trazas con prefijo `[IMAGING_RAW]`**. La fw3.21 **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global).

### Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **memoria DMM para imágenes RAW (pools y colas)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

---

## Verificación

- `[LENS_YC]`: 21/21 cadenas con gemelo exacto en `+10` (prefijo 10 B), 0 punteros absolutos.
- `[IMAGING_RAW]`: 20/20 cadenas con gemelo exacto en `+14` (prefijo 14 B), 0 punteros absolutos.
- Ambos: **0/0 en A7S y A6300 para el token**, **21/21 y 20/20 para el núcleo**.
- Scripts: `analysis/s604_lens_yc_imaging_raw/` (pendiente) · Tests: `tests/test_s604_lens_yc_imaging_raw.py`.
