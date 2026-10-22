# S180 — el módulo `[REMOTE]` (32 trazas) de la A6000 fw3.21

> Hito de la **línea de RE general por módulos de trazas**. Sólo análisis de bytes
> (sin REA/Ghidra, sin ejecutar firmware). Convención **vaddr = 0x43541000 + file_offset**
> (válida para la A6000 fw3.21, la A7S fw3.20 y la A6300 fw2.01).
> Referencias a cadenas: **regla PIC estricta** (canónica del repo,
> `analysis/s106_imaging_cap/scan_pic_refs_strict.py`; nota metodológica:
> `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. **NO VERIFICADO** = pendiente.

Datos: [`remote.json`](remote.json) · Test: [`tests/test_s180_remote.py`](../../tests/test_s180_remote.py)
· Nota de captura: [`docs/capture/s180-remote.md`](../../docs/capture/s180-remote.md)
· Scripts: `scan_strings.py`, `scan_anchors.py`, `scan_accy_tags.py`, `scan_pic_sites.py`,
`scan_pic_local.py`, `scan_funcmap.py`, `scan_logger.py`, `scan_lines.py`, `scan_levels.py`,
`scan_levels2.py`, `scan_logger_targets.py`, `scan_rtti.py`, `scan_vtables.py`,
`scan_keycodes.py`, `scan_tbb.py`, `scan_verify.py`, `dasm.py`, `dasm_any.py`,
`dump_pool.py`, `dump_pool_str.py`, `dump_strings_range.py`, `gen_tables.py`, `build_json.py`.

---

## 1. Resumen / veredicto

**`[REMOTE]` es el subsistema de MANDO A DISTANCIA (control remoto por UART) de la A6000
fw3.21.** La hipótesis del enunciado queda **CONFIRMADA** por los bytes: las 32 cadenas
`[REMOTE]` son exactamente el sub-bloque `REMOTE` que S136 había delimitado dentro del
módulo `[ACCY]` (mismo rango `0x43c25b47`–`0x43c26319`, mismos **33 sitios** y mismas
**16 funciones**). La clase que lo implementa es **`AccyUmDeviceRemote`** (RTTI en
`0x43c26340`, inmediatamente **después** del bloque de trazas) y su **vtable** está en
`0x43fb9114`.

| magnitud | valor |
|---|---|
| cadenas con el token `[REMOTE]` | **32** (32 apariciones = 32 textos) |
| rango de las cadenas | `0x43c25b47` – `0x43c26319` (bloque contiguo) |
| sitios de emisión PIC (regla estricta) | **33** en **16 funciones** |
| cadenas **sin ninguna referencia** | **0** (las 32 vivas) |
| pares PIC verificados a mano | **33 / 33**, 0 fallos, 0 reuso de registro |
| punteros absolutos de 4 B a las 32 | **0** en A6000 y A7S; **2** en A6300 (bytes en `.data`, no son punteros) |
| «gemelo» (núcleo sin prefijo) fuera de la propia cadena | **6 / 32** en A6000 (literales de **otros sub-bloques `ACCY`**, ver §1.1), **0 / 32** en A7S, **0 / 32** en A6300 |
| clase RTTI que implementa el módulo | `AccyUmDeviceRemote` (`0x43c26340`), base `AccyUmDeviceBase` (`0x43c2536d`) |
| id de módulo / niveles del logger | **93** / `1=ERR 2=WARN 3=DEBUG 4=INFO` |
| diferencial del token `[REMOTE]` | A6000 fw3.21 **32** / A7S fw3.20 **0** / A6300 fw2.01 **0** |

### 1.1 Respuesta a las dos hipótesis del enunciado

**(a) «`[REMOTE]` = el mando a distancia contenido en `[ACCY]` (S136)» → CONFIRMADA.**
Mismo rango de 32 cadenas, mismos 33 sitios, mismas 16 funciones que el sub-bloque
`REMOTE` de S136; y la clase RTTI `AccyUmDeviceRemote` (`0x43c26340`) está intercalada
justo detrás del bloque, junto a las otras 8 clases `AccyUm*`.

**(b) «la fw3.21 antepone una copia con prefijo y deja vivo el literal original»
(la «firma» de S177/S179) → REFUTADA para `[REMOTE]`.** El caso es **distinto**:

* **No hay gemelo.** El «núcleo» (el texto tras `[ACCY][NIVEL][REMOTE]:%d:`) **no existe
  como literal autónomo** en ningún firmware: 0/32 en la A7S, 0/32 en la A6300. En la A6000
  hay **6 / 32** coincidencias externas, y **ninguna** es el «original» de una traza
  reescrita: son **literales de otros sub-bloques del mismo módulo `[ACCY]`** que
  reutilizan el mismo texto —
  `[HELLO]` comparte `RetrySendCmd...retry_up:%d` (`0x43c25724`),
  `SendCmd Buffer Busy Request CMD:%S` (`0x43c25817`) y
  `NotifyUartTimedOut...RetryCount:%d` (`0x43c25851`); `[HOUSING]` comparte
  `RestoreInfo...Savedata:%02X %02X` (`0x43c253f3`); y `NotifyAttached` /
  `NotifyDetached` son mensajes genéricos repetidos en `Main`, `HOUSING`, `AVOUT`,
  `AVR`, `HELLO`, `JIRO` y `NULL` (8 y 6 copias respectivamente).
* **No hay doble emisión.** Las 16 funciones del módulo **nunca** llaman al logger global
  `0x43902718`: todas las trazas salen por un **logger propio del sub-bloque**,
  `0x435661e4`, con firma `(id_módulo=93, ?, nivel, fmt, …)`. Los **15 sub-bloques** de
  `[ACCY]` usan **14 loggers distintos** (misma plantilla de código; `Main` y `MAIN`
  comparten `0x43562c94`), lo que confirma que `0x435661e4` es *el* logger de `REMOTE`.
* El prefijo no es de longitud fija, porque el **nivel va dentro** del prefijo:
  `[ACCY][ERR][REMOTE]:%d:` = 23 B, `[ACCY][INFO][REMOTE]:%d:` = `[ACCY][WARN][REMOTE]:%d:` = 24 B,
  `[ACCY][DEBUG][REMOTE]:%d:` = 25 B.

⇒ El diferencial de `[REMOTE]` **no** es de «renombrado» sino de **logging**: en la
A7S fw3.20 y la A6300 fw2.01 **el código del mando remoto existe igual**, pero **sin
ninguna traza** (de hecho, sin ninguna traza `[ACCY]`). Detalle en §7.

---

## 2. Qué es exactamente `[REMOTE]`

### 2.1 La clase

`AccyUmDeviceRemote` es una de las **7 subclases** de `AccyUmDeviceBase` (las otras 6:
`WaterHousing`, `AvOut`, `Avr`, `Hello`, `Jiro`, `Null`; además existe la clase suelta
`AccyUmKeyStatusMgr`, sin clase base).
Su **vtable** (`0x43fb9114`, 8 entradas) es **exactamente** la lista de los 8 métodos
virtuales del accesorio, y **8 de las 16 funciones** del módulo son las implementaciones
de esos métodos:

| slot vtable | entrada | método | trazas que emite |
|---|---|---|---|
| 0 | `0x43566ec1` | `NotifyAttached` | `[ACCY][INFO][REMOTE]:%d:NotifyAttached` |
| 1 | `0x43566a55` | `NotifyApiRequest` | 4 trazas `NotifyApiRequest...` |
| 2 | `0x43566e5d` | `NotifyUartResponse` | `NotifyUartResponse...Set Tally Light`, `Set Tally Light:%02X State:%d` |
| 3 | `0x43566d8d` | `NotifyUartTimedOut` | `NotifyUartTimedOut...`, `TimeoutNotify...`, `EventTimeout Tally Light TIMEOUT` |
| 4 | `0x43566999` | `CallForTransaction` | `CallForTransaction...Wait Tally Light Response` |
| 5 | `0x43566291` | `NotifyUartCommand` | `NotifyUartCommand...UART CMD`, `RecvCmd Unknown Category`, `EventKey Catwgory` |
| 6 | `0x435665f9` | `ExecUartCommand` | `ExecUartCommand`, `To Input KEY:%08X STATE:%08X INFO:%08X` |
| 7 | `0x43566d45` | `NotifyDetached` | `[ACCY][INFO][REMOTE]:%d:NotifyDetached` |

Los 8 nombres de método están **en los propios mensajes de traza** (base textual directa).
La clase base `AccyUmDeviceBase` tiene sus 8 virtuales implementados en una biblioteca
compartida (`0x43fb8f6c` → `0x43a3afe1`…`0x43a3b001`); `AccyUmDeviceRemote` los
**sobrescribe los 8**.

### 2.2 El flujo del mando (medido en el código)

1. **Entrada**: `NotifyUartCommand` (`0x43566290`) recibe la trama UART y valida
   `byte[0] == '#'` (`0x23`) y `byte[1] == '7'` (`0x37`); `byte[2]` es la **categoría**
   `'0'`–`'5'` (`sub r1,r2,#0x30` / `cmp r1,#5` en `0x435662ec`/`0x435662f0`) y se
   despacha con una tabla **`tbb` de 6 entradas** en `0x435662f4` (base `0x435662f8`).
   Si la categoría no existe → `RecvCmd Unknown Category:%02X` (línea 434).
2. **Traducción a tecla**: `ExecUartCommand` (`0x435665f8`) lee el comando pendiente de
   un **buffer en `.bss`** (`add rX,pc` sobre literales `0x00a2a466`, `0x00a2a438`, … →
   `0x440D105E` y alrededores) y decide el grupo de botón con otro **`tbb` de 4 entradas**
   en `0x43566638` (base `0x4356663c`): `'0'`→`0x43566640` **GUIDE FRAME**,
   `'1'`→`0x4356666e` **START STOP**, `'2'`→`0x4356669c` **PHOTO FREEZE**,
   `'3'`→`0x435666d4` **PHOTO REC**. Cada grupo conmuta un flag propio del objeto.
3. **Entrega a la cámara**: la traza `To Input KEY:%08X STATE:%08X INFO:%08X` (línea 673)
   va seguida de `NotifyInput` (`0x43565814`), que mete el evento en la cola OSAL.
4. **Control del Tally** (la luz de tally del accesorio): `NotifyApiRequest`
   (`0x43566a54`) atiende la **petición de API con comando `0x80`** y estado `0..3`;
   `TallyControlCmd` (`0x4356692c`) construye la trama de 6 bytes
   `'%' '7' '6' <estado> '0' '*'` + NUL y la envía con `SendCmd` (`0x435668b4`), que la
   copia al buffer del objeto (`+0x20`, longitud en `+0x1C`).
   Un tercer **`tbb`** en `0x43566960` (4 entradas) traduce el estado de tally a
   `'0'/'1'/'2'/'3'`.
5. **Cierre**: `RemoteClose` (`0x43566b54`) vuelca el estado (Spinal/GF/SS/Freeze/Photo/Zoom)
   y, por cada flag activo, emite su traza `… OFF` entregando la tecla de "suelta" con
   `NotifyInput` (`0x43565814`).

### 2.3 Los 5 grupos de teclas con interruptor (+ Tally)

| grupo | flag en el objeto | tecla (código) | evento "OFF" | traza |
|---|---|---|---|---|
| GUIDE FRAME | `+0x3C` | `0x0A000009` | `0x06000600` (`mov.w r0,#0x6000600` `0x43566bba`) | `GUIDE FRAME OFF` (`0x43c26068`) |
| START STOP | `+0x3D` | `0x0A00000D` | `0x06000700` (pool `0x43566d00`) | `START STOP OFF` (`0x43c260b0`) |
| PHOTO FREEZE | `+0x3E` | `0x0A000008` | `0x06000800` (pool `0x43566d08`) | `PHOTO FREEZE OFF` (`0x43c260f7`) |
| PHOTO REC | `+0x3F` | `0x0A00000C` | `0x06000900` (pool `0x43566d10`) | `PHOTO REC OFF` (`0x43c26140`) |
| ZOOM | `+0x34`/`+0x38` | `0x0A000011` | `0x06000A00` (pool `0x43566d18`, zoom=1) y `0x06000B00` (pool `0x43566d1c`, zoom=2) | `ZOOM OFF` (`0x43c26186`, 2 sitios) |

En el pool hay además `0x0A00000A` (`0x43566d24`): **su uso no está VERIFICADO**.

### 2.4 Base textual de la sigla

* `REMOTE` **sí** tiene base textual: la clase RTTI `AccyUmDeviceRemote`
  (`18AccyUmDeviceRemote`, `0x43c26340`) — el nombre de la clase **es** el
  desarrollo de la etiqueta. En los bytes, `Remote` aparece además en
  `RemoteClose...` (`0x43c26000`) y en la fábrica de dispositivos
  (`Remote Attached`, S136 §2.3).
* `ACCY` y `UM` **no** tienen base textual (S136 §9): **se dejan sin desarrollar**.
  `Spinal`, `GF`, `SS`, `Tally`, `JIRO`, `AVR`, `LANC`, `AISATSU` son literales sin
  explicación en los bytes.

---

## 3. Las 32 trazas (dirección exacta + sitio de referencia)

`addr` = dirección de la cadena; `linea` = número de línea del fichero fuente (primer
vararg `%d`, medido); `sitio` = dirección del `add rX,pc` (regla PIC estricta, verificada
a mano en §8).

| # | addr | nivel | linea | texto | n | sitio(s) | funcion(es) |
|---|---|---|---|---|---|---|---|
| 1 | `0x43c25b47` | INFO | 367 | `[ACCY][INFO][REMOTE]:%d:NotifyUartCommand...UART CMD:%C%C%C%C%C%C [%02X %02X %02X %02X %02X %02X]` | 1 | `0x435662b2` | `0x43566290` |
| 2 | `0x43c25ba9` | WARN | 434 | `[ACCY][WARN][REMOTE]:%d:RecvCmd Unknown Category:%02X` | 1 | `0x4356637c` | `0x43566290` |
| 3 | `0x43c25bdf` | WARN | 442 | `[ACCY][WARN][REMOTE]:%d:EventKey Catwgory:%02X ,Data1:%02X, Data2:%02X` | 1 | `0x43566392` | `0x43566290` |
| 4 | `0x43c25c26` | INFO | 850 | `[ACCY][INFO][REMOTE]:%d:RetrySendCmd...retry_up:%d` | 1 | `0x435663d0` | `0x435663b8` |
| 5 | `0x43c25c59` | ERR | 854 | `[ACCY][ERR][REMOTE]:%d:RetrySendCmd Buffer err` | 1 | `0x435663e6` | `0x435663b8` |
| 6 | `0x43c25c88` | INFO | 696 | `[ACCY][INFO][REMOTE]:%d:SaveInfo...GF:%d SS:%d Freeze:%d Photo:%d Zoom:%d Tally:%d` | 1 | `0x4356650a` | `0x435664d0` |
| 7 | `0x43c25cdb` | DEBUG | 941 | `[ACCY][DEBUG][REMOTE]:%d:Zoom State Change To %d Speed:%d` | 1 | `0x4356656e` | `0x43566558` |
| 8 | `0x43c25d15` | INFO | 718 | `[ACCY][INFO][REMOTE]:%d:RestoreInfo...Savedata:%02X %02X` | 1 | `0x4356659e` | `0x43566580` |
| 9 | `0x43c25d4e` | INFO | 457 | `[ACCY][INFO][REMOTE]:%d:ExecUartCommand` | 1 | `0x43566612` | `0x435665f8` |
| 10 | `0x43c25d76` | INFO | 673 | `[ACCY][INFO][REMOTE]:%d:To Input KEY:%08X STATE:%08X INFO:%08X` | 1 | `0x435667ac` | `0x435665f8` |
| 11 | `0x43c25db5` | INFO | 878 | `[ACCY][INFO][REMOTE]:%d:SendCmd...CMD:%S retry:%d` | 1 | `0x435668d0` | `0x435668b4` |
| 12 | `0x43c25de7` | ERR | 889 | `[ACCY][ERR][REMOTE]:%d:SendCmd Buffer Busy Request CMD:%S` | 1 | `0x435668f8` | `0x435668b4` |
| 13 | `0x43c25e21` | INFO | 815 | `[ACCY][INFO][REMOTE]:%d:TallyControlCmd...retry:%d` | 1 | `0x43566940` | `0x4356692c` |
| 14 | `0x43c25e54` | INFO | 352 | `[ACCY][INFO][REMOTE]:%d:CallForTransaction...Wait Tally Light Response  NextState:%d` | 1 | `0x43566a38` | `0x43566998` |
| 15 | `0x43c25ea9` | INFO | 170 | `[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Command:%02X State:%02X CntlState:%d` | 1 | `0x43566a78` | `0x43566a54` |
| 16 | `0x43c25ef9` | INFO | 188 | `[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Buffer Busy CntlState:%d` | 1 | `0x43566ace` | `0x43566a54` |
| 17 | `0x43c25f3d` | INFO | 192 | `[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Tally Light State:%d  NextState:%d` | 1 | `0x43566aea` | `0x43566a54` |
| 18 | `0x43c25f8b` | INFO | 196 | `[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Not Support Command:%02X or State:%02X` | 1 | `0x43566b00` | `0x43566a54` |
| 19 | `0x43c25fdd` | INFO | 967 | `[ACCY][INFO][REMOTE]:%d:AccyCmdClr` | 1 | `0x43566b3e` | `0x43566b2c` |
| 20 | `0x43c26000` | INFO | 745 | `[ACCY][INFO][REMOTE]:%d:RemoteClose...Spinal:%02X  GF:%02X  SS:%02X  Freeze:%02X  Photo:%02X  Zoom:%02X` | 1 | `0x43566b86` | `0x43566b54` |
| 21 | `0x43c26068` | INFO | 751 | `[ACCY][INFO][REMOTE]:%d:GUIDE FRAME OFF  KEY:%08X STATE:%08X  INFO:%08X` | 1 | `0x43566bb2` | `0x43566b54` |
| 22 | `0x43c260b0` | INFO | 758 | `[ACCY][INFO][REMOTE]:%d:START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X` | 1 | `0x43566be8` | `0x43566b54` |
| 23 | `0x43c260f7` | INFO | 766 | `[ACCY][INFO][REMOTE]:%d:PHOTO FREEZE OFF  KEY:%08X STATE:%08X  INFO:%08X` | 1 | `0x43566c24` | `0x43566b54` |
| 24 | `0x43c26140` | INFO | 773 | `[ACCY][INFO][REMOTE]:%d:PHOTO REC OFF  KEY:%08X STATE:%08X  INFO:%08X` | 1 | `0x43566c56` | `0x43566b54` |
| 25 | `0x43c26186` | INFO | 783 / 789 | `[ACCY][INFO][REMOTE]:%d:ZOOM OFF  KEY:%08X STATE:%08X  INFO:%08X` | **2** | `0x43566c8e`, `0x43566cb4` | `0x43566b54` |
| 26 | `0x43c261c7` | INFO | 147 | `[ACCY][INFO][REMOTE]:%d:NotifyDetached` | 1 | `0x43566d54` | `0x43566d44` |
| 27 | `0x43c261ee` | INFO | 249 | `[ACCY][INFO][REMOTE]:%d:NotifyUartTimedOut...RetryCount:%d` | 1 | `0x43566da2` | `0x43566d8c` |
| 28 | `0x43c26229` | ERR | 257 | `[ACCY][ERR][REMOTE]:%d:TimeoutNotify...Command Not Execution` | 1 | `0x43566db8` | `0x43566d8c` |
| 29 | `0x43c26266` | DEBUG | 284 | `[ACCY][DEBUG][REMOTE]:%d:EventTimeout Tally Light TIMEOUT` | 1 | `0x43566e1c` | `0x43566d8c` |
| 30 | `0x43c262a0` | INFO | 210 | `[ACCY][INFO][REMOTE]:%d:NotifyUartResponse...Set Tally Light:%02X` | 1 | `0x43566e76` | `0x43566e5c` |
| 31 | `0x43c262e2` | DEBUG | 228 | `[ACCY][DEBUG][REMOTE]:%d:Set Tally Light:%02X State:%d` | 1 | `0x43566eaa` | `0x43566e5c` |
| 32 | `0x43c26319` | INFO | 113 | `[ACCY][INFO][REMOTE]:%d:NotifyAttached` | 1 | `0x43566ed0` | `0x43566ec0` |

**Total: 33 sitios en 16 funciones.** Las 32 cadenas están **todas referenciadas**
(0 muertas) y ocupan **un bloque contiguo** de `.rodata`, justo antes del nombre RTTI
`18AccyUmDeviceRemote` (`0x43c26340`) y después del literal
`[ACCY][DEBUG][NULL] NotifyAttached(%d)` (`0x43c25b20`).

---

## 4. Funciones → traza (mapa completo)

| función | método | trazas (sitio → addr) |
|---|---|---|
| `0x43566290` | `NotifyUartCommand` (vtable[5]) | `0x435662b2`→`0x43c25b47` · `0x4356637c`→`0x43c25ba9` · `0x43566392`→`0x43c25bdf` |
| `0x435663b8` | `RetrySendCmd` | `0x435663d0`→`0x43c25c26` · `0x435663e6`→`0x43c25c59` |
| `0x435664d0` | `SaveInfo` | `0x4356650a`→`0x43c25c88` |
| `0x43566558` | `SetZoom` | `0x4356656e`→`0x43c25cdb` |
| `0x43566580` | `RestoreInfo` | `0x4356659e`→`0x43c25d15` |
| `0x435665f8` | `ExecUartCommand` (vtable[6]) | `0x43566612`→`0x43c25d4e` · `0x435667ac`→`0x43c25d76` |
| `0x435668b4` | `SendCmd` | `0x435668d0`→`0x43c25db5` · `0x435668f8`→`0x43c25de7` |
| `0x4356692c` | `TallyControlCmd` | `0x43566940`→`0x43c25e21` |
| `0x43566998` | `CallForTransaction` (vtable[4]) | `0x43566a38`→`0x43c25e54` |
| `0x43566a54` | `NotifyApiRequest` (vtable[1]) | `0x43566a78`→`0x43c25ea9` · `0x43566ace`→`0x43c25ef9` · `0x43566aea`→`0x43c25f3d` · `0x43566b00`→`0x43c25f8b` |
| `0x43566b2c` | `AccyCmdClr` | `0x43566b3e`→`0x43c25fdd` |
| `0x43566b54` | `RemoteClose` | `0x43566b86`→`0x43c26000` · `0x43566bb2`→`0x43c26068` · `0x43566be8`→`0x43c260b0` · `0x43566c24`→`0x43c260f7` · `0x43566c56`→`0x43c26140` · `0x43566c8e`→`0x43c26186` · `0x43566cb4`→`0x43c26186` |
| `0x43566d44` | `NotifyDetached` (vtable[7]) | `0x43566d54`→`0x43c261c7` |
| `0x43566d8c` | `NotifyUartTimedOut` (vtable[3]) | `0x43566da2`→`0x43c261ee` · `0x43566db8`→`0x43c26229` · `0x43566e1c`→`0x43c26266` |
| `0x43566e5c` | `NotifyUartResponse` (vtable[2]) | `0x43566e76`→`0x43c262a0` · `0x43566eaa`→`0x43c262e2` |
| `0x43566ec0` | `NotifyAttached` (vtable[0]) | `0x43566ed0`→`0x43c26319` |

Las 16 funciones están en el rango `0x43566290`–`0x43566f04`, dentro del bloque de
código del módulo `[ACCY]` (`0x43562a08`–`0x43567060`).
**Ninguna de las 33 referencias apunta a una cadena que no sea `[REMOTE]`**: el módulo
no emite ni una sola traza de otro sub-bloque.

---

## 5. Ficheros fuente y nombres

* **Clase RTTI**: `AccyUmDeviceRemote` (`0x43c26340`), `type_info` en `0x43fd7dbc`
  (`__si_class_type_info`, base `AccyUmDeviceBase` `0x43fd7c8c`), vtable en `0x43fb9114`.
* **Nombres de método**: los 8 de la vtable están **en los propios mensajes**
  (`NotifyAttached`, `NotifyDetached`, `NotifyUartCommand`, `NotifyUartResponse`,
  `NotifyUartTimedOut`, `NotifyApiRequest`, `ExecUartCommand`, `CallForTransaction`)
  más los privados `SaveInfo`, `RestoreInfo`, `SendCmd`, `RetrySendCmd`,
  `TallyControlCmd`, `AccyCmdClr`, `RemoteClose`, `SetZoom`.
* **Nombre del fichero fuente**: **NO VERIFICADO / no identificable**. El bloque `[ACCY]`
  completo no referencia ningún nombre de fichero (S136 §5, confirmado aquí: las 16
  funciones de `REMOTE` no referencian ninguna cadena fuera de `[REMOTE]`).
* **Número de línea del fuente**: sí se puede medir, porque el primer vararg `%d` de
  cada traza es el número de línea. Las 32 cadenas dan **32 números de línea distintos**
  (113, 147, 170, 188, 192, 196, 210, 228, 249, 257, 284, 352, 367, 434, 442, 457, 673,
  696, 718, 745, 751, 758, 766, 773, 783, 789, 815, 850, 854, 878, 889, 941, 967 —
  el `ZOOM OFF` se emite desde dos sitios, líneas 783 y 789):
  ⇒ **el sub-bloque `[REMOTE]` está implementado en un fichero de ~1000 líneas**.

---

## 6. Estructura de datos

### 6.1 El objeto `AccyUmDeviceRemote`

Layout medido por los accesos directos (`ldrb/ldr/str` con desplazamiento constante):

| offset | tipo | contenido | evidencia |
|---|---|---|---|
| `+0x04` | byte | contador (incremental en `RestoreInfo`) | `strb r3,[r4,#4]` `0x435665ec` |
| `+0x0C` | byte con signo | **Spinal** | `ldrsb.w sb,[r0,#0xc]` `0x43566b5c` |
| `+0x10` | 32 bit | marca de tiempo de la transacción | `ldr r2,[r6,#0x10]` `0x435669c8` |
| `+0x14` | byte | «buffer listo» (0 ⇒ *buffer error*) | `ldrb r1,[r4,#0x14]` `0x435663d6` |
| `+0x18` | 32 bit | contador de reintentos | `ldr r3,[r0,#0x18]` `0x43566d94` |
| `+0x1C` | 32 bit | longitud del comando pendiente | `str r7,[r4,#0x1c]` `0x4356690a` |
| `+0x20` | 6 B | **comando UART pendiente** (ASCII) | `add r0,r4,#0x20` `0x4356690e` |
| `+0x24` | byte | contador de reintentos en ASCII | `strb r0,[r4,#0x24]` `0x43566408` |
| `+0x30` | 32 bit | máximo de reintentos | `str r5,[r4,#0x30]` `0x435668da` |
| `+0x34` | 32 bit | estado del ZOOM | `str r1,[r0,#0x34]` `0x4356655e` |
| `+0x38` | 32 bit | velocidad del ZOOM | `str r2,[r0,#0x38]` `0x43566560` |
| `+0x3C` | byte | flag **GF** (guide frame) | `ldrb.w r8,[r0,#0x3c]` `0x43566b60` |
| `+0x3D` | byte | flag **SS** (start/stop) | `ldrb.w r7,[r0,#0x3d]` `0x43566b64` |
| `+0x3E` | byte | flag **Freeze** | `ldrb.w r6,[r0,#0x3e]` `0x43566b68` |
| `+0x3F` | byte | flag **Photo** | `ldrb.w r5,[r0,#0x3f]` `0x43566b6c` |
| `+0x40` | byte | estado de **Tally** solicitado | `strb.w r3,[r4,#0x40]` `0x43566a90` |
| `+0x41` | byte | estado de **Tally** actual | `ldrb.w r3,[r4,#0x41]` `0x43566e68` |
| `+0x42` | byte | estado de control / «ocupado» | `ldrb.w r3,[r0,#0x42]` `0x43566a6e` |

### 6.2 El «blob» de estado de 3 bytes (`SaveInfo` / `RestoreInfo`)

`SaveInfo` (`0x435664d0`, línea 696) **empaqueta** el estado en **3 bytes**:

```
0x4356651a  ldrb.w r3, [r4, #0x3e]   ; Freeze
0x43566522  lsls     r3, r3, #2      ; Freeze<<2
0x43566524  orr.w    r3, r3, r2, lsl #3   ; | Photo<<3
0x43566528  ldrb.w r2, [r4, #0x3c]   ; GF
0x4356652c  orrs     r3, r2           ; | GF        (bit 0)
0x4356652e  ldrb.w r2, [r4, #0x3d]   ; SS
0x43566532  orr.w    r3, r3, r2, lsl #1   ; | SS<<1  (bit 1)
0x43566536  and      r0, r0, #3       ; Zoom & 3
0x4356653a  orr.w    r3, r3, r0, lsl #4   ; | Zoom<<4 (bits 4-5)
0x4356653e  strb     r3, [r5]         ; byte 0 = bitfield
0x43566540  ldrb.w r3, [r4, #0x40]   ; Tally
0x43566546  strb     r3, [r5, #1]     ; byte 1 = Tally
0x4356654a  strb     r3, [r5, #2]     ; byte 2 = 0 (reservado)
```

`RestoreInfo` (`0x43566580`, línea 718) lo desempaqueta con `ubfx` sobre los mismos bits
(`0x435665aa`–`0x435665d4`) y llama a `SetZoom` con `(byte0 >> 4) & 3`.

**⇒ la estructura que el módulo «gestiona» es un estado de 6 conmutadores
(GF, SS, Freeze, Photo, Zoom, Tally) serializado en 3 bytes**, más una tabla de
**5 códigos de tecla** y **3 tablas `tbb`** de despacho.

### 6.3 La tabla de códigos de tecla

Es **idéntica** en los tres firmware (pool literal contiguo de 5 dwords):

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| GUIDE FRAME | `0x0A000009` @ `0x435667f0` | `0x0A000009` @ `0x43564874` | `0x0A000009` @ `0x4355f040` |
| START STOP | `0x0A00000D` @ `0x435667f4` | `0x0A00000D` @ `0x43564878` | `0x0A00000D` @ `0x4355f044` |
| PHOTO FREEZE | `0x0A000008` @ `0x435667f8` | `0x0A000008` @ `0x4356487c` | `0x0A000008` @ `0x4355f048` |
| PHOTO REC | `0x0A00000C` @ `0x435667fc` | `0x0A00000C` @ `0x43564880` | `0x0A00000C` @ `0x4355f04c` |
| ZOOM | `0x0A000011` @ `0x43566800` | `0x0A000011` @ `0x43564884` | `0x0A000011` @ `0x4355f050` |

### 6.4 Tablas de despacho (`tbb`)

| tabla | dirección | entradas | destino |
|---|---|---|---|
| categoría → carácter | `0x435662f4` (base `0x435662f8`) | 6 | `[0..3]→0x435662fe`, `[4]→0x4356630e`, `[5]→0x4356631e` |
| comando → grupo de botón | `0x43566638` (base `0x4356663c`) | 4 | `'0'→0x43566640` GF, `'1'→0x4356666e` SS, `'2'→0x4356669c` Freeze, `'3'→0x435666d4` Photo |
| estado de tally → carácter | `0x43566960` (base `0x43566964`) | 4 | `[0]→0x43566976` (`'0'`), `[1]→0x43566968` (`'1'`), `[2]→0x4356696c` (`'2'`), `[3]→0x43566970` (`'3'`) |

---

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 7.1 Tokens y trazas

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| ocurrencias del token `[REMOTE]` | **32** | **0** | **0** |
| ocurrencias del token `[ACCY]` | **106** | **0** | **0** |
| «núcleo» sin prefijo como literal autónomo | 0/32 | **0/32** | **0/32** |
| traza equivalente con otra etiqueta | — | **ninguna** (no hay trazas `[ACCY]` en absoluto) | **ninguna** |

### 7.2 El **código** sí está en los otros dos firmware

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| clase RTTI `AccyUmDeviceRemote` | `0x43c26340` | `0x43c25aed` | `0x43d0ca6c` |
| `type_info` | `0x43fd7dbc` | `0x43fd9b24` | `0x4419941c` |
| vtable (8 entradas) | `0x43fb9114` | `0x43fb2e14` | `0x4416fd74` |
| `NotifyUartCommand` (vtable[5]) | `0x43566290` | `0x4356451c` | `0x4355ec30` |
| tabla de 5 códigos de tecla | `0x435667f0` | `0x43564874` | `0x4355f040` |

**Prueba estructural (no textual)**: el método `NotifyUartCommand` de los tres firmware
tiene **la misma secuencia de instrucciones**, sólo que sin las trazas:

```
A6000  0x435662e4  cmp r1, #0x23        A7S  0x43564534  cmp r1, #0x23
A6000  0x435662e8  cmp r0, #0x37        A7S  0x43564538  cmp r0, #0x37
A6000  0x435662ec  sub.w r1, r2, #0x30  A7S  0x4356453c  sub.w r1, r2, #0x30
A6000  0x435662f0  cmp r1, #5           A7S  0x43564540  cmp r1, #5
A6000  0x435662f4  tbb [pc, r1]         A7S  0x43564544  tbb [pc, r1]
```

El A6300 es igual con **una categoría extra** (`cmp r0,#0x46` = `'F'`, `0x4355ec50`).

### 7.3 Lectura del diferencial

**Lo propio de la A6000 fw3.21 es el LOGGING, no el módulo.** El mando remoto por UART
existe en los tres firmware (misma clase RTTI, misma vtable de 8 métodos, mismo
protocolo ASCII, misma tabla de 5 códigos de tecla); lo que la fw3.21 de la A6000 añade
es **todo el set de trazas `[ACCY]`** (106 cadenas, 15 sub-bloques, un logger propio por
sub-bloque) y en particular las **32 trazas `[REMOTE]`**.

Esto **difiere del patrón de S177/S179**: allí la fw3.21 *antepone* un prefijo a un
literal que ya existía y deja el original vivo (gemelo en `+len(prefijo)`) y emite
**dos** trazas (nueva con logger de módulo + vieja con el logger global). Aquí:

* no hay gemelo (0/32);
* no hay doble emisión (el logger global `0x43902718` **no** aparece en ninguna de las
  16 funciones de `REMOTE`);
* el prefijo no es una anteposición neutra: es **`[ACCY][NIVEL][REMOTE]:`**, con el
  **nivel dentro** (23/24/25 B según `ERR`/`INFO`/`WARN`/`DEBUG`).

⇒ **ETIQUETADO/LOGGING en sentido amplio, pero NO el patrón «prefijo + gemelo» de
S177/S179**. Es el mismo cuadro que S136 §7.2 yaangered para `[ACCY]` entero, refinado
aquí al sub-bloque `REMOTE`.

**Salvedad** (misma que S130 §4 y S136 §7.2): la comparación mezcla **versión y
modelo**; no hay una fw anterior de la A6000 en el repositorio, así que no se puede
separar «nuevo en la fw3.21» de «propio de este modelo».

---

## 8. Verificación y método

* **Regla de referencias**: estricta (canónica del repo). El escaneo **local** de este
  hito (`analysis/s180_remote/scan_pic_local.py`, misma regla, sobre la región de
  código `0x43562000`–`0x43567400`) reproduce **exactamente** el mapa global
  `analysis/s106_imaging_cap/pic_refs_strict_global.json`: **137 destinos, 0
  discrepancias**. No se re-barrió la imagen con otro criterio.
* **Verificación a mano de los pares PIC** (`scan_pic_local.py`, Capstone Thumb con
  `detail=True`): **33 / 33 correctos** (0 fallos, **0 reutilizaciones de registro**
  entre el `ldr` y el `add`). En cada par se comprobó: (a) el `ldr rX,[pc,#imm]` **más
  cercano** del mismo registro, (b) el literal del pool, (c) `destino = literal + (add + 4)`,
  (d) que el registro no se reescribe entre `ldr` y `add`.
  Ejemplo (sitio `0x435662b2`): `ldr r3,[pc,#0xf8]` @`0x435662ac` → pool `0x435663a8` =
  `0x006bf891`; `add r3,pc` @`0x435662b2` → `0x006bf891 + 0x435662b6 = 0x43c25b47` =
  `'[ACCY][INFO][REMOTE]:%d:NotifyUartCommand...UART CMD:%C%C%C%C%C%C …'` ✓.
* **Números de línea**: medidos con `scan_lines.py` (localiza la escritura en `[sp]`
  más cercana a la llamada al logger y resuelve el inmediato del registro origen);
  **32 / 33** automáticos y **1 verificado a mano** (`0x43c25f3d`, línea 192:
  `movs r2,#0xc0` @`0x43566ad6` / `str r2,[sp]` @`0x43566ad8`; el barrido automático
  tomaba la escritura compartida por dos ramas que acaban en el mismo `bl`).
* **Firma del logger**: `scan_levels2.py` comprueba en los **111** sitios `[ACCY]` que
  `r0 = 93` (id de módulo) y que `r2` coincide con el nivel del prefijo — **0
  discrepancias**. Para `REMOTE`: **33/33**.
* **Gemelos y punteros absolutos**: `scan_verify.py`.
* **RTTI y vtables**: `scan_rtti.py`, `scan_vtables.py`.
* **Tests**: `tests/test_s180_remote.py` (comprueban bytes reales: si cambia una
  dirección, un texto o un contador, el test falla).

---

## 9. Interés para la línea del obturador

**Negativo acotado: el módulo `[REMOTE]` NO habla de obturación, de obturador
electrónico, de lectura del sensor de imagen, de exposición ni de parámetros del
obturador.**

Comprobación literal sobre las 32 trazas (`scan_verify.py`):

| término | coincidencias | traza |
|---|---|---|
| `shutter`, `silent`, `curtain`, `electro`, `mech`, `obtur` | **0** | — |
| `sensor`, `readout`, `imager`, `iso`, `apert` | **0** | — |
| `expos`, `expo`, `brack`, `drive`, `release`, `flash` | **0** | — |
| `sync`, `vsync`, `capture`, `shot`, `sweep`, `interval`, `still`, `movie`, `focus` | **0** | — |
| `shut`, `svd`, `shd`, `spl`, `ae `, `af `, `burst`, `wb` | **0** | — |
| `frame` | **1** | `GUIDE FRAME OFF` (`0x43c26068`) — *guía de encuadre* |
| `rec ` | **1** | `PHOTO REC OFF` (`0x43c26140`) — *grabación* |
| `speed` | **1** | `Zoom State Change To %d Speed:%d` (`0x43c25cdb`) — *velocidad del zoom* |
| `time` | **3** | `NotifyUartTimedOut`, `TimeoutNotify`, `EventTimeout Tally Light TIMEOUT` — *timeout del UART* |

Matices que sí conviene registrar (son de **nivel de accesorio**, no de mecanismo):

* `START STOP` (`0x43c260b0`, tecla `0x0A00000D`) es la **pulsación de disparador del
  mando**, pero el módulo **no ejecuta el disparo**: traduce la pulsación a un
  **evento de tecla genérico** (`KEY:0x0A00000D`, `STATE`, `INFO`) y lo entrega por
  `NotifyInput` (`0x43565814`) a la cola OSAL. **Quién decide qué hace esa tecla
  (y por tanto si dispara con el obturador electrónico) está FUERA de este módulo** →
  **NO VERIFICADO**.
* `PHOTO REC` y `PHOTO FREEZE` son interruptores de **grabación** y **congelación**;
  `GF` es la **guía de encuadre**; `Tally` es la **luz de tally** del accesorio.
* El módulo **no escribe ni lee ningún estado del obturador**: sus 33 referencias a
  cadenas son **todas** `[REMOTE]` (0 referencias a cadenas del subsistema de obturación).

⇒ **Para la línea del obturador: S51 (A = NO / B = NO / C = NO) se mantiene.** El valor
de este hito para la línea es *indirecto*: documenta que el **disparador remoto de la
A6000 entra por la cola de teclas genéricas** (`0x0A0000xx`), no por un camino
específico del obturador, lo que refuerza que **el API de entrada de la cámara no es un
camino alternativo al obturador electrónico**.

---

## 10. NO VERIFICADO / abierto

1. **Nombre del fichero fuente** del sub-bloque `[REMOTE]` — NO VERIFICADO (el bloque
   `[ACCY]` no referencia ningún nombre de fichero). Sí se ha medido el **rango de
   líneas** (113–967 ⇒ un fichero de ~1000 líneas).
2. **Significado de la sigla `ACCY` y de `UM`** — NO VERIFICADO (sin base textual).
3. **Significado de `Spinal`** — NO VERIFICADO (literal sin explicar; la misma palabra
   aparece en `Spinal.cpp` dentro de `[CAMERA_MAIN]`, relación no establecida).
4. **Significado de `GF`, `SS`, `Tally`, `JIRO`, `AVR`, `LANC`, `AISATSU`** — literales
   del firmware, sin explicación en los bytes.
5. **Tabla de nombres de tecla `0x0A0000xx` → acción de cámara** — no localizada.
   En particular, **qué hace exactamente la tecla `0x0A00000D` (START STOP)** — NO
   VERIFICADO (y es lo único que roza la línea del obturador).
6. **Cola OSAL de destino** del mensaje `NotifyInput` (`0x007A0020`) y su consumidor —
   NO VERIFICADO.
7. **Código `0x0A00000A`** (pool `0x43566d24`) — su uso NO VERIFICADO.
8. **Por qué** la fw3.21 de la A6000 trae 106 trazas `[ACCY]` y los otros dos firmware
   ninguna (y por qué la A7S/A6300 tienen además las clases `AccyMiDeviceBase` /
   `AccyMiDeviceLight`) — NO VERIFICADO.
9. **Categoría UART `'F'`** (0x46) que sólo existe en la A6300 (`0x4355ec50`) — su
   significado NO VERIFICADO.

---

## 11. Revisión del agente principal

*(vacía — pendiente de revisión)*

---

## 12. Reproducir

```bash
.venv/bin/python analysis/s180_remote/scan_strings.py        # 32 cadenas + diferencial de token
.venv/bin/python analysis/s180_remote/scan_accy_tags.py      # sub-etiquetas [ACCY][*]
.venv/bin/python analysis/s180_remote/scan_pic_sites.py      # sitios PIC (mapa global) + gemelos
.venv/bin/python analysis/s180_remote/scan_pic_local.py      # escaneo local estricto + verificación a mano
.venv/bin/python analysis/s180_remote/scan_funcmap.py       # mapa función -> traza
.venv/bin/python analysis/s180_remote/scan_logger.py         # firma del logger
.venv/bin/python analysis/s180_remote/scan_levels2.py        # id de módulo y nivel de las 111 trazas [ACCY]
.venv/bin/python analysis/s180_remote/scan_lines.py          # números de línea del fuente
.venv/bin/python analysis/s180_remote/scan_rtti.py           # type_info de las clases AccyUm*
.venv/bin/python analysis/s180_remote/scan_vtables.py        # vtables
.venv/bin/python analysis/s180_remote/scan_keycodes.py       # tabla de códigos de tecla en los 3 firmware
.venv/bin/python analysis/s180_remote/scan_tbb.py            # tablas tbb
.venv/bin/python analysis/s180_remote/scan_verify.py         # negativo + punteros absolutos + gemelos
.venv/bin/python analysis/s180_remote/build_json.py          # genera remote.json
.venv/bin/python -m pytest tests/test_s180_remote.py -q
```

Ficheros de datos: `strings_raw.json`, `pic_sites.json`, `pic_local.json`,
`pic_verified.json`, `func_map.json`, `log_calls.json`, `levels_accy.json`,
`logger_targets.json`, `verify.json`, `vtables.json`, `keycodes.json`, `marks.json`,
`calls.json`, `remote.json`.

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (50 tests del hito + comprobaciones a mano):**

1. **Recuento y diferencial**: 32 cadenas con el token `[REMOTE]` en la A6000 fw3.21 (rango
   `0x43c25b47`–`0x43c26319`); token **32 / 0 / 0** (A6000/A7S/A6300).
2. **Estructura (reproducida por mí con la regla estricta)**: **33 sitios** PIC en **16
   funciones**, **0 cadenas muertas**; los **33/33 pares** verificados a mano por el subagente
   (0 fallos, 0 reuso de registro) y su escaneo local reproduce el mapa canónico con **0
   discrepancias**. El mapa global contiene **32** destinos con `[REMOTE]` (una cadena
   —`[ACCY][INFO][REMOTE]:%d:ZOOM OFF  KEY:%08X…` `0x43c26186`— se referencia **dos** veces:
   `0x43566c8e` y `0x43566cb0`) → 33 sitios sobre 32 cadenas ✓.
3. **Precisión estructural que el informe deja implícita y conviene fijar (verificada)**: las
   32 cadenas **no son cadenas propias**, son **subcadenas** de cadenas más largas con el formato
   **`[ACCY][<NIVEL>][REMOTE]:%d:<mensaje>`**, y **la referencia PIC apunta al INICIO de la
   cadena completa** (p. ej. `0x43c25b47` = `[ACCY][INFO][REMOTE]:%d:NotifyUartCommand…`), no a
   la posición de `[REMOTE]`. Repartición de niveles por el prefijo: **INFO 24, ERR 3, DEBUG 3,
   WARN 2** → el **nivel va en la propia cadena**, y el logger `0x435661e4` recibe
   `(id_módulo=93, ?, nivel, fmt, …)`. Por eso el mapa global no lista las cadenas que empiezan
   por `[REMOTE]` (empiezan por `[ACCY][…]`): no es una contradicción, es la misma regla.
4. **Base textual (no inventada)**: la clase RTTI **`AccyUmDeviceRemote`** (`0x43c26340`,
   `type_info` `0x43fd7dbc`, vtable `0x43fb9114` con los 8 métodos virtuales del accesorio)
   → **`REMOTE` sí tiene base textual**; `ACCY`/`UM` se dejan sin desarrollar. Es **el mismo
   código** que el sub-bloque `REMOTE` de `[ACCY]` delimitado en S136 (mismo rango, mismos 33
   sitios, mismas 16 funciones) → **no es un módulo nuevo, es larizzly del sub-bloque**.
5. **Cambio de logging, no de código (diferencial verificado)**: **no** hay gemelo «prefijo +
   original» (a diferencia de S177 y S179): el núcleo autónomo `[REMOTE]` está **0/32** en la A7S
   y el A6300 (las 6 coincidencias en la A6000 son literales de otros sub-bloques `[ACCY]`:
   `[HELLO]` y `[HOUSING]`) y **no hay doble emisión** (el logger global `0x43902718` no
   aparece en ninguna de las 16 funciones). Pero **el código del mando sí existe en los tres**:
   misma clase RTTI (`0x43c25aed` / `0x43d0ca6c`), misma vtable de 8 métodos (`0x43fb2e14` /
   `0x4416fd74`), misma tabla de 5 códigos de tecla (`0x43564874` / `0x4355f040`) y
   `NotifyUartCommand` con la **misma secuencia de instrucciones**
   (`cmp #0x23` / `cmp #0x37` / `sub #0x30` / `cmp #5` / `tbb`).
6. **Estructura de datos (verificada)**: objeto con flags `+0x3C` GF, `+0x3D` SS, `+0x3E`
   Freeze, `+0x3F` Photo, `+0x40/+41/+42` Tally, `+0x34/+0x38` Zoom, `+0x0C` Spinal; estado
   serializado en **3 bytes** (`SaveInfo` `0x435664d0` / `RestoreInfo` `0x43566580`); tabla de
   **5 códigos de tecla** (`0x0A000009`/`0D`/`08`/`0C`/`11`) y **3 tablas `tbb`**
   (`0x435662f4`, `0x43566638`, `0x43566960`).
7. **Negativo acotado**: 0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/
   `sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/
   `vsync`/`capture`/`shot`/`still`/`movie`/`focus`. Lo único es `GUIDE FRAME` (guía), `PHOTO REC`
   (grabación), `Zoom…Speed` y timeouts de UART; el «START STOP» (`0x0A00000D`) es una **tecla
   genérica** entregada por `NotifyInput` `0x43565814` → el módulo **no ejecuta el disparo** →
   **sin efecto en S51** (A/B/C = NO).
