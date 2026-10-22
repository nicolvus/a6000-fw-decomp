# S136 — el módulo `[ACCY]` (106 trazas): el subsistema de **accesorios** de la A6000 fw3.21

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)).
> **Sin efecto en S51** (línea del obturador electrónico): ver §7.

Datos: [`accy.json`](accy.json) · Test: [`tests/test_s136_accy.py`](../../tests/test_s136_accy.py)
· Nota de captura: [`docs/capture/s136-accy.md`](../../docs/capture/s136-accy.md)
· Scripts: [`scan_accy.py`](scan_accy.py), [`scan_funcs.py`](scan_funcs.py),
[`scan_calls.py`](scan_calls.py), [`scan_callers.py`](scan_callers.py),
[`scan_diff.py`](scan_diff.py), [`scan_lines.py`](scan_lines.py),
[`build_json.py`](build_json.py), [`disasm.py`](disasm.py)

---

## 1. Resumen

- **106 cadenas** con el prefijo `[ACCY]`, en el bloque contiguo `0x43c24cac`–`0x43c26319`
  de `.rodata`. **111 sitios** de referencia PIC (regla estricta) y **61 funciones**
  emisoras, todas dentro de `0x43562a08`–`0x43566f20`.
- El bloque está **encajado** entre otros dos módulos en `.rodata`: antes, el final de
  `[DEPTH]` (`Valloc error!` `0x43c24c9e`, `14DepthGaugeMain` `0x43c24b85`); después,
  `[ADF]` (`14AdfInitializer` `0x43c26355`, `AdfMemMgrCtrl` `0x43c265be`, …).
  Las 9 clases RTTI `AccyUm*` están **intercaladas** dentro del propio bloque.
- Las 106 cadenas están **todas referenciadas** (0 muertas).
- El prefijo tiene **tres niveles**: `[ACCY][<nivel>][<sub-módulo>]`, con 15 sub-módulos
  distintos: `HW`, `Main`, `MAIN`, `SENSER`, `UART`, `UTILITY`, `FACTORY`, `HOUSING`,
  `AVOUT`, `AVR`, `BASE`, `HELLO`, `JIRO`, `NULL`, `REMOTE`.
- El módulo **no implementa un periférico de cámara**: implementa un **gestor de
  accesorios que se comunican por un UART propio** (`AccyUartOpen/Close/Send`,
  `IntAccyUartErr`), con un **handshake de 5 bytes** (bloque `HELLO`, que usa la palabra
  japonesa `AISATSU`, **sin traducir en los bytes**) y una capa de **comandos de API**
  por OSAL.
- Los tipos de accesorio los decide una **fábrica** (`FACTORY`): por **ID**
  (`0`=AvOut, `1`=JIRO1.5, `4`=HELLO, `5`=LANC-AVR, resto=`UNSUPPORTED`) y por
  **máscara de bits** (`0x80`=Remote, `0x40`=WaterHousing).
- El nombre de la familia de clases es **`AccyUm*`** (RTTI, 9 clases): `AccyUmDeviceBase`
  es la clase base de 7 dispositivos (`WaterHousing`, `AvOut`, `Avr`, `Hello`, `Jiro`,
  `Null`, `Remote`); `AccyUmKeyStatusMgr` es una clase **suelta** (sin clase base).
  **La sigla no está expandida en ningún byte**: no se inventa su significado.
- **Los ficheros fuente NO son identificables** (ver §5).

## 2. Qué es `[ACCY]`: el mapa del módulo

### 2.1 Las 15 sub-unidades

