# FILM-PB-1 / sub-rcsbackup — Qué lee de verdad `RcsBackupTblData`, qué ficheros de `AVF_INFO` necesita el IFO del MP4 y por qué las fotos sí se ven

26-11-2026 · Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`).
**Direcciones = VA del ELF (base 0).** Desensamblado: `python3 /tmp/elfhelper.py <so> dis <va> <len>` (capstone Thumb-2).
Evidencia cruda: [reports/evidence/film-pb-1-sub-rcsbackup-20261126/](evidence/film-pb-1-sub-rcsbackup-20261126/).
Todo lo que sigue sale de bytes del binario. No se ha ejecutado firmware ni se ha tocado una cámara o una tarjeta.

---

## 0. Resumen (20 líneas)

1. `RcsBackupTblData` (`0x35EA1C`) **no abre ningún fichero de la tarjeta**: es un envoltorio de `0x35E04C`, que hace un `BkRead` de un *pack* de respaldo por `(userId, backupId)` vía el gestor de sectores (`0x2B39B8` → `0x2B2F48` → `0x2B3948`, `ReadFirstPackData`).
2. El pack se llama **`RcsTbl`** y guarda los registros de la última grabación: `rootDirName`, `recDirName`, `recFileName`, flags y `contFileNo` (u16), con un byte de tipo `0..0x19`.
3. `Err RcsBackupTblData` solo se imprime para códigos con cabecera **`0x10`** (`0x3AFAFE`/`0x3AFB06`: `and r3,r0,#0xff000000` / `cmp #0x10000000`). El caso típico es `0x10100001` = la entrada `(user,id)` **no tiene rutina de lectura** en `0xA3699C` (`0x2B39EE` → `0x2B3A28`).
4. `0x10100003` ("sin datos") se **tolera** (`0x35E0FC`); un desajuste lógico devuelve **`0x00500003`** → `" Need Salvage"` y marca `[obj+0x44]=1` (`0x3AFB0C…0x3AFB22`). Ese **no** es el error del log.
5. `FlashLoadForMsv` (`0x698EC8`) tampoco lee la tarjeta: llama a `MsvMcmd::RcsBackupTblData` (`0x3AFA94`) y, si falla, devuelve `0xB0800001` (`0x698EE2`/`0x698EEA`).
6. `mp4Ifo_General::Load` (`0x698FB8`) elige `FlashLoadForMsv` para el medio "FLASH" (`0x698FEA`) y `0x698E78` para "DISC" (`0x698FE2`).
7. `hdAvcIfo_If::CheckSalvageStatus` (`0x5AD53C`) es **solo mutex + despacho** a `vtbl+0xB0` (`0x5AD56E`); no toca ficheros.
8. `MMgrAvcHdIfoAcsr::CheckSalvageStatus` (`0x671DAC`) filtra estados AVI `{2,3,4,6}` (`0x671DD4`, máscara `0x5C`) y `vtbl[0x144]==0`, y registra el código en la línea **791** (`0x671E8E`, `movw r3,#0x317`).
9. Los ficheros reales de `AVF_INFO` que construye `libmpr` son **tres**: `AVIN0001.INP` (base `0x7A9070` + `0xBC`), `AVIN0001.BNP` (+`0xC9`) y `AVIN0001.INT` (+`0xF0`); constructor de rutas `0x12C5C8` (`strcat` `0x1D238C`).
10. Descriptor en `.data` **`0x9D1270`**: `AVIN0001.INP` con tamaño máximo **10000 B** (`0x2710`), `0x80`, `0x4B0`, `0x86` y un ID de 16 B; el `.INT` tiene descriptor propio en `0x9D12C0`.
11. `PRV00001.BIN` (`0x7C7FEA`) lo gestiona `DcfPrvFileAcsr` (xref `0x245108`); es el fichero de **propiedades**, no el índice.
12. `mp4Ifo` **no tiene ninguna ruta ni fichero de índice propio** (negativo verificado): su catálogo es el índice AV (`AVIN0001.INP`), con cache por tipo `GetMp4AvcLoadInfoCache` (`0x7CCA87`).
13. Por eso, si falta el `INP`, el IFO del MP4 no tiene de dónde cargar; `.BNP` es el respaldo; `.INT` la tabla interna; sin ellos el `INP` sigue sirviendo.
14. El camino de **FOTO** (rejilla de miniaturas) no usa ese índice: lee los JPG/EXIF de `DCIM`. Por eso las miniaturas de fotos sí aparecen aunque el IFO del MP4 no cargue.
15. Prueba negativa: los 3 únicos llamantes de la variante DCF (`0x3ABD90`) son un comando de consola `[HDM MCMD]` (`0x3ADE3A`) y el IFO HDM (`0x5D291A`, `0x5D2BE8`); **ninguno** es la rejilla de miniaturas.
16. El propio IFO de foto (`FlashLoadHdm`, `0x5D2BD0`) falla igual si `RcsBackupTblData` falla (`0x5D2BE8…0x5D2C32`). Luego "fotos sí / vídeo no" no distingue "tarjeta legible", sino **quién necesita índice**.
17. Copiar los clips al PC y devolverlos pierde, como mínimo, `AVF_INFO\` entero (`INP`/`BNP`/`INT`) y `PRV00001.BIN`; el que explica el fallo es **`AVIN0001.INP`**.
18. Reparación mínima sin formatear: reponer `AVF_INFO\` completo de la copia original; si no hay copia, `Recuperar BD imág.` o renombrar `AVF_INFO` → `AVF_INFO.old` para forzar `CreateAVIndexFile`.
19. Reparación segura: formatear en la cámara (borra `DCIM` y `MP_ROOT`).
20. **NO_VERIFICADO**: el subcódigo `0x10xxxxxx` exacto del log, el medio físico del pack `RcsTbl` (tarjeta vs NVRAM interna) y el papel exacto de `.INT`.

---

## 1. `RcsBackupTblData` `0x35EA1C` — desensamblado completo y qué hace

### 1.1 Es un envoltorio de depuración, no un lector de ficheros

| VA | Instrucción | Lectura |
|---|---|---|
| `0x35EA1C` | `push.w {r4..fp,lr}` / `sub sp,#0x34` | prólogo; `r4 = this` |
| `0x35EA22` | `add.w r8,r0,#0x4000` | base de los campos altos del objeto |
| `0x35EA3C` | `ldr.w r0,[r8,#0x84]` | `this->logger` |
| `0x35EA64` | `bl 0x353708` | log `"RcsBackupTblData Start"` (`0x81DFA7`, cargado en `0x35EA5A`) |
| `0x35EA68` | `mov r0,r4 ; bl 0x353B7C` | refresco/estado previo |
| `0x35EACA` | `ldr r3,[r3,#0x48]` | `this+0x3080+0x48` = objeto auxiliar 1 (si es NULL, `new(0x3171C)`) |
| `0x35EAD0` | **`bl 0x35E04C`** | **el worker real** |
| `0x35EAD4` | `str r0,[r7,#4]` | guarda el código de retorno |
| `0x35EC90` | `ldr r0,[r7,#4]` / `pop.w {…,pc}` | **devuelve el código de `0x35E04C`** |

