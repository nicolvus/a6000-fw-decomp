# S109 — El módulo `[CDIAG]`: el banco de diagnóstico del códec de la cámara

> Milestone **S109** de la línea de ingeniería inversa **general** del firmware (no es la
> línea SilentShutter / obturador electrónico). Todos los datos son **verificables contra
> los bytes** del `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21).
> Convención de direcciones: **vaddr = 0x43541000 + file_offset** (verificada en hitos
> anteriores). Scripts reproducibles en este mismo directorio.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `analysis/s109_cdiag/cdiag.json` (datos estructurados),
`analysis/s109_cdiag/cdiag_diff.json` (diferencial entre modelos),
`analysis/s109_cdiag/cdiag_refs.json` (todas las referencias PIC de la imagen),
`tests/test_s109_cdiag.py`.

---

## 1. Resumen (VERIFICADO)

`[CDIAG]` es el **subsistema de diagnóstico del códec** ("Co**de**c **Diag**") de la cámara:
un banco de pruebas que, por comando remoto, pide al codificador (AVC de alta y de baja
resolución, y JPEG) que **codifique o decodifique unos datos de prueba almacenados en
fichero** y compruebe **byte a byte** que el resultado coincide con el esperado.

Evidencia directa (todas con dirección):

| evidencia | vaddr | texto |
|---|---|---|
| clase del despachador | `0x43c3b67e` | `8CdCtrlIf` |
| fichero fuente del despachador | `0x43c3b1a8` | `cdCtrlIf.cpp` |
| clase del núcleo | `0x43c3c116` | `10CdCtrlCore` |
| fichero fuente del núcleo | `0x43c3b86c` | `cdCtrlCore.cpp` |
| comparación de datos | `0x43c3e89b` | `13CdUtilCmpData` |
| control de memoria | `0x43c3e53c` | `9CdMemCtrl` |
| control de reloj | `0x43c3e547` | `13CdUtilClkCtrl` |
| mensajes de sincronismo | `0x43c3e8ab` | `13CdUtilSysvMsg` |
| identificador del códec | `0x43c6495a` | `cdcId -> [CDCID_HD_CODEC]` |
| identificador del códec SD | `0x43c64975` | `cdcId -> [CDCID_SD_CODEC]` |

- **270 apariciones del token `[CDIAG]`** en el binario, en el rango `0x43c3b0d4`–`0x43c3e86a`
  (esto es lo que cuenta el mapa de módulos de S79 como "270 trazas").
  De ellas, **255 cadenas empiezan por `[CDIAG]`** y **15 llevan el prefijo `[ERR][CDIAG]`**
  (p. ej. `[ERR][CDIAG][CTRLIF]NOT SUPPORTED -- COMMAND ID [0x%08X] [%s]`, `0x43c3b238`).
- **16 clases** embebidas en la zona y **2 ficheros fuente** (`cdCtrlIf.cpp`, `cdCtrlCore.cpp`).
- El código que lo implementa vive en `0x435a127a`–`0x435a50b6`: **118 funciones** distintas
  delimitadas por `push {…,lr}` … `pop {…,pc}`, con **295 sitios de referencia** a las
  cadenas `[CDIAG]`.

## 2. Qué comprueba el módulo

### 2.1 Los 7 escenarios (modos) de diagnóstico

Las trazas de `[CTRLCORE]` nombran **7 modos** de prueba, uno por cada códec:

`HD REC`, `HD DEC`, `SD REC`, `SD DEC`, `JPEG ENC`, `JPEG DEC`, `JPEG ENCDEC`
(AVC de alta resolución y de baja resolución, y JPEG).

### 2.2 Las 8 operaciones sobre cada modo

Cada modo se puede submitir con una de estas operaciones (`[CDIAG][CTRLCORE]Exec <op> <modo>!!`):

| operación | función `CdCtrlCore` (firma embebida) | vaddr firma | vaddr del dispatcher |
|---|---|---|---|
| `DbgDiagAvc` | `CdCtrlCore::DbgDiagAvc(__uint8_t,__uint8_t,__uint8_t,__uint8_t)` | `0x43c3b6df` | `0x435a1c5c` |
| `ConfirmDoneCodec` | — (sin firma propia) | — | `0x435a1d1c` |
| `CmpData` | `CdCtrlCore::CmpData(__uint8_t,__uint8_t,__uint32_t)` | `0x43c3b72a` | `0x435a1de0` |
| `RunCodec` | `CdCtrlCore::RunCodec(__uint8_t,__uint8_t,__uint32_t)` | `0x43c3c123` | `0x435a1f18` |
| `RelMemArea` | `CdCtrlCore::RelMemArea(__uint8_t,__uint8_t,__uint32_t)` | `0x43c3b768` | `0x435a20b0` |
| `SetMemArea` | `CdCtrlCore::SetMemArea(__uint8_t,__uint8_t,__uint32_t)` | `0x43c3b7ec` | `0x435a2200` |
| `SetData` | `CdCtrlCore::SetData(const __uint8_t*, __uint32_t)` | `0x43c3c162` | `0x435a23b4` |
| `SetDiagMode` | — | — | `0x435a2354` |

`DbgDiagAvc` sólo cubre los **4 modos AVC** (HD REC, HD DEC, SD REC, SD DEC) y el modo
`SD DEC` aparece marcado como no soportado:
`[CDIAG][CTRLCORE]Exec DbgDiagAvc SD DEC!!(NotSupport)` (`0x43c3b91d`).
El modo no contemplado produce `[CDIAG][CTRLCORE]No Support EXEC MODE!!` (`0x43c3b953`).

### 2.3 La comparación byte a byte (`[CMPDATA]` / `CdUtilCmpData`)

16 trazas en `0x43c3e557`–`0x43c3e86a`. El comparador tiene **3 pasos**:

- `step.1`: `[CDIAG][CMPDATA][step.1] [0x%08X]byte... s[0x%02X] d[0x%02X]` (`0x43c3e6dc`),
  con aviso de fin de bloque en origen/destino (`0x43c3e64e`, `0x43c3e695`);
- `step.2`: busca un **desplazamiento** (`dadr found` `0x43c3e71a`, `sadr found` `0x43c3e763`,
  fin `step2 OK` `0x43c3e7ac`);
- `step.3`: alinea las direcciones (`sadr>dadr` `0x43c3e7c6`, `sadr<dadr` `0x43c3e837`).

Volcado del dato comparado: `[CDIAG][CMPDATA]src[0x%08X] dst[0x%08X] size[%d]` (`0x43c3e5ea`).

Los resultados por códec se reportan en los controladores:
`JPEG DEC IMG Differ!!` (`0x43c3ce57`), `JPEG ENC ES Differ!!` (`0x43c3d34f`),
`VideoES Differ!!` (`0x43c3d7c1`), `AudioES Differ!!` (`0x43c3d7e9`).

### 2.4 La memoria (`CdMemCtrl`)

Cada controlador de códec reserva y comparte memoria del "gestor de memoria dinámica":
`MEM ALLOC err [0x%08X]`, `MEM ALLOC COUNT NOT 1 [%d]`, `MEM SHARE err [0x%08X]`,
`MEM FREE err [0x%08X]`; y vuelca la ficha de la unidad:
`index[%d] unit[0x%08X] addr[0x%08X] size[%d] fsize[%d] hdl[0x%08X]`
(p. ej. `0x43c3c247` en `CTRLHDDEC`). La traza canónica es
`[CDIAG][CTRLCORE]memIdx[%d] fileId[%02d:%02d] unitHandle[0x%04X] unitType[0x%08X] size[0x%08X]`
(`0x43c3bfee`): la unidad de memoria queda identificada por **fileId** (el fichero de datos
de prueba) y por **unitType**.

### 2.5 El reloj del códec (`CdUtilClkCtrl`)

Cada controlador cambia el reloj del códec antes de arrancar la codificación. La máquina de
estados tiene 7 estados, con traza propia:

`ClkState IDLE->OPEN` → `Wait OPEN` → `OPEN->CHANGING` → `Wait CHANGING` →
`CHANGING->CHANGED` → `CHANGED->CLOSE` → `CLOSE->IDLE`

(p. ej. las de `CTRLHDDEC`: `0x43c3c463`, `0x43c3c489`, `0x43c3c4ae`, `0x43c3c4d8`,
`0x43c3c501`, `0x43c3c52e`, `0x43c3c558`). Además `ClkType [%d] : OK` (`0x43c3c57f`) y el
estándar de TV: `PAL(50i) MODE Clk[%d]` (`0x43c3c5e9`) / `NTSC(60i) MODE Clk[%d]` (`0x43c3c612`).
El terminal es `Run Codec Set State STATE_CODEC_CLK_CHANGE` (`0x43c3c657`).

### 2.6 El sincronismo vertical (`CdUtilSysvMsg`)

`Reg SysV` (`0x43c3c63c`), `UnReg SysV` (`0x43c3c5cc`) y
`[VSYNC] RUN CODEC INIT` (`0x43c3c5a3`): el diagnóstico **registra unacallback de
sincronismo vertical** para arrancar el códec en el momento exacto.

### 2.7 Los datos de prueba

Cada códec busca su fichero de datos por identificador:
`Found File ID [0x%08X]` (`0x43c3c407` en HD DEC) y el error
`[ERR][CDIAG][CTRLHDDEC]Invalid File ID!! [0x%08X]` (`0x43c3c431`).
El identificador de códec es `cdcId` (`0x43c6495a` / `0x43c64975`: `CDCID_HD_CODEC`,
`CDCID_SD_CODEC`).

## 3. Mapa de las 270 trazas por sub-bloque (VERIFICADO)

Las 255 cadenas que empiezan por `[CDIAG]` se agrupan por la etiqueta de segundo nivel
(la que va entre corchetes). Las 15 restantes (`[ERR][CDIAG]…`) pertenecen a los mismos
sub-bloques y se indican aparte.

| sub-bloque | clase C++ | cadenas | rango de cadenas | funciones (código) |
|---|---|---|---|---|
| `[TSK]` | `CdTskCore` | 1 | `0x43c3b0d4` | `0x435a127a`–`0x435a128e` |
| `[TSKCORE]` (`[ERR]`) | `CdTskCore` | 1 | `0x43c3b0f4` | `0x435a1318`–`0x435a13b4` |
| `[CTRLIF]` | `CdCtrlIf` | 19 | `0x43c3b1b5`–`0x43c3b624` | `0x435a1424`–`0x435a1968` |
| `[CTRLCORE]` | `CdCtrlCore` | 49 | `0x43c3b89f`–`0x43c3c0eb` | `0x435a1c5c`–`0x435a2790` |
| `[CTRLHDDEC]` | `CdCtrlHdDec` | 26 | `0x43c3c1f1`–`0x43c3c657` | `0x435a2810`–`0x435a2d94` |
| `[CTRLHDREC]` | `CdCtrlHdRec` | 27 | `0x43c3c761`–`0x43c3cbeb` | `0x435a2dc4`–`0x435a3410` |
| `[CTRLJPGDEC]` | `CdCtrlJpgDec` | 21 | `0x43c3cca7`–`0x43c3d083` | `0x435a3440`–`0x435a381c` |
| `[CTRLJPGENC]` | `CdCtrlJpgEnc` | 21 | `0x43c3d19f`–`0x43c3d57f` | `0x435a3850`–`0x435a3bc8` |
| `[CTRLJPGENCDEC]` | `CdCtrlJpgEncDec` | 22 | `0x43c3d5f6`–`0x43c3da06` | `0x435a3bfc`–`0x435a3ee2` |
| `[CTRLSDDEC]` | `CdCtrlSdDec` | 26 | `0x43c3da73`–`0x43c3ded9` | `0x435a3fc4`–`0x435a452c` |
| `[CTRLSDREC]` | `CdCtrlSdRec` | 27 | `0x43c3dfda`–`0x43c3e478` | `0x435a455c`–`0x435a4b98` |
| `[CMPDATA]` | `CdUtilCmpData` | 16 | `0x43c3e557`–`0x43c3e86a` | `0x435a4eb0`–`0x435a50b6` |
| **total** | | **255** (+15 con `[ERR]`) | `0x43c3b0d4`–`0x43c3e86a` | `0x435a127a`–`0x435a50b6` |

Las 15 trazas con prefijo `[ERR]` (todas verificadas, con su función):

| vaddr | texto | función |
|---|---|---|
| `0x43c3b0f4` | `[ERR][CDIAG][TSKCORE]DataflowInfraMsgErr [0x%08X]` | `0x435a1318` |
| `0x43c3b238` | `[ERR][CDIAG][CTRLIF]NOT SUPPORTED -- COMMAND ID [0x%08X] [%s]` | `0x435a1424`, `0x435a15e8`, `0x435a17e8` |
| `0x43c3b277` | `[ERR][CDIAG][CTRLIF]SEND MSG EXEC CMD err[0x%04X] …` | `0x435a157c` |
| `0x43c3b3e8` | `[ERR][CDIAG][CTRLIF]NOT SUPPORTED(SENS_SET_DATA) -- MODE ID [0x%08X] [%s]` | `0x435a15e8`, `0x435a17e8` |
| `0x43c3b82d` | `[ERR][CDIAG][CTRLCORE]p_prm is NULL file[%s] func[%s] line[%d]` | `0x435a1b18` |
| `0x43c3b87b` | `[ERR][CDIAG][CTRLCORE]p_prm is NULL` | `0x435a1b18` |
| `0x43c3c431` | `[ERR][CDIAG][CTRLHDDEC]Invalid File ID!! [0x%08X]` | `0x435a2a88` |
| `0x43c3c9a1` | `[ERR][CDIAG][CTRLHDREC]Invalid File ID!! [0x%08X]` | `0x435a30d4` |
| `0x43c3ceac` | `[ERR][CDIAG][CTRLJPGDEC]Invalid File ID!! [0x%08X]` | `0x435a364c` |
| `0x43c3cf05` | `[ERR][CDIAG][CTRLJPGDEC]JPEG DEC FAILED !!` | `0x435a37ac` |
| `0x43c3d3a3` | `[ERR][CDIAG][CTRLJPGENC]Invalid File ID!! [0x%08X]` | `0x435a3a5c` |
| `0x43c3d404` | `[ERR][CDIAG][CTRLJPGENC]JPEG ENC FAILED !!` | `0x435a3b68` |
| `0x43c3d83f` | `[ERR][CDIAG][CTRLJPGENCDEC]Invalid File ID!! [0x%08X]` | `0x435a3e88` |
| `0x43c3dcb3` | `[ERR][CDIAG][CTRLSDDEC]Invalid File ID!! [0x%08X]` | `0x435a421c` |
| `0x43c3e21a` | `[ERR][CDIAG][CTRLSDREC]Invalid File ID!! [0x%08X]` | `0x435a483c` |

## 4. Las 16 clases y los 2 ficheros fuente (VERIFICADO)

### 4.0 La tabla de registro de clases (VERIFICADO)

En `0x43fda6a0` hay una **tabla de 16 pares de 8 bytes** `{vptr, puntero-al-nombre-de-clase}`
que enumera, en este orden, las 16 clases del subsistema:

| entrada | clase | entrada | clase |
|---|---|---|---|
| `0x43fda6a0` | `7CdMsgIf` | `0x43fda6d0` | `11CdCtrlHdRec` |
| `0x43fda6a8` | `9CdTskCore` | `0x43fda6d8` | `12CdCtrlJpgDec` |
| `0x43fda6b0` | `8CdCtrlIf` | `0x43fda6e0` | `12CdCtrlJpgEnc` |
| `0x43fda6b8` | `9CdMsgCore` | `0x43fda6e8` | `15CdCtrlJpgEncDec` |
| `0x43fda6c0` | `10CdCtrlCore` | `0x43fda6f0` | `11CdCtrlSdDec` |
| `0x43fda6c8` | `11CdCtrlHdDec` | `0x43fda6f8` | `11CdCtrlSdRec` |
| | | `0x43fda700` | `9CdMemCtrl` |
| | | `0x43fda708` | `13CdUtilClkCtrl` |
| | | `0x43fda710` | `13CdUtilCmpData` |
| | | `0x43fda718` | `13CdUtilSysvMsg` |

(fin de la tabla: `0x43fda720`; los 16 pares comparten el mismo vptr `0x43fd04f8`).

La **misma tabla existe en la A7S fw3.20** en `0x43fdb6ec` (16 entradas, fin `0x43fdb76c`)
con **el mismo conjunto de clases** (sólo cambia el orden de las 4 primeras:
`CdMsgIf, CdCtrlIf, CdMsgCore, CdTskCore` en la A7S frente a
`CdMsgIf, CdTskCore, CdCtrlIf, CdMsgCore` en la A6000).
En la **A6300 fw2.01** la tabla está en `0x4419b094` y tiene **20 entradas** (las 16 de la
A6000 + `CdExtMsgIf`, `CdExtCtrlIf`, `CdExtCtrlCore`, `CdExtMcCtrl`).

Script: `scan_class_table.py` → `cdiag_class_table.json`.

### 4.1 Nombres de clase embebidos en la zona

Nombres de clase embebidos en la zona (formato `<longitud><Nombre>`):

| vaddr | clase | vaddr | clase |
|---|---|---|---|
| `0x43c3b0cb` | `CdMsgIf` | `0x43c3d5a4` | `CdCtrlJpgEncDec` |
| `0x43c3b0e9` | `CdTskCore` | `0x43c3df16` | `CdCtrlSdDec` |
| `0x43c3b67e` | `CdCtrlIf` | `0x43c3dfcc` | `CdCtrlSdRec` |
| `0x43c3b6d4` | `CdMsgCore` | `0x43c3e53c` | `CdMemCtrl` |
| `0x43c3c116` | `CdCtrlCore` | `0x43c3e547` | `CdUtilClkCtrl` |
| `0x43c3c1e3` | `CdCtrlHdDec` | `0x43c3e89b` | `CdUtilCmpData` |
| `0x43c3c753` | `CdCtrlHdRec` | `0x43c3e8ab` | `CdUtilSysvMsg` |
| `0x43c3cc98` | `CdCtrlJpgDec` | | |
| `0x43c3d11c` | `CdCtrlJpgEnc` | | |

Ficheros fuente embebidos: **`cdCtrlIf.cpp`** (`0x43c3b1a8`) y **`cdCtrlCore.cpp`**
(`0x43c3b86c`). Las clases de códec (`CdCtrlHdDec`, `CdCtrlHdRec`, `CdCtrlJpgDec`,
`CdCtrlJpgEnc`, `CdCtrlJpgEncDec`, `CdCtrlSdDec`, `CdCtrlSdRec`) y las utilidades
(`CdMemCtrl`, `CdUtilClkCtrl`, `CdUtilCmpData`, `CdUtilSysvMsg`) **no tienen su propio
nombre de fichero embebido**: se generan por plantilla/herencia a partir de las clases base
`CdCtrlCore` y `CdCtrlIf` (INFERENCIA; los nombres concretos de fichero no son recuperables
de los bytes).

### 4.1 Las 27 firmas de función embebidas (`CDIAGER …`)

El prefijo `CDIAGER ` introduce la firma C++ completa de la función que dispara la traza
(macro de assert del estilo `[%s] -- file[%s] func[%s] line[%d]`, `0x43c3b176`). Todas:

| vaddr | firma | función |
|---|---|---|
| `0x43c3b126` | `CdCtrlIf::ExecSensCmd(__uint32_t, const OsalRequestPacket*, __uint32_t)` | `0x435a15e8` |
| `0x43c3b647` | `CdCtrlIf::ExecCmd(CdCtrlIf::MSG_SENS_COMMAND*)` | `0x435a1424` |
| `0x43c3b688` | `CdCtrlIf::ExecSensComp(__uint32_t, OsalResponsePacket*, __uint32_t)` | `0x435a15e8` |
| `0x43c3b6df` | `CdCtrlCore::DbgDiagAvc(__uint8_t,__uint8_t,__uint8_t,__uint8_t)` | `0x435a1c5c` |
| `0x43c3b72a` | `CdCtrlCore::CmpData(__uint8_t,__uint8_t,__uint32_t)` | `0x435a1c5c` |
| `0x43c3b768` | `CdCtrlCore::RelMemArea(__uint8_t,__uint8_t,__uint32_t)` | `0x435a1c5c` |
| `0x43c3b7a9` | `CdCtrlCore::SetCompNormal(OsalResponsePacket*, __uint32_t)` | `0x435a1b18` |
| `0x43c3b7ec` | `CdCtrlCore::SetMemArea(__uint8_t,__uint8_t,__uint32_t)` | `0x435a1c5c` |
| `0x43c3c123` | `CdCtrlCore::RunCodec(__uint8_t,__uint8_t,__uint32_t)` | `0x435a1c5c` |
| `0x43c3c162` | `CdCtrlCore::SetData(const __uint8_t*, __uint32_t)` | `0x435a23b4` |
| `0x43c3c19c` | `CdCtrlCore::SetCompDeleteData(OsalResponsePacket*, __uint32_t)` | `0x435a1bf0` |
| `0x43c3c694` | `CdCtrlHdDec::SetMemArea(CdCtrlHdDec::DIAGINFO*)` | `0x435a28ee` |
| `0x43c3c6cc` | `CdCtrlHdDec::RelMemArea(CdCtrlHdDec::DIAGINFO*)` | `0x435a28ee` |
| `0x43c3c704` | `CdCtrlHdRec::SetCodecParam(__uint8_t,__uint8_t,__uint8_t,__uint8_t)` | `0x435a3368` |
| `0x43c3cc28` | `CdCtrlHdRec::RelMemArea(CdCtrlHdRec::DIAGINFO*)` | `0x435a2fb6` |
| `0x43c3cc60` | `CdCtrlHdRec::SetMemArea(CdCtrlHdRec::DIAGINFO*)` | `0x435a2e9c` |
| `0x43c3d0a8` | `CdCtrlJpgDec::SetMemArea(CdCtrlJpgDec::DIAGINFO*)` | `0x435a3482` |
| `0x43c3d0e2` | `CdCtrlJpgDec::RelMemArea(CdCtrlJpgDec::DIAGINFO*)` | `0x435a35b0` |
| `0x43c3d12b` | `CdCtrlJpgEnc::RelMemArea(CdCtrlJpgEnc::DIAGINFO*)` | `0x435a39c0` |
| `0x43c3d165` | `CdCtrlJpgEnc::SetMemArea(CdCtrlJpgEnc::DIAGINFO*)` | `0x435a3892` |
| `0x43c3d5b6` | `CdCtrlJpgEncDec::SetMemArea(CdCtrlJpgEncDec::DIAGINFO*)` | `0x435a3c6a` |
| `0x43c3da33` | `CdCtrlJpgEncDec::RelMemArea(CdCtrlJpgEncDec::DIAGINFO*)` | `0x435a3d76` |
| `0x43c3df24` | `CdCtrlSdDec::RelMemArea(CdCtrlSdDec::DIAGINFO*)` | `0x435a40a2` |
| `0x43c3df5c` | `CdCtrlSdDec::SetMemArea(CdCtrlSdDec::DIAGINFO*)` | `0x435a40a2` |
| `0x43c3df94` | `CdCtrlSdRec::SetMemArea(CdCtrlSdRec::DIAGINFO*)` | `0x435a463e` |
| `0x43c3e4b5` | `CdCtrlSdRec::RelMemArea(CdCtrlSdRec::DIAGINFO*)` | `0x435a4756` |
| `0x43c3e4ed` | `CdCtrlSdRec::SetCodecParam(__uint8_t,__uint8_t,__uint8_t,__uint8_t)` | `0x435a4ae4` |

El tipo de parámetro **`DIAGINFO*`** (`CdCtrlHdDec::DIAGINFO*`, `CdCtrlSdRec::DIAGINFO*`, …)
es la estructura con los datos del diagnóstico: **fileId** (fichero de datos), **memIdx**,
**unitHandle**, **unitType** y **size** — exactamente los campos que vuelca la traza
`memIdx[%d] fileId[%02d:%02d] unitHandle[0x%04X] unitType[0x%08X] size[0x%08X]`
(`0x43c3bfee`).

## 5. Cómo se comunica: OSAL y mensajes (VERIFICADO)

### 5.1 El transporte

Las firmas embebidas usan los tipos de paquete del OSAL:
`const OsalRequestPacket*` (`0x43c3b126`) y `OsalResponsePacket*` (`0x43c3b688`).
El comando viaja como `CdCtrlIf::MSG_SENS_COMMAND*` (`0x43c3b647`), una **estructura de
mensaje propia del subsistema**, y las trazas de `[CTRLIF]` describen su ciclo:

- `[CDIAG][CTRLIF]EXEC CMD cmd[0x%02x] mode[%d] func[%d] prm[%d]` (`0x43c3b1b5`)
- `[CDIAG][CTRLIF]cmdMode[0x%08X] cmd[0x%08X] mode[0x%08X] [%s]` (`0x43c3b316`)
- `[CDIAG][CTRLIF]Data0[0x%02X] Data1[0x%02X]` (`0x43c3b354`)
- `[CDIAG][CTRLIF]SEND MSG EXEC CMD cmd[0x%02x] mode[%d] func[%d] prm[%d]` (`0x43c3b2cf`)
  y su error `[ERR][CDIAG][CTRLIF]SEND MSG EXEC CMD err[0x%04X] …` (`0x43c3b277`).

El campo `mode` es el **modo de comando** (`cmdMode`) y `func` la operación (§2.2).

### 5.2 Los 15 nombres `SENS_*` de la zona del módulo

14 comandos + el nombre del tipo de mensaje. Todos verificados en la zona
(`0x43c3b203`–`0x43c3b66f`):

`SENS_SET_DATA_AREA` (`0x43c3b203`), `SENS_REL_DATA_AREA` (`0x43c3b216`),
`SENS_RUN_CODEC` (`0x43c3b229`), `SENS_MODE_PROC_START` (`0x43c3b397`),
`SENS_MODE_FIN_SEND_DATA` (`0x43c3b3ca`), `SENS_SET_DATA` (`0x43c3b40a`),
`SENS_MODE_FIN_RECV_DATA` (`0x43c3b44b`), `SENS_CNFM_DONE_CODEC` (`0x43c3b47c`),
`SENS_CNFM_SET_DATA_AREA` (`0x43c3b4a6`), `SENS_CNFM_REL_DATA_AREA` (`0x43c3b4d3`),
`SENS_DBG_DIAG_AVC` (`0x43c3b500`), `SENS_SET_DIAG_MODE` (`0x43c3b527`),
`SENS_CMP_DATA` (`0x43c3b5c3`), `SENS_GET_DATA` (`0x43c3b633`), y el nombre del tipo de
mensaje `SENS_COMMAND` (`0x43c3b66f`).

Además, fuera del módulo: `SENS_CODEC_DIAG_MODE` (`0x43c6f339`, dentro del módulo
`[MCSENS]`: `[MCSENS][CTRLIF]SENS_CODEC_DIAG_MODE [0x%08X] [%s]`), `SENS_SET_AVCE_PARAM`
(`0x43cd2f01`) y `SENS_SET_MP2E_PARAM` (`0x43cd2f15`).

El sentido de cada comando se deduce de su pareja "recibido" / "enviado":
`Received SENS_MODE_PROC_START` (`0x43c3b37f`), `Received SENS_MODE_FIN_SEND_DATA`
(`0x43c3b3b2`), `Received SENS_MODE_FIN_RECV_DATA` (`0x43c3b433`),
`Cmd SENS_CNFM_DONE_CODEC` (`0x43c3b469`).

### 5.3 Las llamadas al OSAL

Las cuatro funciones de mensaje del OSAL están identificadas por el propio módulo
`[CLK_CTRL]`, que escribe el nombre de la API en la traza de error justo después de la
llamada (el mismo patrón en las dos direcciones):

| API OSAL | dirección | traza que la nombra | vaddr de la traza |
|---|---|---|---|
| `osal_try_valloc_msg` | `0x435612d0` | `[CLK_CTRL]: [ERR] osal_try_valloc_msg 0x%0x` | `0x43c3ab06` |
| `osal_snd_msg` | `0x4356120c` | `[CLK_CTRL]: [ERR] osal_snd_msg 0x%0x` | `0x43c3ab32` |
| `osal_free_msg` | `0x435612ec` | `[CLK_CTRL]: [ERR] osal_free_msg 0x%0x` | `0x43c3ab57` |
| `osal_rcv_msg` | `0x43561260` | `[CLK_CTRL]: [ERR] osal_rcv_msg 0x%0x` | `0x43c3ab7d` |

(Las direcciones son las *funciones*; el `bl` las apunta con el bit 0 = 1, por eso las
llamadas aparecen como `bl #0x43561261`, `bl #0x4356120d`, etc.)

