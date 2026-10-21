# S66 (subtarea A) — MOUNT/BL: inventario de funciones, protocolo de transporte y estado

**Alcance:** subsistema de montura E-mount (`MOUNT`/`BL`, *body↔lens*) del `av-cam.bin` de A6000
(fw3.21). Solo análisis estático de bytes: no se ejecuta firmware, no se toca cámara, no se flashea.
Este documento **cierra** el punto 3 de «Lo que queda abierto» de `analysis/s66/lens_power_attach.md`
(formato exacto de la trama) y añade el inventario de funciones de la región `0x436dfe00`–`0x436e3000`.

**Estado de los hechos:** `VERIFICADO` = leído en bytes/instrucciones del blob;
`INFERENCIA` = lectura razonada de esos bytes; `NO_VERIFICADO` = pendiente.

Artefactos y evidencia cruda:

| Artefacto | Contenido |
|---|---|
| `analysis/s66/out/func_436e5e3c.txt` | cadenas + llamadas en orden de la tarea principal |
| `/tmp/opencode/mount_str.txt` | 646 cadenas de `0x43c95400`–`0x43c9aa00` con función que las referencia |
| `/tmp/opencode/procinfo.json` | `procedure_info` de REA/Ghidra para los candidatos `push {…,lr}` |
| `/tmp/opencode/dis_2678.txt` | desensamblado completo del analizador de recepción |
| `/tmp/opencode/dis_1918.txt`, `dis_0d74.txt`, `dis_14ac.txt`, `dis_1740.txt`, `dis_am.txt`, `dis_send2.txt` | bloques de envío/recepción |
| `analysis/s58/tdis.py`, `analysis/s66/func_strings.py` | desensamblado Capstone con literales PIC |

Base de carga del blob: `B = 0x43541000`; `file-offset = addr - 0x43541000`.
Blob: `analysis/rea-independent/input/av-cam.bin`, sha256 `b60c845c…56bb9` (11 427 236 B).

---

## 1. Mapa de la región

La región pedida (`0x436dfe00`–`0x436e3000`) contiene **cinco bloques funcionales** bien separados.
Los límites son los `push {…,lr}`/`procedure_info` verificados; donde REA no reconoce la función se
delimita por el siguiente prólogo y se confirma con Capstone (`tdis.py`).

| Rango | Bloque | Contenido |
|---|---|---|
| `0x436dfe1c`–`0x436dfe67` | preludio | 6 hojas: *clear*/getters de globales de la interfaz |
| `0x436dfe6c`–`0x436e069f` | **AM/MCS** | informes de análisis: colas `0x9a`, mensajes `0x125`, volcado de datos de lente |
| `0x436e06bc`–`0x436e0d45` | **estado** | accessors del contexto BL, *gates*, selección de `SendType`, serialización de trama |
| `0x436e0d74`–`0x436e163a` | **colas y envío** | servicio de cola síncrona, validación, reset, secuenciador, `SYNC/ASYNC SEND` |
| `0x436e1664`–`0x436e1bc7` | **ciclo de vida** | *detach*, reglas VSYNC/VD, `DRV_SEND` (UART), seguimiento de power-sequence |
| `0x436e1bc8`–`0x436e3370` | **puente y diagnóstico** | volcado de traza, puente MCS, volcado de estado, analizador RX, LIF |

`Mount_DividedInfo.cpp` empieza en `0x436e39e8` y el driver de comandos B→L/L→B en
`0x436e4156`–`0x436e5e3c`; la tarea principal (`0x436e5e3c`–`0x436e7bf0`) queda **fuera** del rango
pedido, pero se usa aquí como consumidor de la API de envío.

---

## 2. Inventario de funciones

`REA` = función con `procedure_info` de Ghidra/REA (nombre `FUN_…`); `CAP` = delimitada y verificada
solo con Capstone (REA no la tiene como procedimiento). Todas las direcciones son VERIFICADO.

### 2.1 Preludio (hojas de la interfaz)

| Dirección | Bytes | Papel | Evidencia |
|---|---|---|---|
| `0x436dfe1c` | 12 | `0x4393ac98(global, 0, 6)`: pone a cero 6 B de un global | `ldr/movs/b.w` |
| `0x436dfe2c` | 10 | pone a cero 4 B de un global | `str r2,[r3]` |
| `0x436dfe3c` | 6 | devuelve puntero a global | `add r0,pc; bx lr` |
| `0x436dfe48` | 8 | devuelve `u32` de un global | `ldr r0,[r0]` |
| `0x436dfe54` | 6 | devuelve puntero a global (2.º) | `add r0,pc; bx lr` |
| `0x436dfe60` | 8 | devuelve `u8` de un global | `ldrb r0,[r3]` |

