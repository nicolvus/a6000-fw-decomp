# S132 — `[CLK_CTRL]`: el gestor de control de reloj de la A6000 fw3.21

**66 trazas** `[CLK_CTRL]` en `0x43c3a1df`–`0x43c3b09c` (bloque contiguo de rodata).
Regla de referencias: **estricta** (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`).
Resultado: **62/66 referenciadas, 85 sitios, 36 funciones**, todas en un cluster de código
`0x4359ee24`–`0x435a1150` (~9 KB). **4 cadenas muertas** (`0x43c3a2a6`, `0x43c3afc0`,
`0x43c3afe4`, `0x43c3b007`): sin referencia PIC ni puntero absoluto de 4 B.

## Qué es

El módulo se llama **`ClkCtrl`** (`0x43c3aef0`) y es un **módulo DDL** con **14 funciones
públicas** (`0x43c3acb7`–`0x43c3ae86`, tras `"CALL CB3"` `0x43c3acae`), despachadas por
`0x435a0880`. Ids: `0` open_clk · `1` close_clk · `2` open_dly · `3` close_dly ·
`4` set_sync_signal · `5` set_sysv_delay · `6` lock_sync_signal · `7` unlock_sync_signal ·
`8` set_sysv_initial_delay · `9` set_sync_initial_signal · `10` printf_info ·
`12/13/14` "total test …". Corre en **tarea propia** (`"Tsk ClkCtrl Initial"` `0x43c3a5ff`,
`"Main routine start!!"` `0x43c3a61f`), con **máquina de estados** (estado `u8` a `+0x04`): `1` STATE_INIT1 · `2` STATE_NORMAL · `3` STATE_CHANGE_CLK ·
`4` STATE_CHANGE_CLK_LOCKING · `5` STATE_LOCK (`0x4359f9c0` = despachador). Log con **id
de módulo 0xc0**. Los `L=%d` son **números de línea** (68–367) de un único `.cpp` no
identificado.

## Qué controla

* **Arbitraje entre subsistemas**: `open_clk(id)` / `close_clk(id)` (y `open_dly`/`close_dly`);
  conflictos → `"[ERR]Busy!! 0x%04x already opened…"` `0x43c3a93d`.
* **Tipo de reloj `CLKTYPE`** (24P/25P/30P/50I/50P/60I/60P) y **retardo de sincronía
  vertical `SYSV_DELAY` en µs** (`set_sysv_delay`, `"set sysv delay subsystem = %x , delay =
  %d"` `0x43c3af89`; límites `"normal_delay/special_delay MAX OVER"` `0x43c3b06e`/`0x43c3b09c`).
* **Bloqueo de la señal de sync** (`lock/unlock_sync_signal`); con el reloj bloqueado,
  `set_sysv_delay` devuelve `"CLKCTRL_ERR_BUSY...State is LOCK"` `0x43c3af24`.
* **Secuencia de cambio**: `ClkChgExec` `0x4359fb24`, `DelayChgExec` `0x4359fc14`, `"CHANGE_CLK
  dly … : change_vfc=0x%x"` `0x43c3a71b`.
* **Intercambio maestro/esclavo** (`"Receive Message from Master"` `0x43c3abd0`, `"Send
  Message to Slave"` `0x43c3ac86`), con `targetVfc`, `delay_req`, `m_vfc.main/sub`.

## Consumidores (subsistema de reloj)

`CAMERA_MAIN_SYNC` **0x03** (`0x4378dfde`: open/close/**lock/unlock** + eventos 0x2012–0x2015)
· `VDF` **0x0a** · `VEF` **0x0d** · `SYSV/TP_R` **0xc2** · `MC` (shell 24P/25P/30P,
`McMsgAvscDec::ClockChange(FRAME_RATE)`, `McUtilMulti`, `McAvcDecCmdParamCheck`) **0x57** ·
`0x10b` (no id.) · `CAMERA_MAIN` `init_cam_clkctrl` (`init_cam_SetCamParam_main.cpp`):
`CLKTYPE` (mask `0x7f`) y `sysv_delay` (mín. 4000 µs).

## Relación con recursos y con la exposición

* **No usa `CamResource`/`CamSyncResource`**: su arbitraje es propio (ids de 4 hex,
  espacio de numeración **distinto** del `SyncResMgr` 0x00–0x23).
* `CAMERA_MAIN_SYNC` **congela el reloj** durante la sincronización de exposición/lectura
  (punto de contacto con S112/S124).
* **No hay obturador electrónico aquí**: 0 menciones de `shut`/`shutter`/`silen` en las 66
  trazas; no se programan divisores ni Hz: solo tipo de reloj y retardo de sync en µs.

## Diferencial

Los **66 núcleos de mensaje no existen** en la A7S fw3.20 ni en el A6300 fw2.01 (0/66),
pero los tres firmwares comparten **las mismas 14 entradas de API DDL**, el mismo nombre
`ClkCtrl` y los mismos mensajes `init_cam_clkctrl` / `Current clock is …`: el
**subsistema es común**; lo nuevo en la fw3.21 es la **instrumentación** (trazas).
Detalle: [informe](../analysis/s132_clk_ctrl/clk_ctrl.md) · datos: `clk_ctrl.json`,
`callers.json` (en `analysis/s132_clk_ctrl/`).