No hay `open`/`fopen`/`Fsys_*` en toda la función. El único acceso a datos es el que hace `0x35E04C`.

**No existe ninguna cadena de nombre de fichero en `0x35EA1C` ni en `0x35E04C`.** Barrido de literales de ambas
funciones: solo `"RcsBackupTblData Start/End"` (`0x81DFA7`/`0x81DFBE`), `"BKUP RcsTbl Start/End"`
(`0x81C85E`/`0x81C978`), los nombres de campo de §1.3 y los errores `"BKUP Err …"`. Ningún `AVIN*`, ningún
`.INP/.BNP/.INT`, ningún `PRV00001.BIN`.

### 1.2 El worker `0x35E04C` — `BkRead` por `(userId, backupId)`

Cabecera y llamada clave:

```
0035e052  add.w  sl,r0,#0x4000
0035e066  mov    r4,r0                      ; this
0035e084  ldr    r1,=0x81C85E "BKUP RcsTbl Start"
0035e096  bl     0x353708                   ; log de entrada
0035e0b8  ldr.w  r0,[r7,#0x104]             ; args de salida (7 punteros)
...
0035e0ec  ldr.w  r0,[sl,#0x88]              ; r0 = this->[+0x4088]  (userId)
0035e0f0  ldr.w  r1,[sl,#0x8c]              ; r1 = this->[+0x408C]  (backupId)
0035e0f4  bl     0x2B39B8                   ; *** BkRead(userId, backupId, ...) ***
0035e0f8  mov    r5,r0
0035e0fa  cbz    r0,0x35E118                ; 0 = leído
0035e0fc  ldr    r3,=0x10100003
0035e0fe  cmp    r0,r3
0035e100  beq    0x35E118                   ; "sin datos" se tolera
0035e10e  ldr    r1,=0x81C870 "BKUP Err ReadFirstPackData ec"
0035e114  b.w    0x35E94E                   ; log + salir con r5
```

`0x2B39B8` = `ReadFirstPackData` (`0x7E7690`). Su secuencia:

```
002b39b8  push.w {r4..sb,lr}
002b39c8  ldr    r0,=0x7E7690 "ReadFirstPackData"
002b39ce  bl     0x2B1E68                   ; log de entrada
002b39d2  mov    r1,r4                      ; backupId
002b39d4  add.w  r2,r7,#0xf
002b39d8  mov    r0,r5                      ; userId
002b39da  bl     0x2B2F48                   ; *** índice en la tabla de sectores ***
002b39de  ldrb   r2,[r7,#0xf]               ; índice devuelto (0..0x1D)
002b39e0  movs   r1,#0x14
002b39e2  muls   r1,r2,r1                   ; 0x14 B por entrada
002b39e6  ldr    r3,[pc,#..] = 0xA3699C     ; tabla de sectores (30 entradas)
002b39ec  ldr    r2,[r2+4]                  ; [entrada+4] = handle/rutina
002b39ee  cbz    r2,0x2B3A28                ; *** si no hay rutina -> error ***
002b3a28  ldr.w  sb,[pc,#..] = 0x10100001    ; "entry not found / no reader"
002b3a20  bl     0x2B3948                   ; ReadFirstPackData real (sector)
```

