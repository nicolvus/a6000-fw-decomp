# S133 — `[MOUNT_DEBUG]`: el diagnóstico de la montura de lente (132 trazas)

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)). Sin efecto en S51.

Datos: [`mount_debug.json`](mount_debug.json) · Test: [`tests/test_s133_mount_debug.py`](../../tests/test_s133_mount_debug.py)
· Nota de captura: [`docs/capture/s133-mount-debug.md`](../../docs/capture/s133-mount-debug.md)

## 1. Resumen

- **132 cadenas** con el prefijo `[MOUNT_DEBUG]:`, de `0x43c9648d` a `0x43c9a10f`.
- **148 sitios** de referencia PIC (regla estricta) y **65 funciones** emisoras
  (**64** si se cuenta cada cadena por la función de su **primer** sitio; una cadena,
  `[BL ERR]SendingLensNonCommand ID[%d]` `0x43c965b9`, tiene sitios en tres funciones).
- **0 cadenas sin referencia.** Prefijos vecinos medidos: `[MOUNT_ERROR]` **80**,
  `[MOUNT_INFO]` **6**, `[MOUNT_WARNING]` **5** → **223** cadenas `[MOUNT_*]`, **242** sitios
  y **83** funciones.
- El bloque es el **diagnóstico de la montura de lente**: colas y envío del protocolo BL,
  analizador RX, máquina de estados de `Mount_Controller`, `Mount_DividedInfo` (eclipse),
  tareas LIF, detección de extracción de lente y actualización de firmware de lente.
- **No es un diagnóstico del obturador ni del sensor.** Cero apariciones de
  `SHUT`/`SENS`/`APER`/`ACTU`/`DIAG`/`CONTACT`/`FC`/`AF` (sensible a mayúsculas) en las 132
  cadenas; el único `aF` insensible a mayúsculas está dentro de
  `Mount_InitializeEclipseDataForLensDetach` `0x43c97802` y no es una referencia a autofoco.
- El diferencial es tajante: **0** apariciones del token `[MOUNT_` en A7S fw3.20 y en A6300
  fw2.01, y **0/132** mensajes interiores idénticos como cadena independiente.

## 2. Qué comprueba (respuesta medida)

El bloque **traza tráfico y estados**, no los chequeos del protocolo. Los chequeos
(`HEADER_NG`, `FOOTER_NG`, `CHECKSUM_NG`, `DATASIZE_NG`, `COMMTYPE_NG_0`, `SYNC TIMEOUT` y el
volcado de estado de 12 líneas de `0x436e239c`) son **`[MOUNT_ERROR]`**, no `[MOUNT_DEBUG]`.
Lo que sí emite `[MOUNT_DEBUG]` como comprobación es:

| comprobación | cadena | vaddr | sitio |
|---|---|---|---|
| mensaje en blanco / bits altos de `commtype` | `[BL SYNC]BLANK ERR (%02X)` | `0x43c9650a` | `0x436e0e9a` |
| tamaño contra descriptor | `[BL SYNC]DATA SIZE ERROR size(%d)` | `0x43c96533` | `0x436e0ed0` |
| error de lente / transacción | `[BL ERR]LENS ERR`, `[BL ERR]TRANS ERR` | `0x43c96f79`, `0x43c96f99` | `0x436e2a66`, `0x436e2aa6` |
| datos de montura | `[BL ERR]MOUNT_DATA_NG` | `0x43c96feb` | `0x436e2bec` |
| desbordamiento del buffer RX | `[BL ERR]Receive Buffer Overwrite(Lap)` | `0x43c97010` | `0x436e2c04` |
| comandos de cámara `0xC00`–`0xC03` | `[BL]CAM CmdStatus:%04X` | `0x43c979a0` | `0x436e45f2` |
| retorno de esa comprobación | `[BL]Mount_ChkCamCmdState RetVal:%d` | `0x43c979c6` | `0x436e4602` |
| actualización de lente | `[BL]PREPARE UPDATE CHECK OK/NG/NG LENS_NONE` | `0x43c98151`–`0x43c981a7` | `0x436e55fe`–`0x436e561c` |