| sub-módulo | cadenas | rango de cadenas | sitios | funciones | contenido |
|---|---:|---|---:|---:|---|
| `HW` | 1 | `0x43c24cac` | 1 | 1 | `AD=%d, ID=%d` (dirección e ID del accesorio detectado) |
| `Main` | 9 | `0x43c24cca`–`0x43c24ee5` | 9 | 9 | hilo principal: `NotifyAttached/Detached`, `NotifyAttachedUart`, `NotifyApi`, *loop-back* UART, `Suspend/Resume Sus-Attached`, `**** UMMAIN START ****` |
| `MAIN` | 4 | `0x43c24d41`–`0x43c24de9` | 8 | 7 | `NotifyUartCommand`, `NotifyUartResponse`, `Uart Send Err` (2 formatos) |
| `SENSER` | 3 | `0x43c24f10`–`0x43c24f5f` | 3 | 1 | dispatcher de comandos: `unknown block %04X`, `Cmd %04X, S1 %02X`, `unknown command %04X` |
| `UART` | 13 | `0x43c24f88`–`0x43c251a8` | 13 | 5 | driver UART: `AccyUartOpen/Close/Send`, errores open/set-func/rx-start/tx-start/tx-stop/rx-stop, `UART FULL`, `RECIVE DATA`, `SEND DATA`, `IntAccyUartErr` |
| `UTILITY` | 2 | `0x43c251d1`–`0x43c25204` | 2 | 2 | `ConvNum8ToAscii`, `ConvAsciiToNum8` (conversión ASCII↔numérico del protocolo) |
| `FACTORY` | 7 | `0x43c25237`–`0x43c2533d` | 7 | 2 | alta de dispositivo: `HELLO/AvOut/JIRO1.5/LANC-AVR/UNSUPPORTED/Remote/WaterHousing Attached` |
| `HOUSING` | 5 | `0x43c25380`–`0x43c2543c` | 5 | 5 | caja estanca: `NotifyAttached/ContinuousAttached/Detached`, `RestoreInfo`, `NotifyUartTimedOut` |
| `AVOUT` | 2 | `0x43c2549e`–`0x43c254c6` | 2 | 2 | salida AV: `NotifyAttached/Detached` |
| `AVR` | 2 | `0x43c25502`–`0x43c25528` | 2 | 2 | `NotifyAttached/Detached` |
| `BASE` | 7 | `0x43c25560`–`0x43c256c1` | 7 | 2 | base común: `NotifyInput...` (tecla) y `NotifyDial...` (mando), con `valloc err`, `KeyCode:%08X, State:%d, INFO:%d`, `Send_Msg end/free err` |
| `HELLO` | 16 | `0x43c2570d`–`0x43c25a7b` | 16 | 7 | handshake: `RetrySendCmd`, `State Change To`, `SendCmd...CMD:%c%c%c%c%c`, `NotifyUartTimedOut`, `HELLO Command Not Execution`, `EventTimeout AISATSU`, `CateId = %08X`, `Unmatch State/Response/Not Support Category` |
| `JIRO` | 2 | `0x43c25aac`–`0x43c25ad3` | 2 | 2 | `NotifyAttached/Detached` |
| `NULL` | 1 | `0x43c25b20` | 1 | 1 | `NotifyAttached` (dispositivo nulo) |
| `REMOTE` | 32 | `0x43c25b47`–`0x43c26319` | 33 | 16 | **mando remoto**: `NotifyUartCommand`, `RecvCmd Unknown Category`, `EventKey`, `SaveInfo`/`RestoreInfo`, `Zoom State Change`, `To Input KEY:%08X...`, `TallyControlCmd`, `NotifyApiRequest`, `RemoteClose...Spinal:`, `GUIDE FRAME/START STOP/PHOTO FREEZE/PHOTO REC/ZOOM OFF`, `NotifyUartTimedOut`, `Set Tally Light` |

> `Main` y `MAIN` son el **mismo sub-módulo escrito con distinta capitalización** (9 + 4
> cadenas); se conservan tal cual aparecen en los bytes.

### 2.2 Las clases (RTTI) — 9 nombres en `0x43c2536d`–`0x43c26340`

Los nombres están intercalados **entre** las trazas, con la longitud en **ASCII** delante
(`16AccyUmDeviceBase`), y su tabla de `type_info` está en `.data`:

| clase | nombre (vaddr) | `type_info` | vtable | clase base |
|---|---|---|---|---|
| `AccyUmDeviceBase` | `0x43c2536d` | `0x43fd7c8c` | `0x43fd04f8` (`__class_type_info`) | — |
| `AccyUmDeviceWaterHousing` | `0x43c2546e` | `0x43fd7d6c` | `0x43fd03d8` (`__si_class_type_info`) | `AccyUmDeviceBase` |
| `AccyUmKeyStatusMgr` | `0x43c25489` | `0x43fd7d78` | `0x43fd04f8` | **ninguna** |
| `AccyUmDeviceAvOut` | `0x43c254ee` | `0x43fd7d80` | `0x43fd03d8` | `AccyUmDeviceBase` |
| `AccyUmDeviceAvr` | `0x43c2554e` | `0x43fd7d8c` | `0x43fd03d8` | `AccyUmDeviceBase` |
| `AccyUmDeviceHello` | `0x43c256f9` | `0x43fd7d98` | `0x43fd03d8` | `AccyUmDeviceBase` |
| `AccyUmDeviceJiro` | `0x43c25afa` | `0x43fd7da4` | `0x43fd03d8` | `AccyUmDeviceBase` |
| `AccyUmDeviceNull` | `0x43c25b0d` | `0x43fd7db0` | `0x43fd03d8` | `AccyUmDeviceBase` |
| `AccyUmDeviceRemote` | `0x43c26340` | `0x43fd7dbc` | `0x43fd03d8` | `AccyUmDeviceBase` |

Cada `type_info` derivado es un `__si_class_type_info` de 12 B:
`{vtable_si, puntero_al_nombre, puntero_al_typeinfo_de_la_base}`.

### 2.3 La taxonomía de accesorios (medida en el código)

`FACTORY` son **dos funciones**:

| función | discriminante | tipo de accesorio | traza |
|---|---|---|---|
| `0x435646a4` | `cmp r4,#4` (`0x435646ba`) | `HELLO` | `0x43c25237` |
| | `cmp r4,#0` (`0x43564788`) | `AvOut` | `0x43c25260` |
| | `cmp r4,#1` (`0x43564712`) | `JIRO1.5` | `0x43c25289` |
| | `cmp r4,#5` (`0x43564740`) | `LANC-AVR` | `0x43c252b4` |
| | resto | `UNSUPPORTED(%d)` | `0x43c252e0` |
| `0x435647c0` | `ands r4,r6,#0x80` (`0x435647f6`) | `Remote` | `0x43c25313` |
| | `tst.w r6,#0x40` (`0x43564820`) | `WaterHousing` | `0x43c2533d` |

Las fábricas de dispositivo (llamadas desde la fábrica) son:
`HELLO`→`0x43565ac8`, `AvOut`→`0x435655a4`, `JIRO1.5`→`0x43566074`,
`LANC-AVR`→`0x4356573c`, `Remote`→`0x43566484`, `WaterHousing`→`0x43564bc0`.

### 2.4 Transporte

- **UART propio del módulo**: `AccyUartOpen` `0x43563bf8`, `AccyUartClose` `0x43563de8`,
  `AccyUartSend` `0x43563ef4`, recepción `0x43563a94`; los errores llevan `CH:%d`
  (canal) y `%02X` (código). El driver usa `gpio`-style y primitivas de OSAL; es
  **distinto del UART de la montura de lente** (S66), que va por líneas CS/DATA.
- **Cola OSAL**: `osal_try_valloc_msg` `0x435612d0`, `osal_snd_msg` `0x4356120c`,
  `osal_free_msg` `0x435612ec`, `osal_rcv_msg` `0x43561260`.
- **GID emisor del módulo**: `0x008F0139`, escrito en `[msg-4]` en `0x43562270`
  (pool `0x43562284`); el mismo valor aparece en 608 sitios de la imagen.