`0x2B2F48` (`GetSectorManagerInfoTableIndexFromUserID`, `0x7E707D`) traduce `(userId, mediaId)` a índice con
`GetOperationModeFromUserIDAndMediaID` (`0x2B2DF4`, cadena `0x7E6F7C`) y una tabla de `0x9D2404`; imprime
`"  OM:0x%x, userID:0x%02x, mediaID:0x%02x"` (`0x7E6FCD`) y `"  fileType:0x%x..."` (`0x7E70A6`). Es el
**gestor de sectores del medio** (`GetSectorManagerInfoTableIndexFromUserID`, `GetSectorHandleFromOperatioModeAndMediaID`
`0x2B3000`, `ChangeSector`), no el `open()` de un fichero.

### 1.3 Qué estructura lee

`0x35E04C` decodifica el pack según un **byte de tipo** `[r7+0xD7]` (`0x35E1C4`: `cmp r3,#0x19`; `0x35E1CA`: `tbh`),
y rellena los campos que luego imprime con estos literales (todos en `.rodata`):

| Campo | Literal / VA | Instrucción que lo usa |
|---|---|---|
| `rootDirName` | `"   rootDirName "` `0x81E78D` | `0x35EB2A` (`mov r3,sb`) / `0x35EB36` |
| `recDirName` | `"   recDirName  "` `0x81E79D` | `0x35EB40` (`add r3,sb,#8`) |
| `rsvFileFlg` | `"   rsvFileFlg "` `0x81E7AD` | `0x35EB4E` (`ldrh r3,[sb,#0x12]`) |
| `isRootDir` | `"   isRootDir  "` `0x81E7BC` | `0x35EB66` (`ldrb r3,[sb,#0x14]`) |
| `preEndRecFileFlg` | `" p_preEndRecFileFlg "` `0x81E7CB` | `0x35EB7E` (`ldrb r3,[r5]`) |
| `recFileName` | `"   recFileName "` `0x81E7E0` | `0x35EBE0` (`add r3,fp,#0x11`) |
| `endRecFileFlg` | `" p_endRecFileFlg "` `0x81E7F0` | `0x35EBEE` (`ldrb r3,[r5]`) |
| `contFileNo` | `" p_contFileNo "` `0x81E76C` | `0x35EAE6` / `0x35EAF0` (`ldrh r3,[r2]`) |

Tamaños máximos que acepta el decodificador:

```
0035e202  ldr.w  r2,[r7,#0xc8]            ; backupLen
0035e206  cmp.w  r2,#0x2f00               ; 12032 B
0035e20a  bls    0x35E214
0035e20c  movs   r3,#0xff                 ; marca "longitud inválida" en [r7+0xd6]
0035e214  ldr    r0,[r7,#0x2c]            ; destino (rootDirName)
0035e216  ldr    r1,[r7,#0xcc]            ; origen (pack)
0035e21a  bl     0x12111C                ; memcpy
...
0035e250  cmp.w  r2,#0x104               ; 260 B
0035e262  ldr    r0,[r7,#0x1c]            ; destino (recDirName)
```

Es decir: un registro con nombres de directorio (≤8 B), nombre de fichero (≤0x11 B), flags y un número de fichero
contiguo de 16 bits. **No es un fichero del volumen**: es el *journal* de creación de directorios/ficheros.

Prueba de que es un journal de grabación (cadenas de la misma unidad de compilación):

* `0x81C742 "BKUP set DID_REC_START userId"`, `0x81C760 "DID_MAKE_REC_DIR"`, `0x81C781 "DID_REC_FILE"`,
  `0x81C79E "DID_REC_EXT_FILE"`, `0x81C7BF "DID_REC_END"`.
* `0x81C915 "BKUP Err Reconstruct dirFlg"`, `0x81C931 "…fileFlg"`, `0x81C94E "…fileNoFlg"`, `0x81C96D " BKUP File"`.
* `0x8239BB " NEW MAKE DIR!"`, `0x823A24 " NEW MAKE FILE!"`, `0x823A98 " SetBkRecDirNo is preRecBackUpInfo.recDirName!!"`,
  `0x823AC8 " SetBkSeqNo is preRecBackUpInfo.recFileName!!"`, `0x823AF6 " SetBkSeqNo is contFileNo!!"`.

### 1.4 La condición exacta de `Err RcsBackupTblData`

En el llamante MSV `0x3AFA94`:

```
003afaf6  bl     0x35EA1C                  ; RcsBackupTblData()
003afafa  mov    r6,r0
003afafc  cbz    r0,0x3AFB44               ; 0 = OK
003afafe  and    r3,r0,#0xff000000          ; <-- cabecera
003afb06  cmp.w  r3,#0x10000000
003afb0a  beq    0x3AFB28                  ; cabecera 0x10 -> "Err RcsBackupTblData"
003afb0c  ...    " Need Salvage"            ; otra cabecera -> salvage
003afb28  ldr    r1,=0x823999 "Err RcsBackupTblData"
```

