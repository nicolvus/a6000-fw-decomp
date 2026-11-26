# film-pb-1 — Montaje del volumen y carga del IFO MP4: por qué falla y qué condición exacta lo impide

Fecha: 2026-11-26 · Fuente analizada: `libmpr.so` (fw 3.21, `0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`,
ELF32 ARM, stripped, 10.321.204 B) · Evidencia de campo: anillo MPR del dump `ram-servicio-20261020`
(VA `0x82DF9300-0x82DFC400`) ya extraído en `reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt`.

Todo lo que sigue sale de bytes del binario (desensamblado con capstone Thumb-2) y del anillo.
Nada se ha ejecutado: sin firmware, sin cámara, solo lectura.

---

## Resumen (20 líneas)

1. Las cinco cadenas pedidas existen **solo** en `libmpr.so` y salen de cinco funciones distintas, todas identificadas por VA.
2. `MountCmd : Flash Mount Error` lo emite `AviMMgrCmd::MountCmd` (`0x626DB8`, copia gemela con *driveLetter* en `0x627020`)
   en `0x626F18`/`0x626F1C`, y solo desde un bloque de error común (`0x626F08`).
3. `GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted` (`0x625C7A`) se dispara cuando `[this+8]->vtbl[0x140]()` devuelve **0**
   (dispositivo no montado) y registra `0x31000007`.
4. `FlashLoadMp4 : CreateAndLoad Error` (`0x627C86`) se dispara cuando `MMgrMp4IfoAcsr::CreateAndLoad` (`0x67CA6C`) devuelve ≠ 0;
   registra `0x31000006` en la línea 13247.
5. `Err RcsBackupTblData` (`0x823999`, impreso en `0x3AFB2C`) se dispara cuando `RcsBackupTblData()` (`0x35EA1C`) devuelve un
   código con cabecera `0x10` (`(r0 & 0xFF000000) == 0x10000000`), y **no** activa el flag de salvage: solo loguea.
6. `CheckSalvageStatus` (`0x90A075`) es el nombre que `MMgrAvcHdIfoAcsr::CheckSalvageStatus` (`0x671DAC`) pasa al registro MMGR
   en la línea 791 cuando `hdAvcIfo_If::CheckSalvageStatus` (`0x5AD53C`) devuelve error.
7. Los códigos están resueltos por tablas del propio binario: `0x31000006 = ER_CMD_CONFLICT`, `0x31000007 = ER_INTERNAL`
   (tabla `{nombre,código}` MMgrGlobal en `0x8F6CA8`), `0x32400001 = ER_FAILED` (mapper AVI `0x1DA818`),
   `0xB0800001` = fallo genérico de mp4Ifo (traductor `0x6F0D4C`), `0xA0100003` = fallo de comando HD-AVC.
8. Orden real: `GetDeviceInfo`/`MountCmd` (estado del dispositivo + DFS) → `CheckSalvageStatus` (IFO) → `FlashLoad*`
   (gate de estado `0x64C298` con `state==4`) → `CreateAndLoad` → `CreateSub` → `LoadSub` → `Load` → `mp4Ifo_General::Load`
   → `FlashLoadForMsv` → `RcsBackupTblData` (lectura real del volumen).
9. Lo primero que puede fallar es la comprobación de estado del dispositivo (`[this+8]->vtbl[0x140]`), antes de tocar el IFO.
10. `0xB0800001` y `0x31000006` son **códigos por defecto**: no identifican la causa, solo dicen "el subsistema falló".
    El único testigo de la causa real en el anillo es la línea `Err RcsBackupTblData`, que delata un error de E/S (`0x10xxxxxx`).
11. Con tarjeta presente y legible el IFO tampoco carga si el gate de estado no da `4` (`ER_SEQUENCE` + `0x31000007`) o si
    `RcsBackupTblData` falla; en ese segundo caso el código impreso **deja de ser** el genérico y pasa a ser uno específico
    (`0xB0400005`, `0xB0510001`, `0xB0F30001`…), que es lo que distingue "IFO corrupto" de "volumen ilegible".

---

## 1. Localización de los literales y función emisora

