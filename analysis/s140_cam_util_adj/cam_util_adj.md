# S140 — `[CAM_UTIL_ADJ]`: la utilidad de ajuste de la cámara (A6000 fw3.21)

**Hito**: S140 · **Binario**: `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B)
**Convención**: `vaddr = 0x43541000 + file_offset` (verificada en el repo).
**Regla de referencias**: **estricta** (canónica, `analysis/s106_imaging_cap/scan_pic_refs_strict.py`;
mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json`). Los sitios puntuales se han
verificado **a mano** desensamblando (aritmética `ldr`/`add` re-hecha byte a byte).
**Script canónico**: `analysis/s140_cam_util_adj/scan_s140.py` → `cam_util_adj.json`.

---

## 1. Resumen

| dato | valor |
|---|---|
| cadenas `[CAM_UTIL_ADJ]` en A6000 fw3.21 | **22** (bloque contiguo `0x43ccdcee`–`0x43cce0f2`) |
| cadenas referenciadas | **22 / 22** (ninguna muerta) |
| sitios de referencia (regla estricta) | **22** (exactamente 1 por cadena) |
| funciones que las referencian | **3** (`0x439007b0`, `0x43900a24`, `0x43900c44`) |
| cadenas `[CAM_UTIL_ADJ]` en A7S fw3.20 | **0** |
| cadenas `[CAM_UTIL_ADJ]` en A6300 fw2.01 | **0** |
| interiores de texto presentes en A7S / A6300 | **0 / 22** y **0 / 22** |

**Qué es.** `[CAM_UTIL_ADJ]` es la etiqueta de diagnóstico de la *utilidad de ajuste* del
firmware de la A6000: una **tarea OSAL** (`tsk_cam_adjctrl`) que recibe comandos de ajuste y
un **callback** (`cam_adjcmd_handle_cb()`) que los ejecuta. Lo que ejecutan es
**escribir o leer tablas de calibración dentro de la RAM del sensor**
(`Senser RAM Access`, `Table Write`, `Table Read`), direccionadas por
`Module ID` + `Offset` + `Size` (según el log) más 8 bytes de dato (`D0`–`D7`), y el resultado
se devuelve por el canal "Sens Infra" (código de resultado `Sens:AdjCmd CAIF` = `0x04020180`).
El módulo es, por tanto, **la vía de escritura de calibración de fábrica/servicio hacia el
sensor**, no un control de exposición.

**Interés para la línea del obturador**: el módulo **no** toca tiempos de obturación, iris,
ISO ni lectura de imagen. Ver §7 (criterio y evidencia).

---

## 2. Las 22 trazas, con dirección

Orden por vaddr. `sitio` = dirección del `add rX,pc`; `ldr` = `ldr rX,[pc,#imm]` emparejado
(regla estricta). Verificado a mano: `destino = pool + (dirección_del_add + 4)`.