**Condición**: `RcsBackupTblData() != 0` **y** `(código & 0xFF000000) == 0x10000000`.

Los códigos `0x10xxxxxx` son de la capa `BkRead`/pack (`0x10100001…0x10100007`, `0x10800010`; tabla de literales en
`0x2B25C8…0x2B3EE8`). El `0x10100001` concreto sale de `0x2B3A28` cuando `[entrada+4] == 0`, es decir, **cuando el
`(userId, backupId)` no tiene reader registrado en `0xA3699C`**, no cuando el fichero `AVIN0001.INP` falta.

El desajuste lógico (el journal dice una cosa y el volumen otra) es otro código distinto:

```
0035e954  cmp    r2,#0x11                  ; estado "ya escrito"
0035e956  beq    0x35E9BC
0035e958  ldr    r0,[r4,#0x58]
0035e95a  movw   r1,#0x4007
0035e962  bl     0x34E490                  ; log de error
0035e97c  ldr    r1,=0x81E74C "BKUP Err Reconstruct rcsStatFlg"
0035e994  ldr    r5,=0x00500003            ; <-- cabecera 0x00: NEED SALVAGE
```

`0x00500003` tiene cabecera `0x00`, así que **no** imprime `Err RcsBackupTblData`; imprime `" Need Salvage"` y marca
`[this+0x44]=1`. Esa es la firma de "la tarjeta se tocó por fuera", no la del log de este caso.

---

## 2. `FlashLoadForMsv` `0x698EC8` — qué consulta

```text
00698ec8  push {r4,r5,r7,lr}
00698ed2  ldr r0,=0x914EF2 " mp4Ifo_General::FlashLoadForMsv IN ()"
00698ed8  ldr r0,[r4]                 ; this->[0]
00698eda  bl  0x6964E2                ; = *(r0+8): el objeto MSV/MsvMcmd
00698ede  bl  0x3AFA94                ; *** MsvMcmd::RcsBackupTblData() ***
00698ee2  ldr r1,=0xB0800001          ; código por defecto
00698ee4  ldr r2,=0x91443D "IF/mp4Ifo_General.cpp"
00698ee6  movw r3,#0x6d5              ; línea 1749
00698eea  bl  0x6F0D4C                ; traductor/log de mp4Ifo
00698ef0  cbz r0,0x698EF8
00698ef2  mov r0,r4
00698ef4  bl  0x697D70                ; limpieza
```

* **No hay ninguna apertura de fichero** en `0x698EC8`: delega todo en `MsvMcmd::RcsBackupTblData` (`0x3AFA94`) →
  `RcsBackupTblData` (`0x35EA1C`) → `BkRead` (`0x2B39B8`).
* Si el `BkRead` falla, devuelve **`0xB0800001`** (genérico de `mp4Ifo`), que es lo que el log muestra como
  `mp4Ifo faild ... 0xB0800001`.
* `0x6964E2` es un getter de 3 instrucciones: `ldr r0,[r0,#8] ; pop {r7,pc}` (el puntero al objeto MSV).

Su único consumidor en el camino de carga es `mp4Ifo_General::Load` `0x698FB8`:

```
00698fba  mov r4,r0                  ; this
00698fbe  mov r5,r1                  ; device (0=FLASH, 1=DISC)
00698fc4  ldr r0,=0x914FA6 " mp4Ifo_General::Load IN (device="
00698fca  cbnz r5,0x698FD0
00698fcc  ldr r0,=0x7AE670 "FLASH"
00698fd0  ldr r0,=0x8AC35F "DISC"
00698fdc  cmp r5,#1
00698fde  bne 0x698FE8
00698fe0  bl  0x698E78               ; LoadDisc
00698fe8  bl  0x698EC8               ; *** FlashLoadForMsv ***
00698ff0  cbnz r0,0x698FF8
00698ff2  movs r3,#1
00698ff4  strb.w r3,[r4,#0x23]       ; marca "IFO cargado"
```

**Conclusión parcial**: el primer paso de la carga del IFO del MP4 en el medio "FLASH" es leer el journal `RcsTbl`.
Si ese journal no se puede leer, el IFO **ni siquiera llega a mirar el MP4**.

---

## 3. `hdAvcIfo_If::CheckSalvageStatus` `0x5AD53C` — qué consulta

```text
005ad53c  push.w {r4..sb,lr}
005ad544  ldr r0,=0x8B427B "[IFO]Start hdAvcIfo_If::CheckSalvageStatus"
005ad552  ldr r0,[r4,#4]              ; r0 = this->mutex
005ad554  movs r1,#0x4E               ; cmd = 0x4E
005ad558  bl   0x5BAD00                ; ifoFramework_Semaphore::Acquire
005ad55c  cbnz r0,0x5AD582
005ad55e  ldr r2,[r7,#0x20]
005ad560  mov r1,r6
005ad562  ldr r0,[r4]                  ; r0 = backend (hdAvcIfo_*)
005ad564  ldr r3,[r0]                  ; vtable
005ad566  str r2,[sp]
005ad568  ldr r2,[r7,#0x24]
005ad56a  str r2,[sp,#4]
005ad56c  mov r2,r8
005ad56e  ldr.w r5,[r3,#0xB0]          ; slot 0xB0
005ad574  blx r5                       ; *** backend->CheckSalvageStatus(...) ***
005ad576  movs r1,#1
005ad57a  ldr r0,[r4,#4]
005ad57c  bl   0x5BACB0                ; Release
005ad582  ldr r5,=0xA0000001           ; fallo de acquire
```

