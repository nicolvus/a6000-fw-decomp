# S125 — los módulos de trazas `[IMAGING_REL]` (31) y `[IMAGING]` (120) de la A6000 fw3.21

> Hito de la **línea de ingeniería inversa general** (no afecta a S51: A/B/C = NO).
> Solo análisis de bytes sobre `analysis/rea-independent/input/av-cam.bin` (11 427 236 B);
> convención **vaddr = 0x43541000 + file_offset** (verificada).
> Reproducir: `analysis/s125_imaging_rel/scan_imaging_modules.py A6000|A7S|A6300`,
> `build_diff.py`, `build_report_json.py`.

## 1. Resumen

Los dos módulos "menores" que quedaban sin decodificar en la zona del gestor de captura son,
en realidad, **dos cosas muy distintas**:

| módulo | trazas | qué es | código |
|---|---|---|---|
| `[IMAGING_REL]` | **31** | la clase **`Camera::ReleaseLock`** (VERIFICADO por los nombres RTTI del firmware): el gestor de "release" (pulsación del disparador) con su tabla de *capture-ids*, su cola y su *lock* | `0x4379d114`–`0x4379e600` y `0x4381c30c`–`0x4381d150` |
| `[IMAGING]` | **120** | el **subsistema de panorama / stitching** (`still_cnt_panoramaSweep.cpp`, `still_seq_panoramaStitch.cpp`, `still_cnt_panoramaStitch.cpp`, `src/stitch/ddl_stitch.cpp`, `src/srotate/ddl_srotate.cpp`…) **más** el macro genérico `FATAL!` de todo el subsistema de captura | `0x43549020`, `0x43780xxx`, `0x437e6xxx`–`0x437e99xx`, `0x438b8xxx`–`0x438bdxxx` |

Cifras (todas con la **regla PIC estricta** canónica, ver §2):

| | `[IMAGING_REL]` | `[IMAGING]` |
|---|---|---|
| cadenas | **31** (`0x43c9c520`–`0x43cb4bc4`) | **120** (`0x43c9b47c`–`0x43cc6c99`) |
| con referencia | 30 (1 muerta) | 82 (**38 muertas**) |
| sitios PIC | **34** | **608** |
| funciones emisoras | **26** | **346** |
| mensajes genéricos (`FATAL!`) | 0 | 3 (473 de los 608 sitios) |
| mensajes específicos | 31 (34 sitios, 26 funciones) | 117 (135 sitios, 24 funciones) |

**Respuesta a la pregunta del hito:** `REL` **no** es una invención: el firmware lleva la clase
C++ `Camera::ReleaseLock` en sus nombres RTTI (`RelLockS1`, `RelLockBase`, `RelLockS2`,
`RingQueue<…>`, `Queue<…>`), y "REL" = **RELease**. Y `[IMAGING]` no es un "módulo Imaging"
genérico: su parte específica es el motor de **panorama/stitch**, y el resto es el macro
`FATAL! %s:%d` que en la fw3.21 de la A6000 pasó a llevar la etiqueta `[IMAGING]: `.

## 2. Método (VERIFICADO)

- **Extracción de cadenas**: byte a byte sobre el blob, cadenas terminadas en NUL (se aceptan
  bytes de control dentro del literal: `[IMAGING]: %s:%d \n` `0x43cabafb` lleva un `0x0A`).
  Recuento coincidente con el número de apariciones del token en el binario:
  `[IMAGING_REL]` → 31 apariciones, `[IMAGING]:` → 120, `[IMAGING_CAP]:` → 697.
