# La grabación también falla al registrar: `m2psIfo_Backup` contra la tabla FBM

**Fecha:** 2026-11-26 · **Binario:** `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21; base ELF = VA, Thumb; sha256 en `evidence/grabacion-bd-fbm-20261126/sha256.txt`) · **Evidencia:** `reports/evidence/grabacion-bd-fbm-20261126/` (`dis/01…23`, `xrefs.txt`, `escritores-fn.txt`, scripts) · **Cámara no usada; sin `mcp_rea`; estático puro (capstone).**

## Resumen (18 líneas)

1. **DEMOSTRADO**: la grabación también falla al registrar en la BD FBM, y falla **en dos puntos distintos**, ninguno propagado.
2. El registro del clip lo hace `m2psIfo_Backup` con la clave **(userID 4, mediaID = [obj+0xC])** ⇒ sector FBM **0x31** (fila `(4,3)` de `0x9D23FC`).
3. `m2psIfo_rec::OpenRecFile` (`0x5E7A6C`) llama a `0x5CA0B4` en **`0x5E7B8C`** (al abrir el fichero de grabación) y **no guarda `r0`**: `0x5E7B90` recarga `r0` del objeto.
4. `m2psIfo_rec::CloseRecFile` (`0x5E7D28`) lo llama en **`0x5E7E50`** (al cerrar) y hace lo mismo (`0x5E7E54`); el `errorCode=` que imprime (`0x5E7E74`–`0x5E7E82`) y el retorno (`0x5E7E92 mov r0,r5`) son el resultado del paso **anterior** (`0x5E7D9C bl 0x3AD2E4`), no el de la escritura del backup.
5. `0x5CA0B4` primero **cambia de sector**: `0x5CA10E bl 0x5C9F48`; `0x5C9F7A ldr r1,[r4,#0xC]` / `0x5C9F7C movs r0,#4` / **`0x5C9F7E bl 0x2B41B4`** = `ChangeSector(4, mediaID)`.
6. `ChangeSector` (`0x2B41B4`) lee el handle con `0x2B3094` (`0x2B41D8`); si es 0 → **`0x2B41F4 ldr r4,=0x10100006`** («Source backup handle not found», `0x2B41EE`), sin crear nada; `0x5CA10A cbnz r4,0x5CA126` aborta la escritura.
7. Si el handle existiera, el registro sigue por `WritePackBegin` (`0x2B3D24`), que vuelve a sacar el handle de `0xA3699C[idx].+4` (`0x2B3D7C`–`0x2B3D8A`) y con 0 da **`0x2B3D90 ldr r5,=0x10100001`**.
8. Los otros escritores de la lista de contenidos (HDM, userID 0x21, `0x3AC880`/`0x3AC8F8`/`0x3AD15A`/…) van directos a `0x34E638` → `WritePackBegin` → **0x10100001**; en error hacen `cbz r0` y **siguen** (`0x3AC884`→`0x3536DC`).
9. `InitBackupData` (`0x2B43F0`) tiene **solo 5 llamantes**: consola `InitB` `0x2B5B5A` y los cuatro pedidos. **La grabación no está entre ellos**: no crea el sector cuando falla; sólo lo usan el arranque/montaje.
10. Los cuatro sitios y su OM/mediaID: `0x37FC06` y `0x37FD4C` = `InitBackupData(9,8)` (sector `0xA0`) dentro de dos lectores de la tabla BKUP; `0x38FEC4` = `InitBackupData(7, mediaID)` (`[DCF MCMD] InitBackUpTbl`); `0x61D94C` = `InitBackupData(OM(media), mediaID)` del gestor de medios.
11. Qué hacen con el error: los dos de BKUP **loguean** `"BKUP Err InitBackupData ec"` y **devuelven 0** (`0x37FC4E movs r0,#0`); el de DCF loguea y **devuelve 1**; el de `0x61D94C` **ni lo mira** (`0x61D950 b 0x61D984; 0x61D984 movs r0,#0`).
12. **Camino de reconstrucción: existe y no sirve para esto.** `Repair/BeginRepair` (consola `0x9002BA`) y el menú «Recuperar BD imág.» (`BeginRepair <AVINDEX>`, según `film-pb-1-sub-bd-tarjeta-20261128.md` §5.2) → `BeginRepairCmd` (`0x624xxx`) → `MMgrBackup[M2PS]`/`[MP4]` → `AviSeqRepair.cpp` (`0x23C5C0`), `0x7ADB13`, `CreateAVIndexFile` `0x7A7E7C`. Reescribe el índice **de la tarjeta** (`AVF_INFO/AVIN0001.INP`), no los sectores FBM.
13. Ningún camino de reparación llama a `0x2B43F0`/`0x2B4030` (los 5 llamantes son los del punto 9) ⇒ **no puede crear 0x31**; y su re-registro, si pasa por el IFO, choca otra vez en `0x5C9F7E`/`0x2B3D24` con los mismos códigos. Por eso «no cambia nada».
14. **Clip NUEVO tras crear 0x31: sí queda registrado (y se reproduce)**, *siempre que el arranque deje `handle≠0` en idx 10*: lo deciden `FBM::Init` `0x2B4820` (abre el sector), `0x2B3094` (handle) y `WritePackBegin` `0x2B3D24`; **`fn` no interviene** (`0x2B2F48` compara sólo `fileType`). Medido: con el sector creado **con página de datos base** el arranque lo registra (`2/30`, idx10 `h1/s1`; runs D y H); con un `CreateSector32` pelado **no** (`1/30`; run 5).
15. **Clip ANTIGUO: no queda registrado.** `CreateSector32` deja el sector vacío (`0xFF`); no hay código que rellene registros de clips ya grabados. Su lectura da `0x10100003` («sin datos»), que varias rutas **toleran** (`0x520C3C`, `0x35E0FC`, `0x37FBD2`, `0x37FD20`) ⇒ desaparece el error duro, pero el registro no existe: sólo podría salir del IFO primario de la tarjeta (no probado aquí).
16. Excepción útil: si el sector se crea con el **escritor real ya registrado**, `WriteBaseData` llama a `0x2B3F7C` → `fn(arg)` y `0x5CA294` construye el pack base con el IFO vivo (4×`0xA0` bytes, IDs `0xE2`/`0xE1` en `0x5CA328`/`0x5CA336`): eso **sí** dejaría dentro la lista actual.
17. **`LTC 1` no es la opción buena en la cámara real.** `0x2B55A0` imprime `[FBM]LocalTestCall::LTC_01` y registra escritores **dummy** `0x2B5724`/`0x2B5658` que escriben `"MS "/"HDD "/"UNKNOWN "+"packData"` (`0x2B574E`, `0x2B575A`); el escritor real de (4,3) es **`0x5CA354`** (cuerpo `0x5CA294`, `"@@@ Flash Backup BaseData Write EXEC @@@"`), registrado en **`0x5C9B06`** por `m2psIfo_Backup`.
18. Parchear `fn=0x5CA355` a mano **tampoco** vale: `0x2B3FC6 ldr r0,[r4,#0x14]` pasa el `arg` a la función y `0x5CA2A2 ldr r0,[r0,#0x18]` lo desreferencia ⇒ `arg=0` = caída. La opción segura sin el módulo es `FBM EWBDFD 4 3 0` (dummy `0x2B5184`, log y `return 0`), que crea el sector pero no escribe base.

---

## 0. Método y corrección de etiquetas

Todo es desensamblado estático de `libmpr.so` con capstone (Thumb), VA = offset del ELF (`readelf`: PT_LOAD `0x0..0x9BB1C8` con `p_offset==p_vaddr`). Scripts en `evidence/grabacion-bd-fbm-20261126/`: `funcstart.py` (inicio de función), `ptrs.py` (punteros a VA), `strref.py` (xref a cadenas), `strs.py` (cadenas de un rango), `tabla_escritores.py` (los 11 escritores de `fn`), `tabla_estatica.py` (volcado de `0x9D23FC`), `xref_all.py` (llamantes completos). Los desensamblados usan `mprdis.py` del informe `fbm-sector31-consola-20261126` (anota símbolos `.dynsym`, PLT y literales).

**Corrección a las etiquetas del encargo** (las cadenas lo dicen, no la opinión):

| sitio | el encargo decía | es en realidad |
|---|---|---|
| `0x37FC06`, `0x37FD4C` | «mp4» | módulo **BKUP** (`"BKUP Err ReadNextPackData ec"` `0x81C8F8`, `"BKUP Err InitBackupData ec"` `0x82502D`) |
| `0x38FEC4` | «MSV» | **DCF MCMD**: `"[DCF MCMD]Err BackupMgr::InitBackupData ec = ["` `0x82A9DD`, `"[DCF MCMD] InitBackUpTbl"` `0x82AA35` |
| `0x61D94C` | «DCF» | **gestor de medios (MMgr)**: `"MEDIAID : [MEDIA_ID_UNKNOWN]"` `0x8E63CA`, `"InitBackupData : [XAVC] nothing to do"` `0x8E63E8` |

## 1. Los cuatro llamantes de `BackupMgr::InitBackupData` (`0x2B43F0`)

`0x2B43F0` → `WriteBaseData` `0x2B4030` → `0x2B406A bl 0x2B3000` → si `r0≠0` en `0x2B4070/0x2B4072` se va a `0x2B40FC` con `0x10800010`. La guarda es `0x2B3018 ldr r2,[r3,#4]` (fn) + **`0x2B301A cbz r2,0x2B302A`** (salta la fila). Sólo hay **5** llamantes de `0x2B43F0` (`xrefs.txt`):

```
0x2b5b5a   consola FBM `InitB`            (handler 0x2B5B34)
0x37fc06   BKUP  (dentro de 0x37FB54)      InitBackupData(9,8)
0x37fd4c   BKUP  (dentro de 0x37FC80)      InitBackupData(9,8)
0x38fec4   DCF MCMD (0x38FE68)             InitBackupData(7,mediaID)
0x61d94c   MMgr (0x61D930)                 InitBackupData(OM(media),mediaID)
```

### 1.1 `0x37FC06` — BKUP, tras un `ReadFirstPackData(0x22,8)` fallido

`0x37FB54` (`dis/01`): `0x37FB88 bl 0x2B39B8` (=`BkRead`/`ReadFirstPackData`, log `"ReadFirstPackData"` `0x7E7690`); tras el bucle de packs:

```
0037fbf6: adds r0,r7,#4
0037fbf8: bl   0x2b4584              ; libera/cierra el lector
0037fbfc: ldr  r3,=0x10100001
0037fbfe: cmp  r4,r3
0037fc00: bne  0x37fc22              ; otros errores -> otra rama
0037fc02: movs r0,#9                 ; OM  = 9
0037fc04: movs r1,#8                 ; mediaID = 8  -> fileType 0xA0
0037fc06: bl   0x2b43f0              ; InitBackupData(9,8)
0037fc0a: cbz  r0,0x37fc4e           ; si OK, sigue
0037fc0c: ... 0x37fc1a ldr r1,=0x82502d "BKUP Err InitBackupData ec"
0037fc1c: bl   0x353708              ; log del error
0037fc20: b    0x37fc4e
0037fc4e: movs r0,#0                 ; *** la función devuelve 0 (éxito) ***
```

**Cuándo:** al *leer* la tabla BKUP (`userID 0x22`, `media 8`). `0x37FB54` **no tiene llamantes `bl`** (se invoca de forma indirecta, tabla construida en `.bss`), así que no se puede fijar el disparo exacto desde el binario; por las cadenas que usa (`"BKUP backupId/backupLen/divideFlg/copyOffSet"` `0x81C88E`-`0x81C8CA`) es el lector de «diferencia base», no el arranque de la grabación. **Error:** sólo log, y retorno 0.

### 1.2 `0x37FD4C` — el mismo patrón en `GetBaseDifferenceDubbedInfo` (`0x37FC80`)

`dis/02`: `0x37FCCA bl 0x2B39B8` (`(0x22,8)`), `0x37FD44 cmp r5,=0x10100001`, `0x37FD48 movs r0,#9` / `0x37FD4A movs r1,#8` / **`0x37FD4C bl 0x2B43F0`**, error → `0x37FD60 "BKUP Err InitBackupData ec"`, y al final `0x37FD94 movs r5,#0` + `0x37FE80 mov r0,r5` ⇒ **devuelve 0**. Imprime `"GetBaseDifferenceDubbedInfo Info--------"` `0x825048`.

**Cuándo:** cuando el BKUP calcula la «diferencia base» de los medios (información de doblado/publicación), también en lectura. Tiene un llamante estático: **`0x3809AE`**, dentro de la inicialización del módulo DCF que acaba de registrar los escritores `(0x20,mediaID)` y `(0x22,8)` (`0x38096E`, `0x380990`). **Error:** log y retorno 0.

### 1.3 `0x38FEC4` — `[DCF MCMD] InitBackUpTbl` (OM 7)

`0x38FE68` (`dis/03`) elige `mediaID` por `tbb` (`0x38FE90`): `(7,3) (7,4) (7,6) (7,5) (7,2) (7,7) (7,1)`, y cae en `0x38FEC4 bl 0x2B43F0`. Si falla:

```
0038fecc: b 0x38fed8
0038fed8: ldr r0,=0x82a9dd "[DCF MCMD]Err BackupMgr::InitBackupData ec = ["
0038fede: mov r0,r4 ; bl 0x38d1c8          ; imprime el código
0038fee4: ldr r0,=0x92a769 ; b 0x38feea     ; "]" ...
0038feee: ldr r0,=0x82aa35 "[DCF MCMD] InitBackUpTbl"
0038fef8: movs r0,#1 ; pop {r3,r4,r7,pc}    ; *** devuelve 1 (éxito) ***
```

**Cuándo:** al detectar/montar el volumen DCF (tabla de fotos), una vez por medio. **Error:** log con código + retorno 1.

### 1.4 `0x61D94C` — gestor de medios (MMgr), el que pide `(6,3)`

`0x61D930` (`dis/04`) recibe el tipo de medio y traduce a OM:

```
0061d93e: mov  r1,r0                 ; mediaID = 0x61D8D0(this,mediatype)
0061d93c: cmp  r5,#8   -> 0x61d942 movs r0,#4    ; OM 4   (DVD/AVCHD)
0061d946: cmp  r5,#0x10-> 0x61d94a movs r0,#6    ; OM 6   (M2PS/HDM)  <-- (6,3)
0061d952: cmp  r5,#6   -> 0x61d956 movs r0,#0xa  ; OM 10  (BD/AVC)
0061d95a: cmp  r5,#1   -> 0x61d95e movs r0,#7    ; OM 7   (DCF)
0061d962: cmp  r5,#0x80 -> beq 0x61d984          ; nada
0061d966: cmp.w r5,#0x100 -> beq 0x61d984        ; XAVC: "nothing to do"
0061d94c: bl  0x2b43f0               ; InitBackupData(OM, mediaID)
0061d950: b   0x61d984
0061d984: movs r0,#0 ; pop {r4,r5,r7,pc}         ; *** ni se consulta r0 ***
```

`0x61D8D0` (`dis/05`) devuelve el `mediaID`: `0x61D8F8` devuelve **3 ó 4** según `[this+0x120]` (`movne #4 / moveq #3`), más `2`, `5`, `6`, `7`. Es el sitio que produce el **`InitBackupData(6,3)` → `0x10800010`** del contexto. Tiene **20 llamantes** (montaje, cambio de medio, reparación: `0x62473C`, `0x6284E4`, …). **Error:** descartado.

### 1.5 Consecuencia: ninguno de los cuatro está en la grabación

Los cuatro se ejecutan **antes** de grabar: al montar/detectar el medio (`0x61D930`, `0x38FE68`) o al leer la tabla BKUP (`0x37FB54`, `0x37FC80`). Ni `0x5E7A6C` (`OpenRecFile`) ni `0x5E7D28` (`CloseRecFile`) llaman a `0x2B43F0`: la grabación **no intenta crear el sector**, sólo escribir en él (`ChangeSector` + `WritePack*`). Por eso el fallo de la grabación no aparece como `0x10800010` sino como `0x10100006`/`0x10100001`.

## 2. La grabación: dónde se registra el clip y por qué no queda

### 2.1 Quién escribe la BD de vídeo

La fila que importa está en la tabla estática `0x9D23FC` (volcada del propio ELF, `tabla-0x9d23fc.txt`):

```
[13] 04000000 03000000 31000000 06000000   fn=0x00000000 arg=0x00000000
     userID=0x04  mediaID=3  fileType=0x31  OM=6
[14] 21000000 03000000 31000000 06000000   fn=0x00000000 arg=0x00000000
     userID=0x21  mediaID=3  fileType=0x31  OM=6
```

`0x2B3000` compara `(OM, mediaID)` y se queda con la **primera** fila (idx 13, `userID 4`) antes de llegar a la 14; las 37 filas tienen `fn=0` en la imagen (se rellenan en ejecución).

`m2psIfo_Backup` es el dueño de la clave `(userID 4, mediaID)`:
- **registra su escritor** en `0x5C9AEC` (`dis/11`): `0x5C9B02 movs r0,#4`; `0x5C9B04 ldr r3,[r2,#0xC]` (mediaID); **`0x5C9B06 bl 0x2B1DEC`** con `fn=0x5CA354`; `0x5C9B0A mov r0,r4`(=0) ⇒ **el resultado del registro también se tira**.
- **cambia de sector** en `0x5C9F48` (`dis/19`): `0x5C9F7A ldr r1,[r4,#0xC]`, `0x5C9F7C movs r0,#4`, **`0x5C9F7E bl 0x2B41B4`**, y en error `"Flash Backup SECTOR CHANGE ERROR!!"` (`0x5C9FA0`, `0x8C5C71`, línea `0x3EA` del `m2psIfo_Backup.cpp`, `0x8C5B54`).
- **escribe** en `0x5CA0B4` (`dis/12`): `0x5CA10E bl 0x5C9F48`; si `r4≠0` → `0x5CA126 mov r0,r4` (sale sin escribir); si no, `0x2B3D24`/`0x2B3C64`/`0x2B3B94` (`WritePackBegin/WritePack/WritePackEnd`).

### 2.2 Los dos puntos de fallo, con el código que los ignora

`ChangeSector` `0x2B41B4` (`dis/10`):

```
002b41d2: mov r0,r6 / mov r1,r5 / mov r2,r7
002b41d8: bl  0x2b3094                  ; handle = [0xA3699C + 0x14*idx].+4
002b41dc: cbz r0,0x2b41ea               ; 0 = (userID,mediaID) encontrados
002b41ea: ldr r3,[r7]                   ; handle
002b41ec: cbnz r3,0x2b41fc              ; 0 -> error
002b41ee: ldr r0,=0x7e7b17 "ChangeSector()::Source backup handle not found. userID 0x%x 0x%x "
002b41f4: ldr r4,=0x10100006            ; *** 0x10100006 ***
```

`WritePackBegin` `0x2B3D24` (`dis/08`):

```
002b3d7c: ldr r3,=0xa3699c
002b3d80: ldrb r2,[r7,#0x3f]            ; índice devuelto por 0x2B2F48
002b3d84: mla  r2,0x14,r2,r3
002b3d88: ldr  r2,[r2,#4]               ; handle
002b3d8c: cmp  r2,#0
002b3d8e: bne  ...
002b3d90: ldr  r5,=0x10100001           ; *** 0x10100001 ***
```

`0x2B2F48` (`dis/06`) resuelve el índice con `GetFileType` (`0x2B2B18`) y compara **sólo `[entry+0] == fileType`** (`0x2B2F96/0x2B2F98`): **`fn` no interviene en escribir**.

Y quien llama a `0x5CA0B4` desde grabación (`dis/14`, `dis/15`, `dis/16`):

```
005e7a82  "…[I]m2psIfo_rec::OpenRecFile()"       ; 0x8D2902
005e7b8c  bl 0x5ca0b4                            ; escribe (al abrir el fichero)
005e7b90  ldr r0,[r4,#4]                         ; r0 recargado: resultado perdido

005e7d3c  "…[I]m2psIfo_rec::CloseRecFile()"      ; 0x8D293F
005e7d9c  bl 0x3ad2e4                              ; paso previo: r5 = su resultado
005e7e30  cbnz r5,0x5e7e54                        ; si el paso previo falló, NI se escribe
005e7e50  bl 0x5ca0b4                            ; escribe (al cerrar)
005e7e54  ldr r0,[r4,#4]                         ; resultado perdido
005e7e74  movs r2,#8 / ldr r1,="errorCode=" …    ; imprime r5 (el del paso previo)
005e7e92  mov r0,r5                              ; devuelve el del paso previo, no el del backup
```

`CancelMovieRec` (`0x5E7EC0`) hace lo mismo en `0x5E8002`.

**Resultado**: con `0xA3699C[10].+4 == 0` (sector 0x31 ausente), el registro del clip muere en `ChangeSector` con **`0x10100006`**; si el handle existiera pero la escritura fallara, moriría en `WritePackBegin` con **`0x10100001`**. En ambos casos el error se registra en el log del módulo (`m2psIfo_Backup.cpp` líneas `0x3EA`/`0x3C3`, `0x5EB88C`) o ni eso; `OpenRecFile` **no guarda** el retorno y `CloseRecFile` **devuelve el del paso previo** (normalmente 0), así que el fallo no llega a quien cierra la grabación.

### 2.3 El otro escritor (HDM, userID 0x21) ignora igual

`0x3AC880`/`0x3AC8F8`/`0x3ACF38`/`0x3AD15A`/`0x3AD3F4`/`0x3AD496`/`0x3AF800`/`0x3AF894` llaman a `0x34E638` con `userID 0x21` y `dataID 0xE/0xF/0x12/0x13` (los dos primeros son los que disparan los textos `"BKUP set DID_MAKE_REC_DIR"` `0x81C760` y `"BKUP set DID_REC_FILE"` `0x81C781`, porque el `tbb` de `0x34E658` indexa `dataID-0xD` y sólo cubre `0xD..0x11`). `0x34E4C0` traduce `(userID,mediaID)→DID` y `0x34E640`/`0x34E642` reciben `dataID` (r8) y el búfer (fp). `0x34E638` sí **devuelve** el error de `WritePackBegin`/`WritePack`/`WritePackEnd` (`0x34E6CA`, `0x34E6F6`, `0x34E730`; logs `"BKUP Err WritePackBegin/WritePack/WritePackEnd ec"` `0x81C7DB`/`0x81C803`/`0x81C819`), pero los llamantes hacen `cbz r0` y **continúan** (`0x3AC884` → `0x3536DC`; `0x3AF804` → `0x3536DC`).

## 3. ¿Hay reconstrucción que recorra la tarjeta y re-registre? Sí, y no toca la FBM

**Funciones y disparo**

| elemento | dirección / cadena | qué es |
|---|---|---|
| consola `Repair <AVINDEX/AVCHD_NEW/AVCHD/M2PS/STILL/XAVC_RECONST/XAVC/WAV>` | `0x9002BA` (también `RepairInfo` `0x90054A`, `RepairTime` `0x8FFFD6`) | orden de consola |
| consola `RepairAvi [mmgrId] [repairType(AVINDEX/AVCHD_NEW/AVCHD/M2PS/STILL)]` | `0x92CBC9` | variante por gestor |
| `BeginRepairCmd` | `0x6240C0`–`0x624202`; `"BeginRepairCmd : MMgrBackup[M2PS]"` `0x8E945E`, `[MP4]` `0x8E9508`, `[AVCHD]` `0x8E9481` | despacho por tipo |
| `RunInconsistencyM2psRegister` | `0x23C5C0`, `sources/avi_if/AviSeqRepair.cpp` `0x7C504A` | registro M2PS (recorre la tarjeta) |
| `RunInconsistencyAvcMp4Register` | `0x7ADB13` (`"… execute "`), `AviSeqRepair` `0x7C4CEF` | registro AVC/MP4 |
| `CreateAVIndexFile` | `0x7A7E7C` (`"CreateAVIndexFile : avi accsr CREATE"`) | reescribe el índice de la tarjeta |
| menú «Recuperar BD imág.» | `BeginRepair <AVINDEX>` (informe `film-pb-1-sub-bd-tarjeta-20261128.md` §5.2, INFERIDO allí) | UI |

**Condición**: se dispara a mano (menú o consola) o por el evento de reparación del MMgr; nunca desde `FBM::Init` ni desde la grabación.

**¿Depende de las mismas tablas?** Del **índice de la tarjeta** sí (lee `MP_ROOT/*`, escribe `AVF_INFO/AVIN0001.INP`). De `RcsBackupTblData` (`0x35EA1C`) **no directamente**: sus 6 llamantes son `0x37C098`/`0x37C2BA` (callback DCF), `0x3ABDF2`/`0x3ABFC2` (callback HDM) y `0x3AFAF6`/`0x3AFCC6` (MSV), ninguno en `0x62xxxx`/`0x23xxxx`/`0x7Axxxx`. Ahora bien, si el re-registro de un contenido pasa por el módulo dueño (que **sí** lee `RcsBackupTblData`), entonces hereda su fallo: hoy esa lectura devuelve `0x10100001` (`0x2B3A28`). De la **BD FBM** no: en todo el binario sólo **5** sitios llaman a `BackupMgr::InitBackupData` (`0x2B43F0`) y **ninguno** está en la ruta de reparación (lista del §1). Tampoco llama a `WriteBaseData` (`0x2B4030`, 1 llamante: `0x2B43F0`) ni a `CreateSector32`.

**Por qué no ha funcionado**: (a) no crea el sector que falta —no es su trabajo—; (b) cuando el re-registro de un contenido pasa por el IFO (`m2psIfo_Backup`), vuelve a chocar en `0x5C9F7E`/`0x2B3D24` con `0x10100006`/`0x10100001`; (c) si el índice ya estaba «bien», no hay nada que recuperar y el resultado es «no cambia nada», que es lo observado.

## 4. Predicción con código

### 4.1 Clip NUEVO (grabado después de existir el sector 0x31)

1. `FBM::Init` `0x2B4820` recorre los fileTypes y para los que existen hace `CheckExistSector` `0x2B8B48`→`0x2A6690` + `OpenSector32` `0x2B6764`→`0x2A81E8`; deja `0xA3699C[10] = {0x31, handle≠0, 1, 6}` (direcciones de `fbm-initb-20261130.md` §5; medido en el arnés: run D y run H de `reports/film-pb-1-sub-consola-sector31-20261126.md` §5).
   **Condición medida**: eso ocurre cuando el sector se creó con **página de datos base** (las imágenes de `LTC 1` y de `EWBDFD 4 3 0` + `InitB 6 3`: `2/30`, idx10 `h1/s1`). Con un `CreateSector32` pelado el arranque **no** lo abre (`1/30`, run 5 de `fbm-initb-6-3-nflasha4-20261126.md`, causa no determinada). Si el handle sigue 0, el clip nuevo tampoco se registra (§2.2).
2. `OpenRecFile` `0x5E7A6C` → `0x5CA0B4` → `0x5C9F48` → `ChangeSector(4,3)`: `0x2B41EC cbnz r3` con handle≠0 → sigue.
3. `WritePackBegin` `0x2B3D24` → `0x2B3D8E bne` (handle≠0) → escribe; `WritePack` `0x2B3C64` y `WritePackEnd` `0x2B3B94` cierran el pack.
4. La lectura de vuelta es la misma clave: `0x5CA5FE movs r0,#4` + `ldr r1,[r4,#0xC]` → `ReadFirstPackData` `0x2B39B8`.
⇒ **Sí: queda registrado y la lectura lo encuentra**, siempre que idx10 tenga handle (condición del punto 1). No hace falta `fn` para esto.

### 4.2 Clip ANTIGUO (grabado cuando no había sector)

1. Su registro **nunca se escribió**: el intento murió en `0x2B41F4` (0x10100006) o `0x2B3D90` (0x10100001) y nadie lo reintentó.
2. `CreateSector32` `0x11FA5C` sólo reserva la entrada de control: los datos quedan `0xFF` (informe `fbm-initb-6-3-nflasha4-20261126.md` §4).
3. Leer un sector vacío da `0x10100003` (`ReadPack` `0x2B267C`→`0x2B26FC`), y ese código **se tolera**: `0x520C3C beq 0x520c50`, `0x35E0FC beq 0x35e118`, `0x37FBD2 beq 0x37fbf2`, `0x37FD20 beq 0x37fd38`; en `0x5CA602` ni se mira.
4. **No hay ningún camino que rellene los registros de clips ya existentes**: los escritores de registros trazados son `0x34E638` (genérico, necesita `dataID` y lo llaman los módulos al crear/cerrar) y `0x5CA0B4` (lo llaman `OpenRecFile`/`CloseRecFile`/`CancelMovieRec`), más `WritePack` directo del AVCHD (`0x520280`/`0x5202AE`/`0x5202D6`); ninguno recorre los clips que ya están en la tarjeta.
⇒ **No: el clip antiguo no queda registrado.** Su única fuente posible es el IFO primario de la tarjeta (la lectura deja de dar error duro, pero el registro de la BD no está); no probado aquí.

**Excepción que sí registraría lo antiguo**: crear el sector **con el escritor real ya registrado**. `WriteBaseData` `0x2B4030` llama a `0x2B4130 bl 0x2B3F7C` (=`CallUserFuncWriteBaseDataRequest`) y éste a `fn(arg)` (`0x2B3FC2`–`0x2B3FC8`); `0x5CA294` (=`fn` real de (4,x)) arma el pack con el IFO vivo: `0x5CA2EA`–`0x5CA318` copian 4×`0xA0` bytes y `0x5CA326`/`0x5CA336` escriben IDs `0xE2` y `0xE1`. Es decir: **`FBM InitB 6 3` con la tarjeta montada y el módulo M2PS vivo** dejaría dentro la lista actual; con el dummy (`EWBDFD`) o con `LTC 1`, no.

## 5. `LTC 1` no sirve como escritor de producción

`0x2B5598` (`dis/18`) imprime `"[FBM]LocalTestCall::LTC_01"` (`0x7E842F`, `0x2B55A0`) y da de alta cuatro filas (`tabla_escritores.py`):

| quién | userID | mediaID | fn | arg | log |
|---|---|---|---|---|---|
| `0x2B55B0` | 4 | 3 | `0x2B5724` | `0xA36C4C` | `"Dummy EntryWriteBaseDataFunction for [M2PS Application ::Media MS] …"` `0x7E844A` |
| `0x2B55C4` | 0x21 | 3 | `0x2B5658` | `0xA36C4C` | `"… [M2PS DB ::Media MS] …"` `0x7E84DE` |
| `0x2B55E6` | 4 | 4 | `0x2B5724` | `0xA36C50` | `"… ::Media HDD …"` `0x7E8560` |
| `0x2B55FC` | 0x21 | 4 | `0x2B5658` | `0xA36C50` | `"…"` |

Y esos `fn` **fabrican datos de prueba**: `0x2B574E ldr r1,="MS"` (`0x947D7F`) / `0x2B5748 "HDD "` (`0x7E86BC`) / `0x2B5752 "UNKNOWN "` (`0x7E7E69`), y `0x2B575A ldr r1,="packData"` (`0x7E86C1`) → `0x144F82` (strcat) y se escribe el pack. Con `LTC 1` el sector queda con **texto de prueba** como si fuera la BD (por eso el arnés daba `BkRead = 0`, run H).

**Escritores reales por fila** (`escritores-fn.txt`, 11 llamantes de `0x2B1DEC`; `arg` = objeto del módulo, `0x2B1DEC` lo guarda en `entry+0x14`):

| fila | fn real | se registra en | observación |
|---|---|---|---|
| `(4, mediaID)` M2PS | **`0x5CA354`** (cuerpo `0x5CA294`) | **`0x5C9B06`** `m2psIfo_Backup` | escribe el IFO vivo (4×0xA0) |
| `(0x21, mediaID)` HDM | `0x3ABD74` | `0x3AC5AE` | log `"Err HDM EntryWriteBaseDataFunction"` `0x834B68` |
| `(0x23, mediaID)` BD/AVC | `0x3AFA78` | `0x3B0466` | `"Err MSV EntryWriteBaseDataFunction"` `0x83592E` |
| `(0x20, mediaID)` DCF | `0x37C008` | `0x38096E` | `"Err DCF EntryWriteBaseDataFunction"` `0x825273` |
| `(0x22, 8)` BKUP | `0x37AD38` | `0x380990` | `"… Diff"` `0x825296` |
| `(0x10, mediaID)` AVCHD | (paramétrico) | `0x520230` | devuelve `0xA0100002` si falla |

**Veredicto**: escribir el `fn` de `LTC_01` en producción es **incorrecto** (mete datos de prueba en la BD y además sustituye al escritor del módulo cuando éste se registre, o al revés según el orden). Y parchear el `fn` real a mano tampoco: `0x2B3FC6 ldr r0,[r4,#0x14]` pasa el `arg` y `0x5CA2A2 ldr r0,[r0,#0x18]` lo desreferencia, así que `arg=0` revienta; el `arg` válido es el objeto que sólo tiene el módulo. **Lo correcto**: dejar que `m2psIfo_Backup` se registre (`0x5C9B06`) y crear el sector después (`InitB`), o usar `FBM EWBDFD 4 3 0` (dummy `0x2B5184`, sólo log + `return 0`) si no hay módulo.

## 6. Límites

1. Todo estático; **no** se ha ejecutado nada en la cámara ni en QEMU para este informe.
2. No he determinado **cuándo** registra `m2psIfo_Backup` su `fn` en la cámara real (`0x5C9AEC` no tiene llamantes `bl`: es virtual, vtable `0x8C5B38`, ranuras `0x5C9A89`/`0x5C9AA5`). Si registra después del `InitBackupData(6,3)` del montaje, el orden explica que el sector no se cree nunca (huevo-gallina); si registra antes, el `0x10800010` tendría otra causa. **Es el dato que falta para cerrar el «por qué» del todo.**
3. `0x10100003` tolerado no demuestra que el clip antiguo se reproduzca: ese salto sólo evita el error duro; la carga del IFO primario no se ha trazado aquí.
4. `LTC 1` es de la consola de debug (no UI). El `fn` de `(0x21,3)` (`0x3ABD74`) no se ha desensamblado en cuerpo, sólo su registro.
5. Este informe **no reabre** la discusión de `film-pb-1-sub-bd-tarjeta-20261128.md` sobre miniaturas/decodificador: demuestra el fallo de registro en la BD FBM, que es un hecho distinto.

## 7. Reproducción

```sh
bash reports/evidence/grabacion-bd-fbm-20261126/gen_evidencia.sh     # regenera dis/ y xrefs.txt
python3 reports/evidence/grabacion-bd-fbm-20261126/tabla_escritores.py
sed -n '/0x37fbf6/,/0x37fc56/p' reports/evidence/grabacion-bd-fbm-20261126/dis/01-bkup-read-r4-0x37fb54.txt
sed -n '/0x5e7e3c/,/0x5e7e9a/p' reports/evidence/grabacion-bd-fbm-20261126/dis/15-m2psifo-closerecfile-0x5e7d28.txt
```
