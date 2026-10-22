# S132 — el módulo `[CLK_CTRL]` (66 trazas): el control de reloj de la fw3.21 de la A6000

**Hito:** S132 · **Base:** `vaddr = 0x43541000 + file_offset` · **Firmware:** A6000 fw3.21
(`analysis/rea-independent/input/av-cam.bin`, 11 427 236 B)
**Regla de referencias:** **estricta** (canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`, mapa global
`analysis/s106_imaging_cap/pic_refs_strict_global.json`).
**Script de este hito:** `analysis/s132_clk_ctrl/scan_clk_ctrl.py` (cadenas, sub-bloques,
referencias, differential) y `analysis/s132_clk_ctrl/scan_callers.py` (llamadores de la API).
**Salida estructurada:** `analysis/s132_clk_ctrl/clk_ctrl.json`, `analysis/s132_clk_ctrl/callers.json`.

---

## 1. Resumen

* `[CLK_CTRL]` es el **etiquetado de un subsistema ya existente**, no un módulo nuevo:
  el gestor de control de reloj (**ClkCtrl**) de la A6000, expuesto como **14 funciones
  DDL** (`ddl_clkctrl_*`), con **tarea propia**, **máquina de estados**, **arbitraje
  entre subsistemas** (abrir/cerrar el reloj, bloquear/desbloquear la señal de sync) y
  **intercambio de mensajes maestro/esclavo**.
* Las **66 trazas** viven en un bloque contiguo de rodata: `0x43c3a1df`–`0x43c3b09c`.
  Con la regla estricta: **62/66 referenciadas**, **85 sitios de emisión**,
  **36 funciones** emisoras, todas dentro de un único cluster de código
  `0x4359ee24`–`0x435a1150` (~9 KB). **4 cadenas sin referencia** (ver § 8).
* La fw3.21 de la A6000 es la **única de las tres** con este etiquetado: los **66 núcleos
  de mensaje (66/66) no existen** ni en la A7S fw3.20 ni en el A6300 fw2.01. Pero los
  tres firmwares comparten **la misma tabla de 14 nombres de API DDL** y las mismas
  funciones de inicialización (`init_cam_clkctrl`) → **lo nuevo es la instrumentación
  (trazas + traza de la llamada DDL), no la funcionalidad** (ver § 7).
* **Para la línea del obturador:** el módulo **no menciona el obturador** en ninguna de
  sus 66 trazas (0 apariciones de `shut`/`shutter`/`silen`), **no hay ningún obturador
  electrónico aquí** y **no fija frecuencias en Hz ni divisores**: fija (a) un **tipo de
  reloj** (`CLKTYPE`: 24P/25P/30P/50I/50P/60I/60P) y (b) un **retardo de sincronía
  vertical** (`sysv_delay`, en **µs**). Sí es relevante de forma **indirecta**: el
  `sysv_delay` y el `CLKTYPE` gobiernan la duración del frame y, por tanto, el presupuesto
  temporal de la exposición y de la lectura (ver § 6).

## 2. Qué es `[CLK_CTRL]`

**VERIFICADO por bytes:**

| Hecho | Evidencia |
|---|---|
| El módulo se llama `ClkCtrl` | cadena `"ClkCtrl"` en `0x43c3aef0`, referenciada en `0x435a0c58` (registro del módulo) |
| Es un módulo **DDL** (capa de driver) con API numerada | `"CALL CB3"` `0x43c3acae` + tabla `"N)ddl_clkctrl_…"` `0x43c3acb7`–`0x43c3ae86`, desensamblados en el despachador `0x435a0880` |
| Corre en una **tarea propia** | `"[CLK_CTRL]: Tsk ClkCtrl Initial"` `0x43c3a5ff` (f. `0x4359f7b4`) y `"[CLK_CTRL]: Main routine start!!"` `0x43c3a61f` (f. `0x4359f7d8`); la tarea se crea en `0x4359ed30` (`bl 0x439b4244`) |
| El log usa el **id de módulo 0xc0** | todas las llamadas al emisor pasan `movs r0,#0xc0` (p. ej. `0x4359ee50`, `0x4359f9ea`, `0x435a0d94`) |
| La sigla **CLK_CTRL no se desarrolla** en ningún byte | 0 apariciones de una expansión ("clock control"…) en la imagen; no se inventa significado |
| El prefijo `ddl_` es una **convención del firmware**, no inventada | 6 familias con prefijo `ddl_`: `bgm`, `clkctrl`, `jpeg`, `srotate`, `stitch`, `vio`; el token `DDL` aparece en el binario (`DDL_FDET_TIMEINFO` `0x43c6328c`, `"ABB SYSND DDL set_mute err"` `0x43cdf0d3`). **Su desarrollo no aparece**: NO VERIFICADO |

**Contenido funcional (todo VERIFICADO por traza y por desensamblado):**

1. **Arbitraje de subsistemas** — cada consumidor debe **abrir** el reloj antes de
   tocarlo: `open_clk(id)` / `close_clk(id)`, con los errores
   `"[ERR]Busy!! 0x%04x already opened, 0x%04x can't open"` (`0x43c3a93d`) y
   `"[ERR]0x%04x request open... CLK already opend by 0x%04x"` (`0x43c3a9e4`).
   El mismo patrón para el **retardo**: `open_dly`/`close_dly` y
   `"0x%04x request open... DELAY already opend by 0x%04x"` (`0x43c3aa28`).
2. **Tipo de reloj (`CLKTYPE`)** — `set_sync_signal(id, clk)` cambia el reloj;
   `"[CLK_CTRL]: clk_now=%d, ret=%d, id=0x%x, clk_req=%d, L=%d"` `0x43c3b034` (f. `0x435a0f04`)
   y `"[CLK_CTRL]: CHANGE_CLK dly 0x%x -> 0x%x , clk 0x%x -> 0x%x : change_vfc=0x%x"`
   `0x43c3a71b` (f. `0x4359f9c0`).
3. **Retardo de sincronía vertical (`SYSV_DELAY`, µs)** —
   `set_sysv_delay(id, delay)`; `"[CLK_CTRL]: set sysv delay subsystem = %x , delay = %d"`
   `0x43c3af89` (f. `0x435a0d60`); límites `"[ERR]normal_delay MAX OVER:0x%08x"`
   `0x43c3b06e` y `"[ERR]special_delay MAX OVER:0x%08x"` `0x43c3b09c` (f. `0x435a1142`).
4. **Bloqueo de la señal de sincronía** — `lock_sync_signal(id, clk)` /
   `unlock_sync_signal(id)`; `"lock_sync_signal subsystem = %x"` `0x43c3a5a5` (f. `0x4359f4f8`).
   Mientras está bloqueada, `set_sysv_delay` devuelve
   `"[ERR]CLKCTRL_ERR_BUSY...State is LOCK L=%d"` `0x43c3af24` (f. `0x435a0d60`).
5. **Máquina de estados** (5 estados + default), § 5.
6. **Secuencia de cambio de reloj** — `ClkChgExec` (`0x4359fb24`) y
   `DelayChgExec` (`0x4359fc14`).
7. **Intercambio maestro/esclavo** — `"Receive Message from Master src=0x%0x"`
   `0x43c3abd0` (f. `0x435a0596`) y `"Send Message to Slave 0x%0x"` `0x43c3ac86`
   (f. `0x435a0734`); los mensajes llevan `targetVfc` y `delay_req`
   (`0x43c3ac02`) y el reparto de frecuencia vertical `m_vfc.main` / `m_vfc.sub`
   (`0x43c3ac2f`).

## 3. Inventario de las 66 trazas

Rango: `0x43c3a1df` – `0x43c3b09c` (contiguo). Sub-bloques:

| Sub-bloque | n | Contenido |
|---|---|---|
| `DDL_CALL` | 12 | `Call:ddl_clkctrl_*(…)` — una traza por envoltorio de la API |
| `CHANGE_CLK` | 9 | secuencia de cambio de reloj (`STATE_CHANGE_CLK`, `CHANGE_CLK`, `ClkChgExec`, `DelayChgExec`) |
| `OSAL_ERR` | 10 | errores de OSAL (semáforos y mensajes) |
| `SET_DELAY_SYNC` | 8 | ajuste de retardo/señal, errores de estado y de rango |
| `SUBSYS_OPEN_CLOSE` | 6 | apertura/cierre y conflictos de subsistema |
| `MSG_MASTER_SLAVE` | 6 | mensajes maestro/esclavo |
| `VPH_HTP` | 5 | estado del VPH, `10Count`/`subVFC`, envío de `HTP` |
| `STATE` | 3 | `STATE_INIT1`, `STATE_NORMAL`, `STATE_LOCK` |
| `OTROS` | 3 | cadenas **sin referencia** (§ 8) |
| `LOCK` | 2 | `lock/unlock_sync_signal subsystem` |
| `TASK` | 2 | `Tsk ClkCtrl Initial`, `Main routine start!!` |

### 3.1 Tabla completa (dirección · sub-bloque · sitios · función(es) · texto)

| vaddr | sub-bloque | n | función(es) emisoras | texto |
|---|---|---|---|---|
| `0x43c3a1df` | DDL_CALL | 1 | `0x4359ee24` | `Call:ddl_clkctrl_get_clk_chg_enable(0x0%x),ret=0x%0x` |
| `0x43c3a220` | DDL_CALL | 1 | `0x4359ee78` | `Call:ddl_clkctrl_unlock_sync_signal(0x0%x),ret=0x%0x` |
| `0x43c3a261` | DDL_CALL | 1 | `0x4359eed0` | `Call:ddl_clkctrl_lock_sync_signal(0x0%x,0x0%x),ret=0x%0x` |
| `0x43c3a2a6` | DDL_CALL | **0** | — | `Call:ddl_clkctrl_set_sysv_delay_changing(0x0%x,0x0%x),ret=0x%0x` |
| `0x43c3a2f2` | DDL_CALL | 1 | `0x4359ef2c` | `Call:ddl_clkctrl_set_sysv_delay(0x0%x,0x0%x),ret=0x%0x` |
| `0x43c3a335` | DDL_CALL | 1 | `0x4359ef88` | `Call:ddl_clkctrl_set_sync_signal(0x0%x,0x0%x),ret=0x%0x` |
| `0x43c3a379` | DDL_CALL | 1 | `0x4359f000` | `Call:ddl_clkctrl_set_sync_initial_signal(0x0%x),ret=0x%0x` |
| `0x43c3a3bf` | DDL_CALL | 1 | `0x4359f048` | `Call:ddl_clkctrl_set_sysv_initial_delay(0x0%x,0x0%x),ret=0x%0x` |
| `0x43c3a40a` | DDL_CALL | 1 | `0x4359f09c` | `Call:ddl_clkctrl_close_dly(0x0%x),ret=0x%0x` |
| `0x43c3a442` | DDL_CALL | 1 | `0x4359f0e4` | `Call:ddl_clkctrl_open_dly(0x0%x),ret=0x%0x` |
| `0x43c3a479` | DDL_CALL | 1 | `0x4359f12c` | `Call:ddl_clkctrl_close_clk(0x0%x),ret=0x%0x` |
| `0x43c3a4b1` | DDL_CALL | 1 | `0x4359f174` | `Call:ddl_clkctrl_open_clk(0x0%x),ret=0x%0x` |
| `0x43c3a4e8` | OSAL_ERR | 8 | `0x4359f2b4`,`0x4359f360`,`0x4359f4f8`,`0x4359f5f4`,`0x435a01a0`,`0x435a0362` | `[ERR]OSAL_SEM_ERR %08x L=%d` |
| `0x43c3a510` | SET_DELAY_SYNC | 2 | `0x4359f2b4`,`0x4359f360` | `[ERR]State Error:0x%02x` |
| `0x43c3a534` | STATE | 1 | `0x4359f2b4` | `State:STATE_INIT1(InitDelay)` |
| `0x43c3a55d` | STATE | 1 | `0x4359f360` | `State:STATE_NORMAL(InitSignal)` |
| `0x43c3a588` | STATE | 1 | `0x4359f4f8` | `State:STATE_LOCK` |
| `0x43c3a5a5` | LOCK | 1 | `0x4359f4f8` | `lock_sync_signal subsystem = %x` |
| `0x43c3a5d1` | LOCK | 1 | `0x4359f5f4` | `unlock_sync_signal subsystem = %x` |
| `0x43c3a5ff` | TASK | 1 | `0x4359f7b4` | `Tsk ClkCtrl Initial` |
| `0x43c3a61f` | TASK | 1 | `0x4359f7d8` | `Main routine start!!` |
| `0x43c3a640` | OSAL_ERR | 2 | `0x4359f7d8`,`0x435a01a0` | `[ERR] osal rcv err %08x L=%d` |
| `0x43c3a669` | OSAL_ERR | 1 | `0x4359f87c` | `[ERR]osal_sig_sem 0x%08x L=%d` |
| `0x43c3a693` | SET_DELAY_SYNC | 1 | `0x4359f908` | `set sync signal... clk = %d` |
| `0x43c3a6bb` | OSAL_ERR | 2 | `0x4359f908` | `[ERR]osal_try_wai_sem 0x%08x L=%d` |
| `0x43c3a6e9` | CHANGE_CLK | 1 | `0x4359f9c0` | `tsk state = STATE_CHANGE_CLK , L = %d` |
| `0x43c3a71b` | CHANGE_CLK | 2 | `0x4359f9c0` | `CHANGE_CLK dly 0x%x -> 0x%x , clk 0x%x -> 0x%x : change_vfc=0x%x` |
| `0x43c3a768` | CHANGE_CLK | 1 | `0x4359f9c0` | `tsk state = STATE_CHANGE_CLK_LOCKING , L = %d` |
| `0x43c3a7a2` | CHANGE_CLK | 1 | `0x4359f9c0` | `CHANGE_CLK2 dly %x -> %x , clk %x -> %x` |
| `0x43c3a7d6` | CHANGE_CLK | 1 | `0x4359f9c0` | `clk_now=%d, clk_next=%d, change_vfc=0x%x, L=%d` |
| `0x43c3a811` | CHANGE_CLK | 1 | `0x4359fb24` | `ClkChgExec at %x clk=%x, delay=%x->%x` |
| `0x43c3a843` | CHANGE_CLK | 1 | `0x4359fb7e` | `tsk state = %d(%d:NORMAL,%d:LOCK) , L = %d` |
| `0x43c3a87a` | CHANGE_CLK | 1 | `0x4359fb7e` | `clk_now=%x, clk_next=%x, delay_now=%x, change_vfc=0x%x, L=%d` |
| `0x43c3a8c3` | CHANGE_CLK | 1 | `0x4359fc14` | `DelayChgExec at 0x%x, delay=%x` |
| `0x43c3a8ee` | OSAL_ERR | 4 | `0x4359fd90`,`0x4359fe44`,`0x435a0d60`,`0x435a0f04` | `[ERR]osal_wai_sem_tmo %08x L=%d` |
| `0x43c3a91a` | SUBSYS_OPEN_CLOSE | 1 | `0x4359fd90` | `open subsytem = 0x%04x` |
| `0x43c3a93d` | SUBSYS_OPEN_CLOSE | 1 | `0x4359fd90` | `[ERR]Busy!! 0x%04x already opened, 0x%04x can't open` |
| `0x43c3a97e` | SUBSYS_OPEN_CLOSE | 1 | `0x4359fe44` | `close subsytem = 0x%04x` |
| `0x43c3a9a2` | SUBSYS_OPEN_CLOSE | 1 | `0x4359fe44` | `[ERR]Busy!! 0x%04x already opend...0x%04x can't close` |
| `0x43c3a9e4` | SUBSYS_OPEN_CLOSE | 1 | `0x4359fef6` | `[ERR]0x%04x request open... CLK already opend by 0x%04x` |
| `0x43c3aa28` | SUBSYS_OPEN_CLOSE | 1 | `0x4359ff3e` | `0x%04x request open... DELAY already opend by 0x%04x` |
| `0x43c3aa69` | VPH_HTP | 2 | `0x435a007c` | `vph stat:%d,mode:%d` |
| `0x43c3aa89` | VPH_HTP | 1 | `0x435a007c` | `10Count:%d, subVFC:%d` |
| `0x43c3aaab` | VPH_HTP | 1 | `0x435a007c` | `10Count:%d` |
| `0x43c3aac2` | VPH_HTP | 1 | `0x435a01a0` | `Now:0x%08x,target:0x%08x` |
| `0x43c3aae7` | VPH_HTP | 1 | `0x435a01a0` | `Send HTP at 0x%08x` |
| `0x43c3ab06` | OSAL_ERR | 2 | `0x435a0510`,`0x435a0734` | `[ERR] osal_try_valloc_msg 0x%0x` |
| `0x43c3ab32` | OSAL_ERR | 2 | `0x435a0510`,`0x435a0734` | `[ERR] osal_snd_msg 0x%0x` |
| `0x43c3ab57` | OSAL_ERR | 2 | `0x435a0510`,`0x435a0734` | `[ERR] osal_free_msg 0x%0x` |
| `0x43c3ab7d` | OSAL_ERR | 1 | `0x435a0596` | `[ERR] osal_rcv_msg 0x%0x` |
| `0x43c3aba2` | MSG_MASTER_SLAVE | 2 | `0x435a0596` | `[ERR] unknown message?? src=0x%0x` |
| `0x43c3abd0` | MSG_MASTER_SLAVE | 1 | `0x435a0596` | `Receive Message from Master src=0x%0x` |
| `0x43c3ac02` | MSG_MASTER_SLAVE | 2 | `0x435a0596`,`0x435a0734` | `targetVfc=0x%0x, delay_req=0x%0x` |
| `0x43c3ac2f` | MSG_MASTER_SLAVE | 2 | `0x435a0596`,`0x435a0734` | `m_vfc.main=0x%0x, m_vfc.sub=0x%0x` |
| `0x43c3ac5d` | MSG_MASTER_SLAVE | 1 | `0x435a0734` | `[ERR] SndMsgPublic request??` |
| `0x43c3ac86` | MSG_MASTER_SLAVE | 1 | `0x435a0734` | `Send Message to Slave 0x%0x` |
| `0x43c3aef8` | OSAL_ERR | 3 | `0x435a0d60` | `[ERR]osal_try_wai_sem %08x L=%d` |
| `0x43c3af24` | SET_DELAY_SYNC | 1 | `0x435a0d60` | `[ERR]CLKCTRL_ERR_BUSY...State is LOCK L=%d` |
| `0x43c3af5b` | SET_DELAY_SYNC | 1 | `0x435a0d60` | `Delay is no change(delay=%x) L=%d` |
| `0x43c3af89` | SET_DELAY_SYNC | 1 | `0x435a0d60` | `set sysv delay subsystem = %x , delay = %d` |
| `0x43c3afc0` | OTROS | **0** | — | `[ERR]dly_now = 0.5 L=%d` |
| `0x43c3afe4` | OTROS | **0** | — | `[ERR]clk_now = %x L=%d` |
| `0x43c3b007` | OTROS | **0** | — | `[ERR]Not Changing state= %x L=%d` |
| `0x43c3b034` | SET_DELAY_SYNC | 1 | `0x435a0f04` | `clk_now=%d, ret=%d, id=0x%x, clk_req=%d, L=%d` |
| `0x43c3b06e` | SET_DELAY_SYNC | 1 | `0x435a1142` | `[ERR]normal_delay MAX OVER:0x%08x` |
| `0x43c3b09c` | SET_DELAY_SYNC | 1 | `0x435a1142` | `[ERR]special_delay MAX OVER:0x%08x` |

### 3.2 Números de línea (`L=%d`)

Las trazas con `L=%d` son **números de línea del fichero fuente** (verificado: el valor
inmediato que se carga en el hueco de pila del último vararg). Valor **por traza**:
`0x43c3a640`→125, `0x43c3a669`→173, `0x43c3a6bb`→198/202, `0x43c3a6e9`→259,
`0x43c3a768`→270, `0x43c3a7d6`→286, `0x43c3a843`→365, `0x43c3a87a`→367,
`0x43c3a8ee`→68/146, `0x43c3aef8`→159/185/188, `0x43c3af24`→165, `0x43c3af5b`→172,
`0x43c3b034`→110. Verificación manual: `0x4359fa38 mov.w r3,#0x10e` (270) →
`"tsk state = STATE_CHANGE_CLK_LOCKING"`; `0x435a0fd0 movs r3,#0x6e` (110) →
`"clk_now=%d, ret=%d, …"`. El rango 68–367 corresponde a **un único `.cpp`** de ~400 líneas
(NO VERIFICADO: su nombre).

## 4. Las 36 funciones que referencian las trazas

Todas en el cluster `0x4359ee24`–`0x435a1150` (≈9 KB). Función → nº de cadenas:

`0x4359ee24` (1, `get_clk_chg_enable`) · `0x4359ee78` (1, `unlock_sync_signal`) ·
`0x4359eed0` (1, `lock_sync_signal`) · `0x4359ef2c` (1, `set_sysv_delay`) ·
`0x4359ef88` (1, `set_sync_signal`) · `0x4359f000` (1, `set_sync_initial_signal`) ·
`0x4359f048` (1, `set_sysv_initial_delay`) · `0x4359f09c` (1, `close_dly`) ·
`0x4359f0e4` (1, `open_dly`) · `0x4359f12c` (1, `close_clk`) · `0x4359f174` (1, `open_clk`) ·
`0x4359f2b4` (3, `STATE_INIT1`) · `0x4359f360` (3, `STATE_NORMAL`) · `0x4359f4f8` (3, `STATE_LOCK`) ·
`0x4359f5f4` (2, `unlock`) · `0x4359f7b4` (1, tarea) · `0x4359f7d8` (2, rutina principal) ·
`0x4359f87c` (1, semáforo) · `0x4359f908` (3, `set sync signal`) · `0x4359f9c0` (7, **cambio de reloj**) ·
`0x4359fb24` (1, `ClkChgExec`) · `0x4359fb7e` (2) · `0x4359fc14` (1, `DelayChgExec`) ·
`0x4359fd90` (3, `open subsytem`) · `0x4359fe44` (3, `close subsytem`) · `0x4359fef6` (1) ·
`0x4359ff3e` (1) · `0x435a007c` (5, VPH) · `0x435a01a0` (6, HTP) · `0x435a0362` (1) ·
`0x435a0510` (3, envío) · `0x435a0596` (6, recepción) · `0x435a0734` (6, envío a esclavo) ·
`0x435a0d60` (7, `set_sysv_delay`) · `0x435a0f04` (4, `set_sync_signal`) · `0x435a1142` (2, rango).

## 5. La máquina de estados

Estado guardado en `u8` en `+0x04` de la estructura de estado (lectura
`ldr r3,[r0,#4]` en `0x4359f9c8`). Los valores se deducen de las escrituras
`str rX,[r0,#4]` (`0x43a48772` = `str r1,[r0,#4]`):

| Valor | Estado | Evidencia |
|---|---|---|
| 1 | `STATE_INIT1` (InitDelay) | `movs r1,#1; bl 0x43a48772` en `0x4359f308` + traza `0x43c3a534` |
| 2 | `STATE_NORMAL` (InitSignal) | `movs r1,#2; bl 0x43a48772` en `0x4359f3b4` + traza `0x43c3a55d` |
| 3 | `STATE_CHANGE_CLK` | `movs r3,#3; str r3,[r0,#4]` en `0x4359f9de` + traza `0x43c3a6e9` |
| 4 | `STATE_CHANGE_CLK_LOCKING` | `movs r3,#4; str r3,[r0,#4]` en `0x4359fa34` + traza `0x43c3a768` |
| 5 | `STATE_LOCK` | `movs r1,#5; bl 0x43a48772` en `0x4359f548` + traza `0x43c3a588`; y `cmp r0,#5` en `0x435a0dde` → `"CLKCTRL_ERR_BUSY…State is LOCK"` |

Despachador de estados: `0x4359f9c0` (`subs r3,#2; cmp r3,#3; tbb [pc,r3]`):
estado 2 → 3 (`CHANGE_CLK`), 3 → 4 (`CHANGE_CLK_LOCKING`), 4 → trazas
`"CHANGE_CLK2 dly …"` + `"clk_now=%d, clk_next=%d, change_vfc=0x%x"`, 5 → rama
`"Not Changing state"` (rama cuyo texto **no** está cableado: ver § 8).

## 6. La API DDL y quién la usa

### 6.1 Tabla de 14 entradas (idéntica en los tres firmwares)

`"CALL CB3"` `0x43c3acae` + entradas `0x43c3acb7`–`0x43c3ae86`:

| id | nombre (fichero A6000) | id | nombre |
|---|---|---|---|
| 0 | `ddl_clkctrl_open_clk(id)` | 8 | `ddl_clkctrl_set_sysv_initial_delay(normal,special)` |
| 1 | `ddl_clkctrl_close_clk(id)` | 9 | `ddl_clkctrl_set_sync_initial_signal(CLKTYPE)` |
| 2 | `ddl_clkctrl_open_dly(id)` | 10 | `ddl_clkctrl_printf_info` |
| 3 | `ddl_clkctrl_close_dly(id)` | 12 | `total test clk->cly id,clk,dly_tsk` |
| 4 | `ddl_clkctrl_set_sync_signal(id , clk)` | 13 | `total test clk->lock id,clk` |
| 5 | `ddl_clkctrl_set_sysv_delay(id , delay)` | 14 | `total test lock->clk id,clk` |
| 6 | `ddl_clkctrl_lock_sync_signal(id)` | | |
| 7 | `ddl_clkctrl_unlock_sync_signal(id)` | | |

El **despachador** es `0x435a0880`: lee el id en `[r4+4]` y el arg1 en `[r4+8]`,
el arg2 en `[r4+0xc]` (vía `0x439c0640`) y salta a la implementación
(`cmp r0,#0…0xe`). Mapa **verificado desensamblando**:

`0`→`0x4359f174` · `1`→`0x4359f12c` · `2`→`0x4359f0e4` · `3`→`0x4359f09c` ·
`4`→`0x4359ef88` · `5`→`0x4359ef2c` · `6`→`0x4359eed0` · `7`→`0x4359ee78` ·
`8`→`0x4359f048` · `9`→`0x4359f000` · `10`→`0x43a486b6` (`printf_info`) ·
`11`/`12`→`set_sync_signal` + bucle de cambio de retardo (`0x4359ecc0`) ·
`13`→`set_sync_signal`+`lock_sync_signal` · `14`→`lock_sync_signal`.

### 6.2 Consumidores (verificado desensamblando los `bl`)

`analysis/s132_clk_ctrl/callers.json`:

| consumidor | id de subsistema | API que usa | módulo |
|---|---|---|---|
| `0x4378dfde` | **0x03** | open/close/lock/unlock/set_sync_signal | **CAMERA_MAIN_SYNC** |
| `0x4368b3e4` | 0x0a | open/close/set_sync_signal | **VDF** (`VdfDisplayCmdSetPanelOut.cpp`) |
| `0x436afba0` | 0x0d | open/close/set_sync_signal | **VEF** (efectos del finder) |
| `0x4366bd38` | 0xc2 | open/close/set_sync_signal | **SYSV / TP_R** |
| `0x4362840e` | 0x57 | open/close/set_sync_signal | shell MC (24P/25P/30P…) |
| `0x43628e98` | 0x57 | open/close/set_sync_signal | `McMsgAvscDec::ClockChange(FRAME_RATE)` (`mcMsgAvscDec.cpp`) |
| `0x43617f22` | 0x57 | open/close/set_sync_signal | comandos `clk_open`/`clk_chg`/`clk_close` |
| `0x43a79c60` | 0x57 | open/close/set_sync_signal | `McUtilMulti` |
| `0x43622d82` | dinámico (`ldrh [r0,#4]`) | set_sync_signal | `McAvcDecCmdParamCheck::CheckActDecParam1st` (`seqctrl/mcAvcDecCmdParamCheck.cpp`) |
| `0x43a4928a` | 0x10b | open/close/set_sync_signal | (no identificado) |
| `0x43a84942` | dinámico (`ldrh [r0,#4]`) | open/close | (no identificado) |
| `0x437947cc` | — | `set_sysv_initial_delay`, `set_sync_initial_signal` | **CAMERA_MAIN** `init_cam_clkctrl` (`init_cam_SetCamParam_main.cpp`) |
| `0x43ae8c66` | — | `get_clk_chg_enable` | (no identificado) |

### 6.3 Inicialización desde CAMERA_MAIN (relevante para la temporización)

`0x437947cc` (`init_cam_SetCamParam_main.cpp`; también cita `SystemDelay.cpp` `0x43ca3b6b`):

* `"[CAMERA_MAIN]: init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus"` `0x43ca3be5`
  (sitio `0x43794944`): el `CLKTYPE` llega **masked con `0x7f`** (`and r4,r3,#0x7f`
  en `0x43794924`).
* El retardo **normal** se calcula como `max(<0x43ad9076>() + 0x64, 0xfa0)` =
  **mínimo 4000 µs** (`0x437948c0`–`0x437948ce`); el **special** es
  `<0x43ae9154>()` (`0x4379495c`).
* Después `ddl_clkctrl_set_sysv_initial_delay(normal, special)` (`0x43794964`,
  r0 = retardo normal, r1 = retardo special) y
  `ddl_clkctrl_set_sync_initial_signal(CLKTYPE)` (`0x43794970`).

### 6.4 Valores de `CLKTYPE` (verificados)

En el shell MC (`0x4362840e`): `"clktype: 24P, 25P, 30P"` `0x43c72b87`, y las
cadenas `"24P"`, `"25P"`, `"30P"`, `"50I"`, `"60I"`, `"50P"`, `"60P"` más
`"[DEBUG] Current clock is …"` (`0x43c72c0a`–`0x43c72d77`) y
`"[DEBUG] CLKYPE is unknown (set 30P)."` (`0x43c72c12`).
El **agrupador** de tipos está en `0x43a4889a`/`0x43a488e2`/`0x43a48924`
(`cmp r1,#0xa; lsls r3,r1; tst r3,#0x37 / #0x7c0 / #8`) → tres familias de bits
(progresivo / entrelazado / otro).

## 7. Ficheros fuente

* **NO VERIFICADO — nombre del `.cpp` del propio módulo**: el módulo **no imprime
  `file=%s`** y en la A6000 **no existe ninguna cadena `.cpp` con "clk"** (búsqueda sobre
  los 11,4 MB: 0 resultados). Lo único localizable es el **número de línea** (§ 3.2) y el
  nombre de la clase/módulo `"ClkCtrl"` (`0x43c3aef0`).
* Ficheros **verificados** de los consumidores (§ 6.2): `init_cam_SetCamParam_main.cpp`
  (`0x43ca3c56`), `SystemDelay.cpp` (`0x43ca3b6b`), `mcMsgAvscDec.cpp` (`0x43c72f72`),
  `seqctrl/mcAvcDecCmdParamCheck.cpp` (`0x43c70df3`), `mcUtilMulti.cpp` (`0x43c704ca`),
  `VdfDisplayCmdSetPanelOut.cpp` (`0x43c8716b`).
* Otros ficheros citados por el propio subsistema: `mcMsgCore.cpp` (`0x43c6c164`),
  `mcMsgAvscEnc.cpp` (`0x43c732f6`).

## 8. Relación con el gestor de recursos y con la temporización de exposición

### 8.1 Con `CamResource` / `CamSyncResource` (S107/S112/S120)

* El CLK_CTRL **NO usa** el `SyncResMgr`: su arbitraje es **propio**, con un
  **id de subsistema de 4 hex** (`0x%04x`) y una tabla interna de entradas de 8 bytes
  entrada: `add.w r8, r7, r3, lsl #3` en `0x4359f568`, `ldrh r6,[r8,#4]` = clock bloqueado).