| # | Literal (VA en `.rodata`) | Instrucción que lo carga | Impresión | Función emisora (VA) |
|---|---|---|---|---|
| 1 | `"MountCmd : Flash Mount Error \n"` `0x8EA305` | `00626f18 ldr r1,[pc,#0xf8]` | `00626f1c bl 0x650742` | `AviMMgrCmd::MountCmd` `0x626DB8` |
| 1b | idem | `00627204 ldr r1,[pc,#0xf4]` | `00627208 bl 0x650742` | `AviMMgrCmd::MountCmd(driveLetter)` `0x627020` |
| 2 | `"GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted"` `0x8E9EAA` | `00625c7a ldr r1,[pc,#0x230]` | `00625c7c bl 0x650742` | `AviMMgrCmd::GetDeviceInfo` `0x625C4C` |
| 3 | `"FlashLoadMp4 : CreateAndLoad Error"` `0x8EA6B8` | `00627c86 ldr r1,[pc,#0x7c]` | `00627c8e bl 0x650742` | `AviMMgrCmd::FlashLoadMp4` `0x627BEC` |
| 4 | `"Err RcsBackupTblData"` `0x823999` | `003afb2c ldr r1,[pc,#0xa0]` | `003afb38 bl 0x3536dc` | llamante MSV de `RcsBackupTblData` `0x3AFA94` |
| 4b | idem | `003abe28 ldr r1,[pc,#0xa0]` | `003abe34 bl 0x3536dc` | gemela DCF `0x3ABE28` |
| 4c | idem | `0037c0ce` / `0037c17a` | — | otras dos copias (`0x37C0xx`) |
| 5 | `"CheckSalvageStatus"` `0x90A075` | `00671dc0 ldr r5,[pc,#0xe4]` | `00671e94 str r5,[sp,#4]` | `MMgrAvcHdIfoAcsr::CheckSalvageStatus` `0x671DAC` |
| 6 | `"LoadSub : MP4 Load Error."` `0x90D3FE` | `0067c922 ldr r1,[pc,#0x90]` | `0067c926 bl 0x650742` | `MMgrMp4IfoAcsr::LoadSub` `0x67C8CC` |

Nota: **no existe** la cadena `"LoadSub : %s Load Error."`. Hay una por tipo de contenido, en `.rodata` de
`mmgrifoacsr/`:

| Literal | VA |
|---|---|
| `LoadSub : MP4 Load Error.` | `0x90D3FE` |
| `LoadSub : AVCHD IFO Load() Error.` | `0x90ABB5` |
| `LoadSub : XAVC Load Error.` | `0x90E192` |
| `LoadSub : DVAVI Load Error.` | `0x90BC69` |
| `LoadSub : M2PS Load Error.` | `0x90CD9E` |
| `LoadSub : WAV Load Error.` | `0x90D8A9` |

Los nombres de función que el registro MMGR imprime (`(2319) LoadSub()`, `(246) CreateAndLoad()`, `(13247) FlashLoadMp4()`)
son literales compartidos y por eso el *linker* los fusionó: `"LoadSub"` `0x90D5FB`, `"Load"` `0x90D53C`,
`"CreateAndLoad"` `0x90D0DC`, `"LoadExec"`, `"FlashLoadMp4"` `0x8ED0AB`, `"MountCmd"` `0x8E7A76` y `0x8ECFF7`,
`"GetDeviceInfo"` `0x8E79D7`, `"FlashMount"` `0x8E7A0B`. Los ficheros: `avimmgr/AviMMgrCmd.cpp` `0x8E7F72`,
`mmgrifoacsr/MMgrMp4IfoAcsr.cpp` `0x90D18C`, `mmgrifoacsr/MMgrAvcHdIfoAcsr.cpp` `0x8F6798`, `IF/mp4Ifo_General.cpp` `0x91443D`.

---

## 2. Condición exacta de cada punto

### 2.1 `MountCmd : Flash Mount Error` — `AviMMgrCmd::MountCmd` `0x626DB8`

Cabecera de la función (todas las comprobaciones que pueden llevar al error):

```
00626dfc  ldr  r0,[r4,#8]            ; r0 = gestor de dispositivo [this+8]
00626dfe  ldr  r3,[r0]
00626e00  ldr.w r3,[r3,#0x140]       ; vtbl[0x140]
00626e04  blx  r3                    ; (bool) "dispositivo montado/presente"
00626e06  cbnz r0,#0x626e14          ; !=0 -> saltar el montaje
00626e08  mov  r0,r4
00626e0a  bl   0x62684c              ; FlashMount(this)  -> código
00626e0e  mov  r2,r0
00626e10  cmp  r0,#0
00626e12  bne  0x626eca              ; si error -> tratar
00626e14  mov  r0,r6                 ; r6 = this+0x86C
00626e16  bl   0x609d80              ; [blk+4]!=0 && [blk+0x10]!=0
...
00626e28  ldr  r0,[r4,#8]            ; vtbl[0x168]
00626e32  ldrb.w r3,[r4,#0x86a]      ; r3 = "bNeedSalvage"
00626e38  cmp  r0,#0 ; beq 0x626e9a
00626e9a  cbz  r3,0x626ebe           ; sin salvage -> "FlashMount->OK."
00626e9c  (log "MountCmd : FlashMount->OK.PullOutMedia. ")
00626ea6  bl   0x62549c
00626eba  ldr  r2,=0x31000002        ; ER_INVALID_PARAM
00626ebc  b   0x626f08               ;  <-- bloque de error
```

Y el bloque de error, único punto del literal:

```
00626f08  ldr  r0,[r4,#4]            ; registro MMGR, línea 783 (0x30f)
00626f0c  movw r3,#0x30f
00626f10  bl   0x64fad2
00626f14  ldr  r3,=0x9df25a          ; byte de nivel de log
00626f16  ldr  r0,[r4,#0xc]
00626f18  ldr  r1,="MountCmd : Flash Mount Error \n"
00626f1a  ldrb r2,[r3]
00626f1c  bl   0x650742              ; *** la línea del anillo ***
00626f20  mov  r0,r4
00626f22  bl   0x625f7c              ; intento de recuperación -> código en r6
00626f26  mov  r6,r0
00626f28  cbnz r0,0x626f3c
```

**Condiciones que llevan a `0x626F08`** (las dos únicas):

| Vía | Instrucción | Condición |
|---|---|---|
| (A) fallo del montaje | `00626e12 bne 0x626eca` → `00626ecc cmp r0,#0x31001001` → `00626ece bne 0x626f08` | `FlashMount()` devuelve ≠ 0 **y** ≠ `0x31001001` (`ER_DIFFERENT_DEVICE_TYPE`, que se tolera) |
| (B) post-montaje | `00626e9a cbz r3,0x626ebe` | `r0` de `vtbl[0x168]` **== 0** y `[this+0x86A] != 0` → `r2 = 0x31000002` (`ER_INVALID_PARAM`) |

La copia con *driveLetter* (`0x627020`) es idéntica salvo que paramétrica por letra de unidad (imprime
`"driveletter = [%s]"` en `0x627058`) y emite el mismo literal en `0x627204` con el mismo bloque de error (`0x6271F4`,
línea `0x203` = 515).

`FlashMount` (`0x62684C`) es quien monta de verdad:

```
00626872  ldr  r0,[r4,#8]  ; vtbl[8]  -> preparación
0062687c  ldr.w r0,[r4,#0x728]        ; objeto DFS
00626880  bl   0x3bb220               ; *** DFS mount ("###GRecMount IN###") ***
00626886  cbz  r0,0x6268c2            ; 0 = OK
006268a0  (log "FlashMount : FileSystem Mount Error")   ; 0x6268A0
006268c2  [this+8]->vtbl[0x60](1)     ; marca montado
006268d6  bl   0x625c4c               ; GetDeviceInfo
006268e2  bl   0x3bb438               ; post-montaje DFS
00626960  bl   0x64c5dc              ; [this+0x157] = 4   <-- estado "montado" (this+0x140 = 4)
0062696a  (log "FlashMount : FileSystem Flash Mount Success.")
```

### 2.2 `GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted` — `AviMMgrCmd::GetDeviceInfo` `0x625C4C`

```
00625c58  ldr  r0,[r0,#8]
00625c5c  ldr  r3,[r0]
00625c5e  ldr.w r3,[r3,#0x140]       ; vtbl[0x140]  (mismo predicado que en MountCmd)
00625c62  blx  r3
00625c64  mov  r5,r0
00625c66  cbnz r0,0x625c9e           ; !=0 -> seguir leyendo el device info
00625c68  movs r3,#0xff
00625c6a  str.w r3,[r8]              ; *pDeviceType = 0xFF
00625c74  str.w r6,[sb]              ; *pbUnmounted = 1
00625c7a  ldr  r1,="GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted"
00625c7c  bl   0x650742              ; *** la línea del anillo ***
00625c80  ldr  r3,="GetDeviceInfo"
00625c86  ldr  r2,=0x31000007        ; ER_INTERNAL
00625c8a  movw r3,#0x315b            ; línea 12635
00625c98  bl   0x64e27c              ; ## ERROR(MMGR):0x31000007 ## avimmgr/AviMMgrCmd.cpp(12635) GetDeviceInfo()
```

**Condición**: `[this+8]->vtbl[0x140]() == 0`. Código registrado: `0x31000007`.
En el anillo la llamada llega desde `SetSalvageResultInfo` (`0x609D98`, `bl 0x625c4c` en `0x609DC8`), después de fallar
la carga del IFO XAVC.

### 2.3 `FlashLoadMp4 : CreateAndLoad Error` — `AviMMgrCmd::FlashLoadMp4` `0x627BEC`

```
00627c00  (log "FlashLoadMp4 : Started")
00627c06  mov  r0,r4
00627c08  movs r1,#4
00627c0c  bl   0x64c298              ; gate: estado AVI admitido
00627c10  cbnz r0,0x627c48           ; !=0 -> continuar
00627c16  (log "FlashLoadMp4 : ER_SEQUENCE")     ; 0x627C16
00627c24  ldr  r2,=0x31000007 ; línea 0x3394/0x3395 (13204/13205)
...
00627c48  ldr  r0,[r4,#8] ; vtbl[0x74](0)
00627c56  ldr.w r0,[r4,#0x780]       ; objeto MMgrMp4IfoAcsr
00627c5a  mov  r1,sb                 ; loadType
00627c5c  movs r2,#1                 ; bFlashLoad = 1
00627c60  bl   0x67ca6c             ; *** MMgrMp4IfoAcsr::CreateAndLoad ***
00627c64  mov  r5,r0
00627c66  cbnz r0,0x627c7e           ; !=0 -> error
00627c86  ldr  r1,="FlashLoadMp4 : CreateAndLoad Error"
00627c8e  bl   0x650742             ; *** la línea del anillo ***
00627cc2  movw r3,#0x33bf           ; línea 13247
00627cd0  mov  r2,r5
00627cdc  bl   0x64e27c             ; ## ERROR(MMGR):<código> ## avimmgr/AviMMgrCmd.cpp(13247) FlashLoadMp4()
```

