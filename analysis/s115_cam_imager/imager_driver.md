# S115 — `[CAM_IMAGER]`: el driver del imager en la cámara

> Hito de la **línea de ingeniería inversa general**. Conecta con la línea del obturador
> electrónico (S56–S58) en el punto exacto del transporte P2S/DFE y de la máquina de
> lectura/exposición por `drive_mode`. Verificación contra los bytes del
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Sin efecto en S51 (A/B/C = NO).

## 1. Qué es

`[CAM_IMAGER]` es el **driver del imager** (el sensor) dentro de la cámara: el código que
programa el sensor, registra los manejadores de interrupción, implementa el transporte P2S
hacia el DFE y ejecuta la **máquina de lectura/exposición** que depende del `drive_mode`.

- **371 trazas** con el prefijo `[CAM_IMAGER]:`.
- 78 de ellas son del módulo **ZIT** (corrección de defectos del sensor), ya documentado en
  S80 → este hito cubre las **292** restantes (el driver).
- **94 funciones** del módulo, entre `0x43543568` y `0x436dbd66` (el grueso en
  `0x436d5xxx`–`0x436dbxxx`).

## 2. Las cinco familias del driver

### 2.1 P2S: el transporte hacia el imager/DFE

| traza | vaddr |
|---|---|
| `SetIntDisable: Unknown P2S Channel !!` | `0x43c92f71` |
| `P2S Callback Error!!: Double registration` | `0x43c92fa5` |
| `P2S(DFE0) Callback Error!!: Double registration` | `0x43c92fdd` |
| `P2S(DFE1) Callback Error!!: Double registration` | `0x43c9301b` |
| `Imager int_p2s_handler_dfe0 Error!!` / `…dfe1…` | `0x43c93085` / `0x43c930b7` |
| `Imager int_timer_handler Error!! [OSAL ERR:%02x]` | `0x43c930e9` |
| `P2S : Unsupported SyncMode.` | `0x43c93156` |
| `P2SWaitTransComp: wai_flag error %d` | `0x43c93180` |
| `P2STransferSize[%02x]` | `0x43c931b2` |
| `P2SData[Page:%01x] %02x %02x …` | `0x43c931d6` |
| `P2S Error:Last trans is not end. %d %d` | `0x43c93247` |
| `P2S CheckAddrOrder: ORDER ERROR !` | `0x43c9327c` |
| `P2S : P2SFormatter Error.` | `0x43c932ac` |