* Los ids de subsistema del reloj (**0x03, 0x0a, 0x0d, 0x57, 0xc2, 0x10b**) **no coinciden**
  con los ids de recurso del `SyncResMgr` (0x00–0x23: MODE_EE_0/1, IMAGER0, RC, VFX, APL,
  IDT_OPD, PBL/IIB…) → **son espacios de numeración distintos** (NO VERIFICADO si el
  firmware los mantiene separados por diseño o por herencia de otro módulo).
* Semántica equivalente de "recurso exclusivo": `open_clk(id)` es un *adquisición*,
  `close_clk(id)` una *liberación*, y los errores `"Busy!! … already opened"` son el
  equivalente funcional de `RC_ERR` del gestor de recursos, pero **con otro mecanismo**.

### 8.2 Con la temporización de exposición (`[CAMERA_MAIN_SYNC]`, S112/S124)

* El consumidor **más relevante es `CAMERA_MAIN_SYNC`** (`0x4378dfde`, subsistema **0x03**):
  abre el reloj (`open_clk(3)`), **bloquea** la señal de sync (`lock_sync_signal(3,0)`)
  y la **desbloquea** (`unlock_sync_signal(3)`), y emite los eventos **0x2012, 0x2013,
  0x2014, 0x2015** (`bl 0x43901a8c` en `0x4378e02e`, `0x4378e074`, `0x4378e09c`).
  Es decir: **el reloj se congela mientras la cámara principal sincroniza exposición y
  lectura**, y sólo el `CAMERA_MAIN_SYNC` puede cambiar de reloj en ese instante
  (`set_sync_signal(3, nuevo_clk)` en `0x4378e0c2`).
