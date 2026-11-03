# S115 — `[CAM_IMAGER]`: el driver del imager en la cámara

**Hito de la línea de ingeniería inversa general**. Conecta con la línea del obturador
electrónico (S56–S58) en el punto del transporte P2S/DFE y de la máquina de lectura por
`drive_mode`. Sin efecto en S51 (A/B/C = NO).

Informe: [analysis/s115_cam_imager/imager_driver.md](../../analysis/s115_cam_imager/imager_driver.md) ·
Datos: `summary.json`, `func_map.json` · Test: `tests/test_s115_cam_imager.py`.

## Hallazgo central

`[CAM_IMAGER]` es el **driver del imager** (el sensor) dentro de la cámara: **371 trazas**
(78 de ellas del módulo ZIT de defectos, ya documentado en S80 → este hito cubre las **292**
del driver) repartidas en **94 funciones** (`0x43543568`–`0x436dbd66`).

## Las cinco familias

1. **P2S** (transporte al imager/DFE): dos canales (**DFE0**, **DFE1**), datos **por páginas**
   (`P2SData[Page:%01x]`), `P2STransferSize`, `P2SFormatter`, `P2S CheckAddrOrder`,
   `P2SWaitTransComp` y `P2S : Unsupported SyncMode.` → es el camino que S56 ("transporte de
   registros del IMX210, P2S/DFE0") siguió en la línea del obturador.
2. **Interrupciones**: `int_p2s_handler` (con variantes `_dfe0`/`_dfe1`), `int_timer_handler` y
   el temporizador por canal (`Imager TimerSetFunc/TimerStart Error!! [CH:%02x, err:%02x]`).
3. **SIF** (interfaz de sincronización): `SetSyncCode` distingue **sync code en serie o en
   paralelo** (`0x43c94e55`/`0x43c94e92`), más `SetSIFMode`, `SetSIFSigsel`, `SetDitherSet`,
   `SetDataEnableParam`, `ReadSIFScodeCnt`, `SyncCodeDetNum` y `SIF AD_MODE`.
4. **`ImagerCommon`** (16 trazas): la API "macro" hacia el **CISIF** —
   `Update_IIFINSEL`, `SetCISIFRequest`, `GetCISIFSyncCodeRequest`, `MacroPowerOn/SaveOn/OffRequest`,
   `Update_CISIFConnectParam`, `Update_MacroRxEnable` — todas con `do not use CH_1`
   (**un solo canal**).
5. **`SubLVDS`** (9): `PowerOn`/`PowerSaveOn`/`PowerSaveOff`/`ChangeParam`/`GetReceiverEnable`
   por bloque (DFE0/DFE1) con el aviso `SUBLCNTL_DFE1 does not exist on Regulus`.

## Lo más relevante para la línea del obturador

La máquina de lectura/exposición se programa **por `drive_mode`** y sus trazas llevan los
parámetros:

| traza | vaddr | campos |
|---|---|---|
| `SetExps : [PrevDrv][NowDrv][NextDrv][svd][shd][spl][shut]` | `0x43c93cc2` | **shut** |
| `SetExpsZ: […][svrz][shrz][splz][epd][epdsel]` | `0x43c939b5` | variantes "Z" |
| `SetRead : […][AGainCont_EC][AGainCont][AGainDrv]` | `0x43c93fcb` | ganancias |
| `SetReadZ: […][AGainContZ][AGainDrvZ]` | `0x43c93d67` | variantes "Z" |
| `Execute : […][SSBRK_ON][SLEEP_ON]` | `0x43c94076` | **SSBRK** |
| `Execute. […][SSBRK_ON][SIFSyncCode]` | `0x43c940d7` | SSBRK + sync code |
| `Execute0/1: pre%02d now%02d next%02d ssb%01x read%dz%d svr%02dz%02d` | `0x43c93ae2`, `0x43c9413a` | ssb, read, svr |
| `SetMode : […][ntpal:%01x]` | `0x43c93b2f` | NTPAL |

1. El campo **`shut`** de la exposición es el candidato más directo a un parámetro de
   obturador en el lado de la cámara (hipótesis de lectura; no se afirma su significado: ver el cierre CAM-01 al final).
2. **`SSBRK_ON`** conecta con el registro SSB que S56–S58 analizaron.
3. `SetSyncCode` **serie vs paralelo** es donde un obturador tendría que decidirse.

## Diferencial A7S fw3.20

0 trazas con el prefijo `[CAM_IMAGER]` en la A7S, pero **el mismo driver** (P2S, SubLVDS,
ImagerCommon, SIF, NTPAL, SSBRK) está presente **sin etiqueta** y con mucha menos
instrumentación: `SetExps`, `Execute0` y `AGainCont` **no existen** en la A7S (0 apariciones).
189 de las 371 cadenas tienen equivalente texto a texto (el resto son del ZIT y de las trazas
nuevas de fw3.21).

## Cierre CAM-01 (03-11-2026, medido en bytes)

- Ficheros fuente: 167 funciones con traza; 0 citan un fichero fuente (ninguno); 167 ninguno.
- Token `[CAM_IMAGER]`: 371 en A6000 fw3.21, 0 en A7S fw3.20 y 0 en A6300 fw2.01 (sin contraparte por token; no se afirma equivalencia). `SetExps` (2 / 0 / 0), `AGainCont` (3 / 0 / 0) y `Execute0` (1 / 0 / 1) en A6000 / A7S / A6300.
- `svd`, `shd`, `spl`, `shut`, `epd`, `epdsel`, `ssb`, `read`, `svr`, `ntpal`: solo aparecen como campos de trazas; el firmware no los expande.
- Nada de esto modifica S51: no hay ningún mensaje de obturador electrónico.

Método: `analysis/camera_closure/sources.py` y `closure.py` (cadenas `.cpp/.h/.c` desnudas cargadas con la regla PIC estricta dentro de cada función; recuentos de token por modelo con búsqueda exacta de bytes). Siglas, significados de campos y nombres de fichero que el firmware no declara **no son afirmaciones de este informe**: no se atribuye ni se infiere ninguno.