### 2.2 AM/MCS — informes de análisis sobre el comando `0x125`

| Dirección | Bytes | Papel | Cadenas / notas | Tipo |
|---|---|---|---|---|
| `0x436dfe6c`–`0x436dff07` | 156 | añade una entrada a la lista de datos de comandos AM; 13 bloques | `[MCS]addCmdDataList data times overflow` | REA |
| `0x436dff34`–`0x436dffd5` | 162 | construye y encola un informe AM: cabecera de `0x20` B, `strh id/r3`, payload por `0x439c5004(…,0x81,…)` | cola `0x435612d0/0x43561244`, `strb 0x0A` final | REA |
| `0x436dffe0`–`0x436dffff` | 32 | comprobación de miembro de la tabla AM | `[MOUNT AM]NO MEMBER CHECK_DATA:%d` | REA |
| `0x436e0004`–`0x436e0021` | 92 | idem para el bloque de error | `[MOUNT AM]NO MEMBER ERR_INFO:%d` | REA |
| `0x436e006c`–`0x436e00b3` | 72 | reserva los buffers de trabajo AM: `0x43a1b6e0({ctx,0x440,0x200,0x15,0x0E})` y guarda los punteros | tail `0x43ad9dce` | REA |
| `0x436e036c`–`0x436e03a5` | 58 | rellena cabecera AM (`u32 = 0x20`) y la envía por `0x43561244` | — | REA |
| `0x436e03b0`–`0x436e0431` | 130 | **informe AM**: mensaje de `0x9a` B `{u16 1, u16 id, u32 param, u16 len, …}`, `vsnprintf` a `0x80` B, terminador `0x0A 0x00`, encola | `0x439c5004`, `0x4356120c` | REA |
| `0x436e0438`–`0x436e0462` | 42 | despacho genérico por índice (≤3) sobre tabla PIC de 4 punteros, tras `0x436e0134` | `blx r3` | CAP |
| `0x436e046c`–`0x436e04a9` | 62 | crea objeto mensaje `{u8 id@0, void *ptr@4, u16 size@8}` con reserva de `0x440` B | `[BL]SEND AREA ALLOCATE` | REA |
| `0x436e04b4`–`0x436e053f` | 140 | envía cadena de monitor (id 5 = solo id; si no, copia ≤`0x80` B) | — | REA |
| `0x436e0548`–`0x436e05e5` | 158 | envía bloque `{id=2, ptr, size}` (cabecera `0x10`) y, si falla, reintenta con id `0x0F` | — | REA |
| `0x436e05f4`–`0x436e069f` | 172 | vuelca la base de datos de lente: `0x43` registros de `0x32` B | `BL SendData`, `Info1`, `Info2` | REA |

### 2.3 Estado: accessors del contexto BL

Todos leen/escriben el contexto apuntado por el global de `0x43e8111c` (PIC:
`add_addr+4 + lit1 + lit2`). El desplazamiento indicado es el campo del contexto.