- **Mensaje de entrada** (`NotifyInput`, `0x43565814`): payload de 16 B con
  `KeyCode@+0x00`, `ID@+0x04`, `State@+0x08`, `INFO@+0x0C`
  (`str r0,[r3,#4]` `0x4356584c`, `str r6,[r3]` `0x43565850`,
  `str r5,[r3,#8]` `0x43565852`, `str r7,[r3,#0xc]` `0x43565854`),
  enviado con `osal_snd_msg` y primer argumento `0x007A0020` (pool `0x435658bc`).
  El gemelo `NotifyDial` (`0x435658dc`) entrega la misma estructura para el **mando**.

### 2.5 El handshake

El bloque `HELLO` es un protocolo de **5 bytes ASCII**: `SendCmd...CMD:%c%c%c%c%c`
(`0x43c257c8`), `RetrySendCmd...retry_up:%d` (`0x43c2570d`), `State Change To %d`
(`0x43c2576d`), `NotifyUartResponse...State:%02X Date:[...]` (`0x43c258e4`),
`EventTimeout AISATSU Retryout Count:%d` (`0x43c258a6`) y
`NotifyUartResponse AISATSU Complete...State:%d` (`0x43c25945`).
El bloque `UTILITY` (`ConvNum8ToAscii` `0x43c251d1`, `ConvAsciiToNum8` `0x43c25204`)
sirve para traducir ese protocolo ASCII.

### 2.6 Quién usa el módulo

- **Capa API pública**: un bloque de envoltorios en `0x43a3ab00`–`0x43a3b300` que expone
  **28 puntos de entrada** del módulo (57 llamadas `bl` medidas); **no referencian
  ninguna cadena**, así que no dejan rastro de texto. Los destinos son
  `0x435621c8`, `0x4356248c`, `0x435624b0`, `0x43562590`, `0x43562634`, `0x4356288c`,
  `0x435628d8`, `0x43562ae4`, `0x43562b48`, `0x43562bb8`, `0x43562d18`, `0x43562d64`,
  `0x43563220`, `0x435636d0`, `0x435637ac`, `0x43563878`, `0x43564168`, `0x435641ec`,
  `0x43564278`, `0x4356436c`, `0x4356468c`, `0x435649e4`, `0x43564f50`, `0x435651fc`,
  `0x4356597c`, `0x435661cc`, `0x43566484`, `0x43566fdc`.
- **Consumidores externos** (llamadas `bl` medidas):
  | módulo | función llamante | destino ACCY |
  |---|---|---|
  | `[CLK_CTRL]` | `0x435a007c` (`0x435a00f0`) | `0x43562068` |
  | `[SDF]` (`SdfMsgAnalyzer.cpp`) | `0x43639c78` (`0x43639de2`) | `0x43562068` |
  | `[SYSV][HS]` | `0x4366bab0` (`0x4366bbfe`) | `0x43562068` |
  | `[VDF]` (`SystemCmdSysv.cpp`) | `0x4367ea52` (`0x4367f7c8`) | `0x43562068` |
  | `[VEF]` | `0x436ab7ac` (`0x436ab9c0`) | `0x43562068` |
  | `[SFRS]` | `0x439ad008` (`0x439ad15e`) | `0x43562068` |
  | `[ADF]` | `0x43541b02` (`0x43541b2a`, `0x43541b96`) | `0x435624c8`, `0x43562660` |
  | — | `0x4397f548`, `0x43b58932`, `0x43b589e0` | `0x43562068`, `0x4356212c` |

  Nota: `0x43562068` es una **función de librería compartida** (comparación contra una
  tabla de 20 entradas, `cmp r0,#0x13` en `0x4356206a`), no código propio de `[ACCY]`;
  se lista solo por completitud.

## 3. Inventario de las 106 trazas

El inventario completo (dirección, texto, nº de sitios, función que la emite y
diferencial) está en [`accy.json`](accy.json) → `strings[]`. Resumen por sub-bloque:

| sub-bloque | primera … última | nº | sitios | funciones |
|---|---|---:|---:|---:|
| HW | `0x43c24cac` | 1 | 1 | 1 |
| Main | `0x43c24cca` … `0x43c24ee5` | 9 | 9 | 9 |
| MAIN | `0x43c24d41` … `0x43c24de9` | 4 | 8 | 7 |
| SENSER | `0x43c24f10` … `0x43c24f5f` | 3 | 3 | 1 |
| UART | `0x43c24f88` … `0x43c251a8` | 13 | 13 | 5 |
| UTILITY | `0x43c251d1` … `0x43c25204` | 2 | 2 | 2 |
| FACTORY | `0x43c25237` … `0x43c2533d` | 7 | 7 | 2 |
| HOUSING | `0x43c25380` … `0x43c2543c` | 5 | 5 | 5 |
| AVOUT | `0x43c2549e` … `0x43c254c6` | 2 | 2 | 2 |
| AVR | `0x43c25502` … `0x43c25528` | 2 | 2 | 2 |
| BASE | `0x43c25560` … `0x43c256c1` | 7 | 7 | 2 |
| HELLO | `0x43c2570d` … `0x43c25a7b` | 16 | 16 | 7 |
| JIRO | `0x43c25aac` … `0x43c25ad3` | 2 | 2 | 2 |
| NULL | `0x43c25b20` | 1 | 1 | 1 |
| REMOTE | `0x43c25b47` … `0x43c26319` | 32 | 33 | 16 |
| **total** | `0x43c24cac`–`0x43c26319` | **106** | **111** | **61** |

### 3.1 Verificación a mano de sitios (decodificación `ldr`+`add`)

| sitio | instrucción | pool | destino |
|---|---|---|---|
| `0x43562a8c` | `ldr r3,[pc,#0x54]` `0x43562a8a` / `add r3,pc` | `0x43562ae0` = `0x006c221c` | `0x43c24cac` `[ACCY][INFO][HW]:AD=%d, ID=%d` |
| `0x43566be8` | `ldr r3,[pc,#0x148]` `0x43566be4` / `add r3,pc` | `0x43566d30` = `0x006bf4c4` | `0x43c260b0` `[ACCY][INFO][REMOTE]:%d:START STOP OFF…` |
| `0x4356583c` | `ldr r3,[pc,#0x94]` `0x43565834` / `add r3,pc` | `0x435658cc` = `0x006bfd20` | `0x43c25560` `[ACCY][ERR][BASE]:%d:NotifyInput...valloc err:%08X` |

## 4. El **mando remoto** (`REMOTE`) y el disparador remoto

Es el sub-bloque más grande (32 trazas) y el relevante para la línea del obturador.

- `SaveInfo...GF:%d SS:%d Freeze:%d Photo:%d Zoom:%d Tally:%d` `0x43c25c88` y
  `RestoreInfo...Savedata:%02X %02X` `0x43c25d15` guardan el estado de 5 grupos de
  interruptores: **GF** (guide frame), **SS** (start/stop), **Freeze**, **Photo**,
  **Zoom** (+ Tally).
- `RemoteClose...Spinal:%02X  GF:%02X  SS:%02X  Freeze:%02X  Photo:%02X  Zoom:%02X`
  `0x43c26000` (emitida por `0x43566b54`) vuelca ese estado al cerrar el mando.
  El campo `Spinal` es un **literal sin explicación en los bytes** (la misma palabra
  aparece en `Spinal.cpp`, `0x43c9c54f`, dentro de `[CAMERA_MAIN]`; relación no
  establecida).
- Al soltar cada grupo se emite su traza `… OFF` y se **entrega una tecla a la cámara**
  mediante `NotifyInput` (`0x43565814`). Los **códigos de tecla** salen del pool literal
  de `0x43566b54`:

  | traza | dirección | código de tecla | pool |
  |---|---|---|---|
  | `GUIDE FRAME OFF` | `0x43c26068` | `0x0A000009` | `0x43566cf8` |
  | **`START STOP OFF`** | **`0x43c260b0`** | **`0x0A00000D`** | `0x43566cfc` |
  | `PHOTO FREEZE OFF` | `0x43c260f7` | `0x0A000008` | `0x43566d04` |
  | `PHOTO REC OFF` | `0x43c26140` | `0x0A00000C` | `0x43566d0c` |
  | `ZOOM OFF` | `0x43c26186` | `0x0A000011` | `0x43566d14` |