**Condición**: `CreateAndLoad(this+0x780, loadType, bFlashLoad=1)` devuelve ≠ 0.
Gate previo (`0x64C298`, ver §4): si falla, el mensaje es el otro (`"FlashLoadMp4 : ER_SEQUENCE"`, `0x31000007`)
y **no** se llega a `CreateAndLoad`; en el anillo no aparece, luego el gate pasó.

### 2.4 `Err RcsBackupTblData` — llamante MSV de `RcsBackupTblData` `0x3AFA94`

```
003afaee  str  r3,[sp,#0x10]         ; 7 punteros de salida
003afaf6  bl   0x35ea1c             ; *** RcsBackupTblData() ***  (imprime "RcsBackupTblData Start")
003afafa  mov  r6,r0
003afafc  cbz  r0,0x3afb44           ; 0 = leído
003afafe  and  r3,r0,#0xff000000     ; cabecera del código
003afb06  cmp.w r3,#0x10000000
003afb0a  beq  0x3afb28
003afb0c  ... (log " Need Salvage"; [obj+0x44] = 1)   ; cabecera != 0x10 -> marca salvage
003afb28  ldr  r0,[r4,#0x38]
003afb2c  ldr  r1,="Err RcsBackupTblData"
003afb38  bl   0x3536dc             ; *** la línea del anillo ***
003afb3c  ... (libera y sigue; r6 conserva el código de error)
```

**Condición exacta**: `RcsBackupTblData() != 0` **y** `(código & 0xFF000000) == 0x10000000`.
Es decir: fallo de E/S del servicio de ficheros, no corrupción lógica. **No** activa el flag `[obj+0x44]`
(salvage); el otro camino sí. `0x3AFA94` devuelve ese mismo código, y es lo que el wrapper de
`mp4Ifo_General::FlashLoadForMsv` convierte en `0xB0800001` (§3).

### 2.5 `CheckSalvageStatus` — `MMgrAvcHdIfoAcsr::CheckSalvageStatus` `0x671DAC`

```
00671dbe  ldr  r6,="mmgrifoacsr/MMgrAvcHdIfoAcsr.cpp"
00671dc0  ldr  r5,="CheckSalvageStatus"
00671dc2  ldr  r3,[r0,#0xc] ; vtbl[0xf4]  -> estado AVI (0..6)
00671dca  cmp  r0,#6 ; bhi -> salir sin salvage
00671dd0  lsls r0,r3,r0
00671dd4  tst.w r0,#0x5c            ; estados {2,3,4,6} = NEED_SALVAGE / ORG_RESCUE / BAK_RESCUE / UPDATE
00671dd8  beq  0x671de8             ; fuera de esos estados -> return 0
00671de6  b    0x671e06             ; vtbl[0x144]!=0 -> "AVCHD already created."
00671e38  ldr  r3,[r4,#0x3c]        ; handle IFO
00671e46  bl   0x5ad53c             ; hdAvcIfo_If::CheckSalvageStatus(cmd 0x4E)
00671e52  mov  r10,r0
00671e86  mov  r0,r4 ; r1=0x194 ; r2=r10 ; r3=0x317 (791)
00671e96  bl   0x677b8e             ; ## ERROR(HDAVCIFO):<r10> ## mmgrifoacsr/MMgrAvcHdIfoAcsr.cpp(791) CheckSalvageStatus()
```

**Condición**: estado AVI ∈ {2,3,4,6} **y** `vtbl[0x144]() == 0` **y** `hdAvcIfo_If::CheckSalvageStatus` (`0x5AD53C`)
devuelve ≠ 0 (`r10`). En el anillo `r10 = 0xA0100003`.

Origen de `0xA0100003` (cabecera `0xA0` = subsistema HD-AVC/AVCHD): en `0x520BFC` y `0x520C54`

```
00520be0  ldr  r3,=0x10100003
00520be2  cmp  r0,r3 ; beq -> 0xA0F2000C (timeout clasificado)
00520be6  cbnz r0,0x520bfc
00520bfc  ldr  r0,=0xA0100003        ; cualquier otro retorno != 0 de la capa de comando
```

y en `0x52031E`/`0x520314` la misma normalización sobre `0x2b4584`. El banner
`## HD-AVC COMMAND ERROR ##` (`0x52181C`, formato en `0x5210B8`) solo se imprime si el código **no** está en la lista
de códigos esperados de `0x5215AC` (`A0F30001, A0F2000B, A0620003, A0F20016, A0810006, A0510027, A0F2001D, A0F30003, A0F2001E`);
`0xA0100003` no está → banner, tal como aparece en el anillo.