| Dirección | Bytes | Papel | Campo | Tipo |
|---|---|---|---|---|
| `0x436e06bc` | 20 | escribe dos bytes globales (par de estado) | global | REA |
| `0x436e0710`–`0x436e0744` | 52 | **setter CommState** con guardas (0–5) | `+0x00` | REA |
| `0x436e074c` | 20 | getter CommState | `+0x00` | REA |
| `0x436e0760`–`0x436e0797` | 56 | *gate*: `CommState ∈ {1..4}` **y** contador de 16 bits `ctx[0x24]/[0x25] ≥ 0x108` | `+0x24/+0x25` | REA |
| `0x436e07a0` | 20 | setter LensState | `+0x10` | REA |
| `0x436e07b4` | 20 | getter LensState | `+0x10` | REA |
| `0x436e07c8` | 26 | inicializa temporizador (`ctx+4=0`, `ctx+8=now`) con `0x150` como argumento de `0x43ad9eb4` | `+0x04/+0x08` | REA |
| `0x436e07ec`–`0x436e0823` | 56 | mismo *gate* con plazo `0x150`; escribe `ctx+0x0c` | `+0x24/+0x25` | REA |
| `0x436e0858` | 28 | predicado `ctx[0x9a] & 1`, tras `0x436e0760` | `+0x9a.0` | REA |
| `0x436e087c` | 28 | predicado `ctx[0x9a] & 2` | `+0x9a.1` | REA |
| `0x436e08a0` | 28 | predicado `ctx[0x9a] & 0x10` | `+0x9a.4` | REA |
| `0x436e08c4` | 28 | predicado `ctx[0x9a] & 4` | `+0x9a.2` | REA |
| `0x436e08e8` | 28 | predicado `ctx[0x9a] & 8` | `+0x9a.3` | REA |
| `0x436e090c` | 20 | setter | `+0x14` | REA |
| `0x436e0920` | 20 | getter | `+0x14` | REA |
| `0x436e0934` | 26 | getter (usado como puerta de sincronización) | `+0x16` | REA |
| `0x436e0958` / `0x436e096c` | 20 | setter / getter **busy** | `+0x18` | REA |
| `0x436e0980` / `0x436e0994` | 20 | setter / getter **estado de cola** | `+0x1c` | REA |
| `0x436e09a8` / `0x436e09bc` | 20 | setter / getter **MakeData** (mensaje en construcción) | `+0x20` | REA |
| `0x436e09d0` | 36 | setter del contador de 16 bits (2 bytes) | `+0x24` | REA |
| `0x436e09fc` | 24 | getter | `+0x24` | REA |
| `0x436e0a14` | 24 | setter del byte alto | `+0x25` | CAP |
| `0x436e0a2c/0a4c/0a6c` | 32 | setter `u32` | `+0x48` | CAP |
| `0x436e0a80/0a98/0ab0` | 24 | getters `u8` | `+0x4c`, `+0x4d`, `+0x4e` | CAP |
| `0x436e0ac8` | 40 | getter `u16` | `+0x3a` | CAP |
| `0x436e0af0` | 28 | setter de dos bytes | `+0x3a/+0x3b` | CAP |
| `0x436e0b0c` | 20 | getter `u32` | `+?` (puntero de contexto) | CAP |
| `0x436e0b20` | 20 | getter `u32` | `+0x54` | CAP |
| `0x436e0b34` | 20 | getter `u32` | `+0x5c` | CAP |
| `0x436e0b48/0b5c/0b70` | 20 | setter `u8` | `+0x70` | CAP |
| `0x436e0b88` | 24 | getter | `+0x71` (MakeData) | REA |
| `0x436e0bb8`–`0x436e0c05` | 78 | **registra ID/CB pendientes** (`commtype 2` → `+0x28/+0x2c`; `commtype 3` → `+0x30/+0x34`), serializa la trama (`0x43ada0b4`) y lanza el driver | — | REA |
| `0x436e0c10` | 24 | getter | `+0x73` (SendData) | REA |
| `0x436e0c28` | 24 | getter | `+0x74` (SendType) | REA |
| `0x436e0c5c` | 20 | getter `u16` | `+0x76` (ErrCntQueSync) | REA |
| `0x436e0c90` | 20 | getter `u16` | `+0x78` (ErrCntQueVsync) | REA |
| `0x436e0ca8` | 20 | getter | `+0x75` (SameAdrs) | REA |
| `0x436e0ccc`–`0x436e0d1b` | 80 | **elige SendType** (1 o 2) según `PowMode` y escribe `+0x74` | — | REA |
| `0x436e0d28` | 30 | envoltorio de `0x43ad9f70` → `{ok, valor}` | — | REA |

### 2.4 Colas y envío