- La tecla del mando entra por el camino genérico
  `NotifyUartCommand...UART CMD:%C%C%C%C%C%C [...]` `0x43c25b47` →
  `EventKey Catwgory:%02X ,Data1:%02X, Data2:%02X` `0x43c25bdf` →
  `To Input KEY:%08X STATE:%08X INFO:%08X` `0x43c25d76` (`0x435667ac`) →
  `NotifyInput` (`0x43565814`).

**Consecuencia**: el disparador remoto **no** es un comando de obturador: el módulo
lo traduce a un **evento de tecla genérico** (`KEY:0x0A00000D`, `STATE`, `INFO`) que
la cámara consume por la cola OSAL. El módulo `[ACCY]` **no escribe ni lee ningún
estado del obturador**.

## 5. Ficheros fuente

**NO VERIFICADO / no identificables.** Ningún nombre de fichero (`.cpp`, `.c`, `.h`) es
referenciado por el código del módulo: en todo el bloque `0x43562a08`–`0x43567060` la
**única** cadena referenciada que no lleva el prefijo `[ACCY]` es
`Valloc error!` (`0x43c24c9e`, sitio `0x43562a22`). El módulo **no emite trazas con
`file=%s line=%d`**.

Lo que sí se puede afirmar:

1. Los **nombres de clase RTTI** (`AccyUm*`, §2.2) acotan la nomenclatura del módulo.
2. El **primer `%d` de muchas trazas es el número de línea del fichero fuente**
   (se carga con `movs/movw r3,#N` y se pasa por la pila antes del `bl` de impresión).
   Secuencias **monótonas** medidas:
   - `FACTORY`: 183 (`0x435646d2`), 191 (`0x435646fc`), 197 (`0x4356472a`),
     203 (`0x43564758`), 209 (`0x43564778`) → un mismo fichero.
   - `UART`: 54 (`0x43563c0e`), 134, 139, 145, 152, 164, 178, 184, 208, 217, 241
     (`0x43563fa4`) → un mismo fichero.
   - `BASE`: 45 (`0x4356583c`), 60, 64, 68, 89, 99, 104 (`0x4356594e`) → un mismo fichero.
   - `REMOTE` (traces `OFF`): 233, 239, 246, 254, …, 783, 789.
   Es decir: **cada sub-bloque es (muy probablemente) un fichero fuente distinto**,
   con varios cientos de líneas. Los **nombres** siguen siendo desconocidos.
   (Extracción heurística: `scan_lines.py`; los valores de la tabla JSON son los
   verificados manualmente.)

## 6. Relación con la montura (S66) y con el resto de periféricos

- **Montura de lente (S66): subsistema DISTINTO.** S66 localiza el subsistema de
  montura en `0x436dfe6c`–`0x436e9ea4`, con sus propias trazas en
  `0x43c95659`–`0x43c9a900` y sus ficheros `Mount_Controller.cpp` /
  `Mount_DividedInfo.cpp`. `[ACCY]` **no** menciona `mount`, `lens` ni `MOUNT` en
  ninguna de sus 106 trazas, y su código no referencia las cadenas del subsistema de
  montura. Ambos usan UART, pero **son dos UART y dos protocolos distintos**
  (S66: líneas CS/DATA con trama `0xF0…0x55`; ACCY: protocolo ASCII de 5 bytes con
  handshake `HELLO`).
- **Flash, batería, disparador con cable, obturación remota**: **no aparecen**.
  Ninguna de las 106 trazas menciona `flash`, `batt`, `release`, `cable` ni `shutter`.
  El único camino "disparador" es el del **mando remoto** (§4), que entrega teclas.
