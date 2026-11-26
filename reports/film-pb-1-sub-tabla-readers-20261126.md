# FILM-PB-1 / sub-tabla-readers — quién registra `0xA3699C` y por qué `[+4]` queda 0

26-11-2026 · Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`).
**VA = VA del ELF (base 0)**; `.text` `0x00120228-0x007A3E84`, `.rodata` `0x007A3E90-0x00956750`,
`.data` `0x009C42E8-0x009DF808`, `.bss` `0x009DF808-0x00ADBB04` (todas las VA citadas caen dentro).

Estático (capstone Thumb-2, `elfhelper.py`) **+ lectura del volcado de RAM real**
`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin` (estado **que sí falla**: es el volcado que trae el anillo
con `Err RcsBackupTblData`). Sin cámara, sin tarjeta, sin ejecutar firmware.
Evidencia: [reports/evidence/film-pb-1-sub-tabla-readers-20261126/](evidence/film-pb-1-sub-tabla-readers-20261126/).

---

## 0. Resumen (≤20 líneas)

1. La tabla **no es una "tabla de readers"**: es la **Sector Manager Info Table** del *Flash Backup Manager* (FBM) de `libmpr`. El campo `+4` **no es un puntero a función: es el handle de sector de `FlashLib`**. Corrige `sub-mp4ifo-load` §9 y §10.
2. Geometría: **30 entradas de 0x14 B** (idx `0..0x1D`), `0xA3699C..0xA36BF3`. `+0` sector/fileType · `+4` handle · `+8` flag válido · `+0xC`/`+0x10` 2 bytes del primer pack.
3. La rellena **`FBM::Init` `0x2B4820`**, llamada desde **`MprIf::Create` `0x71CC20`** (`0x7126E6`), justo después de `FlashLib::Init`. **No** la rellena un constructor estático, ni `MprIf::Create` por sí mismo, ni el montaje del medio, ni WBI.
4. Recorre la lista estática de 30 sectores **`0x9D2380`**; por sector exige `CheckExistSector==0x45`, `OpenSector32` con handle≠0, `GetSectorInfo` OK y estado ∈{3,4}. Si todo pasa → `SetSectorManagerTable` (`0x2B45A8`) con `+4=handle`, `+8=1`; si falla cualquiera → rama `0x2B4918` con `+4=handle(o 0)`, `+8=+0xC=0`.
5. Escritores (4, exhaustivo): el bucle inline de `Init`/`WarmBootInit`, `SetSectorManagerTable`, `SetSectorManagerInfo` (`0x2B208C`, **solo consola `SetSMI`**) y `DeleteAllSectors` (`0x2B2974`). Ninguno depende del MP4 ni del contenido de la tarjeta.
6. **En la cámara real, 4 de 30 entradas tienen `+4≠0`** (sectores `0x30`, `0x62`, `0xA0`, `0xB2`). Las de foto (`0x90/0x91/0x92`) y 5 de las 7 de vídeo están a **0**.
7. `0x10100001` = "esa entrada no tiene sector abierto", no "falta código". El índice se calcula en runtime: `(userID,mediaID)` → sector (`0x9D23FC`) → posición en `0x9D2380`.
8. Hay **dos** caminos a `[+4]==0`: (a) idx válido con entrada vacía; (b) `(userID,mediaID)` sin fila → `GetFileType` falla y `0x2B2FCC` **salta el `strb`**: el idx es basura (o `0xFF` de `0x2B2FB4`) y se lee fuera de la tabla.
9. Conclusión: el fallo no es de orden de arranque. Es **estado del flash interno**: los sectores FBM del medio tarjeta no existen/no están en estado válido, y la tabla es un *snapshot* tomado una sola vez en `MprIf::Create`.
10. Comprobación en cámara (ya existe en el firmware): comando de consola FBM **`View`** (`0x2B59CA`→`0x2B3260`) imprime las 30 entradas con handle y `USE/NO_USE`, y luego la lista de usuarios con su `[index:%d]` y el error. Alternativas: leer `base+0xA3699C` en RAM, o poner a 1 el flag `0xA36C14` para que `Init` la vuelque al log.

---

## 1. Geometría de `0xA3699C`

`0xA3699C` está en `.bss` (el cargador la deja a 0). No hay **ninguna** referencia por `movw/movt`: todo el acceso
va por *literal pool*. Buscando en todo el fichero el u32 `0x00A3699C` aparecen **24 pools**, y resolviendo qué
instrucción `ldr rX,[pc,#imm]` los carga salen **27 instrucciones**, todas dentro de `0x2B20A4..0x2B4884`
(un solo módulo: FBM) — listado completo en `07-referencias-27.txt`.

| Campo | Tipo | Significado | Escritor (VA de la instrucción) |
|---|---|---|---|
| `+0x00` | u32 | **sector / fileType** (`0x9D2380[i]`), comparado con `ldr` de 32 b en `0x2B2EAA/0x2B2ED8/0x2B2F96` | `0x2B20AC`, `0x2B45F2`, `0x2B4724`, `0x2B4924` |
| `+0x04` | u32 | **handle de sector FlashLib** (de `OpenSector32`) | `0x2B20B2`, `0x2B45FC`, `0x2B4730`, `0x2B4930`, `0x2B298A` (a 0) |
| `+0x08` | u32 | **registrado/válido**: 1 solo si `SetSectorManagerTable` tuvo éxito | `0x2B20B4`, `0x2B45F6`(=1), `0x2B472A`(=0), `0x2B4928`(=0), `0x2B2986`(=0) |
| `+0x0C` | u32 | byte 0 del primer pack del sector | `0x2B20B8`, `0x2B45FE`, `0x2B472C`(=0), `0x2B492C`(=0), `0x2B2988`(=0) |
| `+0x10` | u32 | byte 1 del primer pack del sector | **solo** `0x2B4600` |

**Tamaño de entrada = 0x14**, fijado por la constante `0x14` presente en *todas* las referencias
(`movs r3,#0x14; muls`, `mla r3,r3,r5,sb`, `mul r6,r6,fp`…). **Nº de índices = 30**:

- `SetSectorManagerInfo` `0x2B20A0` `cmp r4,#0x1d` / `0x2B20A2` `bhi` → rechaza `idx > 0x1D`.
- `Init`/`WarmBootInit` recorren la lista `0x9D2380` (30 u32 + terminador `-1`).
- Las tres búsquedas acotan `cmp r5,#0x1e` (`0x2B2EC6`, `0x2B2EF0`, `0x2B2FAE`).

⇒ `30 × 0x14 = 0x258` ⇒ tabla `0xA3699C..0xA36BF3`. Índice ↔ sector (lista estática `0x9D2380`):

```
idx  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
sec 10 11 12 20 21 28 29 2c 2d 30 31 38 39 40 60 61 68 6c 62 63 90 91 92 a0 b1 b2 b3 b8 bc bd
```

**`+4` es un handle, no un puntero a función.** Cadena de prueba: `0x2B39EC ldr r2,[r2,#4]` → `0x2B39FE str r2,[r3,#4]`
(copia a `dst+4`) → `0x2B3A20 bl ReadNextPackData` → `0x2B3976 ldr r1,[r4,#4]` → `0x2B397E bl ReadPack 0x2B267C`
→ `0x2B26A4 mov r0,sl` + `0x2B26AA blx FlashLib::ChangeSeekPoint(m,base,i)`. Es decir: `+4` acaba siendo el **primer
argumento de una llamada a `FlashLib`**, y en la cámara vale `1,3,4,5` (handles pequeños, §5). Nunca se ejecuta como código.

---

## 2. Escritores de la tabla (exhaustivo) y quién los llama

Las 27 referencias se reparten en 4 escritores; el resto son lectores (`Get*Status`, `GetRemainSize`, `Read*PackData`,
`Write*Pack`, `Destroy`, `ChangeSector`, `GetFileType`, `…TableIndex…`, `View`).

| # | Función | VA | Qué escribe | Llamantes |
|---|---|---|---|---|
| 1 | `SetSectorManagerInfo` | `0x2B208C` | `+0,+4,+8,+0xC` desde argumentos | **solo** `0x2B5A3A` = comando de consola `SetSMI` (`0x2B59DC`) |
| 2 | `SetSectorManagerTable` | `0x2B45A8` | `+0, +4=handle, +8=1, +0xC, +0x10` (leyendo el primer pack) | `0x2B46D0` (`WarmBootInit`) y `0x2B48D0` (`Init`) |
| 3 | inline en `Init` / `WarmBootInit` | `0x2B4918` / `0x2B4718` | `+0=sector`, `+4=handle o 0`, `+8=0`, `+0xC=0` | — (es el propio bucle) |
| 4 | `DeleteAllSectors` | `0x2B2974` | pone a 0 `+4,+8,+0xC` de 31 entradas (`add.w r2,r3,#0x26c`) | ninguno en `.text` (solo por puntero/consola) |

Instrucciones clave (transcritas en `02-…`, `03-…`, `04-…`, `05-…`, `06-…`):

```
; #1 SetSectorManagerInfo 0x2B208C  (traza "SetSectorManagerInfo")
002b20a0  cmp  r4,#0x1d  / 002b20a2 bhi -> devuelve 1
002b20a4  ldr  r2,=0xA3699C
002b20a6  movs r3,#0x14   002b20a8 muls r4,r3,r4   002b20aa adds r3,r2,r4
002b20ac  str  r5,[r2,r4]       ; +0x00 = arg1
002b20b2  str  r6,[r3,#4]       ; +0x04 = arg2
002b20b4  str.w r8,[r3,#8]      ; +0x08 = arg3
002b20b8  str  r2,[r3,#0xc]     ; +0x0c = arg4 ([sp+0x18])

; #2 SetSectorManagerTable 0x2B45A8  (traza homónima)
002b45e0  bl   0x2B3948         ; ReadNextPackData(ctx{sector,handle}, ...)
002b45e8  ldr  r1,=0xA3699C
002b45ee  muls r6,r3,r6 (0x14)  002b45f0 adds r3,r1,r6
002b45f2  str  r5,[r1,r6]       ; +0x00 = sector (u16)
002b45f6  str  r1,[r3,#8]  (r1=1) ; +0x08 = 1 "registrado"
002b45fc  str  r4,[r3,#4]       ; +0x04 = handle
002b45fe  str  r1,[r3,#0xc]     ; +0x0c = byte0 del primer pack
002b4600  str  r2,[r3,#0x10]    ; +0x10 = byte1 del primer pack

; #3 rama de fallo del bucle (Init 0x2B4820, idéntica en WarmBootInit 0x2B4624)
002b487c  ldr.w r0,[r8,r5,lsl #2] (=sector) ; 002b4880 blx FlashLib::CheckExistSector
002b4888  cmp  r0,#0x45   / 002b488a bne 0x2B4918     -> rama de fallo
002b4896  blx  FlashLib::OpenSector32(sector,0,&handle)
002b48a6  cbnz r6,0x2B48AC / 002b48A8 ldr r0,[r7,#0x24] / cbz -> 0x2B48AC  (handle 0 = fallo)
002b48b6  bl   0x2B2480  (GetSectorInfo -> FBS_INFO en [r7+4])
002b48be  ldrh r3,[r7,#6] ; subs r3,#3 ; cmp r3,#1 ; bhi 0x2B4918   (estado 3 o 4)
002b48d0  bl   0x2B45A8  (SetSectorManagerTable)   ; éxito
...
002b4918  str  r1,[sb,r2]      ; +0x00 = sector
002b4928  str  r2,[r3,#8]  (0)  ; +0x08 = 0  <-- INVÁLIDA
002b492c  str  r2,[r3,#0xc](0)  ; +0x0c = 0
002b492e  ldr  r2,[r7,#0x24]
002b4930  str  r2,[r3,#4]      ; +0x04 = handle ... o 0 si no se abrió
```

Detalle que importa: en la rama de fallo el handle se **guarda igual** (`0x2B4930`), pero si el sector no existía el
handle venía de `OpenSector32`, que nunca se llamó: `0x2B4876 str r6,[r7,#0x24]` con `r6=0` lo dejó a 0. Por eso
"sector inexistente" y "sector no abierto" producen exactamente el mismo `+4==0`.

---

## 3. Cuándo se rellena y de qué depende

```
MprIf::Create(CreateParam*, MprIf**, bool)        0x71CC20   (llamada a 0x712530 en 0x71CC7A)
  └ 0x712530
       ├ blx FlashLib::Init(SystemType)           0x7126E2 -> 0x11DFE8
       ├ bl  FBM::Init                            0x7126E6 -> 0x2B4820   <== rellena 0xA3699C
       │    ├ ldr  r8,=0x9D2380   (30 sectores)   0x2B4936
       │    ├ por sector: CheckExistSector / OpenSector32 / GetSectorInfo
       │    ├ SetSectorManagerTable 0x2B45A8  (o rama de fallo 0x2B4918)
       │    ├ blx FlashLib::SetBackupMgrCallback(0x2B47E1)   0x2B4946
       │    ├ blx FlashLib::ValidateSync / Sync              0x2B4954/0x2B4958
       │    └ si [0xA36C14]!=0 -> bl 0x2B3260   (volcado de la tabla al log)  0x2B495C
       └ bl 0x4A8864, 0x484B1C, 0x46FB08, 0x512534, ... (resto de subsistemas)  0x7126EA+
```

- El único constructor estático de la zona es la entrada `[02]` de `.init_array` = **`0x2B4A38`**, y **no escribe la
  tabla**: sólo construye los semáforos RWB `0xA36980`, `0x9E691C`, `0x9E6938`, `0x9E6954` (`Semaphore::Semaphore` +
  `__aeabi_atexit`, `0x2B4A44-0x2B4A8E`). El llenado de `0xA3699C` es siempre explícito, por `Init`/`WarmBootInit`.
- **No** depende del montaje del medio, de la tarjeta, ni de WBI: sólo de `FlashLib` (flash interno) y de la lista
  estática `0x9D2380`.
- `WarmBootInit` `0x2B4624` (idéntico, con `FlashLib::WarmBootInit` delante, envoltorio `0x2B4AAC`) es la variante
  de *resume*; ningún `bl` de `.text` llega a `0x2B4AAC` — se invoca por puntero (callback de `FlashLib`).
- Consecuencia operativa: la tabla es un **snapshot** tomado una vez por proceso. Si los sectores se crean o se
  reparan después (Darwin / `CheckAndRepairFlashBackup`), la tabla **no** se refresca hasta reiniciar MPR.

---

## 4. Qué índice usa cada consumidor y por qué puede quedar a 0

El consumidor nunca pide "el índice de MSV": pide `(userID, mediaID)` y FBM lo traduce con la tabla estática
**`0x9D23FC`** (fila de `0x18` B, 37 filas, terminador `+0==0`):

`+0 = userID · +4 = mediaID · +8 = fileType (sector) · +0xC = OM`
(`GetFileType` `0x2B2B18` busca `+0/+4` y devuelve `+8`; `GetOperationModeFromUserIDAndMediaID` `0x2B2DF4` devuelve `+0xC`).

Después: `GetSectorManagerInfoTableIndexFromUserID` `0x2B2F48` recorre las 30 entradas y devuelve **la primera cuyo
`+0 == fileType`** (no comprueba `+8`); `GetNewSectorManagerInfoTableIndexFromUserID` `0x2B2E54` sí distingue
"ocupada" (`+8!=0` → `0x10800010`) de "libre" (`+8==0`).

| Consumidor | (userID, mediaID) | sector | idx |
|---|---|---|---|
| Foto / DCF sobre tarjeta | `(0x10,7)` `(0x04,7)` `(0x21,7)` | `0x90 0x91` | **20, 21** |
| Foto `(0x20,7)` | | `0x92` | **22** |
| Vídeo MP4/XAVC (índice compartido) | `(0x22,8)` | `0xA0` | **23** |
| Vídeo por medio | `(0x23, 2..7)` | `0xB1 0xB2 0xB3 0xB8 0xBC 0xBD` | **24…29** |
| Resto (medios 1..6, aún/vídeo/DVD) | `(0x10 0x04 0x21 0x20 0x01 0x30, 1..6)` | `0x10…0x6C` | 0…19 |

En el camino real del IFO la petición llega así: `0x3AFA94` (wrapper MSV, imprime `Err RcsBackupTblData`) →
`0x35EA1C` → **`0x35E04C` → `0x35E0F4 bl ReadFirstPackData`**, pasando `r0=[obj+0x4088]`, `r1=[obj+0x408c]`
(`0x35E0EC/0x35E0F0`). Es decir, el par `(userID, mediaID)` lo aporta el **objeto de medio**, no una constante:
**NO_VERIFICADO** cuáles son exactamente para el MP4 (no hay `str` directo a `+0x4088/+0x408c` en todo `.text`;
se rellenan por copia/construcción del objeto de 0x3171C B). Lo que sí queda fijado es el conjunto de índices
posibles de la tabla anterior.

Formas de que `[0xA3699C+0x14·idx+4] == 0`:

1. **Sector inexistente en el flash interno** (`CheckExistSector != 0x45`) → rama `0x2B4918` con handle 0.
   Es lo que se ve en `0x2B4688/0x2B4888` (`cmp r0,#0x45`).
2. **No se pudo abrir** (`OpenSector32` error o handle 0, `0x2B48A8-0x2B48AC`).
3. **`GetSectorInfo` falla** (`0x2B48BC`) o el **estado no es 3 ni 4** (`0x2B48BE-0x2B48C6`).
4. **Índice fuera de rango**: `(userID,mediaID)` sin fila en `0x9D23FC` → `GetFileType` devuelve `0x10800010`,
   `0x2B2F86 cbnz r4,#0x2B2FCC` **se salta el `strb.w r5,[r8]`** y el byte de índice queda con basura de pila
   (o `0xFF` de `0x2B2FB4`) → `0x2B39EC` lee fuera de la tabla (`0xFF·0x14 = 0x1FEC` → `0xA38988`, dentro de `.bss`).
5. `DeleteAllSectors` `0x2B2974` (`ForcedClearAllSectors`) vacía las 31 primeras.

Lo que **no** hace falta para nada de esto: WBI, la tarjeta, el tamaño del MP4, el `TvSystem` o el orden de
`MprIf::Create` respecto a otros subsistemas (FBM::Init es el 2º paso, justo tras `FlashLib::Init`).

---

## 5. Estado real medido en la cámara (volcado 20-10)

`ram-servicio-20261020/ram_0x80000000.bin`, proceso MPR con **base `0x8A5CB000`** (⇒ tabla en `0x8B00199C`).
Se localizó sin conocer la base: barrido con paso `0x14` buscando la secuencia exacta de los 30 sectores; **un solo
acierto en 1 GiB**. Anclas que confirman la base: `base+0xA3697C = 0x00073108` (objeto de `new`, `0x2B464C`),
`base+0xA36C20 = 0x0749B970` (puntero al anillo, `0x2B4634`), `base+0xA36970/74 = 7 / 0xA` (últimos `+0xC` copiados,
`0x2B48FA`). El `.text`/`.data` file-backed de ese proceso no está en el volcado (lee 0) — no afecta a `.bss`.

```
[00] 10  +4=00000000  +8=0 | [10] 31  0  0 | [20] 90  0  0 | [24] b1  0  0
[01] 11  0  0            | [11] 38  0  0   | [21] 91  0  0 | [25] b2  5  1  (c=0A)
[02] 12  0  0            | [12] 39  0  0   | [22] 92  0  0 | [26] b3  0  0
[03] 20  0  0            | [13] 40  0  0   | [23] a0  1  1 (c=09,10=08) | [27] b8  0  0
[04] 21  0  0            | [14] 60  0  0   |                 | [28] bc  0  0
[05] 28  0  0            | [15] 61  0  0   |                 | [29] bd  0  0
[06] 29  0  0            | [16] 68  0  0   |
[07] 2c  0  0            | [17] 6c  0  0   |
[08] 2d  0  0            | [18] 62  3  1 (c=07)
[09] 30  4  1 (c=04)     | [19] 63  0  0
```

**4 de 30 con `+4 != 0`** (`0x30`, `0x62`, `0xA0`, `0xB2`); **26 a 0**. Y este volcado es el *mismo* que contiene el
anillo con `[MSV][MS1]Err RcsBackupTblData` y `[DCF][MS1]Err RcsBackupTblData`: la correlación es directa, del mismo
snapshot. Encaja con lo observado: **foto** (idx 20/21/22) tolera el fallo —la miniatura sale del fichero por `dfs`— y
**vídeo** (idx 24…29, p.ej. `0xBD` para el medio tarjeta) no tiene handle ⇒ el IFO no se carga y no hay reproducción.

Que sólo sobrevivan 4 sectores (y con handles `1,3,4,5`) apunta a un flash interno con la mayor parte de los sectores
FBM **borrados o no válidos**, no a un problema de software: el código de registro funciona (4 entradas las registró
bien, con su primer pack leído). Esto reencuadra el síntoma desde "falta un puntero" hacia "faltan sectores de respaldo
en el flash interno de esta unidad".

---

## 6. Cómo se comprueba en cámara

1. **Comando de consola ya existente (lo más rápido).** La tabla de comandos FBM está en `.rodata`
   `0x7E8014..0x7E8060` con los nombres `InitB`, `ChgSec`, `SetOM`, `SetSMI`, **`View`** (uso
   `Display Sector Managet Information`), `ASV` (`Display All Sector Status`), `GASI`, `WDS`, `Flush`, `Delete[All]`,
   `Close`, `ReadPD`, `ReadAllPD`, `WritePack`, `fbm ltc` y los handlers `0x2B5AF4/0x2B5A60/0x2B59DC/0x2B59CA/`
   `0x2B59B8/0x2B5AA8/0x2B5E08/0x2B5DF0`. El volcado es **`0x2B59CA` → `0x2B3260`** (`push {r7,lr}; ldr r0,[r1];
   bl printf; bl 0x2B3260`) y el comando que lo dispara aparece rotulado `View`; el emparejamiento exacto
   nombre↔handler de la tabla se confirma en la cámara con un `help` de esa consola.
   `0x2B3260` imprime:
   ```
     Sector Manager Info Table:
   [    SName     (    ID    )]|[  Handle  ]|[status ]|[   OM   ][Index]
    <nombre>(0x%08x)   0x%08x   USE|NO_USE   <OM>     %02d     x30
     User list:
    <userID> <mediaID> [index:%d]: valid data:%d / remain:%d / base limit:%d / ...
    <userID> <mediaID> [index:??]: GetSectorManagerInfoTableIndexFromUserID() Error(0x%x)
   ```
   Basta contar cuántas líneas no dicen `NO_USE` / no tienen `0x00000000` en la columna `Handle`, y mirar qué fila de
   `User list` devuelve `Error(0x10100001)` — eso resuelve de golpe el §4 (a) vs (b) y da el `(userID,mediaID)` real del MP4.
2. **Volcado de RAM.** Localizar la base de `libmpr` (`/proc/<pid>/maps` del proceso MPR, o el barrido del §5) y leer
   `base + 0xA3699C`, 30 × 0x14 B; contar `u32(+4) != 0`. Equivalente a `h = u32(base+0xA3699C+0x14*idx+4); h==0 ⇒ 0x10100001`.
3. **Por log, sin consola.** Poner a 1 el byte `0xA36C14` (flag de vista, `0x2B495C` en `Init` y `0x2B4756` en
   `WarmBootInit`): el propio `Init` llama a `0x2B3260` y vuelca la tabla al anillo en el arranque.
4. **Trazar el punto exacto.** Shim/breakpoint en `0x2B39E8-0x2B39EE` (`ldrb r2,[r7,#0xf]` = idx, `ldr r2,[r2,#4]` = `+4`):
   imprimir `idx` y `+4` justo antes del `cbz` que devuelve `0x10100001`. Es el mismo patrón de traza que ya se usa
   para `0x6F0D4C`.

---

## 7. Correcciones a lo publicado

1. **`sub-mp4ifo-load` §9**: "+4 es puntero a rutina de lectura / 'entrada sin rutina'". **Falso**: `+4` es el handle
   de sector `FlashLib`; `0x10100001` = "entrada sin sector abierto". El mismo código devuelve `0x10100003` cuando el
   `seekPoint` se sale del sector (`0x2B26FC`), lo que confirma que son códigos de acceso a sector, no de *dispatch*.
2. **`sub-mp4ifo-load` §9 y §20**: "nadie la registra / NO_VERIFICADO quién y cuándo". Ya está: `FBM::Init` `0x2B4820`
   desde `MprIf::Create`, más `WarmBootInit` `0x2B4624`; `0x2B208C` (`SetSectorManagerInfo`) es sólo la API de consola.
3. **`sub-mp4ifo-load` §7.3**: el mapeo `(userId,backupId) → idx` **sí** se ha verificado aquí: la tabla `0x9D23FC`
   (paso `0x18`, no `0x10`) tiene `+0=userID, +4=mediaID, +8=sector, +0xC=OM`; el `idx` sale de buscar `+0 == +8`.
   El aviso de §7.3 ("parece compartida con otro uso") provenía de volcarla con paso equivocado.
4. **La hipótesis de "tabla vacía porque nadie la registra"** queda sustituida por: **"casi vacía porque el flash
   interno no tiene esos sectores en estado válido"** (26/30 a 0, medido en la cámara).

---

## 8. Verificación y reproducción

```bash
B=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so
.venv/bin/python3 reports/evidence/film-pb-1-sub-tabla-readers-20261126/refs_table.py      # 27 referencias
.venv/bin/python3 reports/evidence/film-pb-1-sub-tabla-readers-20261126/namemap.py 0x2B1C00 0x2B5100
.venv/bin/python3 reports/evidence/film-pb-1-sub-tabla-readers-20261126/exidx.py           # inicios via .ARM.exidx
.venv/bin/python3 reports/evidence/film-pb-1-sub-tabla-readers-20261126/mapping.py         # idx<->sector<->usuario + RAM
.venv/bin/python3 reports/evidence/film-pb-1-sub-tabla-readers-20261126/ram_scan_np2.py    # localiza la tabla en 1 GiB
.venv/bin/python3 /tmp/elfhelper.py $B dis 0x2b208c 0x40    # SetSectorManagerInfo
.venv/bin/python3 /tmp/elfhelper.py $B dis 0x2b45a8 0x7c    # SetSectorManagerTable
.venv/bin/python3 /tmp/elfhelper.py $B dis 0x2b4820 0x130   # FBM::Init
.venv/bin/python3 /tmp/elfhelper.py $B dis 0x2b3260 0x140   # View / volcado de la tabla
```

| Evidencia | Contenido |
|---|---|
| `01-geometria-tabla.txt` | 0x14, 30 índices, campos, lista `0x9D2380`, globals vecinos |
| `02-set-sectormanagerinfo.txt` | escritor #1 + su único llamante (consola `SetSMI`) |
| `03-set-sectormanagertable.txt` | escritor #2 (registro real con handle y primer pack) |
| `04-fbm-init.txt` | `FBM::Init`, rama de fallo y cadena `MprIf::Create → 0x712530` |
| `05-warmbootinit.txt` | variante *resume* + hilo con `ReadFirstPackData(0x21,3)` |
| `06-deleteallsectors.txt` | escritor #4 (vaciado de 31 entradas) |
| `07-referencias-27.txt` | las 27 cargas del literal con 6 instrucciones de contexto |
| `08-lectura-0x2b39b8.txt` | `ReadFirstPackData`/`ReadNextPackData` y el camino de `+4` a `FlashLib` |
| `09-tabla-usuarios-0x9d23fc.txt` | 37 filas `(userID,mediaID)→sector,OM` + mapa de índices |
| `10-ram-camara-20261020.txt` | **la tabla en la RAM real: 4 de 30 con handle** |
| `11-nombres-funciones-fbm.txt` | mapa de funciones FBM con nombre de traza |
| `elfhelper.py` `exidx.py` `namemap.py` `refs_table.py` `whois.py` `mapping.py` `ram_scan_np2.py` | scripts usados |

## 9. Límites

- El volcado del 20-10 es **pre-CFW** y le faltan las páginas file-backed (`.text`/`.rodata`/`.data` leen 0); la tabla,
  que es `.bss`, sí está entera. Base `0x8A5CB000` deducida del propio contenido y confirmada con 3 vecinos.
- **NO_VERIFICADO**: el `(userID, mediaID)` concreto que usa el MP4 en runtime (viene de `[obj+0x4088]/[obj+0x408c]`,
  objeto de 0x3171C B); `0xA36C0C` vale 3 en el volcado mientras ninguna entrada tiene `+0x10==3` (posible volcado no
  atómico); y `0x45` como "sector existe" se deduce de la única comparación existente, no de la implementación de
  `FlashLib` (importada por PLT, su proveedor no está entre los `.so` de `nflasha15` en el árbol extraído).
- No se ha tocado la cámara ni la tarjeta. El "arreglo" no se propone aquí: la vía lógica sería re-crear/registrar los
  sectores FBM del flash interno (`CreateSector`/`InitB`/`CheckAndRepairFlashBackup`) antes de reiniciar MPR.