| Dirección | Bytes | Papel | Cadenas | Tipo |
|---|---|---|---|---|
| `0x436e0d74`–`0x436e0e45` | 210 | **SYNC SEND SET ID**: saca el nodo de la cola síncrona, valida tamaño y lo entrega al driver | `SYNC SEND SET ID(%d):CB(0x%8x)`, `SYNC ERR TX DATA SIZE=0`, `SYNC NO DATA` | CAP |
| `0x436e0e74`–`0x436e0ed9` | 102 | valida un mensaje ya formado: bits altos de `commtype` y tamaño contra el descriptor | `[BL SYNC]BLANK ERR (%02X)`, `[BL SYNC]DATA SIZE ERROR size(%d)` | REA |
| `0x436e0eec`–`0x436e0f34` | 72 | **QUEUE_DATA_REMAINDER**: revalida, baja *busy*, sigue con la cola restante | `[BL]QUEUE_DATA_REMAINDER` | CAP |
| `0x436e0f4c`–`0x436e103b` | 240 | **reset global** del contexto (CommState=0, LensState=0, contadores a 0, MakeData/SendData/SendType=`0xFF`) | — | REA |
| `0x436e1054`–`0x436e10b7` | 100 | copia 10 B de estado LIF (`ctx+0x27`…`+0x30`) a la estructura pública | — | REA |
| `0x436e10d8/10e4/10f0` | 18–24 | puntero / reset (`memset 4`) / copia 4 B de la estructura LIF | — | CAP |
| `0x436e1134`–`0x436e115b` | 40 | setter de la puerta de sincronización (`+0x16`); exige `PowMode==5` y `0x436e1118()==0` | — | REA |
| `0x436e1164`–`0x436e123b` | 216 | **ejecutor de secuencia**: tabla de 13 callbacks con retardos (`ctx+0x90/+0x91`) | `[BL ERR]state:%02Xh, code:06h` | REA |
| `0x436e1254`–`0x436e1311` | 190 | **SYNC SEND**: `0x436e00dc(ID)` → `0x436e0134` (tamaño) → nodo `{u32 cb; u8 msg[]}` → encola y arranca | `[BL]SYNC SEND ID(%d):CB(0x%8x)`, `SYNC QUE OVERFLOW` | REA |
| `0x436e1328`–`0x436e1481` | 346 | **ASYNC SEND**: exige `CommState≥2`, tipo de lente ≠ 0, `PowMode ∈ {5,6,0xFF}`; construye `{3,ptr,size}` y encola | `[BL]ASYNC SEND ID(%d):CB(0x%8x)`, `Wait_BL_ASYNC`, `ASYNC ERR MAKE SEND DATA` | REA |
| `0x436e14ac`–`0x436e1523` | 120 | `SendingLensNonCommand` (ID especial `0xFF`) y callback de *detach* restante | `[BL ERR]SendingLensNonCommand ID[%d]`, `[BL]LENS DETACH REMAIN CB(%d)` | CAP |
| `0x436e1524`–`0x436e154d` | 42 | despacho por índice en tabla (`entry+8`) con guarda `cmp r1,#3` y *tail-call* a `0x436e14ac` | — | CAP |
| `0x436e1556`–`0x436e163a` | 228 | **despacho de petición** (`tbb` de 4 casos, índice 0–3): `0x436e0438` (tabla de callbacks AM), `0x436e1524` y `0x436e14ac`; cierra con `0x436e00c4` | — | CAP |

### 2.5 Ciclo de vida y driver

| Dirección | Bytes | Papel | Cadenas | Tipo |
|---|---|---|---|---|
| `0x436e1664`–`0x436e1729` | 198 | **detach**: invoca los callbacks pendientes con ID `0xF0` y drena las colas | `[BL]LENS DETACH REMAIN CB(%d)` | REA |
| `0x436e1740`–`0x436e18a5` | 358 | reglas de VSYNC/VD para `Informations1/2` y contador de paquetes | `VSYNC ERR Informations1/2 Violation of rule`, `PACKET NUM OVER(%d)` | REA |
| `0x436e1918`–`0x436e1b3b` | 548 | **DRV_SEND**: desencola la trama, comprueba *busy* y despacha por `commtype` 1/2/3 hacia UART | `DRV_SEND[%d]`, `DATA SEND ERR QUE_NONE`, `DATA SEND ERR B_SENDING`, `CHECK_SENDDATA_ERR[%d]` | CAP |
| `0x436e1b3c`–`0x436e1bc7` | 140 | seguimiento de la secuencia de power: lee `PowMode` y dos temporizadores y mantiene un byte de reintento | — | CAP |

### 2.6 Puente MCS y diagnóstico