**Enlace verificado con el núcleo de la tarea de diagnóstico**: la función
`0x435a1318` (la que emite `[ERR][CDIAG][TSKCORE]DataflowInfraMsgErr`) llama a `0x435a9f4c`,
y esa función llama a `osal_rcv_msg` en `0x435a9f68`:

```
0x435a1342  bl  0x435a9f4c        ; CdTskCore: recibir mensaje
...
0x435a9f64  add r1, sp, #4
0x435a9f66  mov r0, r5
0x435a9f68  bl  0x43561260        ; -> osal_rcv_msg
```

La capa de mensajes de la tarea (`0x435a9e00`–`0x435b0000`, donde viven `CdMsgIf` y
`CdMsgCore`) usa las cuatro API: **39** llamadas a `osal_try_valloc_msg`, **31** a
`osal_snd_msg`, **48** a `osal_free_msg` y **3** a `osal_rcv_msg` (contadas recorriendo los
`bl` de 32 bits de la zona). Las funciones del propio `[CDIAG]` **no** las llaman
directamente: pasan por esa capa intermedia.

El canal es la **infraestructura de flujo de datos** del OSAL: el error
`[ERR][CDIAG][TSKCORE]DataflowInfraMsgErr [0x%08X]` (`0x43c3b0f4`, referenciada en
`0x435a134c`) y las clases `DataflowInfraMsg` (`0x43c40038`), `DataflowInfraMsgEx`
(`0x43c4004b`), `DataflowInfraReceiver` (`0x43c40073`), `DataflowInfraSender` (`0x43c4008b`),
`DataflowInfraPin` (`0x43c26b6d`).

