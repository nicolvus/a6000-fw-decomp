# S177 — `[CAM_FUNC_MGR]`: el gestor de funciones de cámara (`Camera::Function`)

**43 trazas · 57 sitios (regla PIC estricta) · 25 funciones · 18 clases RTTI · tabla de 65
funciones.** Detalle + datos: `analysis/s177_cam_func_mgr/cam_func_mgr.md` / `.json`.

## Qué es
`[CAM_FUNC_MGR]` es la etiqueta de traza del subsistema **`Camera::Function`** de la A6000
fw3.21: un **gestor/despachador de funciones de cámara** (`Capcon` = capture controller) que
implementa el ciclo de vida de peticiones y respuestas, las enruta entre los cuatro clientes
(`CamUser`, `CameraBackGround`, `Release`, `CamMain`) y las traduce al bus inter-LSI mediante el **puente `LRBridge`**. Base textual: **18 clases RTTI** `N6Camera8Function…` (idénticas en las tres fw) y **18 ficheros fuente**; las siglas `CAM_FUNC_MGR`/`MGR`/`LRB`/`Capcon` no se expanden en ninguna cadena (NO VERIF.).

## Las 43 trazas (vaddr → texto corto; sitio y función en `cam_func_mgr.md`)
```
0x43ca12af CAPCON WARNING  0x43ca12f6 SyncProcMargin  0x43caefe8 ERROR osal_err (12)
0x43caf036 Invalid CapMode  0x43caf077 receive before comp  0x43caf0b4 (FAILED)
0x43caf136 ERROR osalErr (4)  0x43caf17d LSI_NUM_TYPE  0x43caf1b3 UNKNOWN EID
0x43caf1e9 ERROR type  0x43caf648 LRBridge SndV2ndLatchCmp  0x43caf684 LRBridge SndApp2Cmp
0x43caf219..0x43caf5f3 [LRB] *Snd (12) y 0x43caf6bb..0x43cafa95 [LRB] *Rsv (12): REQ_APP_SND,
  APP, APP_CMP, REQ_VSYNC_CUST_SND, VSYNC_CUST, VSYNC_CUST_CMP, REQ_V2ND_SND, V2ND, V2ND_CMP,
  REQ_FSPSUM_SND, FSPSUM, FSPSUM_CMP
0x43cb009b Unexpected ExpFocusTransition  0x43cb010a Unexpected SleepTransition
0x43cb0150 unknown msg in Imager Sleep Process  0x43cb027c Execute unretract command
0x43cb02ad IsNeedScanAf  0x43cb02cf IsNeedAe  0x43cb02f1 Pseudo AF Stop ← MUERTA
```

## Hallazgos con dirección
- **Tabla de funciones**: 65 entradas `{const char *origin; const char *name; u32 id;}` en
  `0x43ff17b8` (paso 12 B). `origin` = `FUNC <= USER` (26), `FUNC <= BG  ` (3),
  `FUNC <= REL ` (7), `FUNC <= CAM ` (27), `???` (2) → **quién puede emitir cada función**;
  `origin` se escribe en runtime por la init `0x43787d88`.
- **12 `type_id` del LRB** (cmp en `0x43805ec0`…`0x43806126`): 0 `REQ_APP_SND`, 1 `APP`,
  2 `APP_CMP`, 3 `REQ_V2ND_SND`, 4 `V2ND`, 5 `V2ND_CMP`, 6 `REQ_VSYNC_CUST_SND`,
  7 `VSYNC_CUST`, 8 `VSYNC_CUST_CMP`, 9 `REQ_FSPSUM_SND`, 10 `FSPSUM`, 11 `FSPSUM_CMP`.
- **Despachador** `0x43805930`: tipo u16 en `[msg+2]`, `sub #0x3000` + `tbb` de 49 casos
  (`0x438059a2`) → bus `0x3000`–`0x3030`. **Traza nueva**: 7 wrappers por fichero
  (`0x43787ac4`…`0x43809a64`) con **id de módulo `3`**, **nivel `0xd`**, fichero y línea.

## Diferencial
| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_FUNC_MGR]` / textos interiores | **43** / — | **0** / **43/43** | **0** / **42/43** |
| clases RTTI `Camera::Function::*` | 18 | 18 | 18 |
| tabla de 65 funciones | `0x43ff17b8` | `0x43ff65d4` (idéntica) | **no existe** |
| LRB *Snd* / traza antigua | `0x43805ea8` / `0x43902718` | `0x437ac620` / `0x438f7114` | `0x437f6200` / `0x43986518` |

→ **Cambio de *logging*, no de código.** En las 43 cadenas los bytes en `vaddr+16` son el
literal **sin** el prefijo `"[CAM_FUNC_MGR]: "` (16 B), texto que ya existía en la A7S
(43/43) y en el A6300 (42/43). La fw3.21 **duplica** la traza: la nueva (`bl` al wrapper del
fichero, módulo 3) y la antigua (`bl 0x43902718` → `vaddr+16`), intacta; ejemplo `0x43805ed6`
(A6000) vs `0x437ac63e` (A7S). La tabla de funciones **no existe en el A6300 fw2.01**
(0 `REPLY_`, 0 `MSG_NONE`, 0 `FUNC <= `).

## Obturador y verificación
**Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`expos`/`iso`/`apert`/`sensor`/`shut`/`svd`/`frame` en las 43 trazas. Gestiona **órdenes de alto nivel** (`REQ_CAPTURE_START/END`, `REQ_AF_START/STOP`, `REQ_AE_START/STOP`, `REQ_MOVIE`, `REQ_TOUCH_SCAN`, `RAW_CONT_CAP_CANCEL`) pero **no baja al nivel del obturador**; `unretract` (`0x43cb027c`) es del obturador **mecánico**. **S51 A/B/C = NO.** **57/57** pares PIC verificados a mano (pool, `destino = literal + (add+4)`, sin reuso de registro). Scripts: `analysis/s177_cam_func_mgr/` · Tests: `tests/test_s177_cam_func_mgr.py`.