| # | vaddr cadena | texto | sitio | ldr | función |
|---|---|---|---|---|---|
| 1 | `0x43ccdcee` | `[CAM_UTIL_ADJ]:  -- Table Write` | `0x439007f8` | `0x439007f0` | `0x439007b0` |
| 2 | `0x43ccdd0e` | `[CAM_UTIL_ADJ]:  -- :[Size] %08x [Orgdata] %x` | `0x4390080e` | `0x4390080c` | `0x439007b0` |
| 3 | `0x43ccdd3c` | `[CAM_UTIL_ADJ]:  -- :[Wdata] %x` | `0x43900824` | `0x43900822` | `0x439007b0` |
| 4 | `0x43ccdd5c` | `[CAM_UTIL_ADJ]:  -- Table Read` | `0x43900864` | `0x4390085c` | `0x439007b0` |
| 5 | `0x43ccdd7b` | `[CAM_UTIL_ADJ]:  -- :[Size] %08x [Rdata] %x` | `0x43900878` | `0x43900876` | `0x439007b0` |
| 6 | `0x43ccdda7` | `[CAM_UTIL_ADJ]:  -- :[Orgdata] %x` | `0x4390088e` | `0x4390088c` | `0x439007b0` |
| 7 | `0x43ccddc9` | `[CAM_UTIL_ADJ]: Senser RAM Access: CMD %x, Block %x` | `0x43900a6a` | `0x43900a68` | `0x43900a24` |
| 8 | `0x43ccddfd` | `[CAM_UTIL_ADJ]:   : [Mode]:%x, [ResCode]:%x, [StepNum]:%x` | `0x43900a84` | `0x43900a82` | `0x43900a24` |
| 9 | `0x43ccde37` | `[CAM_UTIL_ADJ]:   : [Adr]:%08x, [BSize]:%08x,[Size]:%08x` | `0x43900a9e` | `0x43900a9c` | `0x43900a24` |
| 10 | `0x43ccde70` | `[CAM_UTIL_ADJ]:   : [D0]:%04x, [D1]:%04x,[D2]:%04x, [D3]:%04x` | `0x43900abc` | `0x43900aba` | `0x43900a24` |
| 11 | `0x43ccdeae` | `[CAM_UTIL_ADJ]:   : [D4]:%04x, [D5]:%04x,[D6]:%04x, [D7]:%04x` | `0x43900ae2` | `0x43900ae0` | `0x43900a24` |
| 12 | `0x43ccdeec` | `[CAM_UTIL_ADJ]:   : [Module ID]:%08x, [Offset]:%08x, [Size]:%08x` | `0x43900af0` | `0x43900ae8` | `0x43900a24` |
| 13 | `0x43ccdf2d` | `[CAM_UTIL_ADJ]: ---cam_adjcmd_handle_cb()---[CmdCode]:%04x` | `0x43900b04` | `0x43900b00` | `0x43900a24` |
| 14 | `0x43ccdf68` | `[CAM_UTIL_ADJ]:  For SensRamAcs[DataSize]%x` | `0x43900b14` | `0x43900b0c` | `0x43900a24` |
| 15 | `0x43ccdf94` | `[CAM_UTIL_ADJ]:  For SensRamAcs[ModuleID]%x [Value]%x` | `0x43900b26` | `0x43900b1e` | `0x43900a24` |
| 16 | `0x43ccdfca` | `[CAM_UTIL_ADJ]:  [OriginalCmdCode ]:%04x` | `0x43900b3c` | `0x43900b3a` | `0x43900a24` |
| 17 | `0x43ccdff3` | `[CAM_UTIL_ADJ]:  [OriginalDataSize]:%04x` | `0x43900b4e` | `0x43900b4c` | `0x43900a24` |
| 18 | `0x43cce01c` | `[CAM_UTIL_ADJ]:  [OriginalBDataSize]:%04x` | `0x43900b60` | `0x43900b5e` | `0x43900a24` |
| 19 | `0x43cce046` | `[CAM_UTIL_ADJ]: ---Finish SENSER Infra Call Back Operation--- :%x` | `0x43900bc6` | `0x43900bbc` | `0x43900a24` |
| 20 | `0x43cce088` | `[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: begin. [Osal]%d` | `0x43900c5e` | `0x43900c58` | `0x43900c44` |
| 21 | `0x43cce0bd` | `[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: rcv failed(%d).` | `0x43900c86` | `0x43900c7e` | `0x43900c44` |
| 22 | `0x43cce0f2` | `[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: rcv cmd err(%x).` | `0x43900d0a` | `0x43900d02` | `0x43900c44` |

Las 22 cadenas son **contiguas** (`0x43ccdcee`–`0x43cce0f2`, sin huecos con otras cadenas
intercaladas): el módulo ocupa un bloque propio del *pool* de texto.

---

## 3. Las 3 funciones que las referencian

Límites verificados por desensamblado (prólogo `push` … `lr` / epílogo `pop` … `pc`).

### 3.1 `0x439007b0` — `0x439008ac` : lectura/escritura de tabla (`Table Read` / `Table Write`)

6 trazas (nº 1–6). Prólogo `push.w {r4,r5,r6,r7,r8,lr}` en `0x439007b0`; epílogo
`pop.w {r4,r5,r6,r7,r8,pc}` en `0x439008aa`.

- `0x439007ce` `cmp r1,#0xff` → si `r1==0xff` toma la rama **Write** (`0x439007f8`), si no la
  rama **Read** (`0x43900864`).