### 5.4 La escritura de trazas

Todas las trazas `[CDIAG]` salen por el **formateador variádico `0x435ab880`**, al que el
código del módulo llama **310 veces** (recuento de los `bl` de 32 bits sobre los 118
rangos de función). Esa función (bytes verificados):

| vaddr | halfwords | instrucción |
|---|---|---|
| `0x435ab880` | `0xB40F` | `push {r0,r1,r2,r3}` (prólogo) |
| `0x435ab882` | `0x2180` | `movs r1,#0x80` → búfer de 128 bytes |
| `0x435ab896` | `bl` | → `0x439c5004` (formateo tipo `vsnprintf`) |
| `0x435ab8a2` | `0xF640 0x31AD` | `movw r1,#0xbad` → id de módulo `0xbad` |
| `0x435ab8ae` | `0x20BE` | `movs r0,#0xbe` → nivel `0xbe` (190) |
| `0x435ab8b0` | `bl` | → `0x435ab7d4` (emisor de log) |

El emisor alternativo `0x435a0414` (el que usa `[CLK_CTRL]` con nivel `0xc0`) se llama
**15 veces, todas en `0x435a055c`–`0x435a082a`**, es decir **fuera** del código de
`[CDIAG]`: las trazas de diagnóstico no lo usan.