- **Referencias**: esquema PIC, **regla estricta** canónica
  (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`): cada `add rX,pc` se empareja con el
  `ldr rX,[pc,#imm]` **más cercano por detrás** del mismo registro (ventana 4 KB) y solo se
  aceptan destinos en el **inicio** de una cadena. **Toda cifra de sitios de este informe usa
  esta regla.**
- **Funciones**: prólogo Thumb `push {..,lr}` más cercano por detrás (máx. 16 KB).
- **Fichero fuente**: literal `__FILE__` (`.cpp`/`.h`) referenciado dentro de la función.
- **Verificaciones a mano** (no automáticas): `0x4381c354 ldr r3,[pc,#0x30]` (pool
  `0x4381c388`, W=`0x4981ef`) + `0x4381c356 add r3,pc` → `0x43cb4549`;
  `0x43792a5c ldr r3,[pc,#0x1f8]` (pool `0x43792c54`, W=`0x510e1f`) + `0x43792a64 add r3,pc`
  → `0x43ca3887`; `0x4379d142 ldr r3,[pc,#0x34]` (pool `0x4379d178`, W=`0x5081cb`) +
  `0x4379d14a add r3,pc` → `0x43ca5319`.
- **Llamadores**: barrido `bl`/`blx` con Capstone sobre `0x43541000`–`0x43a00000`
  (`analysis/s125_imaging_rel/bl_callers.json`).
- **Equivalencia de convenciones (comprobada)**: el escáner canónico
  (`scan_pic_refs_strict.py`) acepta destinos en el inicio de una *runa imprimible*, y el de
  este hito acepta cadenas que empiezan justo tras un NUL. Con el **mismo** par
  `ldr`/`add`, ambos dan **17 525 destinos** en total y **exactamente los mismos** sitios para
  estos dos módulos (`[IMAGING_REL]`: 30 referenciadas / 34 sitios; `[IMAGING]`: 82 / 608), con
  **0 diferencias**. Las cifras de este informe son por tanto canónicas.

## 3. `[IMAGING_REL]` — la clase `Camera::ReleaseLock`

### 3.1 Qué es (VERIFICADO)

La sigla **REL = RELease** está **expandida por el propio firmware**: junto a las cadenas del
módulo hay nombres RTTI de C++ (mangling Itanium):

| vaddr | nombre RTTI | clase |
|---|---|---|
| `0x43ca5483` | `N6Camera11ReleaseLock9RelLockS1E` | `Camera::ReleaseLock::RelLockS1` |
| `0x43ca54a4` | `N6Camera11ReleaseLock11RelLockBaseE` | `Camera::ReleaseLock::RelLockBase` |
| `0x43cb4b5f` | `N6Camera11ReleaseLock9RelLockS2E` | `Camera::ReleaseLock::RelLockS2` |
| `0x43cb4810` | `N6Camera11ReleaseLock9RingQueueINS0_7Wrapper10msg_headerELi10EEE` | `Camera::ReleaseLock::RingQueue<Wrapper::msg_header,10>` |
| `0x43cb4889` | `N6Camera11ReleaseLock9RingQueueIjLi10EEE` | `Camera::ReleaseLock::RingQueue<unsigned,10>` |
| `0x43cb4851` | `N6Camera11ReleaseLock5QueueINS0_7Wrapper10msg_headerEEE` | `Camera::ReleaseLock::Queue<Wrapper::msg_header>` |
| `0x43cb48b2` | `N6Camera11ReleaseLock5QueueIjEE` | `Camera::ReleaseLock::Queue<unsigned>` |

En el mismo entorno: `N6Camera8Function18ExecReleaseHandlerE` (`0x43cafdd8`) =
`Camera::Function::ExecReleaseHandler` (fichero `ExecReleaseHandler.cpp`) y
`N6Camera8Function7ReleaseE` (`0x43cb03f4`) = `Camera::Function::Release`.

El fichero fuente del módulo es **`Spinal.cpp`** (`0x43c9c54f`), referenciado por el código en
`0x4372a9ae`/`0x4372a9fc` (función `0x4372a98c`). "Spinal" aparece además en
`EV SendSpinalON:LIROSeq` (`0x43ca3c7b`), `EV SetCamParam:LIROSeq` (`0x43ca3c9b`),
`EV SendEEStart:LIROSeq` (`0x43ca3cf3`), `EV EEComp:LIROSeq` (`0x43ca3d05`) y en
`[MechaCommon] LCParam Driver : %d, Temp : %d, Spinal : %d` (`0x43cb626b`).
(`LIRO` es el nombre con el que el repo designa el programa `av-cam.bin`; ver
`docs/capture/silent-shutter-status.md` y `docs/capture/tasks/_common.md`.)

### 3.2 Inventario y mapa función → traza

`[IMAGING_REL]` = 31 cadenas, 5 zonas en `.rodata`, 30 referenciadas, **34 sitios PIC**,
**26 funciones emisoras**. 24 de las 26 funciones tienen **1** traza cada una; las dos
excepciones son `RelQueue` (4 trazas × 2 funciones) y `CapIdTblMgrIf` (8 trazas × 1 función).

| sub-bloque | n | cadenas (vaddr) | función(es) | fichero |
|---|---|---|---|---|
| `RelKey)` | 1 | `0x43ca5319` | `0x4379d114` | — |
| `IsNeedForceS1ON` | 1 | `0x43ca533b` | `0x4379d37a` | — |
| `REL_EVT` | 2 | `0x43ca5377`, `0x43ca53ba` | `0x4379d83a` | — |
| `RelMgr)` | 3 | `0x43ca53e0`, `0x43ca541d`, `0x43ca5450` | `0x4379e354`, `0x4379e3a8`, `0x4379e500` | — |
| `NotifyEEStartEnable` | 1 | `0x43cafd53` | `0x43807488` | `ExecModeHandler.cpp` |
| `CapIdTblMgr)` | 7 | `0x43cb4549`–`0x43cb47aa` | `0x4381c30c`, `0x4381c39c`, `0x4381c448`, `0x4381c4e0`, `0x4381c568`, `0x4381c62a`, `0x4381c6cc` | — |
| `RelQueue)` | 4 | `0x43cb48d2`–`0x43cb4979` | `0x4381c93c`, `0x4381c98c`, `0x4381c9e0`, `0x4381ca38` (Pop/Push) y `0x4381ca90`, `0x4381cadc`, `0x4381cb2c`, `0x4381cb7c` | — |
| `CapIdTblMgrIf)` | 8 | `0x43cb49b0`–`0x43cb4b21` | `0x4381cc7c` | — |
| `RelLock)` | 1 | `0x43cb4b80` | `0x4381d088` | — |
| `NoMprCap` | 1 | `0x43cb4bc4` | `0x4381d114` | — |
| `SyncTask` | 1 | `0x43ca3887` | `0x43792a0c` | `SyncTask.cpp` |
| `Spinal)` (muerta) | 1 | `0x43c9c520` | — | — |

Detalle de las 31 cadenas (texto íntegro, sitio PIC y función):

| vaddr | texto | sitios | función |
|---|---|---|---|
| `0x43c9c520` | `[IMAGING_REL]: Spinal) osal_free_timer: err %x` | **0** | — |
| `0x43ca3887` | `[IMAGING_REL]: (%d,%d,%d)` | 1 (`0x43792a64`) | `0x43792a0c` (`SyncTask.cpp`) |
| `0x43ca5319` | `[IMAGING_REL]: RelKey) %02d: %02d` | 1 (`0x4379d14a`) | `0x4379d114` |
| `0x43ca533b` | `[IMAGING_REL]: it is a strange trig in IsNeedForceS1ON : %d` | 1 (`0x4379d3c0`) | `0x4379d37a` |
| `0x43ca5377` | `[IMAGING_REL]: remote capture cancel due to camuser's release lock` | 1 (`0x4379d9c8`) | `0x4379d83a` |
| `0x43ca53ba` | `[IMAGING_REL]: Unknown REL_EVT (%02X)` | 1 (`0x4379e186`) | `0x4379d83a` |
| `0x43ca53e0` | `[IMAGING_REL]: RelMgr) <ExecMsg> CLEAR_INNER_RP_CAPID_IDX %d` | 1 (`0x4379e376`) | `0x4379e354` |
| `0x43ca541d` | `[IMAGING_REL]: RelMgr) <ExecMsg> CLEAR_INNER_RP %d` | 1 (`0x4379e3c8`) | `0x4379e3a8` |
| `0x43ca5450` | `[IMAGING_REL]: RelMgr) Invalid RelLock Factor %08x` | 1 (`0x4379e5e6`) | `0x4379e500` |
| `0x43cafd53` | `[IMAGING_REL]: NotifyEEStartEnable (%08X)` | 1 (`0x43807930`) | `0x43807488` (`ExecModeHandler.cpp`) |
| `0x43cb4549` | `[IMAGING_REL]: CapIdTblMgr) Initialize irp(%x), cidx(%x), rp(%x), wp(%x), wpd(%x), dm(%x)` | 1 (`0x4381c356`) | `0x4381c30c` |
| `0x43cb45a3` | `[IMAGING_REL]: CapIdTblMgr) IncrementInnerRP … cnum(%x)` | 1 (`0x4381c40c`) | `0x4381c39c` |
| `0x43cb4612` | `[IMAGING_REL]: CapIdTblMgr) ClearInnerRPCapIdIdx …` | 1 (`0x4381c4a8`) | `0x4381c448` |
| `0x43cb4678` | `[IMAGING_REL]: CapIdTblMgr) ClearInnerRP …` | 1 (`0x4381c532`) | `0x4381c4e0` |
| `0x43cb46de` | `[IMAGING_REL]: CapIdTblMgr) IncrementRP …` | 1 (`0x4381c5bc`) | `0x4381c568` |
| `0x43cb4744` | `[IMAGING_REL]: CapIdTblMgr) CheckCapIDAvailability …` | 1 (`0x4381c678`) | `0x4381c62a` |
| `0x43cb47aa` | `[IMAGING_REL]: CapIdTblMgr) GetCaptureID …` | 1 (`0x4381c7ea`) | `0x4381c6cc` |
| `0x43cb48d2` | `[IMAGING_REL]: RelQueue) err. queue is empty (PopBack)` | 2 (`0x4381c950`, `0x4381caa4`) | `0x4381c93c`, `0x4381ca90` |
| `0x43cb4909` | `[IMAGING_REL]: RelQueue) err. queue is empty (PopFront)` | 2 (`0x4381c9a0`, `0x4381caf0`) | `0x4381c98c`, `0x4381cadc` |
| `0x43cb4941` | `[IMAGING_REL]: RelQueue) err. queue is full (PushFront)` | 2 (`0x4381c9f8`, `0x4381cb44`) | `0x4381c9e0`, `0x4381cb2c` |
| `0x43cb4979` | `[IMAGING_REL]: RelQueue) err. queue is full (PushBack)` | 2 (`0x4381ca50`, `0x4381cb94`) | `0x4381ca38`, `0x4381cb7c` |
| `0x43cb49b0` | `[IMAGING_REL]: CapIdTblMgrIf) StartAccess Cmp To %08X` | 1 (`0x4381ccce`) | `0x4381cc7c` |
| `0x43cb49e6` | `[IMAGING_REL]: CapIdTblMgrIf) StartAccess Req From %08X` | 1 (`0x4381cd3e`) | `0x4381cc7c` |
| `0x43cb4a1e` | `[IMAGING_REL]: CapIdTblMgrIf) Init End` | 1 (`0x4381cd7e`) | `0x4381cc7c` |
| `0x43cb4a45` | `[IMAGING_REL]: CapIdTblMgrIf) StopAccess Req From %08X` | 1 (`0x4381cdb6`) | `0x4381cc7c` |
| `0x43cb4a7c` | `[IMAGING_REL]: CapIdTblMgrIf) StopAccess Cmp To   %08X` | 1 (`0x4381cdea`) | `0x4381cc7c` |
| `0x43cb4ab3` | `[IMAGING_REL]: CapIdTblMgrIf) GetTblAddr Req From %08X` | 1 (`0x4381ce2a`) | `0x4381cc7c` |
| `0x43cb4aea` | `[IMAGING_REL]: CapIdTblMgrIf) GetTblAddr Cmp To   %08X` | 1 (`0x4381ce5e`) | `0x4381cc7c` |
| `0x43cb4b21` | `[IMAGING_REL]: CapIdTblMgrIf) pop queue StartAccess From %08X` | 1 (`0x4381ceaa`) | `0x4381cc7c` |
| `0x43cb4b80` | `[IMAGING_REL]: RelLock) You may forget to hold down the LOCK key...` | 1 (`0x4381d0d4`) | `0x4381d088` |
| `0x43cb4bc4` | `[IMAGING_REL]: NoMprCap InnerRp Clear!!` | 1 (`0x4381d13e`) | `0x4381d114` |

### 3.3 Código (VERIFICADO por desensamblado)

Dos **zonas de código** claramente separadas:

**(a) `RelMgr` — `0x4379d114`–`0x4379e600`.**

- `0x4379d83a` es el **despachador de `REL_EVT`**: `subs r2, r3, #1` + `cmp r2, #0x26` +
  `tbh [pc, r2, lsl #1]` → **ids de evento `0x01`–`0x27`** (39 valores); el caso por defecto
  (rama `0x4379e17c`) imprime `[IMAGING_REL]: Unknown REL_EVT (%02X)`. Coincide con la
  decompilación ya existente en `analysis/ghidra/liro-relmgr-exec.json` (`0x4379d83a`).
  **0 llamadores `bl` directos** → se invoca desde una tabla de manejadores.
- `0x4379d114` (`RelKey) %02d: %02d`) recorre una tabla de 4 bytes por entrada
  (`ldr r3,[r7],#4`), guarda cada valor en `[r5,#0x44]` y consulta un byte en
  `[r2,#0xdc]`; **solo imprime cuando ese byte vale 4** (`cmp r2,#4`). Se llama desde
  `0x4379d206`, `0x4379d212`, `0x4379d21e`.
- `0x4379d37a` (`IsNeedForceS1ON`) y `0x4379d3f8` (notificación a `CamUser`) se llaman desde el
  propio despachador (`0x4379d91a`, `0x4379d9a2`, `0x4379da2e`).
- `0x4379e500` (`RelMgr) Invalid RelLock Factor %08x`) construye el "factor" con **dos u32
  leídos de bytes**: `[r1+4..7]` y `[r1+8..0xb]` (`orr.w r3, r3, r2, lsl #8/#16/#24`).

**(b) Tabla de capture-ids y cola — `0x4381c30c`–`0x4381d150`.**

- `CapIdTblMgr` (`0x4381c30c`…`0x4381c6cc`): **7 operaciones** sobre un *ring* de capture-ids
  con 6 campos (`irp` = inner read pointer, `cidx` = índice de capture-id, `rp`/`wp` = punteros
  de lectura/escritura, `wpd`, `dm`): `Initialize`, `IncrementInnerRP`, `ClearInnerRPCapIdIdx`,
  `ClearInnerRP`, `IncrementRP`, `CheckCapIDAvailability`, `GetCaptureID`.
  `0x4381c30c` (Initialize) se llama desde `0x4379e038` y `0x4379e900` (RelMgr);
  `GetCaptureID` (`0x4381c6cc`) desde `0x4379df26` y `0x4379df46` (RelMgr).
- `RelQueue` (`0x4381c93c`…`0x4381cb7c`): 8 funciones (4 pares Pop/Push × Front/Back) sobre las
  clases `Camera::ReleaseLock::Queue` / `RingQueue`.
- `CapIdTblMgrIf` (`0x4381cc7c`): **8 trazas** y **0 llamadores `bl` directos** → se invoca
  **por interfaz** (vtable), coherente con el sufijo `If`.
- `0x4381d088` (`RelLock) You may forget to hold down the LOCK key...`): comprueba una
  **máscara de bits**: lee `[r0+0x54]` (puntero), `[r0+0x20]` (índice `r7`) y `[r0+0x38]`
  (índice de bit `r4`), toma la palabra `ldr.w r8,[r3, r7, lsl #2]`, la enmascara con
  `1 << r4` (`lsls.w r3, r2, r4`) y solo avisa si el bit está a 0 **y** `r7==2`, `r4==0`.
- `0x4381d114` (`NoMprCap InnerRp Clear!!`): llama a `FUN_43b04b3c` (¿existe captura MPR?); si
  **no** existe, limpia el *inner RP* llamando a `0x4381c4e0` (= `CapIdTblMgr) ClearInnerRP`).

### 3.4 La cadena muerta `0x43c9c520`

`[IMAGING_REL]: Spinal) osal_free_timer: err %x` no tiene **ninguna** referencia: ni por la
regla estricta, ni por una regla relajada (se probaron todos los `add rX,pc` a ≤80 B de cada
`ldr`), ni por puntero absoluto de 4 B, ni por `movw`/`movt`. **En la A7S fw3.20 el mismo texto
(`Spinal) osal_free_timer: err %x`, offset `0x761d32`) tampoco tiene referencias** → la
cadena ya estaba muerta antes; la fw3.21 solo le antepone la etiqueta.

## 4. `[IMAGING]` — panorama / stitching + el macro `FATAL!` de la captura

### 4.1 Las dos cosas que conviven bajo la misma etiqueta

| | cadenas | sitios PIC | funciones | fichero |
|---|---|---|---|---|
| **genéricas** (`FATAL! %s:%d` `0x43c9b47c`, `FATAL! %s:%d [0x%x]` `0x43c9f6d9`, `%s:%d \n` `0x43cabafb`) | 3 | **473** | 322 | 125 ficheros del subsistema de captura |
| **específicas** (117 mensajes de panorama/stitch) | 117 | **135** | **24** | **11** ficheros |

Las **3 genéricas** son el macro `FATAL!` que la fw3.21 de la A6000 etiquetó con `[IMAGING]: `:
`[IMAGING]: FATAL! %s:%d` está referenciada desde **443 sitios** repartidos por **305 funciones**
(0x4354xxxx, 0x4378xxxx–0x438fxxxx): son todos los `CaptureManager*`, `CaptureUtility*`,
`RawMemManager*`, `Stage_*`, `Section*`… Es decir, **la etiqueta `[IMAGING]:` cubre en la
fw3.21 todo el subsistema de captura**, no solo el panorama.

Comprobación cruzada con la A7S: allí el mismo macro es la cadena **sin etiqueta**
`FATAL! %s:%d` (offset `0x760f9d`, vaddr `0x43ca1f9d`) con **467 sitios** (misma regla
estricta) y `FATAL! %s:%d [0x%x]` (offset `0x763052`) con **28**. En la A6000 son **443** y
**29**. → la fw3.21 **antepone la etiqueta**, no crea mensajes nuevos.

> Nota sobre el *string tail merging*: en la A6000 la cadena `FATAL! %s:%d` "viva" (sin
> prefijo) **no existe como cadena independiente**: es la cola de
> `[IMAGING]: FATAL! %s:%d` (`0x43c9b47c`+11 = `0x43c9b487`), y por eso la regla PIC canónica
> (que solo acepta destinos en el *inicio* de una cadena) le asigna 0 sitios.

### 4.2 Los 117 mensajes específicos y sus 11 ficheros

| fichero | función(es) | mensajes | sub-bloques |
|---|---|---|---|
| `still_cnt_panoramaSweep.cpp` | `0x437e6b3c`, `0x437e6e78`, `0x437e751c` | 22 (62 sitios) | `[PanoramaSweepStart]`, `[PanoramaSweepEnd]`, `[UpdateSweepCanvas]` |
| `still_seq_panoramaStitch.cpp` | `0x43781424`, `0x43780eb4` | 16 (25 sitios) | `[seq_panoramaParallelStitch]`, `[seq_panoramaClippingDecode]`, `[StitchInterrupt]`, `[panoramaSRotateLeftStitchImage]` |
| `still_cnt_panoramaStitch.cpp` | `0x438bcef8` | 15 (15) | `[PanoramaStitch]` |
| `still_seq_enc.cpp` | `0x437e9068` | 8 (12) | `[seq_brcEncode]` |
| `still_dda_jpg.cpp` | `0x437e8144`–`0x437e83dc` | 6 (6) | `[dda_jpg_*]` |
| `src/srotate/ddl_srotate.cpp` | `0x438bc0a8` | 3 (3) | `[ddls_srotate_sa_start_cb]` |
| `still_dda_rc.cpp` | `0x437e858c` | 2 (2) | `[dda_rc_fill]`, `[dda_rc_resize]` |
| `src/stitch/ddl_stitch.cpp` | `0x438bc720` | 2 (2) | `[ddls_stitch_sa_start_cb]`, `[ddls_stitch_set_flg]` |
| `still_cmp_effect.cpp` | `0x437e643a` | 1 (1) | `[cmp_fill]` |
| `still_csl_ring_buff.cpp` | `0x437e7f50` | 1 (1) | `[allocOutputArea]` |
| *(callbacks sin `__FILE__`)* | `0x43780496`, `0x437804da`, `0x43780522`, `0x437e961c`, `0x437e977a`, `0x437e98ec`, `0x438bc6ac` | 7 (7) | `[seqSRotateCallBack]`, `[seqStitchCallBack]`, `[seqClippingDecCallback]`, `[Jpeg Open/Close Callback]`, `[wrapRcrtFill Callback]` |

Las **38 cadenas sin referencia** (todas del bloque *grande/imagen*: `[PanoramaResize]` 5,
`[PanoramaResizeEncode]` 10, `[seq_bigImageEncode]` 6, `[seq_bigImageClippingDecode]` 4,
`[seq_bigImageResizeEncode]` 4, `[seq_panoramaResize]` 2, `[dda_rc_resize]` 3, `[cmp_*]` 2,
`[ddas_rc_set_rcct_param]`, `[seq_makePanoramaMakerNoteData]`) **ya estaban muertas en la A7S
fw3.20** (0 referencias de las 38 en el blob de la A7S) → son **cadenas heredadas muertas**,
no una regresión de la fw3.21.

### 4.3 Código: la cadena del panorama

Verificada con un barrido de `bl` (`analysis/s125_imaging_rel/bl_callers.json`):

```
Stage_InitializeSweepAndSpoolBranch 0x437f0838   (22 llamadores)
  └─ bl 0x437f1c74 / 0x437f1ce0 → Stage_Panorama 0x43549020
       └─ bl 0x435492aa → PanoramaSweepStart      0x437e6b3c   (still_cnt_panoramaSweep.cpp)
            └─ bl 0x437f0b06 → UpdateSweepCanvas 0x437e751c   (still_cnt_panoramaSweep.cpp)
                 └─ bl 0x437e7aa4 → seq_brcEncode 0x437e9068   (still_seq_enc.cpp)
  └─ bl 0x437f0c90 → PanoramaStitch         0x438bcef8   (still_cnt_panoramaStitch.cpp)
       └─ bl 0x438bd280 → seq_panoramaParallelStitch 0x43781424 (still_seq_panoramaStitch.cpp)
  └─ bl 0x43781658 → seq_panoramaClippingDecode 0x43780eb4 (still_seq_panoramaStitch.cpp)
```

`PanoramaSweepEnd` (`0x437e6e78`), `cmp_fill` (`0x437e643a`), `CapIdTblMgrIf` (`0x4381cc7c`),
`RelLock` (`0x4381d088`), `NoMprCap` (`0x4381d114`), el despachador de `REL_EVT`
(`0x4379d83a`) y `ExecModeHandler` (`0x43807488`) tienen **0 llamadores `bl` directos**
→ se invocan **indirectamente** (tabla de funciones / vtable / cola de mensajes).

Esto **confirma y cierra la cadena de S105** (`docs/capture/s105-panorama-bracket-interval.md`),
que ya había identificado `PanoramaSweepStart 0x437e6b3c`, `UpdateSweepCanvas 0x437e751c`,
`PanoramaSweepEnd 0x437e6e78`, `seq_panoramaClippingDecode 0x43780eb4` y
`PanoramaStitch 0x438bcef8`: **las direcciones coinciden exactamente**.

Además, `Stage_Panorama.cpp` es el fichero de las funciones `0x43549020` (`Stage_Panorama`)
y `0x437f10d4`, y `src/stitch/ddl_stitch.cpp` / `src/srotate/ddl_srotate.cpp` son los ficheros
de los *callbacks* de escalado (`ddls_*`).

### 4.4 Las 37 sub-etiquetas del módulo `[IMAGING]`

`[seq_panoramaParallelStitch]` (13), `[PanoramaResizeEncode]` (10), `[StitchInterrupt]` (9),
`[UpdateSweepCanvas]` (8), `[seq_brcEncode]` (8), `[PanoramaStitch]` (7),
`[PanoramaSweepEnd]` (6), `[seq_bigImageEncode]` (6), `[PanoramaResize]` (5),
`[seq_bigImageClippingDecode]` (4), `[PanoramaSweepStart]` (4),
`[seq_bigImageResizeEncode]` (4), `[dda_rc_resize]` (3), `[ddls_srotate_sa_start_cb]` (3),
`[seq_panoramaResize]` (2), `[dda_jpg_fill]` (2), `[dda_rc_fill]` (2),
`[ddls_stitch_sa_start_cb]` (2), y 19 sub-etiquetas de 1 mensaje
(`[seqSRotateCallBack]`, `[seqStitchCallBack]`, `[seqClippingDecCallback]`,
`[seq_panoramaClippingDecode]`, `[panoramaSRotateLeftStitchImage]`,
`[seq_makePanoramaMakerNoteData]`, `[cmp_fill]`, `[cmp_fill_validArea]`,
`[cmp_resizeMirror]`, `[allocOutputArea]`, `[dda_jpg_close]`, `[dda_jpg_stream_anlyze]`,
`[dda_jpg_get_stream_samplingfactor]`, `[dda_jpg_decode]`, `[ddas_rc_set_rcct_param]`,
`[Jpeg Close Callback]`, `[Jpeg Open Callback]`, `[wrapRcrtFill Callback]`,
`[ddls_stitch_set_flg]`).

## 5. Diferencial A6000 fw3.21 vs A7S fw3.20 y A6300 fw2.01

**Ninguna de las dos cámaras etiqueta estos módulos**: 0 apariciones de `[IMAGING` en el
`av-cam.bin` de la A7S fw3.20 y del A6300 fw2.01. La etiqueta es **nueva de la fw3.21 de la
A6000** (igual que `[IDT_OPD]` en S120 y que el prefijo `[CAMERA_SA]:` en S108).

### 5.1 `[IMAGING]` (120)

| | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|
| cadenas con el prefijo | **0** | **0** |
| mensajes equivalentes **sin** prefijo (texto a texto) | **115 / 120** | **115 / 120** |
| **nuevos de la fw3.21** | **5** | **5** |
| mensajes propios de la otra cámara | **0** | **0** |

Los **5 nuevos** de la fw3.21 (todos en `still_cnt_panoramaSweep.cpp` / `still_seq_panoramaStitch.cpp`):

| A6000 | vaddr | función | equivalente A7S/A6300 |
|---|---|---|---|
| `[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x, status: 0x%08x` | `0x43cab176` | `0x437e6e78` | no existe |
| `[IMAGING]: [PanoramaSweepEnd] Err! %s:%d` | `0x43cab1b0` | `0x437e6e78` | no existe |
| `[IMAGING]: [PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d` | `0x43cab1d9` | `0x437e6e78` | no existe |
| `[IMAGING]: [PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d` | `0x43cab21d` | `0x437e6e78` | no existe |
| `[IMAGING]: [seq_panoramaParallelStitch][OK] StitchProc ALL OK : %s:%d` | `0x43c9ec01` | `0x43781424` | no existe |

La A7S y el A6300 tienen solo 2 mensajes de `PanoramaSweepEnd`
(`[PanoramaSweepEnd] Err: 0x%08x : %s:%d` y `[PanoramaSweepEnd] End : 0x%08x`); la fw3.21 de
la A6000 **añade 4 variantes de error** y el `[OK] StitchProc ALL OK`.

### 5.2 `[IMAGING_REL]` (31)

| | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|
| cadenas con el prefijo | **0** | **0** |
| mensajes equivalentes sin prefijo | **30 / 31** | **22 / 31** |
| nuevos de la fw3.21 | **1** (`(%d,%d,%d)` `0x43ca3887`) | **9** |
| propios de la otra cámara | **0** | **2** |

- **Único nuevo en la fw3.21**: `[IMAGING_REL]: (%d,%d,%d)` (`0x43ca3887`), emitido por
  `0x43792a0c` (`SyncTask.cpp`, el manejador `VD_Pre`/`HS3` — ver
  `docs/capture/s61-message-flow.md`) junto a la cadena `VD_Pre S` (`0x43ca387e`).
- **9 que el A6300 no tiene**: `(%d,%d,%d)`, `RelKey) %02d: %02d`,
  `RelMgr) <ExecMsg> CLEAR_INNER_RP %d`, `RelMgr) <ExecMsg> CLEAR_INNER_RP_CAPID_IDX %d`,
  `RelMgr) Invalid RelLock Factor %08x`, `RelQueue) err. queue is empty (PopBack)`,
  `RelQueue) err. queue is full (PushFront)`, `Spinal) osal_free_timer: err %x`,
  `remote capture cancel due to camuser's release lock`.
  → el A6300 fw2.01 **sí tiene** la clase `Camera::ReleaseLock` (RTTI
  `N6Camera11ReleaseLock9RelLockS2E` `0x43db0f11`), el mensaje `RelLock) You may forget to hold
  down the LOCK key...` (`0x43db0f1c`), 2 de los 4 mensajes de `RelQueue)` (`PopFront`,
  `PushBack`) y los 8 de `CapIdTblMgrIf)`; lo que **no** tiene es la traza de la tecla
  (`RelKey)`), la de `IsNeedForceS1ON`, las tres de `RelMgr)`, la del *release lock* remoto,
  ni la de `(%d,%d,%d)`.
- **2 mensajes propios del A6300**: `CapIdTblMgr) SetMprInitEnd irp(%x), cidx(%x), rp(%x),
  wp(%x), wpd(%x), dm(%x)` (`0x43db0c34`) y `CapIdTblMgrIf) Unknown massage` (`0x43dceaba`).
  El A6300 tiene **8** mensajes de `CapIdTblMgr)` (la A6000 tiene 7: le falta
  `SetMprInitEnd`, que es propio del A6300) y **9** de `CapIdTblMgrIf)` (la A6000 tiene 8:
  le falta `Unknown massage`). El A6300 escribe **«massage»** en vez de «message» →
  **NO VERIFICADO** si el A6300 es anterior o posterior en esa línea de código.

## 6. Relación con `[IMAGING_CAP]` (S106) y con el motor de secciones (S114)

- `[IMAGING_CAP]` (S106, 697 trazas) y `[IMAGING]` (S125, 120 trazas) son **hermanos
  disjuntos** en el mismo `.rodata`: los prefijos `[IMAGING_CAP]:` y `[IMAGING]:` no se
  solapan y ninguna cadena pertenece a los dos módulos.
- El código **sí** está relacionado: `[IMAGING_CAP]` es el gestor de captura *still* y su
  motor de secciones (S114) tiene 17 manejadores en `0x437e9a70`–`0x437eb470`. El código de
  panorama de `[IMAGING]` vive **justo por debajo** (`0x437e643a`–`0x437e98ec`) y
  `0x437f0838` (`Stage_InitializeSweepAndSpoolBranch`) cuelga de
  `CaptureManager::CaptureStart` (`0x437df646`), igual que en S105.
- **El motor de secciones NO incluye el panorama**: ninguno de los 17 manejadores de S114
  (`0x437e9a70`–`0x437eb470`) emite un mensaje específico de `[IMAGING]`; los que aparecen en
  el mapa de este hito (`0x437e9d78` CaptureAfterRead, `0x437eb24c` CaptureRead, …) lo hacen
  **solo con el `FATAL!` genérico**.
- Los dos módulos **comparten el mismo archivo de destino**: `[IMAGING_REL]` vive en
  `Camera::ReleaseLock` (la interfaz de *release* que el gestor de captura usa para disparar)
  y `[IMAGING]` en el motor de panorama, que es quien *produce* las imágenes que
  `[IMAGING_CAP]` acaba de codificar y notificar.

## 7. NO VERIFICADO / abierto

1. **Qué significan exactamente** `irp`, `cidx`, `rp`, `wp`, `wpd`, `dm` de `CapIdTblMgr`
   (los 6 campos que imprime cada mensaje). El firmware no los expande.
2. **Qué es `InnerRP`** ("inner read pointer"?) y por qué `ClearInnerRP` /
   `ClearInnerRPCapIdIdx` son operaciones distintas.
3. **La semántica de los ids de `REL_EVT`** (`0x01`–`0x27`): solo se ha verificado el rango y
   la tabla de salto (`tbh` en `0x4379d852`); falta el significado de cada evento.
4. **`IsNeedForceS1ON`**: qué obliga a forzar el estado S1 y por qué se considera "un disparo
   extraño" (`it is a strange trig in IsNeedForceS1ON : %d` `0x43ca533b`).
5. **El factor de `RelLock`** (`%08x`): se sabe que son dos u32 formados por bytes
   (`[r1+4..7]` y `[r1+8..0xb]`), no qué significan.
6. **Quién llama a `CapIdTblMgrIf` (`0x4381cc7c`)**: 0 llamadores `bl` directos → se invoca por
   interfaz; falta localizar el dispatch por vtable.
7. **Por qué la fw3.21 etiqueta con `[IMAGING]: ` el `FATAL!` genérico** de todo el subsistema
   de captura (443 sitios) y no con un nombre más preciso: NO VERIFICADO (es una decisión de
   etiquetado del fabricante).
8. **Si las 38 cadenas muertas de `[IMAGING]` se limpian en una fw posterior**: NO VERIFICADO.
9. **`[IMAGING_REL]: (%d,%d,%d)`**: qué tres valores imprime (la cadena `VD_Pre S` `0x43ca387e`
   sugiere que son los de la señal VD_Pre, pero no se ha desensamblado el gestor de argumentos).
10. **La extensión de "Spinal"/"LIRO"**: `Spinal.cpp` es el fichero del gestor de release, pero
    no está verificado qué relación hay entre "Spinal" y "LIRO" más allá de las trazas
    `EV *:LIROSeq`.

## 8. Revisión del agente principal

_(vacío — pendiente de revisión)_

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (38 tests del hito + comprobaciones a mano):**

1. **Recuentos**: 31 apariciones de `[IMAGING_REL]` y 120 de `[IMAGING]` en el blob → coinciden.
2. **"REL" = RELease, y está en el RTTI**: la cadena mangled `N6Camera11ReleaseLock9RelLockS1E`
   está en `0x43ca5489` (con `RelLockS1` en `0x43ca5499`), y hay `RelLockBase` (`0x43ca54bb`),
   `RelLockS2` (`0x43cb4b75`), `RelMgr` (`0x43ca53ef`) y `CapIdTblMgr` (`0x43cb4558`).
   *Matiz de direcciones*: el informe cita `RelLockS1 0x43ca5483`, `RelLockBase 0x43ca54a4` y
   `RelLockS2 0x43cb4b5f` — esas son las posiciones **del inicio del nombre mangled**, no de la
   subcadena; las de la subcadena están 0x14-0x17 bytes después. No cambia ninguna conclusión.
3. **Fichero fuente**: `Spinal.cpp` en `0x43c9c54f` ✓ (y el programa es el LIRO, S105).
4. **El `FATAL!` genérico**: la *cadena completa* empieza en `0x43c9b47c` (con el prefijo
   `[IMAGING]: `) y el literal `FATAL! %s:%d` está en `0x43c9b487`; en la A7S hay **2** copias
   del literal → el macro genérico ya existía allí, lo que concuerda con el "0 etiquetas en la
   A7S" del diferencial.
5. **Sin efecto en S51**: ninguno de los dos módulos menciona `shutter`/`silent`/`EFCS` ni
   mecanismo de obturación.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
