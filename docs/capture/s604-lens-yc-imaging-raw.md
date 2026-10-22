# S604 — módulos `[LENS_YC]` (22 trazas) y `[IMAGING_RAW]` (18 trazas): exclusivos de A6000 fw3.21

**Estado: VERIFICADO** — Ambas familias de cadenas existen en A6000 fw3.21 y **0 en A7S fw3.20** y **0 en A6300 fw2.01** (búsqueda literal `strings -a` en los tres `av-cam.bin`).

---

## 1. `[LENS_YC]` — 22 cadenas únicas (REA) / 21 ocurrencias (`strings -a`)

| # | VA | Texto |
|---|---|---|
| 1 | 0x43c9a074 | %s: Open error (0x%x) |
| 2 | 0x43c9a095 | %s: Close error (0x%x) |
| 3 | 0x43c9aed6 | %s: LoadLensAberrationData error (0x%x) |
| 4 | 0x43c9af09 | %s: FreeLensAberrationData error (0x%x) |
| 5 | 0x43c9af3c | %s: AllocLensAberrationData error (0x%x) |
| 6 | 0x43c9b012 | %s: AllocNewWait error (0x%x) |
| 7 | 0x43c9b03b | %s: Alloc error (0x%x) |
| 8 | 0x43c9b05d | %s: Free error (0x%x) |
| 9 | 0x43c9b07e | %s: AsyncSend error (0x%x) |
| 10 | 0x43c9b0a4 | %s: AsyncRecieve error (0x%x) |
| 11 | 0x43c9b0cd | %s: wrong message received |
| 12 | 0x43c9b0f3 | base.msg_code  = 0x%x |
| 13 | 0x43c9b114 | base.option    = 0x%x |
| 14 | 0x43c9b135 | base.prg_num   = 0x%x |
| 15 | 0x43c9b156 | base.timeout   = 0x%x |
| 16 | 0x43c9b177 | base.err_code  = 0x%x |
| 17 | 0x43c9b198 | prg.prg_id     = 0x%x |
| 18 | 0x43c9b1b9 | prg.usr_unq_id = 0x%x |
| 19 | 0x43c9b1da | prg.offset     = 0x%x |
| 20 | 0x43c9b1fb | prg.unit_type  = 0x%x |
| 21 | 0x43c9b21c | %s: Load error (0x%x) |

### Temas funcionales inferidos
- **Ciclo de vida**: Open / Close / Load / Free
- **Aberración del lente**: Carga/liberación/asignación de datos de aberración
- **Memoria**: AllocNewWait, Alloc, Free
- **I/O asíncrono**: AsyncSend, AsyncRecieve
- **Estructura mensaje base**: msg_code, option, prg_num, timeout, err_code
- **Estructura programa**: prg_id, usr_unq_id, offset, unit_type

---

## 2. `[IMAGING_RAW]` — 18 cadenas únicas (REA) / 20 ocurrencias (`strings -a`)

