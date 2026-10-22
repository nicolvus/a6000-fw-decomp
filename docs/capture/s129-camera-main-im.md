# S129 — `[CAMERA_MAIN_IM]`: la monitorización térmica del imager (42 trazas)

**Hito de la línea de ingeniería inversa general** (A6000 fw3.21, bytes de `av-cam.bin`). Informe:
[analysis/s129_camera_main_im/camera_main_im.md](../../analysis/s129_camera_main_im/camera_main_im.md)
· Datos: `camera_main_im.json`, `diff.json` · Test: `tests/test_s129_camera_main_im.py`.

## Hallazgo central

`[CAMERA_MAIN_IM]` es el submódulo **térmico**: no desarrolla la sigla `IM`, pero monitoriza la
**temperatura del imager** (`ImCheckThermal`, `Start`/`EndImThermal`, `ImStart`/`ImEndMovThermal`,
`TimeA ImgTmp`, `THERMAL_CAUTION`/`THERMAL_SHUTDOWN`) y añade 3 trazas de los drivers **ZIT**.

- **42 cadenas**: 40 contiguas en `0x43ca6b32`–`0x43ca71e7`; 2 sueltas en `0x43cb5fc1`, `0x43cb5ffa`.
- **43 sitios PIC** (regla estricta de `analysis/s106_imaging_cap/`), **10 funciones**, **0** sin referencia.
- **1 doble referencia**: `0x43ca70f6` (`ImStartMovThermal set_timer:%x`) desde `0x437b90fe` y `0x437b9268`.

| entrada | sitios | papel |
|---|---|---|
| `0x43547362` | 3 | diferencial térmico de `movie` (`ldrsh` ×2, `subs`, `paramA`/`paramB`) |
| **`0x437b8774`** | **22** | chequeo periódico: temperatura, tablas `movie`/`bulb`/`still`, umbrales Abs/Env, avisos |
| `0x437b8e1c` | 1 | instantánea `EcGain:%x isoAuto:%x bulb:%x` (la llama siempre el despachador) |
| `0x437b8ed4` / `0x437b8fb0` | 3 / 3 | `StartImThermal` / `EndImThermal` |
| `0x437b9064` / `0x437b915c` | 3 / 2 | `RecStart`/`ImStartMovThermal` / `RecEnd`/`ImEndMovThermal` |
| `0x437b91e8` | 3 | callback del temporizador: estado 1→2, `TimeA ImgTmp`, rearma |
| `0x437b93c0` / `0x4386bbec` | 1 / 2 | `ZitZ1cDriver` / `ZitDdcDriver` |

## Piezas verificadas

- **Despachador `0x437b8384`**: id u16 de `[ctx+0x10]` → tabla de 24 pares `{u16 id,u16 code}` en
  `0x43befc32` (`cmp r2,#0x18`); defecto `0xa00`; `0xa20`→`0x437b9064`, `0xa21`→`0x437b915c`;
  `0xac0` con tope 2; siempre acaba en `bl 0x437b8e1c`.
- **Temperatura de S115**: `0x437b877a bl 0x436d6118` (getter, global `0x44026878` →
  `0x43e7f858`) y `0x437b8780 bl 0x436d648c` con `float*` en `[sp,#0x34]` (slot `0x6c`);
  se escala ×**100.0f** (`0x42c80000`), +0.5 y truncado → centésimas; error `0x437b8d38`.
- **Modo de S124**: `0x437b87f6 ldrb [r4,#6]` y `0x437b87fe ldrb [r4,#4]` sobre `0x44026884` →
  `0x43f72b82`; coinciden +4/+6 con PrevDrv/NextDrv, pero bytes y otra base.
  **Intervalos** = campo u16 × `0x186a0`: `0x437b8f42`, `0x437b90e4`, `0x437b924e`.
- **Negativo**: no hay `svd`, `shd`, `spl`, `sint`, `gs:` ni `epdsel`; `shut` solo dentro de
  `shutdownTh` (`0x43ca6ca8`, `0x43ca6d3f`), de `[CAM_IMAGER]` (`0x43c93cc2`, `0x43c939b5`).

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| cadenas con prefijo `[CAMERA_MAIN_IM]:` | 42 | **0** | **0** |
| textos interiores idénticos | — | **34/42** | **33/42** |

→ **RENOMBRADO, no módulo nuevo**: la fw3.21 añade la etiqueta y pocos mensajes de instrumentación
(`RecStart`/`RecEnd`, `TimeA ImgTmp:%d`, `Err:Timer2Callback`, `movie thermal diffTemp`), pero el
mecanismo térmico ya existía; la A6300 añade `EcGain…4K:%x USB:%x` (`0x43da73f6`).

## NO VERIFICADO / abierto

- **Invocación de `0x437b8774`**: 22 sitios pero **ningún `bl` ni puntero de 32 bits** en toda la
  imagen → despacho indirecto no resuelto. Slot `0x6c` ↔ `GetImagerTemperature(float*)`
  (`0x43c936a3`): inferido (no está en ninguna vtable).
- Contexto de `0x437b8774` = struct de S124 (+4/+6 coinciden, base distinta): sin verificar; tampoco
  el significado de los 24 ids, quién envía `0xa20`/`0xa21`/`0xac0` ni el helper `0x4378dd78`.
- **Fichero fuente**: no hay `*Thermal*.cpp`; vecinos `CS_imaging.cpp` (`0x43ca3dd7`),
  `SyncYCOut.cpp` (`0x43ca4de4`) y `lc_PreReadAF.cpp` (`0x43ca793f`).