## 6. Cómo se referencia una cadena (método, VERIFICADO)

Las cadenas **no** se apuntan con punteros absolutos. El código hace

```
ldr  rX, [pc, #inm]      ; el pool guarda un desplazamiento W
add  rX, pc              ; destino = W + (dirección_del_add + 4)
```

`scan_cdiag.py` barre toda la imagen (11.4 MB, ~5 s) y empareja cada `add rX,pc` con el
**`ldr rX,[pc,#imm]` más cercano por detrás y del mismo registro**; el destino debe caer
exactamente en el inicio de una cadena. Con esa regla:

- **226 de las 255** cadenas que empiezan por `[CDIAG]` tienen referencia directa
  (295 sitios de referencia en total, contando también las 15 cadenas `[ERR][CDIAG]`);
- **29** no la tienen **y tampoco hay ningún puntero absoluto de 4 B** a su dirección en toda
  la imagen ⇒ son cadenas muertas que el enlazador conservó. Son exactamente:
  **25** trazas `ClkState …` / `ClkType` / `[VSYNC] RUN CODEC INIT` de los tres
  controladores **JPEG** (`CTRLJPGDEC`, `CTRLJPGENC`, `CTRLJPGENCDEC`) y **4** trazas
  `MEM SHARE err` (`0x43c3c29c` HD DEC, `0x43c3cd91` JPG DEC, `0x43c3d289` JPG ENC,
  `0x43c3db1e` SD DEC);