La comprobación de comandos de cámara es la función `0x436e4598`
(`push {r0,r1,r4,r5,r6,lr}`): llama a `0x436e2368` (`bl` en `0x436e459c`), lee `[r0+0x28]`
con `ldrb.w` en `0x436e45a4` y `[r0+0x24]` con `ldrh` en `0x436e45a8`; compara con `0xC00`
(`cmp.w r3,#0xc00` en `0x436e45b6`) y `0xC03` (`movw r2,#0xc03` en `0x436e45be`), y emite
las dos trazas de la tabla. Sus llamadores medidos son `0x436e5f7c` y `0x436e5ffa`.

## 3. Mapa de las 132 trazas por sub-bloque

`n` = cadenas cuyo **primer** sitio cae en el sub-bloque (suma 132); "sitios" y "funciones
tocadas" incluyen los sitios de esas cadenas en otros sub-bloques (suman 148 y 65). Los
sub-bloques son regiones de función ya verificadas en [`analysis/s66/mount_functions.md`](../s66/mount_functions.md).

| sub-bloque | n | rango de cadenas | sitios | funciones tocadas | ejemplos |
|---|---:|---|---:|---:|---|
| **sync_send** — colas y envío | 13 | `0x43c9648d`–`0x43c9678b` | `0x436e0dcc`–`0x436e1718` | 8 | `[BL]SYNC SEND SET ID(%d):CB(0x%8x)` `0x43c9648d`; `[BL ERR]SendingLensNonCommand ID[%d]` `0x43c965b9` (3 funciones); `[BL]LENS DETACH REMAIN CB(%d)` `0x43c9678b` |
| **drv_uart** — envío UART | 1 | `0x43c96946` | `0x436e1a40`–`0x436e1ab0` | 1 | `[BL]DRV_SEND[%d]` `0x43c96946` |
| **rx_analyzer** — analizador RX | 8 | `0x43c96e73`–`0x43c97010` | `0x436e284e`–`0x436e2c04` | 1 | `[BL]SYNC RECIVE ID(%d):CB(0x%8x)` `0x43c96f49`; `[B->L]ALPHALENS:%d,%d` `0x43c96ea2` |
| **cap_lif** — log y crédito LIF | 3 | `0x43c97161`–`0x43c971b4` | `0x436e3550`–`0x436e37ea` | 2 | `[BL]osal_capstart Ret=%04x` `0x43c97161`; `[BL]osal_capstop Ret=%04x` `0x43c9718b`; `LIF CREDIT RegistErro…` `0x43c971b4` |
| **divided_eclipse** — `Mount_DividedInfo` | 10 | `0x43c97218`–`0x43c97802` | `0x436e3a14`–`0x436e406c` | 8 | `[BL]EclipseDataComState [%d] => [%d]` `0x43c9734d`; `Mount_EclipseComInit Mount_DividedInfo.cpp line %d` `0x43c97754`; `Mount_InitializeEclipseDataForLensDetach…` `0x43c97802` |
| **mount_controller** — `Mount_Controller` | 47 | `0x43c9788a`–`0x43c98417` | `0x436e42d2`–`0x436e5dea` | 35 | `[B->L]CS_POWER` `0x43c978db`; `[B->L]ATTACH_INFO1` `0x43c978f9`; `[BL]LENS_POWER_4.8V` `0x43c97cff`; `[B->L]STARTUP_INFO` `0x43c983f5` |
| **main_task** — tarea principal BL | 37 | `0x43c98460`–`0x43c98a9e` | `0x436e6046`–`0x436e7a38` | 1 | `[BL]LOGIC_POWER:%d` `0x43c98460`; `[BL]POWEROFF_HANDSHAKE_END` `0x43c986b6`; `[BL]LOGIC_ON` `0x43c9882f`; `[BL]POWER PARAM…` `0x43c98a9e` |
| **lif_tasks** — botones y callbacks | 7 | `0x43c98b58`–`0x43c98c8e` | `0x436e7cb8`–`0x436e9db2` | 7 | `[BL] TSK_LIF is called by %d` `0x43c98b58`; `[BL]CHG FHButton old=%d new=%d` `0x43c98bb0`; `[BL]LensOpState…` `0x43c98c09`; `[BL]BL_ASYNC_RCV_PAGE_CB` `0x43c98c8e` |
| **lens_remove** — extracción de lente | 1 | `0x43c9a10f` | `0x436fe196` | 1 | `[BL]CHG LENS REMOVE DET old=%d new=%d` `0x43c9a10f` |
| **fw_update** — firmware de lente | 5 | `0x43c9805f`–`0x43c981dc` | `0x436fe740`–`0x436fe890` | 1 | `[BL]PREPARE UPDATE REQ RCV` `0x43c9805f`; `[BL]PREPARE UPDATE OK/NG/WAIT` `0x43c98089`–`0x43c980d3`; `[BL]UPDATE UNPLUG USB` `0x43c981dc` |

