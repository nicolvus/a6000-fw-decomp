# S600 — módulo `[CAM_FUNC_MGR]` (43 trazas): exclusivo de A6000 fw3.21

**Auditoría 23-10-2026:** la exclusividad verificada es la del prefijo de traza en los tres binarios comparados. No demuestra ausencia de código equivalente en otro modelo ni identifica por sí sola un módulo nuevo. Los tests corregidos leen los archivos reales y ya no convierten un error de ruta en cero coincidencias.

**Estado: VERIFICADO** — 36 cadenas únicas (REA `search_strings`) / 43 ocurrencias totales (`strings -a`) con el prefijo `[CAM_FUNC_MGR]` en la A6000 fw3.21; **0 en A7S fw3.20** y **0 en A6300 fw2.01** (búsqueda literal en los tres `av-cam.bin`).

---

## 1. Censo de trazas (36 únicas, direcciones virtuales base 0x43000000)

| # | VA | Texto (truncado) |
|---|---|---|
| 1 | 0x43ca1307 | CAPCON WARNING! FILE:%s LINE=%d func:%s param=%x %x %x |
| 2 | 0x43ca134e | SyncProcMargin[usec] HS0:%u HS1:%u HS2:%u HS3@CPU2:%u HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u VDDrive:%u VDPost:%u |
| 3 | 0x43caf040 | ERROR !!! osal_err:0x%04x %s : %d |
| 4 | 0x43caf08e | SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d] |
| 5 | 0x43caf0cf | receive[%d,%d] before comp[%d,%d] (QUEUEING) |
| 6 | 0x43caf10c | receive[%d,%d] before comp[%d,%d] (FAILED) |
| 7 | 0x43caf18e | ERROR !!! osalErr:0x%04x %s : %d |
| 8 | 0x43caf1d5 | ERROR !!! LSI_NUM_TYPE:0x%04x %s : %d |
| 9 | 0x43caf20b | UNKNOWN EID !!! type:[0x%02x] %s : %d |
| 10 | 0x43caf241 | ERROR !!! type:[0x%02x] %s : %d |
| 11 | 0x43caf271 | [LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 12 | 0x43caf2c7 | [LRB]APP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 13 | 0x43caf315 | [LRB]APP_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 14 | 0x43caf367 | [LRB]REQ_VSYNC_CUST_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x |
| 15 | 0x43caf43d | [LRB]VSYNC_CUST_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x |
| 16 | 0x43caf4ff | [LRB]V2ND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 17 | 0x43caf5a1 | [LRB]REQ_FSPSUM_SND Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 18 | 0x43caf64b | [LRB]FSPSUM_CMP Snd type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 19 | 0x43caf6a0 | ERROR !!! LRBridge SndV2ndLatchCmp. %s : %d |
| 20 | 0x43caf6dc | ERROR !!! LRBridge SndApp2Cmp. %s : %d |
| 21 | 0x43caf713 | [LRB]REQ_APP_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 22 | 0x43caf769 | [LRB]APP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 23 | 0x43caf7b7 | [LRB]APP_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 24 | 0x43caf809 | [LRB]REQ_VSYNC_CUST_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x |
| 25 | 0x43caf8df | [LRB]VSYNC_CUST_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x |
| 26 | 0x43caf9a1 | [LRB]V2ND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 27 | 0x43cafa43 | [LRB]REQ_FSPSUM_SND Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 28 | 0x43cafaed | [LRB]FSPSUM_CMP Rsv type_id:0x%02x from_lsi:0x%02x req_seq_id:0x%02x |
| 29 | 0x43cb00f3 | Unexpected ExpFocusTransition : message [%x] timing [%d] |
| 30 | 0x43cb0162 | Unexpected SleepTransition : message [%x] timing [%d] |
| 31 | 0x43cb01a8 | unknown message in Imager Sleep Process: %x |
| 32 | 0x43cb0305 | IsNeedScanAf (%d) |
| 33 | 0x43cb0327 | IsNeedAe     (%d) |
| 34 | 0x43cb0349 | Pseudo AF Stop %d |

*(Las 7 ocurrencias extra de `strings -a` son duplicados/parciales de las mismas 36 cadenas únicas definidas en Ghidra.)*

---

## 2. Funciones emisoras (REA `xrefs` + `procedure_pseudo_code`)

| VA | Función (Ghidra) | Rol | Trazas emitidas |
|---|---|---|---|
| 0x43787bc8 | `FUN_43787bc8` | Logger `CAPCON WARNING` (7 parámetros) | #1 |
| 0x43803e84 | `FUN_43803e84` | **SetCapMode handler** — valida `CapMode` | #4 |
| 0x43804010 | `FUN_43804010` | **Request queueing (Snd)** — slot en `obj+0x26` | #5, #6 |
| 0x43805860 | `FUN_43805860` | Logger error OSAL | #3 |
| 0x438058c8 | `FUN_438058c8` | **Message send (Snd)** — `osal_try_valloc_msg`/`osal_snd_msg` | #3, #7 (dual) |
| 0x43805f00 | `FUN_43805f00` | **LRB dispatcher (Snd)** — 12 tipos 0x00–0x0b | #11–#18 |
| 0x4380621c | `FUN_4380621c` | Handler → llama `FUN_43805f00` | #11, #12 (vía DAT_438062c4) |
| 0x43806458 | `FUN_43806458` | Handler → llama `FUN_43805f00` | #13, #14 (vía DAT_43806500) |
| 0x43806520 | `FUN_43806520` | Handler → llama `FUN_43805f00` | #15–#18 (vía DAT_438065c8) |
| 0x438065e8 | `FUN_438065e8` | Envía **REQ_APP_SND** (tipo 0x0b) | #19 |
| 0x43806654 | `FUN_43806654` | Envía **APP_SND** (tipo 0x05) | #20 |
| 0x438066c0 | `FUN_438066c0` | Envía **APP_SND** (tipo 0x02) | #20 |
| 0x4380672c | `FUN_4380672c` | **LRB dispatcher (Rsv)** — 12 tipos 0x00–0x0b | #21–#28 |
| 0x43809d78 | `FUN_43809d78` | Predicados AF/AE | #32, #33 |
| 0x43809d9a | (mismo cuerpo) | — | #32, #33 |

---

## 3. Estructuras y protocolos inferidos

### 3.1 LRB = Link Bridge (mensajería inter-LSI)
- **Snd** = Send (envío de petición)
- **Rsv** = Reserve/Response (respuesta/completación)
- 12 tipos de mensaje (0x00–0x0b):
  - 0x00 `REQ_APP`, 0x01 `APP`, 0x02 `APP_CMP`
  - 0x03 `REQ_VSYNC_CUST`, 0x04 `VSYNC_CUST`, 0x05 `VSYNC_CUST_CMP`
  - 0x06 `REQ_V2ND`, 0x07 `V2ND`, 0x08 `V2ND_CMP`
  - 0x09 `REQ_FSPSUM`, 0x0a `FSPSUM`, 0x0b `FSPSUM_CMP`

### 3.2 Habilitación por bitmask (en objeto apuntado por `DAT_438061b4 + DAT_438061b8`)
| Offset | Bits | Tipos cubiertos |
|---|---|---|
| +0x41 | 1,2,4 | 0x00, 0x01, 0x02, 0x09, 0x0a, 0x0b |
| +0x44 | 1,2,4 | 0x06, 0x07, 0x08 |
| +0x46 | 1,2,4 | 0x03, 0x04, 0x05 |

### 3.3 Contador de secuencia
- En `param_1 + 0x57a` (incrementado en cada `Snd`).

### 3.4 OSAL (cola de mensajes)
- `osal_try_valloc_msg` 0x435612d0
- `osal_snd_msg` 0x4356120c
- `osal_rcv_msg` 0x43561260
- `osal_free_msg` 0x435612ec

---

## 4. Manejo de `CapMode` (en `FUN_43803e84`)

| CapMode | Acción |
|---|---|
| 0x19 (25) | Ruta especial: `FUN_4372a538(0)`, `FUN_4372a65c(0x1a)` |
| 0x17 (23) | `param_1+0xa = 1` |
| 0x1c (28) | `param_1+0xc=2, +0xd=0, +0xe=0, +0xf=0` |
| 0x03 (3) | `param_1+0xc=3, +0xd=0, +0xe=0, +0xf=0` |
| Otros (0x00–0x1d, bitmask `DAT_43803ff0`) | Path normal vía `FUN_43803dd8` + `FUN_43902770` |
| Fuera de rango / bitmask 0 | Error `0xf000`, guarda parámetros en globals `DAT_43804008+0xfc..` |

---

## 5. Diferencial A7S fw3.20 / A6300 fw2.01

| Firmware | Cadenas `[CAM_FUNC_MGR]` | Conclusión |
|---|---|---|
| A6000 fw3.21 | 36 únicas / 43 totales | **Módulo presente** |
| A7S fw3.20 | 0 | **Ausente** |
| A6300 fw2.01 | 0 | **Ausente** |

**Verificación:** `strings -a` literal en los tres `av-cam.bin` (SHA256 distintos). REA `search_strings` en A6000 confirma 36 cadenas únicas con xrefs válidas.

---

## 6. Evidencia y reproducibilidad

- **JSON + tests:** `analysis/s600_cam_func_mgr/`
  - `cam_func_mgr.json` — catálogo completo
  - `test_cam_func_mgr_exclusivity.py` — test automatizado (3 asserts)
- **Herramientas:** REA (MCP `search_strings`, `xrefs`, `procedure_pseudo_code`) + `strings -a` / `grep` como control positivo.
- **Binario:** `av-cam.bin` A6000 fw3.21 (SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`).

---

## 7. Límites / NO_VERIFICADO

- Nombres de función son auto-generados por Ghidra (`FUN_...`); no se recuperaron nombres de archivo fuente (`.cpp`).
- Semántica exacta de `CapMode` 0x19/0x17/0x1c/0x03 no mapeada a modos de captura públicos.
- LRB = "Link Bridge" es inferencia a partir de `Snd`/`Rsv` y `from_lsi`/`req_seq_id`; no confirmado en símbolos.
- No se probó alcance en runtime (sin firmware ejecutado).
- La ausencia en A7S/A6300 es **estática**; no prueba que el hardware no pueda soportar la funcionalidad.

---

## 8. Conclusión para la línea del obturador electrónico

**Sin efecto directo en S51 (A/B/C = NO).** El módulo gestiona **funciones de cámara** (cambio de modo de captura, mensajería inter-LSI, sincronismo HS/VD, AF/AE) pero **no menciona** `shutter`, `silent`, `electronic`, `EFCS`, `curtain`, `mechanical`, `flicker`. Es un módulo de **control/orquestación** exclusivo de la A6000 fw3.21, probablemente introducido por la reorganización de logging (S128: 18 módulos `RENOMBRADO`, 20 `NUEVO/PROPIO`).

---

**Próximo:** S601 — decodificar `[CAM_SCALAR]` (34 trazas), exclusivo A6000.