- las distancias `add`−`ldr` de todas las referencias son **≤ 10 bytes** (2, 4, 6, 8 y 10
  bytes), lo que confirma el emparejamiento.

Ejemplo verificado a mano (bytes leídos, no inferido):

```
0x435a1450  ldr  r0,[pc,#0x26]     ; pool en 0x435a14ec = 0x000699d5f
0x435a1452  add  r0, pc            ; 0x699d5f + 0x435a1456 = 0x43c3b1b5
                                   ; = "[CDIAG][CTRLIF]EXEC CMD cmd[0x%02x] mode[%d] func[%d] prm[%d]"
```

Las funciones se delimitan por `push {…,lr}` … `pop {…,pc}` (o `push.w`/`pop.w`), con el
matiz de que el compilador puede *hoistear* el `ldr`+`add` **antes** del `push` del prólogo
(por eso el inicio de la función se extiende hasta el retorno anterior).

## 7. Relación con los demás subsistemas

| subsistema | relación (con evidencia) |
|---|---|
| **Códec AVC / JPEG** | es lo que se somete a prueba: `[CDIAG][CTRLCORE]Exec RunCodec HD REC!!` (`0x43c3bbe0`), `… JPEG ENCDEC!!` (`0x43c3bcd2`), `JPEG ENC END... [%d]bits` (`0x43c3d42f`), `JPEG DEC END... w[%d] h[%d]` (`0x43c3cf30`) |
| **Reloj / `CLK_CTRL`** | su código empieza justo antes (`0x4359ee48`) y el de `[CDIAG]` justo después (`0x435a127a`): son tareas vecinas en el mismo bloque; comparten además el estado de reloj (`ClkState …`, `PAL(50i)/NTSC(60i) MODE Clk`) y la API `ddl_clkctrl_*` (`0x4359f250`…) |
| **Memoria dinámica** | `CdMemCtrl` (`0x43c3e53c`): `MEM ALLOC/SHARE/FREE`, `unitHandle`, `unitType`, `size` |
| **OSAL / flujo de datos** | `OsalRequestPacket`/`OsalResponsePacket`, `osal_snd_msg`/`osal_rcv_msg`/`osal_try_valloc_msg`/`osal_free_msg`, `DataflowInfra*` |
| **Sincronismo vertical (SysV)** | `CdUtilSysvMsg` (`0x43c3e8ab`): `Reg SysV`/`UnReg SysV`/`[VSYNC] RUN CODEC INIT` |
| **`MCSENS`** | módulo hermano (13 trazas, `0x43c42670`–`0x43c73649`) que comparte la familia de comandos `SENS_*`: `[MCSENS][CTRLIF]SENS_CODEC_DIAG_MODE [0x%08X] [%s]` (`0x43c6f339`) |
| **AVC (módulo `mcAvc*`)** | el códec que se somete a prueba es el de `mcAvcEnc*`/`mcAvcDec*` (`ExCodec.cpp` `0x43c41cb2`, `mcAvcEncSeqCtrl.cpp` `0x43c4bd17`); el propio `CdCtrlCore::DbgDiagAvc` lo activa |
| **Sensor / imager / DFE** | **sin relación directa**: en las 270 trazas no aparece ni una vez `shutter`, `imager`, `sensor`, `DFE`, `dmm` o `readout` (búsqueda case-insensitive). El diagnóstico del códec no toca el obturador ni el sensor ⇒ **sin efecto sobre S51** (obturador electrónico): A/B/C = NO |