El orden del bloque de cadenas **no** sigue el orden del código: `fw_update` emite
`0x43c9805f`–`0x43c981dc` desde `0x436fe500`, mientras `mount_controller` emite
`0x43c98151`–`0x43c981a7` desde `0x436e55c2`. Por eso el reparto se cuenta por la función
del **primer** sitio de cada cadena, no por la posición de la cadena.

## 4. Mecanismo de emisión (verificado en bytes)

Los 148 sitios se resuelven a **9 sinks** (0 sin resolver) siguiendo `add rX, pc`, los `b`
incondicionales y, cuando hay epílogo, el `b.w` de cola:

| sink | sitios | papel |
|---|---:|---|
| `0x436e41e4` | **94** | wrapper principal; el formato viaja en `r3` |
| `0x436e03b0` | **29** | emisor directo; el formato viaja en un argumento |
| `0x436e3914` | **10** | wrapper con el mismo esquema |
| `0x436fe410` | **6** | wrapper con el mismo esquema (zona de firmware de lente) |
| `0x436e808c` | **4** | wrapper con el mismo esquema (zona de tareas LIF) |
| `0x436e9c70` | **2** | wrapper; fija `0x125` con `movw r3,#0x125` en `0x436e9c9a` |
| `0x436e36a8` | **1** | wrapper con el mismo esquema |
| `0x436e7bec` | **1** | wrapper con el mismo esquema |
| `0x436fdfc4` | **1** | wrapper con el mismo esquema (`lens_remove`) |

**Sink directo `0x436e03b0`** (`push {r3}` en `0x436e03b0`; `push.w {r0,r1,r2,r4,r5,r6,r7,r8,sb,sl,lr}`
en `0x436e03b4`): `movs r2,#0x9a` en `0x436e03c8`; `bl 0x435612d0` (`osal_try_valloc_msg`) en
`0x436e03cc`; `bl 0x439c5004` (`vsnprintf`, tamaño `0x81`) en `0x436e03f6`; `bl 0x43ad9eae`
en `0x436e041e`; `bl 0x4356120c` (`osal_snd_msg`) en `0x436e0426`. Campos del mensaje:
`[+0]=1` (`strh`), `[+2]=` tag, `[+4]=` `r1`, `[+0x10]=` `r2`, `[+0x12]=` longitud+1 y el
texto en `+0x14`.

**Wrapper `0x436e41e4`** (mismo esquema): `movs r2,#0x9a` en `0x436e41fe`;
`bl 0x435612d0` en `0x436e4202`; `bl 0x43561244` en `0x436e4236`; `vsnprintf` en
`0x436e424c`; `bl 0x43ada13c` en `0x436e4274`; `osal_snd_msg` en `0x436e427c`. La cadena de
formato viaja en `r3` y se recupera con `push {r3}` + `add r5,sp,#0x4c` (`ldr sl,[r5],#4`
en `0x436e41f6`).

**Patrón de llamada típico** (`0x436e4b42`–`0x436e4b4a`): `movw r0,#0x125` (tag),
`movs r2,#3`, `add r3,pc` en `0x436e4b48`, `bl 0x436e41e4` en `0x436e4b4a`.

**Sitios de cola** (4): `0x436e4378` hace `pop.w {r4,lr}` en `0x436e437a` + `b.w 0x436e41e4`
en `0x436e437e`; `0x436e55fe`, `0x436e560e` y `0x436e561c` saltan a `0x436e561e` y desde
allí a la cola de `0x436e41e4`.