---

## 3. Los cinco códigos, resueltos

Tabla `{nombre, código}` MMgrGlobal volcada del binario (`0x8F6CA8`, 53 entradas) — es la que usan los `## ERROR(MMGR)`
y la que fija el espacio `0x31xxxxxx`:

| Código | Nombre oficial | Nota |
|---|---|---|
| `0x31000001` | `MMgrGlobal::ER_OK` | |
| `0x31000002` | `MMgrGlobal::ER_INVALID_PARAM` | usado por `MountCmd` en la vía (B) |
| `0x31000003` | `MMgrGlobal::ER_FAILED` | |
| `0x31000004` | `MMgrGlobal::ER_DISABLED` | |
| `0x31000005` | `MMgrGlobal::ER_APP_FORMAT` | |
| **`0x31000006`** | **`MMgrGlobal::ER_CMD_CONFLICT`** | |
| **`0x31000007`** | **`MMgrGlobal::ER_INTERNAL`** | |
| `0x31000008` | `MMgrGlobal::ER_SEQUENCE` | |
| `0x31001001` | `MMgrGlobal::ER_DIFFERENT_DEVICE_TYPE` | tolerado por `MountCmd` |
| `0x31002003` | `MMgrGlobal::ER_DISC_CORRUPT` | |
| `0x3100200C` | `MMgrGlobal::ER_NOT_MOUNTED` | |

Resolución pedida:

| Código | Nombre / origen | Quién lo genera (VA) | Significado funcional |
|---|---|---|---|
| `0x31000006` | `ER_CMD_CONFLICT` | **rama por defecto** del traductor MMGR `0x64E300`: `0064ecec ldr r4,[pc,#0xe4]` → `[0x64edd4]=0x31000006`. Se toma cuando el código de subsistema no encaja en ninguna clase conocida (`0x0C…` ATA, `0x0E…` DFS, `0xA0…`/`0xB0…` IFO, etc.) | "conflicto de estado": el comando no procede con el estado actual del módulo. Como es el *default*, equivale a "error no clasificado" |
| `0x31000007` | `ER_INTERNAL` | `0x625C86` (`GetDeviceInfo` sin montar), `0x627C24`/`0x627C3E` (gate `ER_SEQUENCE` de `FlashLoadMp4`), `0x67B1AC` (handle IFO nulo), `0x633Bxx` (`GetNextCreateRecDirectoryNumber`) | precondición interna no cumplida: dispositivo sin montar, IFO sin handle, pasada de secuencia inválida |
| `0xB0800001` | fallo genérico de `mp4Ifo` (no hay tabla de nombres: se imprime numérico en `### mp4Ifo faild at … ErrCd:`) | wrapper `0x6F0D4C` invocado desde `0x698EEA` (`mp4Ifo_General::FlashLoadForMsv`, línea 1749). Ramas que dan ese valor: `006f0e40 beq 0x6f0ebc` (código `0xXX100000`) y `006f0ebc ldr r4,=0xB0800001` (default); también el "código del llamante" `r1=0xB0800001` en `006f0e96 mov r4,ip` | "la operación de mp4Ifo falló"; **no identifica causa** |
| `0xA0100003` | error de comando HD-AVC, cmd `0x4E` (CheckSalvageStatus) | `0x520BFC` / `0x520C54` / `0x52031E` / `0x56EE38` / `0x58ED72` / `0x593624` | el canal de comando al módulo HD-AVC devolvió error no clasificado (el único clasificado es `0x10100003` → `0xA0F2000C`) |
| `0x32400001` | `ER_FAILED` (AVI) | mapper `0x1DA818`: `001da86a subs r2,#1` (`0x32400002-1`), `001da86c cmp r0,r2`, `001da870 b 0x1da8a8`, `001da8a8 ldr r0,=0x902333 "ER_FAILED"`; el código se usa como retorno en todas las salidas de error de `AviSeqMedia` (`0x2159C4`, `0x2159DC`, `0x215A02`, `0x215A14` = línea 1637 …) | fallo genérico de la capa `avi_if` |

Códigos "vecinos" útiles como discriminante (§6): `0xB0200001`, `0xB0400001`, `0xB0400005`, `0xB0400006`, `0xB0510001`,
`0xB0810001`, `0xB0F30001`, `0x13500002`, `0x1380000A` (todos salen del mismo traductor `0x6F0D4C`).

---

## 4. Orden real de la cadena