## 8. Diferencial A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

Comparación **literal de las 270 cadenas** `[CDIAG]` (mismo texto, no solo el mismo recuento):

| | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| tokens `[CDIAG]` | **270** | **270** |
| rango de los tokens | `0x43c3b0d4`–`0x43c3e86a` | `0x43c3b740`–`0x43c3eed6` |
| cadenas **comunes** (texto idéntico) | **270** | **270** |
| cadenas exclusivas de A6000 | **0** | — |
| cadenas exclusivas de la A7S | — | **0** |
| firmas `CDIAGER …` | 27 | 27 |
| clases `Cd*` | 16 | 16 (mismo conjunto) |
| tabla de registro de clases | `0x43fda6a0`, 16 entradas | `0x43fdb6ec`, 16 entradas |
| ficheros `cd*.cpp` | 2 (`cdCtrlIf.cpp`, `cdCtrlCore.cpp`) | 2 (los mismos) |

⇒ **El subsistema `[CDIAG]` es idéntico, cadena por cadena, entre la fw3.21 de la A6000 y la
fw3.20 de la A7S.** No hay ningún cambio funcional ni de instrumentación en este módulo
entre ambos firmwares (a diferencia de lo que ocurre con `CAMERA_MAIN_*` o `IMAGING_CAP`,
donde S79/S106 ya detectaron cambios de etiquetado).