| # | VA | Texto |
|---|---|---|
| 1 | 0x43caa727 | RawMemMgr) DisableSetMode_Unlock Multiple call count:%d |
| 2 | 0x43caa76e | RawMemMgr) Callback Dummy! |
| 3 | 0x43caa7b5 | RawMemMgr) GetMem Warning: Please wait callback. %x |
| 4 | 0x43caa7f8 | RawMemMgr) isMemEmpty State Err: now state. %x |
| 5 | 0x43caa836 | RawMemMgr) FreeRemainingMem State Err: now state. %x |
| 6 | 0x43caa8f0 | RawMemMgr) FreeAll state Error: %d |
| 7 | 0x43caa922 | RawMemMgr) ReserveAll State Err: now state. %x |
| 8 | 0x43caa9d9 | RawMemMgr_MemPool) Wait Alloc |
| 9 | 0x43caaa06 | RawMemMgr_MemPool) Wait Alloc - Comp(%d) |
| 10 | 0x43caaa3e | RawMemMgr_MemPool) AllocArea(MemQue) Dmm Err: type[0x%08x] err[%d] |
| 11 | 0x43caaa90 | RawMemMgr_MemPool) AllocArea(ImgPrm) Dmm Err: err[%d] |
| 12 | 0x43caaad5 | RawMemMgr_MemPool) AllocArea(MemQue) Dmm Err: err[%d] |
| 13 | 0x43caac1e | RawMemMgr_MemQue) Req id:[0x%08x] FrontQue que:[0x%x] Empty! ** |
| 14 | 0x43caac6d | RawMemMgr_MemQue) Req id:[0x%08x] FrontQue que:[0x%x] id:[0x%08x] remain:[%d] ** |
| 15 | 0x43caaccd | RawMemMgr_MemQue: Remaining Queue id:[0x%04x] param:[0x%08x]  ** |
| 16 | 0x43caad1d | RawMemMgr_MemQue: SetMemoryPool Err:[%d] |
| 17 | 0x43caad55 | RawMemMgr_MemQue: Add Que Front Full Err:[0x%04x] param:[0x%08x]  ** |
| 18 | 0x43caada9 | RawMemMgr_MemQue: Add Que Full Err:[0x%04x] param:[0x%08x]  ** |

### Temas funcionales inferidos
- **RawMemMgr**: DisableSetMode_Unlock, Callback Dummy, GetMem, isMemEmpty, FreeRemainingMem, FreeAll, ReserveAll
- **MemPool**: Wait Alloc, AllocArea (MemQue/ImgPrm), DMM errors
- **MemQue**: Req id/FrontQue/Empty/Remaining Queue, SetMemoryPool, Add Que Front/Full

---

## 3. Diferencial A7S fw3.20 / A6300 fw2.01

| Firmware | `[LENS_YC]` | `[IMAGING_RAW]` | Conclusión |
|---|---|---|---|
| A6000 fw3.21 | 22 únicas / 21 totales | 18 únicas / 20 totales | **Módulos presentes** |
| A7S fw3.20 | 0 | 0 | **Ausentes** |
| A6300 fw2.01 | 0 | 0 | **Ausentes** |

**Verificación:** `strings -a` literal en los tres `av-cam.bin` (SHA256 distintos). REA `search_strings` en A6000 confirma 22 + 18 cadenas únicas.

---

## 4. Evidencia y reproducibilidad

- **JSON + test:** `analysis/s604_lens_yc_imaging_raw/`
  - `lens_yc_imaging_raw.json` — catálogo completo
  - `test_lens_yc_imaging_raw_exclusivity.py` — test automatizado (6 asserts)
- **Herramientas:** REA (MCP `search_strings`) + `strings -a` / `grep` como control positivo.
- **Binario:** `av-cam.bin` A6000 fw3.21 (SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).

---

## 5. Límites / NO_VERIFICADO

- **No se realizó decompilación** ni análisis de xrefs para estos módulos (time-boxed).
- Nombres de archivo fuente no recuperados.
- Semántica de Lens Aberration, RawMemMgr, MemPool, MemQue inferida de formato de trazas.
- No se probó alcance en runtime (sin firmware ejecutado).
- La ausencia en A7S/A6300 es **estática**; no prueba incapacidad de hardware.

---

## 6. Conclusión para la línea del obturador electrónico

**Sin efecto directo en S51 (A/B/C = NO).**
- `[LENS_YC]`: Comunicación con lente (abertura, aberración cromática, datos de programa) y I/O asíncrono.
- `[IMAGING_RAW]`: Gestor de memoria raw (RawMemMgr) con pools, colas, DMM, estados de reserva/liberación.
- Ninguno menciona `shutter`, `silent`, `electronic`, `EFCS`, `curtain`, `mechanical`, `flicker`.

---

**Próximo:** S605 — regenerar cola con siguientes módulos pendientes del censo S178 (priorizar exclusivos A6000).