* El **VDF** (`0x4368b3e4`) y el **VEF** (`0x436afba0`) también toman el reloj
  (subsistemas 0x0a y 0x0d) → el cambio de reloj impacta al finder.
* El **decodificador de vídeo** cambia de reloj por **`FRAME_RATE`**
  (`McMsgAvscDec::ClockChange`, `mcMsgAvscDec.cpp` `0x43c72f72`) → 24P/25P/30P/50I/60I.
* **Lo que este módulo NO hace** (verificado): no programa divisores ni frequencies en
  Hz (ninguna traza contiene Hz), no menciona el obturador, no menciona el imager ni el
  modo de lectura, y no fija tiempos de exposición. Fija **el tipo de reloj** y **el
  retardo de sincronía vertical en µs**.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| Comprobación | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| apariciones del token `[CLK_CTRL]` | **66** | **0** | **0** |
| núcleos de las 66 trazas presentes (texto exacto, sin la etiqueta) | 66 | **0** | **0** |
| entradas de la tabla de API DDL `ddl_clkctrl_*` | **14** (ids 0–10, 12, 13, 14) | **14**, idénticas | **14**, idénticas |
| `"CALL CB3"` | `0x43c3acae` | `0x43c3b4ed` | `0x43d2332d` |
| nombre de módulo `"ClkCtrl"` | `0x43c3aef0` | `0x43c3b72e` | `0x43d2356e` |
| `init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus` | `0x43ca3be5` | `0x43ca947e` | `0x43daf633` |
| `ddl_clkctrl_set_sync_signal err = %d` | `0x43c3aea5` | `0x43c3b6e4` | `0x43d23524` |
| `"Current clock is 24P/25P/30P/50I/50P/60I/60P"` | sí | sí | sí |
| `STATE_CHANGE_CLK`, `ClkChgExec`, `DelayChgExec`, `change_vfc`, `subVFC` | sí | **0** | **0** |
| despachador DDL equivalente | `0x435a0880` | `0x435a3720` (misma estructura: cases 0–3 → `0x43a2df8c`/`0x43a2df5c`/`0x43a2df2c`/`0x43a2defc`) | — |