| Dirección | Bytes | Papel | Cadenas | Tipo |
|---|---|---|---|---|
| `0x436e1bc8`–`0x436e21bd` | 1526 | **volcado de traza** del estado de montura/lente (47 llamadas) | `Mount: …`, `%02X,%02X,…`, `Data Pointer NULL` | REA |
| `0x436e2234`–`0x436e233d` | 266 | **puente MCS**: arma el payload AM desde datos de lente (`param1`=1/2) y lo reporta | — | REA |
| `0x436e2348`–`0x436e2363` | 28 | copia 13 `u32` de un bloque de parámetros a los globales del secuenciador | — | REA |
| `0x436e2390` | 12 | getter del contador de *timeout* LC (`u16`) | `LC T.O. Cnt` | REA |
| `0x436e239c`–`0x436e260b` | 624 | **volcado de estado** (12 líneas) | `CommState/LensState`, `PowMode/PowSeq`, `VsyncErrCnt`, `LIFState/Err`, `LensTransErrCnt`, … | REA |
| `0x436e2678`–`0x436e2cf7` | 1664 | **analizador RX**: valida cabecera/footer/checksum/tamaño/tipo y despacha por ID | `HEADER_NG`, `FOOTER_NG`, `CHECKSUM_NG`, `DATASIZE_NG`, `COMMTYPE_NG_0/1`, `SYNC/ASYNC RECIVE ID(%d):CB(0x%8x)` | CAP |
| `0x436e2cf8`–`0x436e2e31` | 314 | espera de `CAM_INFO2` con reintento y temporizador `0x17` | `CAM_INFO2_RCV_WAIT_TIMEOUT_ERR[Timer=%d(ms)][ErrCnt=%d]`, `…TWAI_ERR ercd=%d` | CAP |
| `0x436e2e32`–`0x436e2f63` | 306 | **máquina de estados del comando LIF** (`0xC00`–`0xC07`) | `LIF Command Change : 0x%X >>> 0x%X`, `LIF Command : Illegal Command Received!!! : cmd=%04X` | CAP |
| `0x436e2f64`–`0x436e3370` | ~1036 | **segundo volcado de traza** (estado + contadores en formato corto) | — | REA (REA declara 1016 B desde `0x436e2f64`) |

> Nota de delimitación (`VERIFICADO`): en 10 funciones REA responde `not_in_procedure` y se han
> delimitado con Capstone: `0x436e0438`, `0x436e0d74`, `0x436e0eec`, `0x436e14ac`, `0x436e1526`
> (inicio real `0x436e1524`),
> `0x436e1918`, `0x436e1b3c`, `0x436e2678`, `0x436e2cf8`, `0x436e2e32`. Además, `procedure_info`
> sitúa `0x436e1554` dos bytes antes del prólogo real (`0x436e1556`), por lo que los límites de esa
> función se tomaron del `push {r0,r1,r4,r5,r6,lr}`. Una consulta vacía de REA **no** prueba
> ausencia de función.

---

## 3. Protocolo de transporte (VERIFICADO)

### 3.1 Trama en el cable

Constructor: `0x43b7b276` (llamado desde `0x43ada0b4`), con el objeto
`{u8 tipo@0, void *ptr@4, u16 size@8}` de `0x436e046c`. `ptr` apunta a un bloque de `0x440` B y los
datos empiezan en `ptr+5`.

| Offset | Tamaño | Valor | Evidencia |
|---|---|---|---|
| `+0` | 1 | `0xF0` (cabecera) | `movs r3,#0xf0; strb r3,[r0]` @ `0x43b7b29c` |
| `+1` | 2 | longitud total (`size + 8`), **LE** | `strb.w r8,[r0,#1]`, `asr r8,#8`, `strb [r0,#2]` |
| `+3` | 1 | tipo de comunicación = `tipo & 7` (`bfi r3,r2,#0,#3`) | `0x43b7b2bc` |
| `+4` | 1 | parámetro del emisor (0 en todos los envíos del blob) | `strb.w sb,[r0,#4]` |
| `+5` | 1 | **ID de comando** (primer byte del payload) | ver §3.4 |
| `+6` | `size-1` | datos del comando | `0x439c5320` (copia) |
| `len-3` | 2 | checksum, **LE** | `strb r0,[r7,r6]`, `asrs r0,#8`, `strb [r5,#1]` |
| `len-1` | 1 | `0x55` (footer) | `movs r3,#0x55; strb r3,[r5,#2]` |

**Checksum** (`0x43b7b25e`, veneer de `0x43ada0a8`): suma aritmética de bytes truncada a 16 bits
(`movs r0,#0` … `adds r0,r0,r4` … `uxth r0,r0`), calculada sobre `buf+1` durante `len-4` bytes; es
decir, cubre longitud + tipo + parámetro + ID + datos, y **excluye** cabecera, checksum y footer.

Tras serializar, la trama se inserta en el anillo de TX de la UART (`0x43a1b3e0`: semáforo `0x18`,
índice en `[r4+4]`, capacidad en `[r4+5]`).