→ El P2S es un transporte **por páginas** (`Page:%01x`) con dos canales (**DFE0**, **DFE1**),
comprobación de **orden de direcciones**, un **formateador** de datos y sincronización por
espera (`WaitTransComp`). Es exactamente el camino que S56 ("transporte de registros del IMX210
(P2S/DFE0), CISIF = receptor") siguió en la línea del obturador: aquí se ve su instrumentación
en el lado de la cámara.

### 2.2 Interrupciones

`int_p2s_handler` (con variantes `_dfe0`/`_dfe1`), `int_timer_handler` y
`Imager TimerSetFunc/TimerStart Error!! [CH:%02x, err:%02x]` (`0x436d8b16`, `0x436d8bda`): el
imager tiene un temporizador propio por canal (`CH`).

### 2.3 SIF: la interfaz de sincronización

11 trazas: `SIF SetSyncCode : Serial Synccode Not Selected` (`0x43c94e55`) y
`Parallel Synccode Not Selected` (`0x43c94e92`), `SetSIFSigsel`, `SetSIFMode`, `SetDitherSet`,
`SetDataEnableParam`, `ReadSIFScodeCnt`, `SIF SyncCodeDetNum. [SyncCodeDetNum:%04x]`
(`0x43c93a33`) y `SIF AD_MODE Setting Error!! [ad_mode:%02x]`.

→ el **sync code** del sensor se puede seleccionar **en serie o en paralelo**, y hay un
`AD_MODE` (AD = auto-detect?) con su propio modo. Es el `SIFSyncCode` que S96 ya vio en el
motor de imagen (`GetPrelightImagerDriveMode`).

### 2.4 `ImagerCommon`: la API "macro" hacia el CISIF

16 trazas, todas con la forma `ImagerCommon::<M> Unknown index number` / `do not use CH_1`:
`Update_IIFINSEL` (`0x43c94486`), `SetCISIFRequest` (`0x43c9450d`),
`GetCISIFSyncCodeRequest` (`0x43c9458a`), `MacroPowerOnRequest` (`0x43c94617`),
`MacroPowerSaveOnRequest` (`0x43c9469c`), `MacroPowerOffRequest` (`0x43c94729`),
`Update_CISIFConnectParam` (`0x43c947b0`), `Update_MacroRxEnable` (`0x43c9483f`).

→ el imager expone una **API de un solo canal (`CH_1`)** hacia el **CISIF**, que es el
receptor de los mensajes de control del sensor identificado en S56.

### 2.5 `SubLVDS`: el serializador LVDS

9 trazas: `SubLVDS PowerOn/PowerSaveOn/PowerSaveOff/ChangeParam/GetReceiverEnable`, cada una
con el aviso `SUBLCNTL_DFE1 does not exist on Regulus` (`0x43c953e7`…) y
`unknown subl_block_sel` → **dos bloques** (DFE0/DFE1) y un hardware distinto (*Regulus*).

## 3. La máquina de lectura/exposición por `drive_mode` (lo más relevante para el obturador)

Este es el núcleo del driver y donde se ve la parametrización de cada modo de lectura:

| traza | vaddr | campos |
|---|---|---|
| `SetExps : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [svd:%02x] [shd:%02x] [spl:%02x] [shut:%01x]` | `0x43c93cc2` | **svd, shd, spl, shut** |
| `SetExpsZ: […][svrz:%02x] [shrz:%02x] [splz:%02x] [epd:%02d] [epdsel:%02d]` | `0x43c939b5` | variantes "Z" + epd/epdsel |
| `SetRead : […][AGainCont_EC:%02x] [AGainCont:%02x] [AGainDrv:%02x]` | `0x43c93fcb` | ganancias analógicas |
| `SetReadZ: […][AGainContZ:%02x] [AGainDrvZ:%02x]` | `0x43c93d67` | variantes "Z" |
| `Execute : […][SSBRK_ON:%01x] [SLEEP_ON:%01x]` | `0x43c94076` | **SSBRK** y SLEEP |
| `Execute. […][SSBRK_ON:%01x] [SIFSyncCode:%02x]` | `0x43c940d7` | SSBRK + sync code |
| `Execute0: pre%02d now%02d next%02d ssb%01x read%dz%d svr%02dz%02d` | `0x43c93ae2` | ssb, read, svr |
| `Execute1: …` | `0x43c9413a` | ídem, segundo camino |
| `SetMode : […][ntpal:%01x]` | `0x43c93b2f` | NTPAL |
| `Invalid SetExposure Error!! [drive_mode:%2d]` / `SetRead` / `Execute` | `0x43c9397a`, `0x43c93d30`, `0x43c93a6c` | modo no válido |
| `GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]` | `0x43c94a9f` | transición de modo |
| `GetParam:NTPAL boot=%d now=%d` | `0x43c94b3c` | |
| `numReadMode > READMODE_NUM_MAX.` | `0x43cf7743` | número de modos de lectura |

**Lo que esto aporta a la línea del obturador electrónico:**

1. La exposición se programa **por `drive_mode`** con un bloque de parámetros que incluye un
   campo **`shut`** (`0x43c93cc2`) y sus variantes "Z" (`svrz`, `shrz`, `splz`) — el candidato
   más directo a un parámetro de obturador en el lado de la cámara. **NO VERIFICADO**: no se
   ha decodificado qué significa `shut` ni si el A6000 escribe un valor distinto del de la A7S.
2. La ejecución de la lectura lleva **`SSBRK_ON`** y `SIFSyncCode` — el **SSB** es el registro
   que S56–S58 Analizaron en la línea del obturador (ID1/SSB).
3. `SetSyncCode` distingue **sync code en serie vs en paralelo**: es el punto donde un
   obturador mecánico/electrónico tendría que decidirse.

## 4. Mapa función → traza

94 funciones con la regla "ancha"; con la **regla canónica estricta** son **76 funciones** y
**357 de las 371 cadenas** referenciadas (417 sitios). Las que más trazas emiten:

| función | n | primera traza |
|---|---|---|
| `0x436d77d0` | 11 | `PowerOff` |
| `0x436d6ca0` | 9 | `PowerOn` |
| `0x436d594e` | 6 | `P2S Callback Error!!: Double registration` |
| `0x436d839c` | 6 | `Invalid Execute Error!! [drive_mode:%2d]` |
| `0x435440a0` | 5 | `SIF SetSyncCode : Serial Synccode Not Selected` |
| `0x436d67ec` | 5 | `Invalid SetExposure Error!! [drive_mode:%2d]` |
| `0x436d8b16` | 5 | `Imager TimerSetFunc Error!! [CH:%02x, err:%02x]` |
| `0x436d8c96` | 4 | `ImagerCommon::SetCISIFRequest Unknown index number` |

## 5. Diferencial con la A7S fw3.20

| elemento | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| prefijo `[CAM_IMAGER]` | 371 trazas | **0** |
| `SetExps`, `Execute0`, `AGainCont` | presentes | **0** |
| `SetRead` / `SSBRK` / `SubLVDS` / `ImagerCommon` / `SIFSyncCode` / `P2S` / `NTPAL` | presentes | presentes (6/2/9/10/3/9/4 apariciones) |
| mensajes equivalentes (texto normalizado) | 189 de 371 | — |

→ el **mismo driver** (mismo vocabulario: P2S, SubLVDS, ImagerCommon, SIF, NTPAL, SSBRK) está
en la A7S, pero **sin la etiqueta de módulo** y con **mucha menos instrumentación**: la fw3.21
de la A6000 añade la etiqueta `[CAM_IMAGER]:` y, sobre todo, las trazas por `drive_mode`
(`SetExps`/`SetExpsZ`/`SetReadZ`/`Execute0`/`Execute1`) que **no existen** en la A7S.

## 6. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 371 trazas `[CAM_IMAGER]` | `extract_imager.py` cuenta el prefijo en los bytes |
| 292 del driver + 78 de ZIT | separación por el prefijo del texto |
| 94 funciones | mapa PIC + prólogos Thumb |
| P2S con 2 canales y páginas | lectura de las trazas `P2S(DFE0/DFE1)`, `P2SData[Page:%01x]` |
| `ImagerCommon` = API de 1 canal | las 16 trazas repiten `do not use CH_1` |
| A7S sin el prefijo y sin `SetExps`/`Execute0`/`AGainCont` | conteo directo sobre el blob de la A7S |

## 7. NO VERIFICADO / abierto

- El **significado** de los campos `svd`, `shd`, `spl`, **`shut`**, `epd`, `epdsel`, `ssb`,
  `read`, `svr`, `ntpal` y de las variantes "Z" (`svrz`, `shrz`, `splz`, `AGainContZ`,
  `AGainDrvZ`): son **hipótesis** las más plausibles (sv=?, sh=shutter?, spl=?) y el firmware
  no los expande.
- Si `shut` cambia de valor entre A6000 y A7S para el mismo `drive_mode` (punto directo para
  la pregunta del obturador): **no comprobado** (requiere la tabla de parámetros por modo, que
  no está en las trazas).
- La tabla de parámetros por `drive_mode` (69 modos según S96) y su relación con
  `read%dz%d` (z = zona de lectura).
- Los nombres internos de la A7S: el módulo equivalente existe pero sin etiqueta; no se ha
  identificado su prefijo.
- Nada de esto **modifica** S51 (A/B/C = NO): no aparece ningún mensaje de obturador
  electrónico.

## 8. Ficheros de este hito

| fichero | contenido |
|---|---|
| `strings_raw.json` | las 371 cadenas con vaddr/offset/texto |
| `func_map.json` | mapa función → traza (94 funciones) |
| `summary.json` | sub-bloques, vocabulario P2S, manejadores de IRQ y diferencial A7S |
| `extract_imager.py` | script de extracción (reproducible) |