## 5. Funciones y ficheros fuente

Las **65 funciones** están listadas con sus sitios y cadenas en el JSON. Las más cargadas:

| función | sitios | cadenas | papel |
|---|---:|---:|---|
| `0x436e5e3c` | 44 | 37 | tarea principal BL (rango verificado en S66); secuencia de power, arranque y apagado |
| `0x436e48fc` | 10 | 8 | `[HS]` *handshake*: `CS_HIGH`/`CS_LOW`/`COMPLETE` (comparte 3 cadenas con `0x436e4d68`) |
| `0x436e2678` | 8 | 8 | analizador RX del protocolo BL |
| `0x436e1254` / `0x436e1328` / `0x436e14ac` | 6 / 4 / 2 | 5 / 4 / 2 | envío sync/async y `SendingLensNonCommand` |
| `0x436e4598` | 2 | 2 | `Mount_ChkCamCmdState` (comandos `0xC00`–`0xC03`) |
| `0x436e3508` | 2 | 2 | control de la captura de log de montura |

Solo **2 funciones** quedan marcadas `approx` en el JSON (`0x436e1328` y `0x436e3bf8`): el
prólogo `push` es correcto, pero el test automático no puede demostrar que el desensamblado
lineal llegue al sitio sin atravesar una piscina de literales.

**Ficheros fuente citados textualmente** por las cadenas:

| fichero | cadenas | vaddrs | etiqueta |
|---|---:|---|---|
| `Mount_Controller.cpp` | 1 | `0x43c9671a` | `[MOUNT_ERROR]` |
| `Mount_DividedInfo.cpp` | 5 | `0x43c972fb`, `0x43c9756f`, `0x43c97754`, `0x43c977bc`, `0x43c97802` | 3 ERROR + 2 DEBUG |

`Mount_Controller.cpp` solo aparece en un mensaje de error (`[BL]ASYNC ERR Mount_Controller.cpp %d lines`,
`0x43c9671a`, sitio `0x436e146a`); ninguna de las 132 trazas DEBUG cita un `.cpp`. Los dos
mensajes DEBUG de `Mount_DividedInfo.cpp` son `Mount_EclipseComInit` (`0x43c97754`) y
`Mount_InitializeEclipseDataForLensDetach` (`0x43c97802`).

La captura de log de diagnóstico (`0x436e3508`) usa `/mnt/Mount_ms_log_%03d.dat`
(`0x43c97146`, `snprintf` en `0x436e3538`), arranca con `osal_capstart` (`r1=4` en
`0x436e3546`) y para con `osal_capstop` (`r1=5` en `0x436e357c`).

## 6. Relación con la montura, el AF/sensor y el obturador

- **Montura (S66)**: los 10 sub-bloques caen en funciones ya inventariadas en S66
  (colas `0x436e0d74`–`0x436e163a`, driver `0x436e1918`, analizador `0x436e2678`,
  `Mount_DividedInfo` desde `0x436e39e8`, controlador `0x436e4156`–`0x436e5e3c`, tarea
  principal `0x436e5e3c`–`0x436e7bf0`). El bloque **es** la instrumentación de esa montura.
- **AF/sensor (S127)**: no hay cruce textual. Las 132 trazas no contienen `AF` (mayúsculas)
  ni `SENS`; el único `aF` es parte de `…DataForLensDetach` (`0x43c97802`). Los puentes
  `0x4377e0e8` y `0x437d24c8` no contienen sitios del mapa estricto; el primero es llamado
  desde `0x43793ef6`, en la región `[CAMERA_MAIN_SYNC]`, y el segundo desde `0x4377f822`,
  pero **su atribución de módulo es NO VERIFICADO**.
- **Obturador (S51)**: ninguna de las 132 trazas menciona obturador, sensor, apertura ni
  actuador (`SHUT` 0, `SENS` 0, `APER` 0, `ACTU` 0). Es un diagnóstico de la **montura de
  lente**; no hay evidencia de que toque el obturador. Que no lo mencione no prueba que no
  exista una interacción indirecta.