- Escribe la respuesta en la estructura recibida: `[r0]=8`, `[r0+1]=7`, `[r0+2]=u16`,
  `[r0+8]=1`, `[r0+0xc]=1` (o `r5` en la rama Write).
- Copia el dato con `blx 0x439c5320` (memcpy) entre `r0+0x10`/`r0+0x24` y la tabla de entradas
  (`ldr.w r0,[r7,r6,lsl #2]`).
- Es la única función de las tres que aparece en la **tabla de despacho** (§4).

### 3.2 `0x43900a24` — `0x43900bde` : `cam_adjcmd_handle_cb()`

13 trazas (nº 7–19). Prólogo `push.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,lr}` en `0x43900a24`;
epílogo `pop.w {r4,r5,r6,r7,r8,lr}` en `0x43900bd6` + cola `b.w 0x439009f0`.

Es el **callback de comando de ajuste**. Recibe en `r0` un puntero `r4` a una estructura de
comando y la vuelca en el log antes de despacharla. Campos **verificados** por desensamblado:

| offset | tipo | qué lo nombra el log |
|---|---|---|
| `+0x00` | u8 | `Mode` (traza 8) |
| `+0x01` | u8 | `ResCode` (traza 8) |
| `+0x02` | u16 | `StepNum` (traza 8) |
| `+0x04` | u32 | `BSize` (traza 9) / `OriginalBDataSize` (traza 18) |
| `+0x10` | u32 | `Adr` (traza 9) |
| `+0x14` | u32 | `Size` (traza 9) / `OriginalDataSize` (traza 17) |
| `+0x18` | u16 | `Block` (traza 7) |
| `+0x1a` | u16 | `CMD` (traza 7) / `CmdCode` (traza 13) / `OriginalCmdCode` (traza 16) |
| `+0x1c`–`+0x1f` | u8×4 | `D0`,`D1`,`D2`,`D3` (traza 10) |
| `+0x20`–`+0x23` | u8×4 | `D4`,`D5`,`D6`,`D7` (traza 11) |

Valores compuestos que se calculan en el prólogo y se pasan al log y al despacho:

| registro | construcción | uso |
|---|---|---|
| `r5` | u16 de los bytes `+0x1e`,`+0x1f` (`0x43900a34` `orr.w r5,r3,r5,lsl #8`) | **índice de despacho** (`cbz r5` / `cmp r5,#2` / `cmp r5,#1` en `0x43900b8a`–`0x43900b96`) y 1.er argumento de `SensRamAcs[ModuleID]` |
| `r6` | u16 de los bytes `+0x1c`,`+0x1d` (`0x43900a3e` `orr.w r6,r3,r6,lsl #8`) | 2.º argumento de `SensRamAcs[…][Value]` |
| `r7` | u8 de `+0x1a` (`0x43900afc`) | `CmdCode`; debe valer `0xFE` o `0xFF` para entrar en el despacho (`0x43900b82` `sub.w r3,r7,#0xfe`) |
| `r8` | u32 de `+0x20`–`+0x23` (`0x43900a46`–`0x43900a5a`) | `SensRamAcs[DataSize]` |

Por tanto la selección de operación la hace el **índice `r5`** (semivariable `+0x1e`): `0` →
stub, `1` → `0x439007b0` (Table Read/Write), `2` → stub, `>2` → stub por defecto (§4).
Además, `r5` es el valor que el log rotula `Module ID` (traza 12) y `r6` el que rotula
`Offset` (traza 12) / `Value` (traza 15).

> Nota: la traza 12 (`[Module ID]:%08x, [Offset]:%08x, [Size]:%08x`) imprime **tres** huecos
> u32 pero solo dos se inicializan frescos (`stm.w sp,{r5,r6}` en `0x43900af2`); el tercero
> conserva un valor de la llamada anterior. El valor real de ese tercer hueco es
> **NO VERIFICADO**.

### 3.3 `0x43900c44` — `0x43900d30` : `tsk_cam_adjctrl` (bucle de tarea OSAL)

3 trazas (nº 20–22). Prólogo `push {r4,r5,r6,r7,lr}` en `0x43900c44`.