### 3.2 Recepción y validación (analizador `0x436e2678`)

Orden exacto de comprobaciones (cada fallo registra su log y devuelve un código):

1. `0x43ad9d08` rellena un descriptor de 8 B: el segundo campo es el puntero al buffer de recepción
   (`r5` = base) y el primero vuelve como índice de canal (`r4`, usado luego en `0x436e27c6`).
2. `len = u16(buf[1], buf[2])` (`ldrb r8,[r5,#2]; lsl #8; add r3`).
3. `buf[0] == 0xF0` → si no, `HEADER_NG` (código 3) @ `0x436e2736`.
4. `buf[len-1] == 0x55` → si no, `FOOTER_NG` (código 5) @ `0x436e275e`.
5. checksum: `u16(buf[len-3], buf[len-2])` contra `0x43ada0a8(buf+1, len-4)` → si no, `CHECKSUM_NG` (4).
6. **DATASIZE**: `0x43ad9cb4(canal)` = `u16` del descriptor del canal UART
   (stride `0x31c`, campo `+4` en `0x43a1b1e4`), comparado con `len` → si no, `DATASIZE_NG` (2).
   `INFERENCIA`: ese campo es el número de bytes realmente recibidos por el canal, de modo que la
   longitud declarada en la cabecera debe coincidir con lo recibido.
7. `buf[3] & 7` debe estar en `1..3`; `0` → `COMMTYPE_NG_0` (6); otro → `MOUNT_ERR_COMMTYPE_NG_1` (7).
8. Despacho por `buf[5]` (ID) mediante `0x436e0134`; si el ID no está en la tabla de descriptores de
   la lente → `MOUNT_ERR_ANALYSE_NG:ID = %02Xh`. Si el tamaño no cuadra con el descriptor →
   `MOUNT_ERR_DATASIZE OVER ANALYSE_NG:ID = %02Xh size [%d][%d]`.

Códigos usados por este bloque: `2` (datasize), `3` (header), `4` (checksum), `5` (footer),
`6`/`7` (commtype), más `MOUNT_ERR_LENS_ERR` y `MOUNT_ERR_TRANS_ERR`. El código `1` es el que se pasa
como argumento a `0x436e239c` en la ruta de **SYNC TIMEOUT** (`0x436e26a4`).

**Ruta de timeout** (`VERIFICADO`): si el analizador se invoca con `r0 == -1` (`0x436e267c`) y hay una
petición síncrona pendiente (`ctx+0x28 != 0`), registra `[BL]SYNC TIMEOUT` (`0x43c96d…`), vuelca el
estado con código `1`, limpia la cola y llama al callback pendiente con `0xF1` (`0x436e26da`).

### 3.3 Tipos de comunicación (`buf[3] & 7`)

| Tipo | Uso | Evidencia |
|---|---|---|
| `1` | *Informations* (VSYNC/VD): ruta propia que valida reglas de `Informations1/2` (`0x436e1740`) y copia el estado de lente (`+0x14`) | `0x436e2824`–`0x436e28c6` |
| `2` | **síncrono**: debe coincidir con el ID pendiente `ctx+0x28`; al llegar se invoca el CB `ctx+0x2c` | `0x436e29d6`–`0x436e2a16` |
| `3` | **asíncrono**: no casa con un ID pendiente; se procesa por el camino de datos | `0x436e2a28`+ |

### 3.4 Envío: dos caminos y una cola

```
SYNC  (0x436e1254): ID → 0x436e00dc (¿la lente conoce el comando?)
                    → 0x436e0134 (descriptor: {u16 id, u16 size, u16 extra})
                    → nodo {u32 cb; u8 msg[size]} (0x43ad9ce8) → cola
                    → 0x436e7e84(7) arranca el servicio
                    → 0x436e0d74 saca el nodo → 0x436e0bb8: ctx+0x28=ID, ctx+0x2c=CB
ASYNC (0x436e1328): guardas de CommState/PowMode → 0x436e046c({3, ptr, size})
                    → 0x436e0bb8: ctx+0x30=ID, ctx+0x34=CB
0x436e0bb8 → 0x43ada0b4 → 0x43b7b276 (trama) → 0x43a1b3e0 (anillo TX)
           → si ctx+0x18 == 0 → 0x436e7e84(2)
DRV_SEND (0x436e1918): 0x43ad9ce0 (desencola) → comprueba busy → commtype 1/2/3 → UART
```