```
(0) App -> MprIf: CBID_GET_PRE_FIRST_MOUNT_INFO            [anillo, errCd 0x00000000, 0 entradas]
      |
(1) AviMMgrCmd::GetDeviceInfo      0x625C4C
      [this+8]->vtbl[0x140]() == 0  -->  "DEVICE Unmounted" + 0x31000007 (linea 12635)
      |
(2) AviMMgrCmd::MountCmd           0x626DB8 / 0x627020
      [this+8]->vtbl[0x140]() == 0  -->  FlashMount 0x62684C
                                          [this+0x728] -> DFS mount 0x3BB220 ("###GRecMount IN###")
                                          OK -> vtbl[0x60](1); [this+0x140]=4 (0x64C5DC); GetDeviceInfo; MS-ID
      checks post-montaje: 0x609D80(this+0x86C), vtbl[0x168](), [this+0x86A] (bNeedSalvage)
      si no cuadra                   -->  "MountCmd : Flash Mount Error" (0x626F18) + 0x31000002
      |
(3) MMgrXxxIfoAcsr::CheckSalvageStatus      (AVCHD 0x671DAC, MP4 equivalente)
      estado AVI in {2,3,4,6} && vtbl[0x144]==0
      IFO CheckSalvageStatus 0x5AD53C  -->  error 0xA0100003  -->  linea 791
      |
(4) AviMMgrCmd::LoadExec --> FlashLoadXxx   (MP4: 0x627BEC)
      gate 0x64C298(this, 4):  state==4 && [this+0x148]==0 && [this+0x14C]==0
      si falla                        -->  "FlashLoadXxx : ER_SEQUENCE" + 0x31000007
      |
(5) MMgrMp4IfoAcsr::CreateAndLoad  0x67CA6C
      [this+0x48] != 0 -> "already created"
      CreateSub 0x67C5C4 -> [this+0x48]
      LoadSub 0x67C8CC
      error                           -->  linea 246 + 0x31000006  (codigo traducido)
      |
(6) MMgrMp4IfoAcsr::LoadSub        0x67C8CC
      codigo = [this+0x48]->Load(loadType, bFlashLoad)      (0x6E823C = mp4Ifo_If::Load)
      != 0 -> "LoadSub : MP4 Load Error." ; linea 2319 con el codigo
      |
(7) mp4Ifo_If::Load                0x6E823C  ->  vtbl[8]  ->  mp4Ifo_General::Load 0x698FB8
      device==1 -> DiscLoadForMsv  0x698E78   |  device==0 -> FlashLoadForMsv 0x698EC8
      |
(8) mp4Ifo_General::FlashLoadForMsv  0x698EC8
      bl 0x3AFA94  ->  RcsBackupTblData 0x35EA1C   (lectura REAL del volumen)
      error con cabecera 0x10 -> "Err RcsBackupTblData"
      wrapper 0x6F0D4C(codigo, 0xB0800001, "IF/mp4Ifo_General.cpp", 1749)
      |
(9) traduccion MMGR 0x64E300 -> default 0x31000006 -> "(246) CreateAndLoad()"
      AviMMgrCmd::FlashLoadMp4 0x627BEC -> "FlashLoadMp4 : CreateAndLoad Error" -> "(13247) FlashLoadMp4()"
```

**Precondiciones para que el IFO MP4 cargue** (todas obligatorias, en este orden):

1. `[this+8]->vtbl[0x140]() != 0` — el gestor de dispositivo considera el medio montado/presente.
2. `FlashMount` OK: `DFS mount` (`0x3BB220`) devuelve 0 **o** `0x31001001` (tipo distinto, tolerado).
3. Comprobaciones post-montaje coherentes: `0x609D80(this+0x86C) != 0` y el par `vtbl[0x168]()` / `bNeedSalvage` no cae en
   el caso "media fuera + salvage".
4. `state ([this+0x140]) == 4` y `[this+0x148] == 0` y `[this+0x14C] == 0` (gate `0x64C298` con máscara 4).
5. `CreateSub` OK (asigna/crea el IFO), `[this+0x48] != 0`.
6. `mp4Ifo` puede leer su tabla de respaldo: `RcsBackupTblData()` == 0 (o, al menos, código sin cabecera `0x10`… y aun así
   el error se propaga).
7. `mp4Ifo_General::Load` devuelve 0 → marca `[obj+0x23] = 1` ("cargado").

**Lo primero que puede fallar** es el paso 1 (predicado de dispositivo), y es el único que se evalúa **antes** de tocar
el IFO o el volumen: en el anillo aparece primero como `GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted` + `0x31000007`.

---

## 5. Conclusión

### 5.1 Si el volumen/tarjeta falta o no es legible

Secuencia exacta observada (y explicada por el código):

1. `DFS mount` de la unidad (`0x3BB220`, tras `pdeviceName : "/dev/mmca"`) no puede abrir/validar el volumen.
2. `AviMMgrCmd::MountCmd` acaba en `0x626F08` → `"MountCmd : Flash Mount Error "` (`0x626F18`) y, según la vía,
   `0x3100xxxx`/`0x31000002`.
3. `[this+8]->vtbl[0x140]()` queda a 0 → **cualquier** `GetDeviceInfo` posterior imprime
   `"GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted"` y registra `0x31000007` (`ER_INTERNAL`).
