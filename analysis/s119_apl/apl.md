# S119 — el módulo `[APL]` (42 trazas): la capa de aplicación sobre HW y SA

**Firmware:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`, 11 427 236 B)
**Base virtual:** `vaddr = 0x43541000 + file_offset` (verificada)
**Método:** solo análisis de bytes (Capstone 5.0.7 + escáner PIC propio). Sin REA/Ghidra, sin
ejecutar firmware, sin cámara, sin red.

---

## 1. Resumen

* Las **42 trazas `[APL]`** de la A6000 fw3.21 **no son un módulo con prefijo propio**: son un
  **sub-bloque `[APL]` dentro de las cadenas `[CAMERA_SA]:`** (S108). Las 42 cadenas completas
  empiezan por `"[CAMERA_SA]: "` y van de `0x43cebde1` a `0x43cec4fe` (contiguas); la etiqueta
  `[APL]` está 13 bytes más dentro, de `0x43cebdee` a `0x43cec50b`.
* Las emite **una sola familia de 5 funciones** del driver de cámara: `0x439cea30` (7 trazas),
  `0x439cebe4` (9), `0x439cedd0` (4), `0x439ceeb8` (20) y `0x439cf3b8` (2). Las 42 trazas tienen
  referencia PIC verificada (1:1 con su punto de emisión).
* Es la **capa de aplicación sobre el acelerador escalar (SA) y sobre un bloque de hardware
  ("HW")**: abre el HW y el SA, reserva el bloque de parámetros de entrada (`InputPrm`), pide el
  mapa de memoria al HW (`HME_BaseTar_Addr`, `HME_BaseRef_Addr`, `Work_Addr`, `Vec_Addr`,
  `Result_Addr`, `HME_BaseTar_LineAddAddr`), programa el modo y la MMU, arranca, espera, aborta
  ante *timeout* y devuelve la imagen de referencia de salida (`Output Ref Img`).
* Los `unit_hndl` que aparecen en 13 trazas **no son handles del SA sino handles de unidad del
  gestor de memoria dinámico `[CAM_DMM]`** (S113): se abren con `0x43903280` (Open), se cierran con
  `0x43903414` (Close) y se liberan con `0x43902fbc` (Free).
* **Su único consumidor es el módulo `[CAMERA_MAIN_TC]`** (el pipeline de *time compression* /
  movie), que lo llama como "**ApolloSA**". No lo llama ni el gestor de captura `[IMAGING_CAP]`
  (S106) ni `Camera::CamCore` (S107).
* **Diferencial A7S fw3.20:** las **mismas 42 cadenas, texto a texto** (42/42 comunes, 0
  exclusivas en ningún sentido) y la **misma estructura de 5 funciones**; lo único que cambia es
  que la A7S **no lleva el prefijo `"[CAMERA_SA]: "`**.

---

## 2. Qué es `[APL]`

En la A6000 fw3.21 hay **cinco familias distintas** de cadenas con "APL"; este hito cubre sólo la
primera:

| familia | nº | rango | a qué pertenece |
|---|---|---|---|
| **`[APL]` (42)** | 42 | `0x43cebde1`–`0x43cec4fe` | **este hito**: driver de cámara sobre HW+SA |
| `[APL DBG]` (9) | 9 | `0x43cb7b15`–`0x43cb7c93` | depuración del motor de imagen (`[CAMERA_MAIN_YC]`, S110) |
| `[APL Callback]` (1) | 1 | `0x43c7e9ae` | callback de error del módulo SDF/CCNR |
| `[APL Driver]` (1) | 1 | `0x43c9059a` | *timeout* de IIB en la zona `[CAMCORE]` |
| `[APL0]`/`[APL1]` (2) | 2 | `0x43ca28cc`, `0x43ca2903` | volcado de registros (HME), zona `[CAMERA_MAIN_SYNC]` |

(En total hay **55** apariciones del literal `[APL` en el blob: 42 de este módulo + 9 + 1 + 1 + 2.)

**No hay que desarrollar las siglas**: el firmware no expande `APL`, `HW`, `SA`, `HME`, `MMU` ni
`Zima`. Lo único que el firmware dice del bloque es el nombre que le da su consumidor:
`[CAMERA_MAIN_TC]: ApolloSA_Main(start) %d %d %d %d %d %d %d %d 0x%X 0x%X` (`0x43cb6ac7`),
`[CAMERA_MAIN_TC]: ApolloSA_Main(end) %d %d %d %d %d` (`0x43cb6c0d`),
`[CAMERA_MAIN_TC]: ApolloSA_Fin(start) %d` (`0x43cb6cc5`),
`[CAMERA_MAIN_TC]: ApolloSA_Fin(end)` (`0x43cb6cee`),
`[CAMERA_MAIN_TC]: ApolloSA_Cancel(start) %d` (`0x43cb6c6f`),
`[CAMERA_MAIN_TC]: ApolloSA_Cancel(end) %d` (`0x43cb6c9b`) y la existencia de
`Apollo.cpp` (`0x43cc6e15`) y `Stage_Apollo.cpp` (`0x43cc6e0f`), ambos en la zona `[IMAGING_CAP]`.

### 2.1 Doble emisión: cada traza se registra dos veces

El código llama a **dos** routines por cada error, con **dos punteros distintos a la misma cadena**:

```
0x439cea78  add r3, pc     ; r3 = 0x43cebde1  ->  "[CAMERA_SA]: [APL] HW Open Err %d"
0x439cea7a  bl  0x439ce984 ; emisor de traza de modulo (r0 = 0xb6)
0x439cea82  add r0, pc     ; r0 = 0x43cebdee  ->  "[APL] HW Open Err %d"
0x439cea84  bl  0x43902718 ; printf del texto interior
```

`0x439ce984` es el emisor genérico de traza por módulo (OSAL: `osal_try_valloc_msg` `0x435612d0`,
`0x43561244`, `0x4356120c`, `0x435612ec`) y `0x43902718` imprime el texto sin la etiqueta de
módulo. Por eso **cada traza tiene dos direcciones**: la del inicio de la cadena completa
(`vaddr_full`) y la de la etiqueta `[APL]` (`vaddr_tag`, = `vaddr_full` + 13).

---

## 3. Inventario de las 42 trazas

`vaddr` = dirección de la **etiqueta `[APL]`**; `full` = inicio de la cadena completa
(`"[CAMERA_SA]: …"`); `sitio` = instrucción `add rX,pc` que la referencia (regla estricta).

| # | texto (`[APL] …`) | vaddr | full | sitio | función |
|---|---|---|---|---|---|
| 1 | `HW Open Err %d` | `0x43cebdee` | `0x43cebde1` | `0x439cea78` | `0x439cea30` |
| 2 | `SA Open Err` | `0x43cebe10` | `0x43cebe03` | `0x439ceaa0` | `0x439cea30` |
| 3 | `HW Close Err1 %d` | `0x43cebe2f` | `0x43cebe22` | `0x439ceac4` | `0x439cea30` |
| 4 | `Calloc InputPrm Err` | `0x43cebe53` | `0x43cebe46` | `0x439ceaea` | `0x439cea30` |
| 5 | `SA & HW Close Err1 %d %d` | `0x43cebe7a` | `0x43cebe6d` | `0x439ceb1a` | `0x439cea30` |
| 6 | `Open InputPrm Err` | `0x43cebea6` | `0x43cebe99` | `0x439ceb3e` | `0x439cea30` |
| 7 | `SA & HW Close Err2 %d %d` | `0x43cebecb` | `0x43cebebe` | `0x439ceb6c` | `0x439cea30` |
| 8 | `Close Err1 (unit_hndl:0x%x)` | `0x43cebef7` | `0x43cebeea` | `0x439cec18` | `0x439cebe4` |
| 9 | `Close Err2 (unit_hndl:0x%x)` | `0x43cebf26` | `0x43cebf19` | `0x439cec44` | `0x439cebe4` |
| 10 | `Close Err3 (unit_hndl:0x%x)` | `0x43cebf55` | `0x43cebf48` | `0x439cec6c` | `0x439cebe4` |
| 11 | `Close Err4 (unit_hndl:0x%x)` | `0x43cebf84` | `0x43cebf77` | `0x439cec9c` | `0x439cebe4` |
| 12 | `Close Err5 (unit_hndl:0x%x)` | `0x43cebfb3` | `0x43cebfa6` | `0x439cecc4` | `0x439cebe4` |
| 13 | `Close Err6 (unit_hndl:0x%x)` | `0x43cebfe2` | `0x43cebfd5` | `0x439cecec` | `0x439cebe4` |
| 14 | `Close Err7 (unit_hndl:0x%x)` | `0x43cec011` | `0x43cec004` | `0x439ced14` | `0x439cebe4` |
| 15 | `SA Close Err1` | `0x43cec040` | `0x43cec033` | `0x439ced3c` | `0x439cebe4` |
| 16 | `HW Close Err2 %d` | `0x43cec061` | `0x43cec054` | `0x439ced60` | `0x439cebe4` |
| 17 | `Open Err1 (unit_hndl:0x%x)` | `0x43cec085` | `0x43cec078` | `0x439cee06` | `0x439cedd0` |
| 18 | `Free & Close Err1 (unit_hndl:0x%x)` | `0x43cec0b3` | `0x43cec0a6` | `0x439cee26` | `0x439cedd0` |
| 19 | `Open Err2 (unit_hndl:0x%x)` | `0x43cec0e9` | `0x43cec0dc` | `0x439cee4c` | `0x439cedd0` |
| 20 | `Free & Close Err2 (unit_hndl:0x%x)` | `0x43cec117` | `0x43cec10a` | `0x439cee6c` | `0x439cedd0` |
| 21 | `GetZimaNo Err %d` | `0x43cec14d` | `0x43cec140` | `0x439cef1c` | `0x439ceeb8` |
| 22 | `Open Err3 (unit_hndl:0x%x)` | `0x43cec171` | `0x43cec164` | `0x439cef58` | `0x439ceeb8` |
| 23 | `GetMemInfo Err1 (unit_hndl:0x%x)` | `0x43cec19f` | `0x43cec192` | `0x439cefa4` | `0x439ceeb8` |
| 24 | `` `HME_BaseTar_Addr' invalid 0x%X 0x%X 0x%X 0x%X `` | `0x43cec1d3` | `0x43cec1c6` | `0x439cefd2` | `0x439ceeb8` |
| 25 | `GetMemInfo Err2 (unit_hndl:0x%x)` | `0x43cec215` | `0x43cec208` | `0x439cf00c` | `0x439ceeb8` |
| 26 | `` `HME_BaseRef_Addr' invalid 0x%X 0x%X 0x%X 0x%X `` | `0x43cec249` | `0x43cec23c` | `0x439cf03a` | `0x439ceeb8` |
| 27 | `GetMemInfo Err3 (unit_hndl:0x%x)` | `0x43cec28b` | `0x43cec27e` | `0x439cf07a` | `0x439ceeb8` |
| 28 | `` `Work_Addr' invalid 0x%X `` | `0x43cec2bf` | `0x43cec2b2` | `0x439cf09a` | `0x439ceeb8` |
| 29 | `GetMemInfo Err4 (unit_hndl:0x%x)` | `0x43cec2eb` | `0x43cec2de` | `0x439cf0d4` | `0x439ceeb8` |
| 30 | `` `Vec_Addr' invalid 0x%X `` | `0x43cec31f` | `0x43cec312` | `0x439cf0f6` | `0x439ceeb8` |
| 31 | `GetMemInfo Err5 (unit_hndl:0x%x)` | `0x43cec34a` | `0x43cec33d` | `0x439cf126` | `0x439ceeb8` |
| 32 | `` `Result_Addr' invalid 0x%X `` | `0x43cec37e` | `0x43cec371` | `0x439cf14c` | `0x439ceeb8` |
| 33 | `` `HME_BaseTar_LineAddAddr' invalid 0x%X `` | `0x43cec3ac` | `0x43cec39f` | `0x439cf170` | `0x439ceeb8` |
| 34 | `HW GetCoreNum Err %d` | `0x43cec3e6` | `0x43cec3d9` | `0x439cf19c` | `0x439ceeb8` |
| 35 | `HW SetMode Err %d` | `0x43cec40e` | `0x43cec401` | `0x439cf1e4` | `0x439ceeb8` |
| 36 | `MmuMakeParam Err %d` | `0x43cec433` | `0x43cec426` | `0x439cf21a` | `0x439ceeb8` |
| 37 | `Open Err4 (unit_hndl:0x%x)` | `0x43cec45a` | `0x43cec44d` | `0x439cf2dc` | `0x439ceeb8` |
| 38 | `HW TimeOut` | `0x43cec488` | `0x43cec47b` | `0x439cf31c` | `0x439ceeb8` |
| 39 | `HW Abort Err %d` | `0x43cec4a6` | `0x43cec499` | `0x439cf33e` | `0x439ceeb8` |
| 40 | `Output Ref Img` | `0x43cec4c9` | `0x43cec4bc` | `0x439cf366` | `0x439ceeb8` |
| 41 | `SA Open Err2` | `0x43cec4eb` | `0x43cec4de` | `0x439cf3ea` | `0x439cf3b8` |
| 42 | `SA Close Err2` | `0x43cec50b` | `0x43cec4fe` | `0x439cf40e` | `0x439cf3b8` |

**42/42 con referencia PIC; 0 cadenas muertas.**

---

## 4. Mapa función → traza

Las 5 funciones emisoras son contiguas (`0x439cea30`–`0x439cf428`) y están delimitadas por
`push {..,lr}` … `pop {..,pc}` (`0x439ceb9a`, `0x439ced7c`, `0x439cee8c`, `0x439cf38a`,
`0x439cf426`).

| función | papel (verificado por las llamadas `bl`) | trazas |
|---|---|---|
| `0x439cea30` | **Open**: abre HW → abre SA → (rollback) cierra HW → reserva `InputPrm` → (rollback) cierra SA+HW → abre el `InputPrm` → (rollback) cierra SA+HW | 7 |
| `0x439cebe4` | **Close**: cierra **7 handles** (`ctx+0x8 … ctx+0x14`), cierra SA, cierra HW | 9 |
| `0x439cedd0` | **Free & Close**: abre `InputPrm` → lo libera (2 rondas) | 4 |
| `0x439ceeb8` | **Open + ejecución**: `GetExecUnit` → abre handle → 5× `GetMemInfo` → valida 6 direcciones → `GetCoreNum` → `SetMode` → `MmuMakeParam` → abre handle → arranca → vigila *timeout* → aborta → `Output Ref Img` | 20 |
| `0x439cf3b8` | **SA open/close** (vía `ExecuteOpenMSG` / `ExecuteCloseMSG`) | 2 |

### 4.1 Sub-bloques (partición exacta y disjunta: 3+4+13+2+2+5+6+1+4+2 = 42)

| sub-bloque | nº | rango (vaddr de la etiqueta) |
|---|---|---|
| HW Open/Close | 3 | `0x43cebdee`–`0x43cec061` |
| SA Open/Close | 4 | `0x43cebe10`–`0x43cec50b` |
| Handles: Open/Close/Free | 13 | `0x43cec085`–`0x43cec171` |
| Rollback SA & HW | 2 | `0x43cebe7a`–`0x43cebecb` |
| InputPrm | 2 | `0x43cebe53`–`0x43cebea6` |
| GetMemInfo | 5 | `0x43cec19f`–`0x43cec34a` |
| Direcciones de memoria (HME/Work/Vec/Result) | 6 | `0x43cec1d3`–`0x43cec3ac` |
| GetZimaNo | 1 | `0x43cec14d` |
| Programación HW/MMU | 4 | `0x43cec3e6`–`0x43cec4a6` |
| Ejecución | 2 | `0x43cec488`–`0x43cec4c9` |

---

## 5. Qué abre y qué cierra

### 5.1 El contexto de la APL (estructura `ctx`)

`ctx` es un bloque que rellena el consumidor `[CAMERA_MAIN_TC]` en `0x438765fc` antes de llamar:

| offset | tipo | contenido (origen en `0x4387660a`–`0x43876648`) | uso |
|---|---|---|---|
| `+0x00` | byte | nº de unidad | `0x43b6d796` (SA open) / `0x43b6d77c` (SA close) |
| `+0x04` | palabra | puntero al contexto del HW | `0x43b7db64` (HW open) / `0x43b7dbd6` (HW close) |
| `+0x08 … +0x14` | 7 medias palabras | **handles de unidad del DMM** (`0x0,0x2,0x4,0x6,0x8` del parámetro de entrada) | `0x43b6d598` open / `0x43b6d5ac` close / `0x43b6d5b4` free |
| `+0x18`, `+0x1c`, `+0x20` | palabras | parámetros de dirección/tamaño | validaciones `HME_*`, `Vec_Addr`, `Result_Addr` |

El handle de `ctx+0x0e` se pone a `0xffff` si el modo no es 3/6/8 (`0x43876644`: `mov.w r3,#-1`), y
el cierre lo **omite** en ese caso (`0x439cec80`: `movw r3,#0xffff` / `cmp r1,r3` / `beq`).

### 5.2 Las 7 aperturas/cierres de handle (`0x439cebe4`)

Siete llamadas a `0x43b6d5ac` (tail-call a `0x43903414` = **DMM Close**, S113) con los handles de
`ctx+0x8`, `+0xa`, `+0xc`, `+0xe`, `+0x10`, `+0x12`, `+0x14` → `Close Err1` … `Close Err7`.
Las aperturas van por `0x43b6d598` (→ `0x43903280` = **DMM Open**): **5** llamadas en el módulo
(1 en `0x439cea30` → `Open InputPrm Err`; 2 en `0x439cedd0` → `Open Err1`/`Open Err2`; 2 en
`0x439ceeb8` → `Open Err3`/`Open Err4`), y las liberaciones por `0x43b6d5b4` (→ `0x43902fbc` =
**DMM Free**): **2** llamadas en `0x439cedd0` → `Free & Close Err1`/`Free & Close Err2`.

Las trazas `Open Err*`/`Close Err*`/`Free & Close Err*` llevan **`unit_hndl:0x%x`**: es el handle
del DMM, no un handle del SA.

### 5.3 Apertura del HW y del SA

```
0x439cea66  bl 0x43b7db64   ; HW open   -> 0 si OK, 0xff si falla (0x43b7dbce)
0x439cea78  add r3, pc      ; "[CAMERA_SA]: [APL] HW Open Err %d"
0x439cea90  bl 0x43b6d796   ; SA open   (thunk -> 0x439d143c ExecuteOpenMSG)
0x439ceaa0  add r3, pc      ; "[CAMERA_SA]: [APL] SA Open Err"
0x439ceab0  bl 0x43b7dbd6   ; HW close  (rollback)
0x439ceac4  add r3, pc      ; "[CAMERA_SA]: [APL] HW Close Err1 %d"
```

El cierre equivalente está en `0x439cebe4`: `0x43b6d77c` (SA close, thunk → `0x439d133c`
`ExecuteCloseMSG`) → `SA Close Err1`, y `0x43b7dbd6` (HW close) → `HW Close Err2 %d`.
`0x439cf3b8` repite SA open/close con los mensajes `SA Open Err2` / `SA Close Err2`.

---

## 6. Los parámetros de entrada (`InputPrm`)

* La reserva se hace con **`0x439d0f58`**, que es la función que el driver del SA se autodenomina
  **`CallocCamSaParam`** (la cadena `CallocCamSaParam` `0x43ced623` se referencia desde
  `0x439d0f80`, dentro de esa función). La traza la llama **"InputPrm"**:
  `Calloc InputPrm Err` `0x43cebe53` (sitio `0x439ceaea`) y `Open InputPrm Err` `0x43cebea6`
  (sitio `0x439ceb3e`, tras `0x43b6d598` = DMM open con `ctx+0x12`).
* `ctx+0x12` es el **nº de unidad** que se pide al DMM para el bloque de parámetros
  (`ldrh r1,[r4,#0x12]` en `0x439ceb2c`).
* El bloque reservado se pasa después a `GetMemInfo` (`0x439d1bd0`, autodenominada `GetMemInfo`,
  cadena `0x43ced075`) en `0x439cef90`, `0x439ceff8`, `0x439cf066`, `0x439cf0c0`, `0x439cf112`:
  **cinco llamadas**, una por handle → `GetMemInfo Err1`…`Err5`.
* **NO VERIFICADO:** el tamaño y el layout interno de `InputPrm`; el firmware sólo expone sus
  campos por nombre (`HME_BaseTar_Addr`, `HME_BaseRef_Addr`, `Work_Addr`, `Vec_Addr`,
  `Result_Addr`, `HME_BaseTar_LineAddAddr`), nunca su estructura.

---

## 7. Los comandos sobre el acelerador y el hardware

Llamadas `bl` verificadas de las 5 funciones (sólo destinos válidos = prólogo de función o
thunk conocido):

| destino | rol deduced de las trazas | quién lo llama |
|---|---|---|
| `0x43b7db64` | **HW open** (0 = OK, `0xff` = error) | `0x439cea30` |
| `0x43b7dbd6` | **HW close** | `0x439cea30`, `0x439cebe4` |
| `0x43b7dc74` | **HW GetCoreNum** | `0x439ceeb8` |
| `0x43b7dc26` | **HW SetMode** | `0x439ceeb8` |
| `0x43b5ea54` | **MmuMakeParam** | `0x439ceeb8` |
| `0x43a2ff38` | **HW abort** (se llama sólo tras *timeout*) | `0x439ceeb8` |
| `0x43b6d796` → `0x439d143c` | **SA open** (`ExecuteOpenMSG`) | `0x439cea30`, `0x439cf3b8` |
| `0x43b6d77c` → `0x439d133c` | **SA close** (`ExecuteCloseMSG`) | `0x439cea30`, `0x439cebe4`, `0x439cf3b8` |
| `0x43b6d7a8` → `0x439d185c` | **`ExecuteCalcStartMSG`** (arranque del cálculo en el SA) | `0x439ceeb8` |
| `0x439d168c` | **`GetExecUnit`** (nombre propio `GetExecUnit` `0x43ced643`) → la traza lo llama "GetZimaNo" | `0x439ceeb8` |
| `0x439d1bd0` | **`GetMemInfo`** (nombre propio `GetMemInfo` `0x43ced075`) | `0x439ceeb8` |
| `0x439d0f58` | **`CallocCamSaParam`** (nombre propio `0x43ced623`) | `0x439cea30` |
| `0x43b6d598` → `0x43903280` | **DMM Open** (S113) | `0x439cea30`, `0x439cedd0`, `0x439ceeb8` |
| `0x43b6d5ac` → `0x43903414` | **DMM Close** (S113) | `0x439cebe4` |
| `0x43b6d5b4` → `0x43902fbc` | **DMM Free** (S113) | `0x439cedd0` |

Secuencia de la ejecución (`0x439ceeb8`):

```
0x439cef0a  bl 0x439d168c  ; GetExecUnit      -> "GetZimaNo Err %d"
0x439cef46  bl 0x43b6d598  ; DMM open         -> "Open Err3 (unit_hndl:0x%x)"
0x439cef90  bl 0x439d1bd0  ; GetMemInfo #1    -> "GetMemInfo Err1" / "`HME_BaseTar_Addr' invalid"
0x439ceff8  bl 0x439d1bd0  ; GetMemInfo #2    -> "GetMemInfo Err2" / "`HME_BaseRef_Addr' invalid"
0x439cf066  bl 0x439d1bd0  ; GetMemInfo #3    -> "GetMemInfo Err3" / "`Work_Addr' invalid"
0x439cf0c0  bl 0x439d1bd0  ; GetMemInfo #4    -> "GetMemInfo Err4" / "`Vec_Addr' invalid"
0x439cf112  bl 0x439d1bd0  ; GetMemInfo #5    -> "GetMemInfo Err5" / "`Result_Addr' invalid"
                                                        / "`HME_BaseTar_LineAddAddr' invalid"
0x439cf18a  bl 0x43b7dc74  ; HW GetCoreNum    -> "HW GetCoreNum Err %d"
0x439cf1cc  bl 0x43b7dc26  ; HW SetMode       -> "HW SetMode Err %d"
0x439cf208  bl 0x43b5ea54  ; MmuMakeParam     -> "MmuMakeParam Err %d"
0x439cf2ca  bl 0x43b6d598  ; DMM open         -> "Open Err4 (unit_hndl:0x%x)"
0x439cf306  bl 0x43b6d7a8  ; ExecuteCalcStartMSG (arranque del calculo en el SA)
0x439cf310  cmp r3,#0x10   ; estado == 0x10  -> "HW TimeOut"  (0x439cf31c)
0x439cf32c  bl 0x43a2ff38  ; HW abort         -> "HW Abort Err %d"
0x439cf366  add r3, pc     ; "Output Ref Img" (éxito: se guarda la img de ref. de salida)
```

Los códigos de error devueltos por la función de cierre se ven en el código: `r5 = 2` (fallo al
cerrar un handle), `r5 = 8` (fallo al cerrar el HW, `0x439ced70`), `r5 = 6` (rama sin abrir,
`0x439cf1d6`).

**Las tres funciones del SA se autoidentifican** (pasan su nombre como `%s` del formato de
traza), lo que permite nombrarlas sin inventar:

| función | auto-nombre (dirección) | cómo |
|---|---|---|
| `0x439d0f58` | `CallocCamSaParam` `0x43ced623` | `add r5, pc` en `0x439d0f82` → `[CAMERA_SA]: %s: AllocNewWait error` |
| `0x439d168c` | `GetExecUnit` `0x43ced643` | `add r4, pc` en `0x439d16b8` → `[CAMERA_SA]: %s: ddl_saGetExecUnit error func_code[0x%x]` |
| `0x439d1bd0` | `GetMemInfo` `0x43ced075` | `add r5, pc` en `0x439d1bfa` → `[CAMERA_SA]: %s: Open error, mem_mgr_err = %x` |

Además `CallocCamSaParam` reserva la memoria con la API del **DMM**: llama a `0x439037c0`
(`AsyncAllocNew`, S113) y espera el resultado (`AllocNewWait error` `0x43ced0c2`).

---

## 8. Ficheros fuente

**El módulo `[APL]` no registra su fichero de origen.** Las 42 trazas no llevan `file=%s line=%d`
y ninguna de las 5 funciones referencia un nombre de fichero (0 referencias `.cpp/.c/.h` desde
`0x439ce900`–`0x439cf430`).

Los nombres de fichero más próximos **no** le pertenecen:

| nombre | dirección | a qué pertenece |
|---|---|---|
| `ScalarInfraSuperStableMovieManager.cpp` | `0x43ceb0aa` | bloque `[SFRS]` (S116), 1 KB antes del bloque `[APL]` |
| `Stage_Apollo.cpp` | `0x43cc6e0f` | `[IMAGING_CAP]` / Stage_Apollo (S106) |
| `Apollo.cpp` | `0x43cc6e15` | `[IMAGING_CAP]` (S106); **sin referencia PIC localizada** |

**NO VERIFICADO:** el/los fichero(s) reales que implementan el módulo `[APL]`. Lafw3.21 no los
embebe en la zona del módulo.

---

## 9. Relación con CamCore (S107), el SA (S108) y el gestor de captura (S106)

| módulo | relación con `[APL]` | evidencia |
|---|---|---|
| **SA** (`[CAMERA_SA]`, S108; API `sa_func_*`, S84) | **inferior**: `[APL]` es **cliente** del driver `Camera::SaFuncDrv` (implementación en `0x439d0f00`–`0x439d1e40`). Usa `CallocCamSaParam`, `GetMemInfo`, `GetExecUnit`, `ExecuteOpenMSG`, `ExecuteCloseMSG`. A su vez el SA usa el MMU (`Mmu - SA_MMU_NUM_MEM_ERR` `0x43cf0c15`) | llamadas `bl` de §7 |
| **DMM** (`[CAM_DMM]`, S113) | **inferior**: los `unit_hndl` son handles de unidad del DMM (`Open` `0x43903280`, `Close` `0x43903414`, `Free` `0x43902fbc`, todos dentro del bloque del DMM `0x439011d8`–`0x43903d5c`) | thunks `0x43b6d598/5ac/5b4` |
| **CamCore** (`[CAMCORE]`, S107) | **sin relación directa**: CamCore **no** llama a ninguna de las 5 funciones del módulo `[APL]` (cada una tiene **un único** llamador, en `[CAMERA_MAIN_TC]`). Ambos son clientes del mismo SA y comparten el gestor de memoria | búsqueda de `bl` a `0x439cea30/0x439cebe4/0x439cedd0/0x439ceeb8/0x439cf3b8`: 1 sitio cada uno, ninguno en la zona de CamCore |
| **Gestor de captura** (`[IMAGING_CAP]`, S106) | **sin relación directa**: `[IMAGING_CAP]` no llama al módulo `[APL]`. Lo que sí comparte es el SA (`sa_func_*`) y el bloque "Apollo" (`Stage_Apollo.cpp`, `ApolloSA_Main`, `[CAMERA_MAIN_TC]: APL_MEM_INFO …` `0x43cb6b10`, `[CAMERA_MAIN_TC]: APL_IMG_INFO …` `0x43cb6b57`, `[CAMERA_MAIN_TC]: APL_PANORAMA_INFO …` `0x43cb6b8b`) | ídem + las trazas `[CAMERA_MAIN_TC]: APL_*` |

### 9.1 El consumidor real: `[CAMERA_MAIN_TC]` ("ApolloSA")

Las 5 funciones del módulo tienen **un único llamador cada una**, y todos están en la zona
`[CAMERA_MAIN_TC]`:

| función del módulo | llamador | traza del consumidor |
|---|---|---|
| `0x439cf3b8` (SA open/close) | `0x438765ca` (fn `0x438765c8`) | `TC:APL:Err: SA Preload %d` `0x43cb700e` |
| `0x439cea30` (Open) | `0x43876650` (fn `0x438765fc`) | `TC:APL:Err: SA Acquire %d` `0x43cb703a` |
| `0x439ceeb8` (Open+exec) | `0x438766da` (fn `0x438765fc`) | `TC:APL:Err: SA Start %d %d` `0x43cb7092` |
| `0x439cebe4` (Close) | `0x43876714` (fn `0x438765fc`) | `TC:APL:Err: SA release1 %d` `0x43cb70bf` |
| `0x439cedd0` (Free & Close) | `0x43876a82` (fn `0x43876a80`) | `TC:APL:Err: SA release2 %d` `0x43cb714d` |

El consumidor también gestiona, con el mismo prefijo, `SA Prm Open2` `0x43cb71d0`, `SA Rslt Open`
`0x43cb71fb`, `SA Vect Open` `0x43cb7226`, `SA Prm Close2` `0x43cb7251`, `SA Rslt Close`
`0x43cb727d`, `SA Vect Close` `0x43cb72a9`, `SA ChkRslt %d` `0x43cb7121`, y los límites
`ApolloSA_Main(start)` `0x43cb6ac7` / `ApolloSA_Main(end)` `0x43cb6c0d` /
`ApolloSA_Fin(start)` `0x43cb6cc5` / `ApolloSA_Fin(end)` `0x43cb6cee` /
`ApolloSA_Cancel(start)` `0x43cb6c6f` / `ApolloSA_Cancel(end)` `0x43cb6c9b`. Es decir: **la APL es
el motor que el pipeline de vídeo (`[CAMERA_MAIN_TC]`) usa como coprocesador de imagen**, y el
"ApolloSA" es su nombre en ese módulo.

**Nota de alcance:** el módulo `[CAMERA_MAIN_TC]` **no** es un hito anterior; queda pendiente
reconstruirlo por separado.

---

## 10. Diferencial A6000 fw3.21 vs A7S fw3.20

| | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| cadenas con `[APL]` | **42** (`0x43cebde1`–`0x43cec4fe`) | **42** (`0x43ce1588`–`0x43ce1a90`) |
| prefijo de módulo | `"[CAMERA_SA]: "` en las 42 | **ninguno**: las 42 empiezan por `[APL]` |
| **comunes texto a texto** | — | **42 / 42** |
| exclusivas de la A6000 | — | **0** |
| exclusivas de la A7S | — | **0** |
| estructura | 5 funciones (7/9/4/20/2 trazas) | **idéntica**: `0x439bcd80` (7), `0x439bcea0` (9), `0x439bcfc8` (4), `0x439bd05c` (20), `0x439bd3a4` (2) |
| llamadores | 1 por función, en `[CAMERA_MAIN_TC]` (`0x4387xxxx`) | 1 por función, en `0x43870bf6`/`0x43870c64`/`0x43870ccc`/`0x43870cf2`/`0x43870fb2` |
| módulo `[CAMERA_MAIN_TC]` | 1 (con prefijo) | **0** (los mismos mensajes `TC:APL:Err: …` existen sin prefijo, p.ej. `0x43cb6cdc`) |

→ **El módulo `[APL]` es el mismo en la A6000 fw3.21 y en la A7S fw3.20**: mismas 42 cadenas,
misma máquina de estados de 5 funciones, mismo consumidor. La fw3.21 de la A6000 **sólo añade la
etiqueta de módulo `"[CAMERA_SA]: "`** (el mismo patrón que S108 ya documentó para las 231 trazas
de `[CAMERA_SA]`).

**A6300 fw2.01** (verificado por búsqueda de texto): **42** cadenas `[APL]`, **42/42** comunes con
la A6000, 0 exclusivas.

---

## 11. Nota metodológica: regla PIC canónica vs. estricta

Las cadenas **no** se apuntan con punteros absolutos: el código hace `ldr rX,[pc,#imm]` + `add rX,pc`
(destino = `W + (dir_add + 4)`). Aplicada la regla canónica del repo (probar **todos** los `ldr`
del registro dentro de 4 KB y aceptar sólo destinos en el **inicio** de una cadena), las 42 trazas
dan **67 pares (traza, sitio)** frente a los **42** de la regla estricta (`ldr` más cercano por
debajo): **25 pares sobrantes**, todos ellos **falsos positivos** comprobados desensamblando:

* `0x439b1eea` (`Close Err5`) — el sitio referencia en realidad
  `[SFRS][ERR] ***SUPERSTABLEMOVIE_VFXOUTPUTMEM_SHARE_FAILED, 0x%x` (`0x43ceb7cd`);
* `0x439b288e` (`HME_BaseTar_Addr`) — el `ldr` más cercano resuelve a `0x43f35894` (puntero, no cadena);
* `0x439b297a` (`Work_Addr`) — el `ldr` más cercano resuelve a `vfx result error:%x` (`0x43c8f302`);
* `0x439cd498` (`HW Abort Err`) — el `ldr` más cercano resuelve a `0x43f39d64` (puntero, no cadena);
* los 21 restantes caen dentro de la misma función y son el "segundo" `add` del bloque de error
  (el que imprime el texto sin etiqueta), que la regla canónica empareja con el `ldr` de otra traza.

**Conclusión del hito:** para este módulo la regla estricta (=`ldr` más cercano) da el mapa
función→traza exacto y 1:1; la canónica añade ruido. El mapa canónico completo queda en
`analysis/s119_apl/apl.json` → `canon_false_positives`.

---

## 12. NO VERIFICADO / abierto

1. **Significado de `APL`, `HW`, `SA`, `HME`, `MMU`, `Zima`**: el firmware no expande ninguna de
   estas siglas. Lo único verificado es el nombre de negocio "**ApolloSA**" que usa el consumidor
   `[CAMERA_MAIN_TC]`.
2. **Identidad de las funciones del bloque HW** (`0x43b7db64` open, `0x43b7dbd6` close,
   `0x43b7dc74` GetCoreNum, `0x43b7dc26` SetMode, `0x43b5ea54` MmuMakeParam, `0x43a2ff38`
   abort): **no hay ninguna cadena de nombre** en el firmware que las identifique; los nombres
   usados aquí proceden de las trazas que las invocan.
3. **`GetZimaNo` vs `GetExecUnit`**: la traza `GetZimaNo Err %d` (`0x43cec14d`) se emite tras
   llamar a `0x439d168c`, que se autodenomina `GetExecUnit`. **Por qué el mensaje dice "Zima"**
   (¿el número de unidad *Zima*? ¿un canal?) queda sin explicar.
4. **Layout y tamaño de `InputPrm`** y de las 6 direcciones `HME_*`/`Work_Addr`/`Vec_Addr`/
   `Result_Addr`: sólo se sabe que las devuelve `GetMemInfo` y que se validan con máscaras
   (`and.w` en `0x439cefba`, `0x439cf162`, `0x439cf13c`).
5. **Fichero fuente del módulo**: no está embebido (ver §8).
6. **Relación con `Camera::CamCore`** (S107): verificada la **ausencia** de llamadas directas, pero
   no está verificado si comparten algún recurso de HW o una cola común.
7. **Valores numéricos** de los códigos de error que devuelve la APL (`2`, `6`, `8`, `0xff`): no hay
   tabla de meanings en el firmware.
8. **El módulo `[CAMERA_MAIN_TC]`** (el consumidor) no está reconstruido: es un hito pendiente.
9. La A7S/A6300 tienen las 42 cadenas en otro lugar del blob; no se ha comprobado si su *código*
   es idéntico byte a byte (sólo la estructura de 5 funciones y los textos).

---

## 13. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## 14. Reproducibilidad

| artefacto | qué hace |
|---|---|
| `analysis/s119_apl/scan_pic_refs_local.py` | escáner PIC (regla canónica) limitado a la zona de datos `0x43c90000`–`0x43d00000` → `pic_refs.json` |
| `analysis/s119_apl/map_funcs.py` | mapa PIC estricto vs. canónico de las 42 trazas → `apl_map.json` |
| `analysis/s119_apl/annotate_code.py` | desensamblado anotado con la cadena resuelta (estricta y canónica) |
| `analysis/s119_apl/find_callers.py` | busca los `bl` que apuntan a un conjunto de funciones → `callers.json` |
| `analysis/s119_apl/a7s_map.py` | mapa del módulo en la A7S fw3.20 → `apl_a7s_map.json` |
| `analysis/s119_apl/build_apl_json.py` | genera `analysis/s119_apl/apl.json` (datos estructurados) |
| `analysis/s119_apl/disasm_apl_*.txt` | desensamblados anotados del cluster del módulo (open / close / free&close / exec / SA) |
| `tests/test_s119_apl.py` | 47 tests sobre bytes reales (direcciones, textos, recuentos, PIC, llamantes) |

---

## Revisión del agente principal (21-10-2026)

**Verificado byte a byte (correcto) — y es un hallazgo estructural:**

1. **Las 42 apariciones de `[APL]` NO son un módulo propio**: las 42 están **dentro** de
   mensajes que empiezan por `"[CAMERA_SA]: "` (prefijo de 13 bytes), es decir
   `"[CAMERA_SA]: [APL] HW Open Err %d"` `0x43cebde1`, `"[CAMERA_SA]: [APL] SA Open Err"`
   `0x43cebe03`, `"[CAMERA_SA]: [APL] Calloc InputPrm Err"` `0x43cebe46`… Ninguna cadena
   *empieza* por `[APL]`. → **`[APL]` es una etiqueta de segundo nivel dentro de
   `[CAMERA_SA]`**, y la entrada "APL 42" del mapa de módulos de S79 es una sub-etiqueta, no
   un módulo independiente.
2. **Diferencial A7S fw3.20** (verificado): allí las 42 cadenas **sí empiezan** por `[APL]`
   (`[APL] HW Open Err %d` `0x43ce1588`, `[APL] SA Open Err` `0x43ce159d`…) → en la A6000 la
   fw3.21 antepone la etiqueta de módulo `[CAMERA_SA]: ` **delante** de la de sub-módulo
   `[APL]`. Es un cambio de **instrumentación**, no de funcionalidad: los 42 textos coinciden
   uno a uno.
3. **Mapa**: 5 funciones emisoras (`0x439cea30` Open 7, `0x439cebe4` Close 9, `0x439cedd0`
   Free&Close 4, `0x439ceeb8` Open+ejecución 20, `0x439cf3b8` SA open/close 2) con **42/42
   referencias PIC 1:1** bajo la regla estricta, y las 5 funciones equivalentes en la A7S
   (`0x439bcd80`, `0x439bcea0`, `0x439bcfc8`, `0x439bd05c`, `0x439bd3a4`).
4. **Consumidor único**: `[CAMERA_MAIN_TC]` ("ApolloSA"), con **un solo llamador** por función
   (`0x438765ca`, `0x43876650`, `0x438766da`, `0x43876714`, `0x43876a82`); ni `[IMAGING_CAP]`
   (S106) ni `CamCore` (S107) lo llaman.
5. **Aporte metodológico**: el subagente comprobó desensamblando que la regla "ancha" da
   **67** pares para 42 cadenas reales → **25 falsos positivos** (p. ej. `0x439b1eea` resuelve a
   un mensaje de `[SFRS]` y `0x439b288e`/`0x439cd498` a punteros que no son cadenas). Es la
   **tercera** calibración independiente que confirma que la regla canónica debe ser la
   **estricta** (`[SFRA]` 118, `[AIP]` 37, `[APL]` 42: los tres coinciden exactamente con la
   verificación a mano).