No hay ninguna E/S: es un **wrapper de mutex + despacho**. Lo que "consulta" es el estado interno del backend
`hdAvcIfo_*` (slot `+0xB0`), no un fichero del volumen.

Su llamante `MMgrAvcHdIfoAcsr::CheckSalvageStatus` `0x671DAC`:

```text
00671db8  ldr r0,[r0,#0xc]            ; objeto AVI
00671dc2  ldr r3,[r0]                 ; vtable
00671dc4  ldr.w r3,[r3,#0xf4]
00671dc8  blx r3                      ; estado AVI (0..6)
00671dca  cmp r0,#6
00671dcc  bhi 0x671DE8                ; fuera de rango -> no salvage
00671dce  movs r3,#1
00671dd0  lsls.w r0,r3,r0
00671dd4  tst.w r0,#0x5C              ; bits 2,3,4,6
00671dd8  beq 0x671DE8                ; estado no salvage -> 0
00671dda  ldr r0,[r4,#0xc]
00671dde  ldr.w r3,[r3,#0x144]
00671de2  blx r3                      ; vtbl[0x144]()
00671de4  cbz r0,0x671E38             ; 0 -> seguir; !=0 -> "AVCHD already created"
00671e38  ldr r3,[r4,#0x3c]           ; handle IFO
00671e3c  cbz r3,0x671E56
00671e3e  mov r0,r3
00671e40  ldr r1,[r4,#0x30]
00671e42  movs r2,#2
00671e44  mov r3,r8
00671e46  str.w fp,[sp]
00671e4a  str.w sb,[sp,#4]
00671e4e  bl 0x5AD53C                  ; hdAvcIfo_If::CheckSalvageStatus
00671e52  mov sl,r0
00671e86  mov r0,r4
00671e88  mov.w r1,#0x194
00671e8c  mov r2,sl
00671e8e  movw r3,#0x317               ; *** línea 791 ***
00671e96  bl 0x677B8E                  ; ## ERROR(HDAVCIFO):<código> ## ... (791)
```

**Condición**: estado AVI ∈ `{2,3,4,6}` **y** `vtbl[0x144]() == 0` **y** `0x5AD53C` devuelve ≠ 0. En el anillo ese
código es `0xA0100003` (fallo de comando HD-AVC, cmd `0x4E`), ya resuelto en
[film-pb-1-sub-mount-ifo-20261126.md](film-pb-1-sub-mount-ifo-20261126.md) §2.5.

---

## 4. Los ficheros reales de `AVF_INFO` (y los que no lo son)

### 4.1 El constructor de rutas `0x12C5C8` (VERIFICADO)

`0x12C5C8(this, out1, out2, out3)` arranca con `r5=out1`, `r4=out2`, `r8=out3`, `fp=this+5` (prefijo del volumen)
y construye tres cadenas con `strcat` (`0x1D238C`):

```text
0012c5f6  mov r1,fp          ; prefijo (p.ej. "ms:/")
0012c5fa  bl  0x1D238C
0012c5fe  adds r1,r7,#4      ; separador (1 char, [this+0x15])
0012c602  bl  0x1D238C
0012c606  ldr r1,=0x7A637F "AVF_INFO"
0012c60a  bl  0x1D238C
0012c60e  adds r1,r7,#4
0012c612  bl  0x1D238C
0012c616  ldr r0,[r6,#0x4c]  ; índice de medio
0012c618  bl  0x144084       ; = &tabla 0x7A9070
0012c61c  add.w r1,r0,#0xBC  ; +0xBC = 0x7A912C = "AVIN0001.INP"
0012c622  bl  0x1D238C       ; out1 = <pref>AVF_INFO<sep>AVIN0001.INP
...
0012c652  bl  0x144084
0012c656  add.w r1,r0,#0xC9  ; +0xC9 = 0x7A9139 = "AVIN0001.BNP"
0012c65c  bl  0x1D238C       ; out2 = ...AVIN0001.BNP
...
0012c68c  bl  0x144084
0012c690  add.w r1,r0,#0xF0  ; +0xF0 = 0x7A9160 = "AVIN0001.INT"
0012c696  bl  0x1D238C       ; out3 = ...AVIN0001.INT
```

Base de la tabla: `0x144084` es `ldr r0,[pc,#0]` → `0x7A9070` (`0x14408C`). Offsets exactos:

| Fichero | Offset desde `0x7A9070` | VA de la cadena | Evidencia |
|---|---|---|---|
| `AVIN0001.INP` | `0xBC` | `0x7A912C` | `0x12C61C` (`add.w r1,r0,#0xbc`) |
| `AVIN0001.BNP` | `0xC9` | `0x7A9139` | `0x12C656` (`add.w r1,r0,#0xc9`) |
| `AVIN0001.INT` | `0xF0` | `0x7A9160` | `0x12C690` (`add.w r1,r0,#0xf0`) |