4. Las comprobaciones de salvage del IFO (AVCHD `0x671DAC`, MP4 homóloga) entran por el estado AVI ∈ {2,3,4,6} y llaman
   al IFO; el comando HD-AVC `0x4E` falla con `0xA0100003` (no clasificado) → banner `## HD-AVC COMMAND ERROR ##`
   y línea 791.
5. Los `Load()` de cada IFO fallan; `MMgrXxxIfoAcsr::LoadSub` devuelve el código del IFO y `CreateAndLoad` lo traduce al
   **genérico** `0x31000006` (`ER_CMD_CONFLICT`, rama por defecto).
6. En MP4 el punto exacto de la lectura fallida es `RcsBackupTblData` (`0x35EA1C`), que devuelve un código `0x10xxxxxx`
   (E/S): se imprime `"Err RcsBackupTblData"` y `mp4Ifo` lo normaliza a `0xB0800001` (línea 1749).
7. `AviMMgrCmd::FlashLoadMp4` imprime `"FlashLoadMp4 : CreateAndLoad Error"` y registra `(13247) 0x31000006`.
8. Efectos laterales coherentes en el mismo anillo: `StillCacheRead … dfs::seek errcode=0x0E100001`,
   `Failed to read errcd=0xC3000101` (fallos de DFS/DFS-cache al leer miniaturas).

**Firma** de este caso: cadena `0xB0800001`/`0xA0100003`/`0xB0800005` → **siempre** traducidos a `0x31000006`, es decir,
códigos *por defecto*. El binario solo emite códigos específicos cuando puede clasificar el fallo.

### 5.2 Si la tarjeta está presente y es legible: qué tendría que estar mal

| Hipótesis | Qué se vería en el anillo | Por qué (código) |
|---|---|---|
| **Estado AVI ≠ 4** (IFO no cargado, montaje nunca declarado, `[this+0x148]`/`[0x14C]` ocupados) | `FlashLoadMp4 : ER_SEQUENCE` + `(13204/13205) 0x31000007`; **no** habría `CreateAndLoad Error` | gate `0x64C298` con máscara 4: `0064c2d6 cmp r8,#4` / `0064c2dc cbnz r6` / `0064c2de cmp r4,#0` |
| **IFO/BD corrupto pero volumen legible** | `## ERROR(MMGR):0xB0400005 / 0xB0510001 / 0xB0F30001 / 0xB0400006##` en vez de `0xB0800001` | traductor `0x6F0D4C`: los grupos `0xXX04…`, `0xXX05…`, `0xXXF3…`, `0xXX81…` tienen código propio; solo `0xXX80…` y el default dan `0xB0800001` |
| **Tabla de respaldo ilegible aun con tarjeta "legible" en PC** | idéntico al caso 5.1 (`Err RcsBackupTblData` + `0xB0800001` + `0x31000006`) | `0x3AFAFE`: solo la cabecera `0x10` produce esa línea; una corrupción lógica daría `" Need Salvage"` y `[obj+0x44]=1` |
| **Fallo de asignación/creación del IFO** | `CreateAndLoad` ≠ 0 sin pasar por `LoadSub` (no habría `LoadSub : MP4 Load Error.`) | `0067caca mov fp,r0 ; cbnz r0,0x67caf0` tras `CreateSub 0x67C5C4` |
| **Tipo de dispositivo distinto** (`ER_DIFFERENT_DEVICE_TYPE`) | no es error: `MountCmd` lo tolera | `00626ecc cmp r0,#0x31001001` / `00626ece bne` |

En resumen: **con tarjeta sana el IFO solo puede dejar de cargar por estado** (gate `ER_SEQUENCE`) o por **fallo
clasificable** del propio IFO; el patrón `Err RcsBackupTblData → 0xB0800001 → 0x31000006` es la huella de que el
volumen **no era legible por DFS** en ese instante, no de que el MP4 estuviera corrupto.

---

## 6. Límites de esta conclusión (NO_VERIFICADO)

- **NO_VERIFICADO** — Que el estado leído en `[this+0xc]->vtbl[0xF4]()` (`MMgrAvcHdIfoAcsr::CheckSalvageStatus`) use el mismo
  enum que imprime `AviStatusInfo` (`0x1DA1EC`, `AVI_STATE_*`, 0…8). El valor encaja con la máscara `0x5C`
  ({2,3,4,6} = NEED_SALVAGE / NEED_ORG_RESCUE / NEED_BAK_RESCUE / NEED_UPDATE) pero no se ha resuelto la vtable.
- **NO_VERIFICADO** — Identidad semántica de las virtuales `vtbl[0x140]`, `vtbl[0x60]`, `vtbl[0x168]`, `vtbl[0xF4]`,
  `vtbl[0x144]`, `vtbl[0x74]`, `vtbl[0x88]`: se deducen del uso (`0x140` → 0 ⇒ "DEVICE Unmounted"; `0x60(1)` tras montar)
  pero la clase no tiene símbolos (binario *stripped*) y no se ha resuelto la vtable.