**Conclusión del diferencial:** el **subsistema es común a los tres firmwares** (misma
superficie de API, mismos mensajes de inicialización, misma lógica de arbitraje), pero la
fw3.21 de la A6000 lo entrega **instrumentado** (66 trazas + traza de cada llamada DDL).
Es, por tanto, un caso de **"CONTENIDO NUEVO" en el sentido de S130** (mensajes nuevos),
**no** de módulo nuevo: el comportamiento observable (abrir/cerrar, bloquear, cambiar
reloj, retardo de sync) es el mismo.

## 10. NO VERIFICADO / abierto

1. **Nombre del fichero fuente** del módulo `[CLK_CTRL]` (no hay `.cpp` con "clk" en la
   imagen; solo se ha obtenido el rango de líneas 68–367).
2. **Significado de las siglas**: `CLK_CTRL`, `DDL`, `HTP`, `vph`, `subVFC`, `10Count`,
   `change_vfc`, `m_vfc` — ninguna aparece expandida en ningún byte (el prefijo `ddl_` sí es
   una convención real del firmware, con 6 familias: `bgm`, `clkctrl`, `jpeg`, `srotate`,
   `stitch`, `vio`).
3. **Relación entre el id de subsistema del reloj y el de `CamSyncResource`** (son
   espacios de numeración distintos; no se ha averiguado si hay tabla de equivalencia).