### 8.1 A6300 fw2.01 (referencia, VERIFICADO)

La A6300 tiene **310** tokens `[CDIAG]`: las 270 comunes **más 40 nuevas**, todas de 4K:

- nueva clase de controlador `[CDIAG][CTRL4KREC]` (24 cadenas: `MEM ALLOC/SHARE/FREE`,
  `ClkState …`, `Reg/UnReg SysV`, `LOOP NUM`, `Found File ID`, …);
- nuevos modos en `[CTRLCORE]`: `Exec DbgDiagAvc 4K REC!!`, `Exec RunCodec 4K DEC!!`,
  `Exec SetData 4K ENC!!`, `Exec SetMemArea 4K REC!!`, `Exec CmpData 4K DEC!!`,
  `Exec ConfirmDoneCodec 4K REC!!`, `Exec RelMemArea 4K DEC!!` (16 cadenas);
- nuevas clases: `CdCtrl4KDec` (`0x43d2c857`), `CdCtrl4KRec` (`0x43d2d1dd`),
  `CdExtMsgIf` (`0x43d2377f`), `CdExtCtrlIf` (`0x43d23f0f`), `CdExtCtrlCore` (`0x43d28331`),
  `CdExtMcCtrl` (`0x43d28aec`) → la **tabla de registro de clases** de la A6300
  (`0x4419b094`) tiene **20 entradas** (16 + 4 `CdExt*`) y **6 ficheros**:
  `cdExtMsgIf.cpp`, `cdCtrlIf.cpp`, `cdExtCtrlIf.cpp`, `cdCtrlCore.cpp`, `cdExtCtrlCore.cpp`,
  `cdExtMcCtrl.cpp`;
- además aparecen `CodecDiagLog` (`0x43d29377`) y `UlogioLog` (`0x43d29361`).

## 9. NO VERIFICADO / abierto

- **Nombres de fichero** de las clases de códec (`CdCtrlHdDec`, `CdCtrlSdRec`, …) y de las
  utilidades (`CdMemCtrl`, `CdUtilClkCtrl`, `CdUtilCmpData`, `CdUtilSysvMsg`): no hay
  cadenas de fichero embebidas para ellas; sólo se pueden inferir por analogía con
  `cdCtrlIf.cpp` / `cdCtrlCore.cpp`.
- **Formato binario** de `CdCtrlIf::MSG_SENS_COMMAND`, de `DIAGINFO` y de los mensajes
  `SENS_*` (sólo se conocen los campos que imprimen las trazas: `cmd`, `mode`, `func`,
  `prm`, `Data0`, `Data1`).