- **Mando (dial)**: sí — `NotifyDial...KeyCode:%08X, State:%d, INFO:%d` `0x43c2567d`
  (`0x435658dc`).
- **Caja estanca (`WaterHousing`)**, **salida AV (`AvOut`)**, **JIRO1.5**,
  **LANC-AVR** y **NULL**: sí, como clases de dispositivo.

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 7.1 El token

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| apariciones de `[ACCY]` | **106** | **0** | **0** |
| `UMMAIN` | 1 | 0 | 0 |
| `AccyUart` | 5 | 0 | 0 |
| `NotifyAttached` | 9 | 0 | 0 |
| `NotifyDetached` | 7 | 0 | 0 |
| `START STOP` | 1 | 0 | 0 |
| `Tally` | 7 | 0 | 0 |

Además, **ninguna** de las 106 cadenas (ni su «núcleo», el texto tras
`[ACCY][NIVEL][SUB]`) aparece **literalmente** en la A7S ni en la A6300: 0/106 en ambos.

### 7.2 Corrección importante: el módulo **sí existe** en los otros dos firmwares

Las **clases** `AccyUm*` **existen** en la A7S fw3.20 y en la A6300 fw2.01, en el mismo
bloque de `.rodata` y con la misma jerarquía:

| | bloque RTTI | `AccyUmDeviceBase` | `…WaterHousing` | `…KeyStatusMgr` | `…AvOut` | `…Avr` | `…Hello` | `…Jiro` | `…Null` | `…Remote` | `AccyMiDeviceBase` | `AccyMiDeviceLight` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A6000 fw3.21 | `0x43c2536d`–`0x43c26340` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | **NO** | **NO** |
| A7S fw3.20 | `0x43c25a23`–`0x43c25afc` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | **SÍ** | **SÍ** |
| A6300 fw2.01 | `0x43d0c9a2`–`0x43d0ca7d` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | **SÍ** | **SÍ** |

Es decir: **lo propio de la A6000 fw3.21 no es el módulo, es su *traza***. En la A7S y
en la A6300 el módulo existe como código (mismas clases, mismo protocolo) pero **sin
ninguna traza de depuración**; en su lugar tienen una **tabla de nombres de comando**
(`accy`, `edr`, `EnableDummyRecv`, `DisableDummyRecv`, `SendCommand`, `MsSleep`,
`rx`/`RxResponse`, `rxc`/`RxCommand`, `sq`/`SetQue`, `GetQue`, en `0x43c259b5`–`0x43c25a1c`
de la A7S) y **dos clases `AccyMi*`** que la A6000 no tiene.

**Salvedad (misma que S130 §4)**: la comparación mezcla **versión y modelo**; no hay
una fw anterior de la A6000 en el repositorio, así que no se puede separar
«nuevo en la fw3.21» de «propio de este modelo».

## 8. Línea del obturador: veredicto

**No hay relación directa con el obturador, ni mecánico ni electrónico.**

1. **0/106** trazas contienen `shut`, `silent`, `electro`, `mech`, `curtain`, `mirror`,
   `imager`, `sensor`, `readout`, `flash`, `lens`, `mount`, `batt`.
2. El código del módulo **solo referencia una cadena ajena a `[ACCY]`**: `Valloc error!`
   (`0x43c24c9e`). Por tanto **no toca** ninguna cadena del subsistema de obturación
   (`[SFRS][PINSEND]`, `shutter mute on/off` `0x43c8253b`, `shutCycleCount`, …).
3. Lo más cercano al disparador remoto es la tecla **`START STOP`**
   (`0x43c260b0` → `KEY:0x0A00000D`), que se entrega como **evento de tecla genérico**
   por `NotifyInput` (`0x43565814`). **El módulo no decide ni ejecuta el disparo**:
   solo traduce pulsaciones de un accesorio a eventos de entrada de la cámara.
