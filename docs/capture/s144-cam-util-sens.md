# S144 — `[CAM_UTIL_SENS]`: la utilidad de la memoria interna del sensor (A6000 fw3.21)

**Hito**: S144 · **Binario**: `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21)
**Convención**: `vaddr = 0x43541000 + file_offset` · **Regla PIC**: estricta (canónica del repo).

**Qué es**: utilidad de cámara que gestiona los **ficheros de la memoria interna del sensor
(«IM»)**: abre un fichero por número/dirección/tamaño, le asigna número de fichero y notifica el
evento al gestor de servicio («MS»). Es además el **callback de cambio de BKID**, que al cambiar de
bloque **monta/desmonta** el servicio. Mecánica: escribir 4 parámetros en un bloque global y enviar
un **mensaje OSAL** con plantilla fija.

| dato | valor |
|---|---|
| cadenas `[CAM_UTIL_SENS]` | **21** (`0x43cce1ea`–`0x43cce66b`; bloque `0x43cce1ea`–`0x43cce6ad`) |
| referenciadas / sitios (estricta) | **21/21**, **39** sitios |
| funciones emisoras | **5**: `0x439012d0`, `0x43901d50`, `0x43902168`, `0x439023b8`, `0x43902418` |
| bloque de parámetros global | `0x43f062c8` (bytes `+8..+0xb` = 4 parámetros; los 12 primeros B = plantilla del mensaje) |
| byte «MountSTAT» · byte «Flg» · callback del gestor MS | `0x43fa29f0` · `0x43fa2d23` · `0x43f062d4` |
| id OSAL **log** (ADJ y SENS) · **comando** | `0x008f0139` · `0x008f013a` |
| id de módulo en el log | `0xb5` (idéntico en ADJ y SENS) |
| CB de BKID | puntero absoluto `0x439012d1` en `0x44022d84` (0 llamadas `bl`) |

**Llamantes (verificados)**: `0x43901d50` → 17 `bl` (`[CAMERA_MAIN_LC]` `0x4376bf92`,
`[IMAGING_CAP]` `0x43783136`/`0x437ee214`, `[CAMERA_MAIN_TC]` `0x4387375c`…`0x4387888a`,
`[CAMERA_MAIN_YC]` `0x438b834a`, `[IDT]`/`[IDT_OPD]` `0x439f7bda`…`0x439f7e34`); `0x43902168` → 4 `bl`
(`[IMAGING_CAP]` `SACC_Debug` `0x43782644`/`0x43782650`/`0x43782904`, `0x4382cea2`);
`0x439023b8` → 1 `bl` (`tsk_cam_adjctrl` de `[CAM_UTIL_ADJ]`, `0x43900c9c`); `0x43902418` → 1 `bl`
(`0x437894dc`); `0x439012d0` → 0 `bl`, pero llama a `0x43900e30` (Mount) y `0x43900f18` (UnMount) de
`[CAMERA_ADJ]`. ⇒ es la pieza que **escribe volcados de imagen (RAW/YC) en la memoria del sensor**
(`MemAreaMSDebug`, `SACC_Debug`, `miniRAW`, `WiriteMsDebug`); la función se llama en el firmware
`cam_util_debug_file_write` (`0x43c9ef02`, `0x43c9f336`, `0x43cb50cf`).

**Relación con `[CAM_UTIL_ADJ]` (S143)**: misma banda (`0x4390xxxx`), **mismo id de módulo OSAL
`0xb5`**, **mismos ids de mensaje**, mismo patrón «4 parámetros + mensaje OSAL»; dependencia
**cruzada**: ADJ→SENS (`0x43900c9c`) y SENS→ADJ/`[CAMERA_ADJ]` (`0x439012fa`, `0x43901302`).

**Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01**: `[CAM_UTIL_SENS]` **21 / 0 / 0**;
interiores de las 21 trazas **21/21 · 0/21 · 0/21**; pero `cam_util_debug_file_write` **3 / 2 / 2**,
`MemAreaMSDebug` **4 / 4 / 10** y `Sens:` **27 / 27 / 27** ⇒ lo nuevo en la fw3.21 es la
**instrumentación** (la etiqueta), **no la función** (igual que S143 con `[CAM_UTIL_ADJ]`).

**Para la línea del obturador**: el módulo **NO** pasa obturación, iris, ISO ni parámetros de
lectura al sensor. Negativo automático sobre las 21 trazas **y** sobre las 47 cadenas referenciadas
por el código de `0x43901000`–`0x43902610`: **0** coincidencias de
`shut/iris/iso/exposure/silent/elec/efcs/fps`. Sus únicos destinos de llamada son OSAL, thunks de
vtable, formateo, `memcpy` y ayudantes propios. **Sin efecto en S51 (A/B/C = NO).**

**NO VERIFICADO**: «IM» y «MS» **no se desarrollan** (sin expansión en ningún byte); semántica de
`BKID`/`SWFLG`/`MODEFLG`/`MountSTAT`/`FsysMode`; naturaleza de la tabla de `0x44022d84`; canal por el
que «Debug IM Open» llega al driver; plantilla de 12 B (a cero en el fichero: se rellena en runtime);
código equivalente en A7S/A6300; fichero fuente (ningún `.cpp`/`.h` referenciado desde
`0x43900000`–`0x43910000`).

**Revisión del agente principal**: (vacío).

[Informe](../../analysis/s144_cam_util_sens/cam_util_sens.md) · [datos](../../analysis/s144_cam_util_sens/cam_util_sens.json)
· 22 tests (`tests/test_s144_cam_util_sens.py`).