- **Valores numéricos** de `cmd`, `mode` y `func`: se conocen los 7 nombres de modo
  (HD REC…JPEG ENCDEC) y las 8 operaciones, pero **no** su codificación numérica.
- **Las 29 cadenas sin referencia** (§6): se ha comprobado que no hay referencia PIC ni
  puntero absoluto, pero no puede descartarse que el enlazador las reservara para código
  muerto de otra variante de firmware.
- **Quién es el maestro** que emite los comandos `SENS_*` (el "Master"/VFC aparece en las
  trazas de `[CLK_CTRL]`, pero no hay ninguna traza de `[CDIAG]` que nombre al emisor).
- **Relación con el bloque `Scenario END` / `[CodecSeq]`** (`0x43c3e8bb` y siguientes): el
  módulo `[CodecSeq]` está justo detrás de `[CDIAG]` en memoria y comparte vocabulario
  (`ENC_OPEN`, `DEC_START`, `MSGID_PIN_CONNECT YC`), pero **no** está verificado que
  `[CodecSeq]` forme parte de `[CDIAG]` (el prefijo de log es distinto).
- **Sincronización con la A7S en el *código***: la comparación es de cadenas; no se ha
  verificado que el código de la A7S en `av-cam.bin` esté en la misma dirección relativa
  ni que sea binariamente idéntico.

## 10. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s109_cdiag/scan_cdiag.py      # -> cdiag.json
.venv/bin/python analysis/s109_cdiag/scan_diff.py       # -> cdiag_diff.json (+ merge)
.venv/bin/python analysis/s109_cdiag/scan_cdiag_refs.py # -> cdiag_refs.json (todas las refs PIC)
.venv/bin/python analysis/s109_cdiag/disasm.py 0x435a15e8 40   # desensamblado puntual
.venv/bin/python -m pytest tests/test_s109_cdiag.py -q
```

| fichero | contenido |
|---|---|
| `analysis/s109_cdiag/cdiag.json` | datos estructurados: 255+15 cadenas con vaddr/texto/referencias/función, 27 firmas, 16 clases, 2 ficheros, sub-bloques, agregado por clase, tabla de registro de clases y diferencial |
| `analysis/s109_cdiag/cdiag_diff.json` | comparación literal A6000/A7S/A6300 |
| `analysis/s109_cdiag/cdiag_class_table.json` | tabla de registro de clases de los tres firmwares |
| `analysis/s109_cdiag/cdiag_refs.json` | destinos de las 18 210 referencias PIC de la imagen |
| `analysis/s109_cdiag/scan_cdiag.py` | extracción reproducible (cadenas, refs, funciones, clases, diferencial) |
| `analysis/s109_cdiag/scan_diff.py` | diferencial literal entre los tres firmwares |
| `analysis/s109_cdiag/scan_class_table.py` | tabla de registro de clases |
| `analysis/s109_cdiag/scan_cdiag_refs.py` | barrido PIC de toda la imagen |
| `analysis/s109_cdiag/scan_unreferenced.py` | comprobación de referencias alternativas |
| `analysis/s109_cdiag/disasm.py` | volcado de desensamblado Thumb puntual |

## 11. Revisión del agente principal

*(vacío — se rellenará después)*

---

## Revisión del agente principal (21-10-2026)

**Verificado byte a byte (correcto):**

1. **Recuento**: 270 tokens `[CDIAG]`; 255 cadenas que empiezan por `[CDIAG]` y 15 `[ERR][CDIAG]`.
2. **Firmas y ficheros**: `CDIAGER CdCtrlCore::DbgDiagAvc(__uint8_t, __uint8_t, __uint8_t, __uint8_t)` `0x43c3b6df`,
   `CDIAGER CdCtrlCore::CmpData(__uint8_t, __uint8_t, __uint32_t)` `0x43c3b72a`,
   `CDIAGER CdCtrlCore::RunCodec(__uint8_t, __uint8_t, __uint32_t)` `0x43c3c123`,
   `cdCtrlIf.cpp` `0x43c3b1a8`, `cdCtrlCore.cpp` `0x43c3b86c` y los nombres RTTI
   `8CdCtrlIf` `0x43c3b67e`, `13CdUtilSysvMsg` `0x43c3e8ab`.
3. **Tabla de registro de clases** en `0x43fda6a0`: 16 pares de 4 B. **Detalle que el informe
   no destaca**: la primera palabra de los 16 pares es **siempre la misma** (`0x43fd04f8`) y la
   segunda es un puntero al nombre RTTI (`8CdCtrlIf` `0x43c3b67e`, `13CdUtilSysvMsg`
   `0x43c3e8ab`, …). Es decir, la tabla no es una tabla de vtables por clase, sino una tabla
   `{vtable_base_común, nombre_de_clase}`: sirve para **resolver una clase a su nombre**, con un
   puntero base compartido. La A7S tiene la equivalente en `0x43fdb6ec`.
4. **Diferencial A7S fw3.20**: 270 tokens, **270 cadenas comunes y 0 exclusivas** en ningún
   sentido, mismas 16 clases, mismos 2 ficheros y mismas 27 firmas → el módulo es idéntico.
   El A6300 fw2.01 tiene 310 tokens = 270 + **40 de 4K** (`[CTRL4KREC]`, `CdCtrl4KDec/Rec`,
   `CdExt*`, `CodecDiagLog`).
5. **Negativo**: 0 menciones de `shutter`/`silent`/`imager`/`sensor`/`dmm` en las 270 trazas →
   sin efecto sobre S51.

**Nota**: el subagente incluye `cdiag_refs.json` (18 210 destinos PIC de la imagen, 792 KB).
El rango de cadenas válidas del escáner compartido ya cubre toda la imagen, así que ese fichero
es reproducible; se conserva como dato del hito.