Los dos llamantes del constructor son `0x12E50C` (carga del índice AV) y `0x1F628A`. En `0x12E544` el `INP` es el
que se pasa a `0x159A88` (apertura/lectura); el `BNP` va como segundo buffer y el `INT` como tercero.

### 4.2 Descriptor de `.data` `0x9D1270` (VERIFICADO por bytes)

```
009d1270  41 56 49 4e 30 30 30 31 2e 49 4e 50 00 00 00 00   "AVIN0001.INP"
009d1280  80 00 00 00  10 27 00 00  ff ff ff ff  01 00 00 00
009d1290  b0 04 00 00  86 00 00 00  ff 06 75 81 fa 7b e2 90
009d12a0  45 27 84 b0  5e 61 10 ad  46 60 02 00 ...
```

Campos (little-endian): `name[16]`; `0x80`; `0x2710` = **10000 B** (tamaño máximo del INP); `0xFFFFFFFF`;
`1`; `0x4B0`; `0x86`; ID de 16 B `FF067581FA7BE290452784B05E6110AD`. El `.INT` tiene su propio descriptor en
`0x9D12C0` (campos distintos: `01 01 A0 00 78 00 …`), lo que confirma que es un fichero **aparte**, no un alias.

### 4.3 `PRV00001.BIN`

Cadena `0x7C7FEA` (precedida de bytes `1F 1C 1F 1E…`, parte de una tabla de nombres). Único xref: `0x245108`,
dentro del módulo `DcfPrvFileAcsr` (`0x7A6E19` `[DcfPrvFileAcsr] Error = 0x%x , Line = %d`; `0x7C805A`
`DcfPrvFileAcsr::m_pDataTable`). Es el fichero de **propiedades** (fecha, protección, thumbnail), no el índice AV.

### 4.4 `OTDISCBN.IND` / `MODELCFG.IND`

Cadenas `0x7A91C0` / `0x7A91CD`; xrefs `0x1447E4`, `0x1449D8` / `0x144894`, `0x144AB8`. Son de *disc burn* y
configuración de modelo; irrelevantes para reproducir un MP4.

### 4.5 Tabla tipo→extensión `0x3B7960` (contexto)

```
003b7960  ldr r0,=0x837AA3 ".BNP"     ; tipo 0
003b7964  ldr r0,=0x837AA8 ".INP"     ; tipo 1
003b7968  ldr r0,=0x837AAD ".INT"     ; tipo 2
003b796c  ldr r0,=0x7EA95A ".IND"     ; tipo 3
003b7970  ldr r0,=0x7ABDA4 ".JPG"     ; tipo 4
...
```

Confirma que `BNP`/`INP`/`INT` son **tres tipos de fichero distintos** del mismo subsistema.

---

## 5. ¿Usa el camino de FOTO los mismos ficheros?

**No para las miniaturas.** La rejilla de miniaturas de foto lee los JPEG de `DCIM` (y su EXIF); no abre el índice AV.

Evidencia negativa (barrido de llamantes con `elfhelper calls`):

| Función | Llamantes | Qué son |
|---|---|---|
| `0x35EA1C` `RcsBackupTblData` | `0x37C098`, `0x37C2BA`, `0x3ABDF2`, `0x3ABFC2`, `0x3AFAF6`, `0x3AFCC6` | cuatro métodos `*Mcmd::RcsBackupTblData` (HDM/DCF/MSV) y sus envoltorios |
| `0x3AFA94` `MsvMcmd::RcsBackupTblData` | `0x39CE3A`, `0x3B0B26`, `0x5D38CE`, `0x5ED6D2`, **`0x698EDE`** | inicialización de objetos MSV + comando de consola `[MSV MCMD]` (`0x3B0B26`) + `FlashLoadForMsv` |
| `0x3ABD90` `dcf_If::RcsBackupTblData` | `0x3ADE3A`, `0x5D291A`, **`0x5D2BE8`** | comando de consola `[HDM MCMD]` (`0x3ADE3A`) + `hdmIf::CheckSalvageStatus` + `FlashLoadHdm` |
| `0x698EC8` `FlashLoadForMsv` | `0x698F46`, `0x698FEA` | `CheckSalvageStatus` y `Load` de `mp4Ifo_General` |
| `0x12C5C8` constructor `AVF_INFO` | `0x12E50C`, `0x1F628A` | carga del índice AV |

No aparece ningún llamante en `dcf_Lib` de listado/thumbnail. Y el propio IFO de foto (`FlashLoadHdm` `0x5D2BD0`)
**también** aborta si `0x3ABD90` falla:

```
005d2bd6  ldr r0,=0x8CAB7F "[IFO]FlashLoadHdm()"
005d2bdc  ldr r0,=0x8CAA31 "[IFO]hdmIf::RcsBackupTblData() Call !"
005d2be2  ldr r0,[r4,#0x48]
005d2be4  bl  0x5CE00A
005d2be8  bl  0x3ABD90               ; dcf_If::RcsBackupTblData
005d2bec  mov r5,r0
005d2bee  cbz r0,0x5D2C24
...
005d2c12  ldr r0,=0x8CAAA6 "[IFO]hdmIf::UnLoad() Call !"
005d2c30  mov r0,r5 ; pop {r4,r5,r7,pc}   ; devuelve el error
```