4. **NO VERIFICADO**: qué acción concreta ejecuta la tecla `0x0A00000D` (no hay tabla
   de nombres de tecla en el firmware; no se ha encontrado un mapa `0x0A0000xx`→acción).
5. **NO VERIFICADO**: el significado de `Spinal` en este contexto (el mismo término
   aparece en `Spinal.cpp` dentro de `[CAMERA_MAIN]`, pero no se ha establecido la
   relación).

**Conclusión para S51**: el hito **no aporta** ningún dato sobre el obturador
electrónico; **S51 A/B/C = NO** se mantiene.

## 9. NO VERIFICADO / abierto

1. **Ficheros fuente** del módulo: desconocidos (§5). Solo se conocen los nombres de
   clase RTTI `AccyUm*` y los números de línea (parciales).
2. **Sigla `ACCY` / `UM`**: no está expandida en ningún byte; no se desarrolla.
   (`UM` aparece en `**** UMMAIN START ****`, `0x43c24ee5`, pero no se demuestra que
   signifique «unit management».)
3. **Significado de `Spinal`**, `GF`, `SS`, `Tally`, `JIRO`, `AVR`, `LANC`, `AISATSU`:
   literales del firmware, sin explicación en los bytes.
4. **Tabla de nombres de tecla** `0x0A0000xx` → acción de cámara: no localizada.
5. **Contenido de los comandos** del protocolo de 5 bytes (`%c%c%c%c%c`): no hay tabla
   de identificadores de comando ni de *category* (`CateId = %08X` `0x43c2598c`,
   `EventKey Catwgory:%02X` `0x43c25bdf`) recuperable estáticamente.
6. **Cola OSAL de destino** del mensaje de entrada: se conoce el valor pasado a
   `osal_snd_msg` (`0x007A0020`), pero no su nombre ni su consumidor.
7. **`AccyMiDeviceBase` / `AccyMiDeviceLight`**: presentes en la A7S/A6300 y ausentes en
   la A6000; su papel no está elucidado.
8. **Extensión del módulo fuera del bloque de trazas**: las funciones auxiliares
   `0x4356288c`–`0x43562a08` y `0x43566fdc`–`0x43567060` (sin traza) y el bloque API
   `0x43a3ab00`–`0x43a3b300` (28 puntos de entrada) están **medidos por llamadas**,
   no decompilados.

## 10. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (16 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 106 apariciones de `[ACCY]` en la A6000 fw3.21 entre `0x43c24cac` y
   `0x43c26319`; **0** en la A7S fw3.20 y el A6300 fw2.01 → confirmado con `bytes.count()` en los
   tres blobs.
2. **La corrección de la premisa es correcta y es el hallazgo**: el **módulo sí existe** en la A7S
   y el A6300 — las clases `AccyUmDeviceBase` y `AccyUmKeyStatusMgr` están en los tres blobs
   (1/1/1) — pero **sin trazas**; allí hay además dos clases `AccyMi*` que la A6000 no tiene.
   → lo propio de la fw3.21 de la A6000 es el **logging**, no el módulo. (Lo confirma el propio
   escaneo: `AccyUartOpen` y `NotifyInput` solo existen en la A6000 → son *símbolos* nuevos, no
   solo trazas.)
3. **Taxonomía de subclases**: `AccyUmDeviceBase` + 7 derivadas (`WaterHousing`, `AvOut`, `Avr`,
   `Hello`, `Jiro`, `Null`, `Remote`) → tabla `type_info` en `0x43fd7c8c`–`0x43fd7dbc`; máscara
   `0x80`=Remote, `0x40`=WaterHousing; el disparador remoto aparece solo como **tecla del mando**
   (`START STOP OFF` `0x43c260b0` → `KEY:0x0A00000D`) entregada por `NotifyInput` `0x43565814` →
   **no decide ni ejecuta el disparo**.
4. **Negativo acotado**: 0/106 trazas mencionan obturador, flash, lente, montura o batería; el
   disparador remoto no es un camino de disparo → **sin efecto en S51**.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