## 7. Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| cadenas `[MOUNT_DEBUG]` | 132 | **0** | **0** |
| cadenas `[MOUNT_*]` | 223 | **0** | **0** |
| mensajes interiores idénticos como cadena independiente | 132/132 | **0/132** | **0/132** |
| mensajes interiores que aparecen como subcadena | — | **2** | **2** |

Los dos aciertos por subcadena son **falsos positivos**:

1. `[BL]Wait_BL_ASYNC` (`0x43c966a8`) aparece dentro de
   `[BL]Wait_BL_ASYNC_RCV (%+hd)` en A7S (offset `7719423`) y A6300 (`8777157`).
2. `POFF` (`0x43c98a29`) aparece dentro de `SaveUsr:POFF Req` en A7S (`7698757`) y A6300
   (`8747017`).

El mecanismo **no es nuevo**: `/mnt/Mount_ms_log_%03d.dat` (1/1/1), `Mount_DividedInfo.cpp`
(5/3/4), `Mount_Controller.cpp` (1/2/1), `LENS DETACH` (2/1/1) y `Eclipse` (13/6/6) existen
en las tres cámaras. Lo nuevo en fw3.21 es la **instrumentación `[MOUNT_*]`**. El A7S
conserva el módulo con otro vocabulario (`[BL]SYNC ERR TX DATA SIZE=0` `0x75e884`,
`[BL]SYNC NO DATA` `0x75e8a0`, `[BL]HEADER_NG` `0x75ee0b`, volcado `0x75eca3`–`0x75eddd`);
el A6300 añade `DIVIDEDINFO_COM_STATE`/`STEADYSHOTINFO_COM_STATE` (`0x863348`/`0x863593`).

## 8. Abierto / NO VERIFICADO

- La **atribución de módulo** de los puentes `0x4377e0e8` y `0x437d24c8` es NO VERIFICADO:
  no contienen sitios del mapa estricto y no se ha medido su módulo de origen.
- **No existe** ninguna cadena `Diagnosis`/`DIAGNOSIS`/`diagnosis` en A6000, A7S ni A6300
  (0 hits en las tres). La faceta "Diagnosis" del encargo no se puede verificar con bytes;
  lo medido es el bloque `[MOUNT_DEBUG]`.
- `BL` no está expandido en el firmware; no se ha medido si significa un bloque interno,
  *BackLight* u otra cosa.
- No se ha medido el **consumidor** de los mensajes (`osal_snd_msg`) ni el módulo que los
  formatea; solo el emisor y el mensaje construido.
- La semántica de `CS_*`, `ATTACH_INFO*`, `PowerSeq` y de los estados `0/1/2` del log no está
  verificada; solo los nombres literales y las comparaciones.
- No se ha localizado la definición de las macros `[MOUNT_DEBUG]`/`[MOUNT_ERROR]`/
  `[MOUNT_INFO]`/`[MOUNT_WARNING]`; su compilación condicional es NO VERIFICADO.
- Nada de lo hallado toca la línea del obturador: **S51 se mantiene**. No se puede afirmar ni
  negar una interacción indirecta.

## 9. Revisión del agente principal

_(vacía)_

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (42 tests del hito + comprobaciones a mano):**

1. **Recuentos**: 132 apariciones de `[MOUNT_DEBUG]` entre `0x43c9648d` y `0x43c9a10f`; y el
   resto de la familia: `[MOUNT_ERROR]` 80, `[MOUNT_INFO]` 6, `[MOUNT_WARNING]` 5 → **223**
   cadenas `[MOUNT_*]` en la A6000. En la A7S: **0** de cada prefijo.
2. **Diferencial**: 0/132 mensajes interiores coincidentes en la A7S y en el A6300 → el
   etiquetado `[MOUNT_*]` y sus mensajes son **material propio de la A6000 fw3.21** (con la
   salvedad versión/modelo de S130 §4); el mecanismo de captura (`/mnt/Mount_ms_log_%03d.dat`)
   y el módulo Eclipse son **preexistentes** en las tres cámaras → lo nuevo es la
   *instrumentación*, no la función.
3. **Negativo acotado**: ninguna traza del módulo menciona obturador, sensor, apertura, actuador
   ni autofoco → sin efecto en S51.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