`0x436e00dc` es la comprobación «la lente conoce el comando»: dos bitmaps, uno en `+1` del bloque y
otro en `tabla + 0x20*índice`, indexados por `(ID-1) >> 3` y bit `(ID-1) & 7` (`VERIFICADO`).

`0x436e0134` recorre la tabla de descriptores de 6 B por entrada (`{u16 id, u16 size, u16 extra}`),
terminador `0x100`, máximo `0x600` B, y copia la entrada a la salida. La tabla se registra en tiempo
de ejecución (`0x440240a8` → `0x43fea2a0`), por lo que **en la imagen estática contiene código**: sus
contenido real no es recuperable sin runtime (`NO_VERIFICADO`).

---

## 4. Estado: campos, valores y máquinas

### 4.1 Campos del contexto (VERIFICADO por accessors)

| Offset | Campo | Accessor | Notas |
|---|---|---|---|
| `+0x00` | CommState | `0x436e0710` / `0x436e074c` | setter con guardas |
| `+0x04`/`+0x08` | temporizador (inicio / valor) | `0x436e07c8` | |
| `+0x0c` | marca de *gate* | `0x436e07ec` | |
| `+0x10` | LensState | `0x436e07a0` / `0x436e07b4` | |
| `+0x14` | LensState2 / estado de informes | `0x436e090c` / `0x436e0920` | copiado por el tipo 1 |
| `+0x16` | puerta de sincronización | `0x436e1134` (set) / `0x436e0934` (get) | exige `PowMode==5` |
| `+0x18` | *busy* del driver | `0x436e0958` / `0x436e096c` | |
| `+0x1c` | estado de cola | `0x436e0980` / `0x436e0994` | |
| `+0x20` | MakeData | `0x436e09a8` / `0x436e09bc` | |
| `+0x24`/`+0x25` | contador de 16 bits | `0x436e09d0`/`0x436e0a14`/`0x436e09fc` | comparado con `0x108`/`0x150` |
| `+0x28`/`+0x2c` | ID y CB síncronos | `0x436e0bb8` | |
| `+0x30`/`+0x34` | ID y CB asíncronos | `0x436e0bb8` | |
| `+0x3a`/`+0x3b` | contador/par de bytes | `0x436e0ac8`/`0x436e0af0` | |
| `+0x48`, `+0x4c`–`+0x4e` | contadores de informes | `0x436e0a2c`…`0x436e0ab0` | |
| `+0x54`, `+0x5c` | punteros/valores de 32 bits | `0x436e0b20`, `0x436e0b34` | |
| `+0x70`–`+0x72` | flags de envío | `0x436e0b70`, `0x436e0b88` | |
| `+0x71` | MakeData (dump) | `0x436e0b88` | contador |
| `+0x73` | SendData | `0x436e0c10` | |
| `+0x74` | SendType | `0x436e0c28` / `0x436e0ccc` | 1 o 2 |
| `+0x75` | SameAdrs | `0x436e0ca8` | |
| `+0x76` | ErrCntQueSync | `0x436e0c5c` | `u16` |
| `+0x78` | ErrCntQueVsync | `0x436e0c90` | `u16` |
| `+0x9a` | flags de predicado (bits 0–4) | `0x436e0858`…`0x436e08e8` | |
| `+0x27`–`+0x30` | estado LIF (10 B) | `0x436e1054` | copiado a estructura pública |

### 4.2 CommState (`0x436e0710`, VERIFICADO)

El setter solo escribe si la transición es legal; en otro caso retorna sin cambio:

- `0`, `1`: siempre.
- `2`: solo si `*ctx ≤ 1` (es decir, desde 0 o 1).
- `3`, `4`, `5`: solo si `*ctx == valor-1` (progresión estricta).
- otro: ignorado.

### 4.3 `PowMode` → estado (`VERIFICADO` por bytes)

Tabla de 16 B en `0x43c95735`, indexada por `PowMode-1`:

```
01 02 00 00 06 06 03 00 00 00 00 04 04 00 00 05
```

`0x436e0ccc` usa esa misma idea con máscaras de bits para decidir `SendType`:
si el bit de `PowMode` cae en la máscara `0x60` → tipo 2; si cae en la otra máscara → tipo 1.

### 4.4 Comando LIF (`0x436e2e32`, VERIFICADO el mecanismo)

`tbb` sobre `cmd - 0xC00` (8 entradas; tabla en `0x436e2e68`), con destinos
`0x436e2e70/2e7a/2e8c/2eb2/2ebe/2ec8/2eda/2f06`:

| cmd | Transición | Condición |
|---|---|---|
| `0xC00` | → `0xC00` | estado inicial |
| `0xC01` | → `0xC01` | `0x436e5828() != 0` |
| `0xC02` | → `0xC02` | `cmd_actual-0xC01 ≤ 6` y bit en máscara `0x4d` |
| `0xC03` | → `0xC03` | incondicional |
| `0xC04` | → `0xC04` | incondicional |
| `0xC05` | → `0xC05` | `0x436e587c() != 0` |
| `0xC06` | → `0xC06` | bit en máscara `0xa5` y `0x436e58d4() != 0` |
| `0xC07` | → `0xC07` | incondicional |

Cada cambio se registra como `LIF Command Change : 0x%X >>> 0x%X`; un `cmd` fuera de `0xC00`–`0xC07`
produce `LIF Command : Illegal Command Received!!! : cmd=%04X`. La semántica de cada estado
(qué operación de cámara representa) es `INFERENCIA`: los logs de la tarea principal asocian
`0xC05` a *PB* y `0xC06` a *POFF* (`0x43c98714`).

### 4.5 Volcado de estado (`0x436e239c`, VERIFICADO por orden de llamadas)

Orden exacto de getters y etiquetas:

| # | Getter | Etiqueta |
|---|---|---|
| 1 | `0x436e074c` | `CommState/LensState %02X%02X` (par 1) |
| 2 | `0x436e07b4` | (par 1, segundo) |
| 3 | `0x436e5728` | `PowMode/PowSeq %02X%02X` |
| 4 | `0x436e7b88` | (par 2, segundo) |
| 5 | `0x436e2390` | `LC T.O. Cnt %04X` |
| 6 | `0x436e029c` | `VsyncErrCnt %04X` |
| 7 | `0x436e0308` | `LIFState/Err %02X%02X` (par 1) |
| 8 | `0x436e0b88` | `MakeData/SendData %02X%02X` |
| 9 | `0x436e0c28` | `SendType/SameAdrs %02X%02X` |
| 10 | `0x436e0ca8` | (par 2, segundo) |
| 11 | `0x436e0c5c` | `ErrCntQueSync %04X` |
| 12 | `0x436e0c90` | `ErrCntQueVsync %04X` |

`0x436e10d8` (puntero a la estructura LIF) se usa para las líneas `LIFState/Err` y `LensErr`.

---

## 5. Qué queda abierto (`NO_VERIFICADO`)

1. **Contenido de la tabla de descriptores** de comandos (`0x440240a8` → `0x43fea2a0`): es
   *runtime-initialized*; en la imagen estática hay código, no datos. Sin runtime no se puede
   enumerar `{id, size, extra}` por comando.
2. **Semántica de los estados LIF `0xC00`–`0xC04` y `0xC07`**: el mecanismo está verificado, la
   correspondencia con operaciones de cámara solo está inferida para `0xC05`/`0xC06`.
3. **Significado del campo `+0x04` de la trama** (siempre 0 en el blob): podría ser un canal o un
   contador de secuencia. `INFERENCIA`: reservado.
4. **Unidades y temporización** de `DATASIZE` y de los plazos `0x108`/`0x150` (ticks del contador
   `ctx+0x24`), sin base de tiempo confirmada.
5. **Uso de `commtype 1`**: se sabe que transporta *Informations* y que el analizador copia
   `+0x14`; el reparto exacto entre `Informations1` e `Informations2` no está cerrado.
6. **Funciones 0x436e2f64** (segundo volcado): REA declara 1016 B pero el flujo real llega a
   `0x436e3370`; falta confirmar los límites exactos y el formato de cada línea.

---

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
# desensamblado con literales PIC
python3 analysis/s58/tdis.py A6000 0x436e2678 0x436e2cf8
# cadenas + llamadas en orden dentro de una función
python3 analysis/s66/func_strings.py A6000 0x436e239c 0x436e260c --calls
# mapa cadena → función
python3 analysis/s66/mount_strings_map.py A6000 --lo 0x43c95400 --hi 0x43c9aa00
```

REA (Ghidra 12.1.4) se usó vía el demonio compartido
(`analysis/rea-independent/bin/q.py analysis/rea-independent/run/rea.sock guion.json salida.jsonl`)
para `procedure_info` y pseudocódigo; el resto se resolvió con Capstone sobre los bytes.