Por tanto: **"las fotos sí se ven" no prueba que el volumen esté sano; prueba que la rejilla de fotos no pasa por el
IFO**. Si se abriera el IFO de foto (p. ej. reproducción con índice, no thumbnail), fallaría igual.

---

## 6. Lista exacta de ficheros de `AVF_INFO` que necesita el IFO del MP4

`mp4Ifo` **no tiene rutas ni fichero de índice propio** (verificado: no hay ninguna cadena `AVF_INFO`/`AVIN`/`.INP`
en el módulo `mp4Ifo_*`; su catálogo es el índice AV). El IFO del MP4 se apoya en el índice AV, que es
`AVF_INFO\AVIN0001.INP`. Lista y efecto de cada ausencia:

| # | Fichero | ¿Necesario para cargar el IFO MP4? | Qué pasa si falta | Confianza |
|---|---|---|---|---|
| 1 | `AVF_INFO\AVIN0001.INP` | **SÍ** — es el índice AV primario; de él sale `GetMp4AvcLoadInfoCache` (`0x7CCA87`) | `IsExistAVIndexDirectory`/`ReadAVIndexFile` fallan → no hay catálogo → `CreateAndLoad` falla. Es **el** fichero que explica el fallo | VERIFICADO (nombre, descriptor y cache); efecto = INFERIDO fuerte |
| 2 | `AVF_INFO\AVIN0001.BNP` | No si el INP es válido | Se pierde la copia de respaldo; la cámara no puede restaurar el INP si se corrompe. Con INP bueno, el IFO carga | VERIFICADO nombre; efecto INFERIDO |
| 3 | `AVF_INFO\AVIN0001.INT` | No si el INP es válido | Se pierde la tabla interna (descriptor propio `0x9D12C0`); la cámara la reconstruye. No debería impedir la carga | NO_VERIFICADO (papel exacto) |
| 4 | `AVF_INFO\PRV00001.BIN` | **No** | Se pierden fechas/protección/thumbnail de las fotos; el índice se puede reconstruir. No bloquea el IFO del MP4 | VERIFICADO nombre/clase; efecto INFERIDO |
| 5 | `AVF_INFO\OTDISCBN.IND` | No | Solo afecta a *disc burn* | VERIFICADO nombre; efecto INFERIDO |
| 6 | `AVF_INFO\MODELCFG.IND` | No | Configuración de modelo | VERIFICADO nombre; efecto INFERIDO |
| 7 | `AVF_INFO\` (directorio) | **SÍ** (debe existir y ser encontrable) | `Fsys_FindFirst("ms:/AVF_INFO")` → `0x2109`; `IsExistAVIndexDirectory` (`0x7A65F4` → `0x13C0E8`) falla → reconstrucción | VERIFICADO el sondeo/medido; efecto INFERIDO |

**Nota importante**: el `RcsTbl` que lee `RcsBackupTblData` **no es ninguno de estos ficheros**. Es un pack de
sectores con `(userId, backupId)`. Por eso un `Err RcsBackupTblData` (cabecera `0x10`) **no se arregla copiando
`AVF_INFO`**: apunta a la capa de sectores/respaldo. Lo que sí se arregla copiando es un `" Need Salvage"`
(`0x00500003`) o una reconstrucción de índice.

---

## 7. El caso "copiar los clips al PC y devolverlos"

### 7.1 Qué se pierde en ese viaje

| Se pierde | Por qué | Consecuencia |
|---|---|---|
| `AVF_INFO\AVIN0001.INP` | Ningún explorador copia por defecto `AVF_INFO` si solo se arrastra `MP_ROOT` o `PRIVATE`; y muchos tools omiten extensiones desconocidas | **Sin índice AV no hay catálogo de MP4** → el IFO no carga |
| `AVF_INFO\AVIN0001.BNP` | Ídem | Sin respaldo; si el INP se corrompe, no hay recuperación |
| `AVF_INFO\AVIN0001.INT` | Ídem | La tabla interna se reconstruye (o no) |
| `AVF_INFO\PRV00001.BIN` | Fichero "raro" de 10000 B largos; se omite con frecuencia | Fechas/protección/thumbnail de fotos |
| Atributos y *timestamps* | Copiar/pegar cambia `mtime` y el orden de directorio | El journal `RcsTbl` deja de cuadrar → `" Need Salvage"` |
| Sectores reservados del `RcsTbl` | **No son visibles como ficheros**; un copiar/pegar no los reproduce | `Err RcsBackupTblData` (`0x10xxxxxx`) si el pack se perdió |

### 7.2 Cuál explica el fallo

* Si el log real es **`Err RcsBackupTblData`** → el que falla es el **pack de respaldo `RcsTbl`** (`BkRead`), no un
  fichero de `AVF_INFO`. Ningún fichero copiado lo arregla; hay que dejar que la cámara reescriba ese pack.
* Si el log es **`" Need Salvage"`** (o no hay log y el IFO simplemente no lista) → el que falta es
  **`AVF_INFO\AVIN0001.INP`**. Es el caso clásico de "copié los MP4 y los devolví".
* Si faltan los cuatro ficheros, el primero que hay que reponer es el **INP**; los otros tres son respaldo,
  tabla interna y propiedades.

### 7.3 Reparación mínima sin formatear

1. **R0 (0 riesgo)**: copia íntegra de `AVF_INFO\` y `MP_ROOT\*\*.MP4` con tamaños y `mtime` **antes de tocar nada**.
2. **R1 (mínimo)**: reponer `AVF_INFO\` completo desde la copia original (los 4 ficheros, mismos nombres y ruta).
   Si no hay copia:
   * Menú → Herramienta tarjeta memoria → **«Recuperar BD imág.»** (dispara `BeginRepair <AVINDEX>` `0x9002BA` →
     `RunInconsistencyAvcMp4Register` `0x7ADB04`; reescribe `AVF_INFO`). **INFERIDO**, no medido.
   * Si no reacciona: renombrar `AVF_INFO` → `AVF_INFO.old` y encender. `IsExistAVIndexDirectory` falla →
     `CreateAVIndexFile` reconstruye escaneando `MP_ROOT\*\*.MP4`. **INFERIDO**; pierde puntos de reanudación y
     renumeración de EntryID.
3. **R2 (bajo)**: renombrar solo `AVIN0001.INP` → `.bak`, dejando `.BNP`/`.INT`, para forzar la restauración desde
   el respaldo (`AVINDEX_FILE_RESTORE_*` `0x7C9D48`, `AVINDEX_FILE_ORG_RESCUE_*` `0x7CAC41`).
4. **Verificación** (con la tarjeta en el PC): `AVF_INFO\AVIN0001.INP` existe, tamaño ≠ 0 y `mtime` nuevo;
   `grep -a MAH0 AVF_INFO/AVIN0001.INP` encuentra el nombre del clip; la cámara lista los clips.

### 7.4 Reparación segura

**Formatear en la cámara** (Menú → Herramienta tarjeta memoria → Formatear). Borra `DCIM` y `MP_ROOT`, y la cámara
crea `AVF_INFO` y el journal desde cero. Es la única que garantiza un `RcsTbl` coherente. No usar "formatear" en el
PC: reproduce el problema.

---

## 8. Corrección a lo que decía `docs/STATE.md`

`STATE.md` llama a `RcsBackupTblData` "la única lectura real del volumen" y usa `Err RcsBackupTblData` como huella de
"volumen ilegible". Los bytes dicen algo más preciso:

* **No es una lectura de fichero**: es un `BkRead` de un pack de sectores (`RcsTbl`) por `(userId, backupId)`.
* Un `0x10100001` significa **"esa entrada no tiene reader registrado"** (`0x2B39EE` → `0x2B3A28`), no "el fichero
  `AVIN0001.INP` no está".
* Por tanto, `Err RcsBackupTblData` **no** demuestra que la tarjeta sea ilegible ni que falte `AVF_INFO`; demuestra
  que falló la capa de respaldo/`pack`. Para culpar a `AVF_INFO` hay que usar la rama `" Need Salvage"` o la
  reconstrucción del índice, no esta línea.

Mantengo la cadena de orden (`MountCmd` → `CheckSalvageStatus` → gate `0x64C298` → `CreateAndLoad` → `LoadSub` →
`Load` → `FlashLoadForMsv` → `RcsBackupTblData`) tal como estaba; lo que cambia es la interpretación del último paso.

---

## 9. Límites / NO_VERIFICADO

* **NO_VERIFICADO** el subcódigo `0x10xxxxxx` exacto que produjo el log: `0x10100001`, `0x10100002`, `0x10100003`
  (tolerado), `0x10100004…7`, `0x10800010`. El log solo imprime que la cabecera es `0x10`.
* **NO_VERIFICADO** el medio físico del pack `RcsTbl`: el código lo resuelve con
  `GetOperationModeFromUserIDAndMediaID` (`0x2B2DF4`) y `GetSectorHandleFromOperatioModeAndMediaID` (`0x2B3000`);
  no se ha podido fijar si el `mediaID` es la tarjeta o la NVRAM interna. Lo que sí está verificado es que **no es
  un `open()` de `AVF_INFO`**.
* **NO_VERIFICADO** el papel exacto de `AVIN0001.INT` (descriptor propio en `0x9D12C0`, campos `01 01 A0 00 78 00`)
  y el de `PRV00001.BIN` más allá de "propiedades".
* **NO_VERIFICADO** que la rejilla de miniaturas de foto no pase por el IFO en *todas* las rutas de firmware: el
  barrido de llamantes es de `libmpr.so`; podría haber otra imagen (`libobj`, `im.elf`) con su propio listado.
* Las cifras de 7 clips, duraciones y `MAH04198` son del informe [film-pb-1-sub-tarjeta-20261127.md](film-pb-1-sub-tarjeta-20261127.md);
  no se han vuelto a medir aquí.