- `0x43900c54` `bl 0x43561260` → recepción de mensaje OSAL (timeout `-1`).
- `0x43900c66` `bl 0x43900728` → traza `tsk_cam_adjctrl: begin. [Osal]%d`.
- `0x43900c78` `bl 0x43900c1c` → despacho de la respuesta.
- `0x43900c92` `ldrh r6,[r3,#0x1a]` → código de comando recibido:
  `0` → `bl 0x439023b8` (`[CAM_UTIL_SENS] UTIL MS Mgr) Call CB`),
  `2` → rama de tratamiento (`0x43900ca2`), otro → traza `rcv cmd err(%x)`.
- Reintenta en bucle (`b 0x43900c4c` en `0x43900d2e`).

### 3.4 Ayudantes de la zona (sin traza propia de este módulo)

| vaddr | papel (verificado por desensamblado) |
|---|---|
| `0x43900728` | log: formatea y envía la traza (`r0=0xb5`, `r1=2`, `r2=4`, `r3`=formato, varargs en pila) |
| `0x4390092c` | construye (OSAL msg de `0x2c` B) y **envía** el mensaje al infra |
| `0x439009c8` | escribe (`Module ID`, valor) en una variable global (`[r2+8]`, `[r2+0xa]`) |
| `0x439009f0` | escribe (tipo, a, b, c) en la variable global y despacha a `0x4390092c` |
| `0x43900c1c` | guarda la respuesta y, si la lista de destino no está lista, deriva a `0x4390092c` |
| `0x439023b8` | `[CAM_UTIL_SENS] UTIL MS Mgr) Call CB` |
| `0x43b2a0b8` | stub de respuesta «no soportado» (pone `{8,7,cmd,0,0}`) |

Destino del mensaje saliente: id `0x008f013a` (pool en `0x439009bc`) y plantilla de 12 B en
`0x43c04d70` = `{0x00e200e1, 0x00e400e3, 0x00e600e5}` (el significado de esos ids es
**NO VERIFICADO**).

---

## 4. Tabla de despacho de `cam_adjcmd_handle_cb()`

En `0x440121f8` (PIC: `ldr r3,[pc,#0x74]` en `0x43900b98` + `add r3,pc` en `0x43900b9a`;
`pool[0x43900c10] = 0x0071165a` → `0x0071165a + 0x43900b9e = 0x440121f8`).
Entradas de 8 B (`add.w r5,r3,r5,lsl #3` + `ldr r5,[r5,#4]`):

| índice | vaddr entrada | puntero | destino |
|---|---|---|---|
| 0 | `0x440121f8` | `0x43b2a0b9` | `0x43b2a0b8` — stub «no soportado» |
| 1 | `0x44012200` | `0x439007b1` | **`0x439007b0`** — Table Read/Write |
| 2 | `0x44012208` | `0x43b2a0b9` | `0x43b2a0b8` — stub «no soportado» |

Es decir: **de 3 operaciones posibles, solo una está implementada** (índice 1 = lectura/escritura
de tabla); las otras dos caen en el stub que devuelve una respuesta vacía.
El puntero del callback (`0x43900a25` = `cam_adjcmd_handle_cb` con bit Thumb) está en la tabla
de *callbacks* en `0x4401f7a4` (array de punteros de función).

---

## 5. Ficheros fuente

**No se ha podido atribuir un fichero fuente propio al módulo**: ninguna de las 22 trazas,
ni ninguna de las 3 funciones ni de sus ayudantes referencia un nombre `.cpp`/`.h`
(recalculado sobre todo el binario: los 595 nombres de fichero embebidos tienen 313
referencias PIC y **ninguna** cae en `0x439007b0`–`0x43900d30`; ningún nombre de fichero
tiene puntero absoluto de 4 B). → **NO VERIFICADO / no consta**.

Lo que sí es verificable por cercanía y familia de nombres:

- La capa «Sens» que este módulo usa **sí** tiene nombres de fichero embebidos:
  `amSensCtrlCore.cpp` (`0x43cdb45a`, referenciado desde `0x43920bda`),
  `amSensCtrlIf.cpp` (`0x43cd88cc`, referenciado desde `0x4391abfa` y `0x4391acda`),
  `amSensMsgIf.cpp` (`0x43cd2eb3`, referenciado desde `0x43911222` y `0x439112d6`);
  y las copias `mcSensCtrlCore.cpp` (`0x43c73689`, sitio `0x43629c5a`),
  `mcSensCtrlIf.cpp` (`0x43c6f2e9`, sitios `0x4361ff94`, `0x43620018`),
  `mcSensMsgIf.cpp` (`0x43c423c7`, sitios `0x435b3626`, `0x435b366c`).
  El código `am*` vive en la **misma banda** (`0x4391xxxx`–`0x4392xxxx`) que
  `[CAM_UTIL_ADJ]` (`0x4390xxxx`), a ~0x10000 B de distancia.
  → *Inferencia* (no prueba): `[CAM_UTIL_ADJ]` es una TU hermana de la familia `amSens*`.
- El único nombre de fichero del firmware que contiene «Adjust» es `Stage_Adjust.cpp`
  (`0x43cc6cc6`), que pertenece a la línea de captura (`[IMAGING_CAP]`, S106), **no** a este
  módulo: no hay ninguna referencia entre sus sitios (`0x4390xxxx`) y `Stage_Adjust.cpp`.
- El módulo `[ADJ]` (24 cadenas, `0x43c26dc1`–`0x43c2720d`) es **otro** cosa: es el ajuste
  **de audio/ADF** (`[ADJ]AdfSenserCtrl::SetParamSetMicMode err %x`,
  `[ADJ]ADJ_CMD_AVBB_ADF_AUD_VOLUME`). No confundir con `[CAM_UTIL_ADJ]`.

---

## 6. Relación con los módulos ya documentados

Vecindario de código (banda `0x43900000`–`0x43910000`, recuento de cadenas por prefijo):

| prefijo | cadenas | funciones |
|---|---|---|
| `(sin etiqueta)` | 274 | 100+ |
| `[CAM_DMM]` (S113) | 54 | 14 |
| `[CAM_UTIL_SENS]` | 39 | 5 (`0x439012d0`, `0x43901d50`, `0x43902168`, `0x439023b8`, `0x43902418`) |
| **`[CAM_UTIL_ADJ]`** | **22** | **3** |
| `[CAM_UTIL]` | 7 | 5 |
| `[ZPD]` | 5 | 4 |
| `[CAMERA_ADJ]` | 3 | 3 (`0x43900d54`, `0x43900e30`, `0x43900f1c`) |

- **`[CAM_UTIL_SENS]`** — hermano directo. Es el que gestiona los ficheros de **memoria
  interna del sensor** («Debug IM ASync Open», `[FileNum]%04x [Adr]%x [Size]%x`,
  `SET FILE NUM Func`, `UTIL MS Mgr) Call CB`). `[CAM_UTIL_ADJ]` **consume** esos ficheros:
  la función `0x439023b8` (`[CAM_UTIL_SENS] UTIL MS Mgr) Call CB`) es llamada directamente
  desde `tsk_cam_adjctrl` (`0x43900c9c`) cuando el código de comando es `0`.
- **`[CAMERA_ADJ]`** — 3 trazas, funciones inmediatamente posteriores a las de este módulo
  (`0x43900d54` «Utility Adjust Ctrl OSAL MEM ALLOC Error», `0x43900e30` «Utility MS Mount
  Start…», `0x43900f1c` «Utility MS UnMount Start…»): es la capa de **montaje/desmontaje del
  servicio de ajuste** (`MS` = el gestor de *mount*), que se apoya en `[CAM_UTIL_ADJ]`.
- **`[CAM_UTIL]`** — el módulo padre (log genérico, `AV DDS Alloc Msg Err`, `EvtDrvnTsk`,
  `osal_try_valloc_msg`); el log de `0x43900728` pertenece a esta familia.
- **`[CAMERA_MAIN]` (S126), `[CAMERA_MAIN_LC]` (S127), `[CAMERA_MAIN_CC]` (S123)** — sin
  relación de código verificada: las 3 funciones de `[CAM_UTIL_ADJ]` solo llaman a
  ayudantes locales (`0x4390xxxx`), a OSAL (`0x43561260/0x435612d0/0x435612ec/0x4356120c`)
  y a utilidades de memoria (`0x439c5320`, `0x439c5a04`).