4. **Unidad exacta de `delay`**: la traza de CAMERA_MAIN dice `sysv_delay=%dus` (µs) y el
   `MAX OVER` habla de `normal_delay`/`special_delay`; no se ha medido el rango máximo
   permitido ni la relación con el frame.
5. **Contenido exacto del mensaje OSAL de 12 bytes** emitido por `0x4359ed7c`
   (cabecera tipo 2 / `0xc0` + 6 campos); no se ha decodificado el código de campo.
6. **`10Count`**: no se ha averiguado qué cuenta ni por qué es "10".
7. **Rol de "maestro" y "esclavo"**: `0x435a0596`/`0x435a0734` intercambian mensajes, pero
   no se ha identificado qué CPU o tarea es cuál en cada configuración.
8. **Semántica de `ddl_clkctrl_get_clk_chg_enable`** (`0x4359ee24`): devuelve si el cambio
   de reloj está habilitado; no se ha trazado su consumidor (`0x43ae8c66`).
9. **Cifras de referencia**: 85 sitios y 36 funciones con la **regla estricta**; la regla
   ancha daría falsos positivos (p. ej. 519 candidatos para la cadena muerta
   `0x43c3a2a6`), por lo que no se publican.
10. Las **4 cadenas sin referencia** (`0x43c3a2a6`, `0x43c3afc0`, `0x43c3afe4`,
    `0x43c3b007`): **verificado** que no tienen referencia PIC (regla estricta, mapa global
    de 17 525 destinos) **ni** puntero absoluto de 4 B en la imagen. Son texto muerto
    (p. ej. la rama "Not Changing state" del despachador de estados `0x4359faea` llama al
    emisor de mensaje pero **no** al emisor de texto).

