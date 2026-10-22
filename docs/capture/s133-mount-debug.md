# S133 — `[MOUNT_DEBUG]` es el diagnóstico de la montura de lente, no del obturador

**Hito:** línea general de RE · **Binario:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`, vaddr = `0x43541000` + offset) · **Regla de referencias:** estricta (canónica). **Sin efecto en S51.**

Informe: [`mount_debug.md`](../../analysis/s133_mount_debug/mount_debug.md) · Datos: [`mount_debug.json`](../../analysis/s133_mount_debug/mount_debug.json) · Test: [`tests/test_s133_mount_debug.py`](../../tests/test_s133_mount_debug.py)

## Hallazgo

- **132 cadenas** `[MOUNT_DEBUG]:` de `0x43c9648d` a `0x43c9a10f`; **148 sitios** PIC y **65 funciones** emisoras (**64** por primer sitio: una cadena tiene sitios en 3 funciones). **0 sin referencia.**
- Prefijos vecinos: `[MOUNT_ERROR]` **80**, `[MOUNT_INFO]` **6**, `[MOUNT_WARNING]` **5** → **223** `[MOUNT_*]`, **242** sitios, **83** funciones.
- Es el diagnóstico de la **montura de lente**: colas/envío del protocolo BL, analizador RX, `Mount_Controller`, `Mount_DividedInfo` (eclipse), tareas LIF, extracción de lente y actualización de firmware de lente.
- **No menciona obturador, sensor, apertura, actuador ni AF**: `SHUT`/`SENS`/`APER`/`ACTU`/`DIAG`/`CONTACT`/`FC`/`AF` dan **0** en las 132; el único `aF` está en `Mount_InitializeEclipseDataForLensDetach` `0x43c97802`. Nada toca S51.

## Qué comprueba

Los chequeos del protocolo (`HEADER_NG`, `FOOTER_NG`, `CHECKSUM_NG`, `DATASIZE_NG`, `COMMTYPE_NG_0`, `SYNC TIMEOUT`, volcado de `0x436e239c`) son **`[MOUNT_ERROR]`**, no DEBUG. El bloque DEBUG traza tráfico y estados: `[BL SYNC]BLANK ERR` `0x43c9650a`, `[BL SYNC]DATA SIZE ERROR size(%d)` `0x43c96533`, `[BL ERR]LENS ERR` `0x43c96f79`, `[BL ERR]Receive Buffer Overwrite(Lap)` `0x43c97010`, y los comandos de cámara `0xC00`–`0xC03` de `0x436e4598` (`[BL]CAM CmdStatus:%04X` `0x43c979a0`, `[BL]Mount_ChkCamCmdState RetVal:%d` `0x43c979c6`).

## Reparto medido (10 sub-bloques, suma 132/148/65)

| sub-bloque | cadenas | sitios | funcs | rango de cadenas |
|---|---:|---:|---:|---|
| sync_send | 13 | 17 | 8 | `0x43c9648d`–`0x43c9678b` |
| drv_uart | 1 | 2 | 1 | `0x43c96946` |
| rx_analyzer | 8 | 8 | 1 | `0x43c96e73`–`0x43c97010` |
| cap_lif | 3 | 3 | 2 | `0x43c97161`–`0x43c971b4` |
| divided_eclipse | 10 | 10 | 8 | `0x43c97218`–`0x43c97802` |
| mount_controller | 47 | 50 | 35 | `0x43c9788a`–`0x43c98417` |
| main_task | 37 | 44 | 1 | `0x43c98460`–`0x43c98a9e` |
| lif_tasks | 7 | 7 | 7 | `0x43c98b58`–`0x43c98c8e` |
| lens_remove | 1 | 1 | 1 | `0x43c9a10f` |
| fw_update | 5 | 6 | 1 | `0x43c9805f`–`0x43c981dc` |

## Emisión y fuentes

Los 148 sitios van a 9 sinks: `0x436e41e4` **94**, `0x436e03b0` **29**, `0x436e3914` **10**, `0x436fe410` **6**, `0x436e808c` **4**, `0x436e9c70` **2**, `0x436e36a8`/`0x436e7bec`/`0x436fdfc4` **1** cada uno; **0 sin resolver**. Todos comparten `push {r3}` + `movs r2,#0x9a` + `bl 0x435612d0` (alloc), `vsnprintf`, y `osal_snd_msg` (`bl 0x4356120c`). Fuentes citadas: `Mount_Controller.cpp` `0x43c9671a` (solo ERROR) y `Mount_DividedInfo.cpp` `0x43c972fb`, `0x43c9756f`, `0x43c97754`, `0x43c977bc`, `0x43c97802`. Log de montura: `/mnt/Mount_ms_log_%03d.dat` `0x43c97146`, desde `0x436e3508`.

## Diferencial

| | A6000 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| `[MOUNT_DEBUG]` | 132 | **0** | **0** |
| `[MOUNT_*]` | 223 | **0** | **0** |
| mensajes interiores idénticos | 132/132 | **0/132** | **0/132** |

Solo 2 aciertos por subcadena, ambos falsos positivos: `[BL]Wait_BL_ASYNC` dentro de `[BL]Wait_BL_ASYNC_RCV (%+hd)` y `POFF` dentro de `SaveUsr:POFF Req`. La captura de log, `Mount_DividedInfo.cpp`, `Mount_Controller.cpp`, `LENS DETACH` y `Eclipse` ya existen en las tres; lo nuevo es la instrumentación `[MOUNT_*]`.

## Abierto / NO VERIFICADO

- Atribución de módulo de los puentes `0x4377e0e8` y `0x437d24c8`: **NO VERIFICADO** (0 sitios del mapa estricto).
- No existe `Diagnosis`/`DIAGNOSIS`/`diagnosis` en ninguna de las tres cámaras (0 hits): la faceta "Diagnosis" no se puede verificar; lo medido es `[MOUNT_DEBUG]`.
- `BL` sin expandir; consumidor de los mensajes y semántica de `CS_*`/`ATTACH_INFO*`/`PowerSeq` no medidos; definición de las macros `[MOUNT_*]` no localizada.