- **`[IMAGING_CAP]` (S106)** — relación **de transporte, no de código**: el código de resultado
  `Sens:AdjCmd CAIF` (`0x43c90020`, cmd `0x04020180`) indica que el comando de ajuste viaja
  por el canal CAIF, que es el mismo transporte que usa la línea de captura
  (`CaifCom_Control.cpp`, `0x43ca8e14`).
- **`[VDF]`/`[VEF]` (S86), `[CLK_CTRL]` (S132)** — sin relación verificable.

---

## 7. Interés para la línea del obturador (iris / ISO / shutter / lectura del sensor)

**Veredicto: el módulo NO toca tiempos de obturación, iris, ISO ni la lectura de imagen.**

Criterio y evidencia:

1. **Ninguna de las 22 trazas** menciona obturador, iris, ISO, WB, exposición ni lectura de
   imagen. El vocabulario completo del módulo es: tabla, lectura/escritura, `Module ID`,
   `Offset`, `Size`, `D0`–`D7`, `CmdCode`, `DataSize`, `BDataSize`, `StepNum`, `ResCode`.
2. **Ninguna de las 3 funciones** llama a una API de obturador/iris/ISO. Sus únicos destinos de
   llamada (extraídos con el decodificador `bl`/`blx` de 32 bits) son:
   - `0x439007b0` → `0x43900728` (log) y `0x43b2a0ce` (error); copias con `blx 0x439c5320`.
   - `0x43900a24` → `0x43900728` (log), `0x439009f0`, `0x439009c8`, `0x43b2a0ce`; copia con
     `blx 0x439c5320` y despacho con `blx r5` (manejador de la tabla de §4).
   - `0x43900c44` → `0x43561260` (recibir mensaje OSAL), `0x435612ec` (liberar mensaje),
     `0x43900728` (log), `0x439009f0`, `0x439009c8`, `0x43900c1c`, `0x439023b8`
     (`[CAM_UTIL_SENS]`), `0x439008cc`; limpieza con `blx 0x439c5a04`.
   Ni una sola de esas direcciones pertenece a una API de obturación, iris o ISO.
3. Lo que **sí** hace es escribir/leer **tablas arbitrarias** en la RAM del sensor
   (`Senser RAM Access`, `Table Write`, `Table Read`, `Sens:RAM Write` `0x04000188`,
   `Sens:RAM Read` `0x04020189`). El módulo **no sabe** qué calibración contiene cada tabla:
   solo reenvía `Module ID` + `Offset` + `Size` + 8 bytes. Qué `Module ID` corresponde a iris,
   ISO, obturación o WB está decidido **fuera** de este módulo → **NO VERIFICADO aquí**.
4. Por tanto, en un cuerpo con más funciones, esta es una vía **genérica de escritura de
   calibración en el sensor**, pero **no** el punto donde se materializaría un «Silent»/EFCS:
   ese efecto, si existe, estaría en el control de exposición (`[IMAGING_CAP]`, S106) o en los
   parámetros de disparo, no en la escritura de tablas de calibración.

---

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 8.1 La etiqueta `[CAM_UTIL_ADJ]` es **propia de la A6000 fw3.21**