## 11. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (180 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 66 apariciones de `[CLK_CTRL]` en la A6000 fw3.21 y **0** en la A7S
   fw3.20 y el A6300 fw2.01 → confirmado con `bytes.count()` en los tres blobs. Bloque de
   `.rodata` `0x43c3a1df`–`0x43c3b09c`.
2. **Cadillas citadas, verificadas byte a byte**: `CALL CB3` `0x43c3acae`, `ClkCtrl`
   `0x43c3aef0`, `[CAMERA_MAIN]: init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus` `0x43ca3be5`,
   `ddl_clkctrl_set_sync_signal err = %d` `0x43c3aea5`; el despachador DDL `0x435a0880` es
   una función real (prólogo Thumb `0xb570`).
3. **Tabla de API DDL**: `ddl_clkctrl_` aparece 14 veces en la A7S, 15 en el A6300 y **26** en la
   A6000 → los tres comparten la misma superficie de API y la A6000 añade la traza de cada
   llamada → lo nuevo es la **instrumentación**, no la funcionalidad. Consistente con la
   clasificación de S130.
4. **Negativo acotado para la línea del obturador**: el módulo fija un **tipo de reloj**
   (`CLKTYPE`: 24P/25P/30P/50I/50P/60I/60P) y un **retardo de sincronía vertical**
   (`sysv_delay`, en µs) → gobierna la duración del frame y, por tanto, el *presupuesto* temporal
   de exposición y lectura, pero **no** frequencies de obturación ni ningún selector de
   mecanismo → **sin efecto en S51**.
5. **Muertes verificadas**: las 4 cadenas sin referencia (`0x43c3a2a6`, `0x43c3afc0`,
   `0x43c3afe4`, `0x43c3b007`) se comprobaron sin referencia PIC (mapa global de 17 525
   destinos) **ni** puntero absoluto de 4 B → texto muerto.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