- **NO_VERIFICADO** — Cuál de las dos vías de `MountCmd` disparó la línea del anillo. Ambos caminos (A y B) usan el mismo
  literal y el anillo **no es una transcripción completa**: falta, por ejemplo, `"MountCmd : "` (`0x626DDC`), que se imprime
  al entrar en la función, y `"###GRecMount IN###"` (`0x3BB22E`), que se imprime en el propio `DFS mount`. Conclusión: la
  ausencia de las líneas `"FlashMount : …"` en el anillo **no** prueba que `FlashMount` no fallara.
- **NO_VERIFICADO** — Valor exacto del byte de nivel en `0x9DF25A`/`0x9DF25C` en el momento del fallo (está en `.data`,
  se fija en ejecución).
- **NO_VERIFICADO** — Semántica nominal del espacio `0x10xxxxxx` (códigos del servicio común de ficheros). Se ha verificado
  su uso (`0x3AFAFE` = "error de E/S" → `Err RcsBackupTblData`; `0x6F0E40` = familia `0x100000` → `0xB0800001`) y su
  presencia en fallos DFS (`0x0E100001` en StillCache), pero no existe tabla de nombres para esa cabecera en `libmpr.so`.
- **NO_VERIFICADO** — Cualquier valor en RAM de la sesión del 20-10-2026 salvo el propio anillo (no se ha leído memoria
  de proceso ni NVRAM en esta tarea).
- El anillo corresponde a una sesión con `/dev/ms` primero y conmutación a `/dev/mmca`; no se puede afirmar si la tarjeta
  estaba ausente, mal contactada o con el volumen dañado. Las tres producen la misma firma.

---

## 7. Evidencia

`reports/evidence/film-pb-1-sub-mount-ifo-20261126/` (regenerable con `extraer_evidencia.py`):

| Fichero | Contenido |
|---|---|
| `01-avimmgr-mountcmd.txt` | `AviMMgrCmd::MountCmd` `0x626DB8` (+0x1A0) |
| `02-avimmgr-mountcmd-driveletter.txt` | variante con `driveLetter` `0x627020` |
| `03-avimmgr-flashmount.txt` | `AviMMgrCmd::FlashMount` `0x62684C` (DFS mount, estado=4) |
| `04-avimmgr-getdeviceinfo.txt` | `AviMMgrCmd::GetDeviceInfo` `0x625C4C` |
| `05-avimmgr-flashloadmp4.txt` | `AviMMgrCmd::FlashLoadMp4` `0x627BEC` |
| `06-mmgr-createandload.txt` | `MMgrMp4IfoAcsr::CreateAndLoad` `0x67CA6C` (línea 246) |
| `07-mmgr-loadsub.txt` | `MMgrMp4IfoAcsr::LoadSub` `0x67C8CC` (línea 2319) |
| `08-mmgr-load.txt` | `MMgrMp4IfoAcsr::Load` `0x67C9C0` |
| `09-acsr-avchd-checksalvagestatus.txt` | `MMgrAvcHdIfoAcsr::CheckSalvageStatus` `0x671DAC` (línea 791) |
| `10-mp4ifo-flashloadformsv.txt` | `mp4Ifo_General::FlashLoadForMsv` `0x698EC8` (línea 1749) |
| `11-mp4ifo-checksalvagestatus.txt` | `mp4Ifo_General::CheckSalvageStatus` `0x698F18` (línea 1340) |
| `12-mp4ifo-load.txt` | `mp4Ifo_General::Load` `0x698FB8` (FLASH/DISC) |
| `13-msv-rcsbackuptbldata-caller.txt` | llamante de `RcsBackupTblData` `0x3AFA94` (`Err RcsBackupTblData`) |
| `14-gate-64c298.txt` | gate de estado `state==mask` |
| `15-tabla-mmgrglobal-errores.txt` | tabla `{nombre,código}` MMgrGlobal `0x8F6CA8` |
| `16-mapper-avi-1da818.txt` | `0x32xxxxxx` → nombre (`0x32400001` = `ER_FAILED`) |
| `17-enum-avi-state.txt` | enum `AVI_STATE_*` |
| `18-mp4ifo-traductor-*.txt` | traductor `0x6F0D4C` (ramas que dan `0xB0800001`) |
| `19-mmgr-logger-prefijos.txt` | prefijo por cabecera del código (`(DFS)`/`(HDAVCIFO)`/`(AVI)`/… ) |
| `20-mmgr-traductor-default.txt` | rama por defecto `0x31000006` |
| `extraer_evidencia.py` | regenera todo; `--dump` resume el anillo (SHA-256 verificado) |

Anillo de referencia (sin cambios): `reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt`,
SHA-256 del dump `f96c6152f697a8680f6d342cfdc0133bc28b8ab85a6baf48c19358546ff2fdbf`.