| marcador | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_UTIL_ADJ]` | 22 | **0** | **0** |
| interiores de las 22 trazas presentes | 22/22 | **0/22** | **0/22** |
| `tsk_cam_adjctrl` | 3 | 0 | 0 |
| `cam_adjcmd_handle_cb` | 1 | 0 | 0 |
| `SensRamAcs` | 2 | 0 | 0 |
| `Senser RAM Access` | 1 | 0 | 0 |
| `-- Table Write` / `-- Table Read` | 1 / 1 | 0 / 0 | 0 / 0 |
| `OriginalCmdCode` / `OriginalDataSize` / `OriginalBDataSize` | 1 / 1 / 1 | 0 / 0 / 0 | 0 / 0 |
| `Finish SENSER Infra Call Back Operation` | 1 | 0 | 0 |
| prefijo `[CAM_UTIL]` | 10 | **0** | **0** |
| prefijo `[CAM_UTIL_SENS]` | 21 | **0** | **0** |
| prefijo `[CAMERA_ADJ]` | 3 | **0** | **0** |

(Confirmado también por S130, que ya había visto que el token no aparece ni una vez en A7S ni
en A6300; aquí se añade el barrido de los marcadores auxiliares y de los otros prefijos.)

### 8.2 Pero la **capa de comandos «Sens» es común a los tres firmwares**

Es el resultado más importante del diferencial y corrige la lectura «nuevo en A6000»:

- Las **27** cadenas `Sens:*` (`Sens:BkWrPoffAsync`, `Sens:BkSyncCb`, `Sens:AdjCmd CAIF`,
  `Sens:Invalid block/code/offset/size`, `Sens:Read only`, `Sens:Write only`, `Sens:no buf`,
  `Sens:RAM Write`, `Sens:RAM Read`, `Sens:AdjCmd DwnCamera`, `Sens:System error`,
  `Sens:DwnCamera Done`, …) existen **con texto idéntico** en los tres firmwares
  (27 / 27 / 27).
- La **tabla de códigos de comando** `{cmd u32, size u32, str_ptr u32}` (12 B por entrada) que
  las indexa está presente en los tres: **51 entradas** en los tres, con los **mismos `cmd`
  y los mismos `size`**, desde `0x0400015d` hasta `0x0400018f`.
  - A6000: vaddr de la tabla `0x43fe858c` (offset `0xaa758c`).
  - A7S fw3.20: offset `0xaabb60`; A6300 fw2.01: offset `0xc6c230`.
  - Entradas clave (idénticas en los tres): `Sens:AdjCmd CAIF` = `0x04020180` (size 12),
    `Sens:RAM Write` = `0x04000188` (size 1), `Sens:RAM Read` = `0x04020189` (size 1),
    `Sens:AdjCmd DwnCamera` = `0x0400018a` (size 12), `Sens:DwnCamera Done` = `0x0400018c`.
  - Única diferencia de texto en la tabla: el cmd `0x04000167` es `Reserved` en la A6000 y
    `POFF return` en A7S y A6300.
- **Consecuencia**: la *funcionalidad* (escritura/lectura de tablas de calibración en la RAM del
  sensor, descarga de calibración a la cámara) **ya existía** en los otros dos cuerpos; lo
  **nuevo en la A6000 fw3.21** es la capa de *logging/diagnóstico* con la etiqueta
  `[CAM_UTIL_ADJ]` (y las etiquetas hermanas `[CAM_UTIL]`, `[CAM_UTIL_SENS]`, `[CAMERA_ADJ]`),
  es decir, **instrumentación**, no una función nueva.
  Corolario: la A6000 es un cuerpo con **más funciones de diagnóstico** en el subsistema de
  ajuste, pero el subsistema en sí no es exclusivo suyo.

### 8.3 Hallazgo colateral: la convención de vaddr de A7S y A6300

Los punteros de cadena de la tabla «Sens» de A7S (`0x43c98acf` → offset `0x757acf`) y de A6300
(`0x43d98993` → offset `0x857993`) resuelven exactamente al texto esperado con
`vaddr = 0x43541000 + file_offset`, **igual que la A6000**. Es decir, la convención
`0x43541000 + offset` es válida también para los `av-cam.bin` de A7S fw3.20 y A6300 fw2.01
(verificado en 3 punteros por firmware, con el texto resuelto byte a byte).

---

## 9. NO VERIFICADO / abierto

1. **Fichero fuente propio del módulo**: no consta. Ningún `.cpp`/`.h` es referenciado desde
   `0x439007b0`–`0x43900d30`. La pertenencia a la familia `amSens*` es **inferencia**.
2. **Significado de `Module ID`** (valor `r5`, semivariable `+0x1e`): el log lo rotula así y
   además **selecciona la operación** (0/1/2), pero **no se ha identificado qué tabla de
   calibración corresponde a qué identificador**, ni si alguno es iris, ISO, shutter o WB.
   **NO VERIFICADO** en este hito.
3. **Significado de los ids OSAL** `0x008f013a` (destino) y de la plantilla
   `{0x00e200e1, 0x00e400e3, 0x00e600e5}` (`0x43c04d70`): no decodificados. **NO VERIFICADO**.
4. **Índices 0 y 2** de la tabla de despacho `0x440121f8`: implementados como stub «no
   soportado»; qué operaciones recordings corresponden **NO VERIFICADO**.
5. **`[CAMERA_ADJ]`** (3 trazas, `0x43900d54`, `0x43900e30`, `0x43900f1c`): no documentado en
   este hito; su relación con `[CAM_UTIL_ADJ]` es de vecindad y de nombre («Utility Adjust
   Ctrl», «Utility MS Mount/UnMount Start»), no de llamada verificada.
6. **Qué es «MS»** en `[CAM_UTIL_SENS] UTIL MS Mgr` / `[CAMERA_ADJ] Utility MS Mount Start`:
   no se desarrolla la sigla (sin base textual suficiente).
7. **Qué es «Senser»**: el firmware escribe literalmente «Senser RAM Access» y «SENSER Infra
   Call Back Operation»; se conserva la grafía del firmware **sin desarrollar la sigla**.
8. **La cadena `[CAM_UTIL_ADJ]` aparece en 22 cadenas pero el bloque de texto del módulo está
   precedido por `[CAM_UTIL]: AV DDS …` (`0x43ccdcaa`) y seguido por `[CAM_UTIL_SENS]`
   (`0x43cce1ea`)**: el orden de los prefijos en el *pool* de texto no implica jerarquía de
   módulos (es el orden de compilación). No se infiere jerarquía.
9. **Convenciones de vaddr de A7S/A6300**: verificadas sólo para los punteros de la tabla
   «Sens» (3 por firmware); no se ha auditado el resto de esos binarios.

---

## 10. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (30 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 22 apariciones de `[CAM_UTIL_ADJ]` en la A6000 fw3.21 entre `0x43ccdcee` y
   `0x43cce0f2`; **0** en la A7S fw3.20 y el A6300 fw2.01 (comprobado también para `[CAM_UTIL_SENS]`
   21/0/0, `[CAM_UTIL]` 10/0/0 y `[CAMERA_ADJ]` 3/0/0) → la etiqueta es **propia de la fw3.21**.
2. **El hallazgo de fondo, verificado**: la **capa de comandos «Sens» es común a los tres firmware**
   (27 cadenas `Sens:*` y `Sens:AdjCmd CAIF` / `Sens:RAM Write` / `Sens:RAM Read` presentes 1/1/1),
   con la **tabla de 51 entradas** de 12 B (`{cmd,size,str}`) en `0x43fe858c` → lo nuevo en la
   A6000 es la **instrumentación** (`[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]`, `[CAM_UTIL]`,
   `[CAMERA_ADJ]`), **no** la función.
3. **Estructura**: 22 sitios (1 por cadena) en **3 funciones** (`0x439007b0`–`0x439008ac` Table
   Write/Read; `0x43900a24`–`0x43900bde` `cam_adjcmd_handle_cb()`; `0x43900c44`–`0x43900d30`
   `tsk_cam_adjctrl`), tabla de despacho en `0x440121f8` (idx 1 → `0x439007b0`; idx 0 y 2 → stub
   `0x43b2a0b8`, o sea **1 de 3 operaciones implementada**) y puntero de callback `0x43900a25`
   registrado en `0x4401f7a4`.
4. **Negativo acotado para la línea del obturador**: ninguna de las 22 trazas nombra obturación, iris,
   ISO ni lectura de sensor, y los únicos destinos de llamada son log, OSAL, `[CAM_UTIL_SENS]` y
   memcpy/memset → es una **vía genérica de escritura de calibración en la RAM del sensor**, no el
   punto de materialización de un Silent/EFCS → **sin efecto en S51**.
5. **Colateral útil y reutilizable**: la convención **vaddr = 0x43541000 + offset** también vale
   para la A7S fw3.20 y el A6300 fw2.01, verificado mediante los punteros de la tabla `Sens` →
   confirmado con **otro** par de blobs, lo que refuerza la convención del repo.
