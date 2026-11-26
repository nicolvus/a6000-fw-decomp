# FILM-PB-1 — Sub-auditoría: de dónde sale el tamaño del área del reproductor y por qué puede pedirse 0

Fecha: 26-11-2026. Estático, sin cámara y sin flashear. Objetos:

- `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
  (Thumb-2; **VA = offset de fichero** en el primer LOAD, igual que en los informes previos).
- `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/kmod/dmm.ko`
  (ELF32 ARM *relocatable*, **con símbolos**; aquí las direcciones son **offsets de sección**
  —`.text` 0x0-0xFAFC, `.init.text` 0x0-0x140—, no VA de ejecución).
- Cargadores: `dev/nflasha7_unpacked_unpacked/sbin/init` y `lib/libIMDB.so`.

Herramientas: `python3 /tmp/elfhelper.py` (capstone, Thumb) y `/tmp/kodis.py` (ARM + reubicaciones),
más lectura directa de `.rodata`/`.data`. **No se ha usado `mcp_rea` para binarios.**

## Resumen (≤20 líneas)

1. `StreamCache::SetArea` (0x7594E0) tiene **10 llamadas**; dos leen el par dirección/tamaño de un
   descriptor `MemInfo` en los campos **+0x138 / +0x140**: `ThumbnailRecorder::SetMemoryTable`
   (0x330120-0x330128) y `SetUpPlayerInstance` (0x4392D2-0x4392D6 → 0x439456-0x43945C).
2. Ese descriptor **no se construye en el reproductor**: es un singleton en `.bss`, **0xA4F368**,
   con entradas de **0x18 B** (`+0`=vAdrs, `+4`=pAdrs/offset, `+8`=**size**, `+0x10`=offset 64 bits).
   `0x138/0x18 = 13` y `0x140 = 13*0x18+8`; `0x108/0x110` es la entrada **11** (movie).
3. Lo rellena `MemInfo::DistributeBufInfo` (0x5F703C): escrituras en **0x5F73BE/0x5F73CE** (`+0`),
   **0x5F73DC** (`+4`), **0x5F73E0** (`+8` = tamaño) y **0x5F73C4/0x5F73D6** (`+0x10`).
4. El contenido sale de una **tabla estática por modo** (`mp_modeTblForBufTbl`, 0x8D87E8):
   «Still Pb» (modeId 2) → **0x9DBD20**, «Movie Pb» (1) → **0x9DB0E4**, «Still Rec» (4) → **0x9DA8E0**.
5. El modo se elige en `MemInfo::Type2Mode` (0x5F699C) con `(type, subType)` y **`m_systemType`**
   (`[0x9DEFE0]`, valor de fichero 1) usando tablas `.data`: 0x9DE7C8 / 0x9DE898 / 0x9DEDC0.
6. Las direcciones físicas se mmap'ean con `MemConfig::Mmap` (0x5F6544) sobre **/dev/stream** o
   /dev/mem + `Fsys_SetStreamArea`. **El tamaño NO se pide al DMM ni al gestor de memoria**: es
   tabla de configuración estática (modelo/sistema/modo).
7. `MemInfo::Init` (0x5F74D4, llamado desde 0x7125CE) **no toca 0xA4F368**: solo abre /dev/stream2
   y rellena la tabla de áreas FIJAS (0xA4FD88, `memset(…,0,0x108)` en 0x5F7644-0x5F764C).
8. Por eso **`0` = campo nunca escrito** (la tabla nace a cero en `.bss`), no un cálculo que salga 0.
9. Y también **`0` = campo borrado**: `0x5F63CA(entrada,0)` pone a cero `+0/+4/+8/+0x10`
   (0x5F63D4-0x5F63DA) y lo invoca `StreamAreaFree` (0x5F802C) vía `0x5F7EA8([0x9DECAC],0xA4F368,mask)`
   (0x5F804E-0x5F8054) para las entradas cuyo `areaType` casa con la máscara de `0x5F685C`.
10. Tercera vía: `setupMode` fuera de 1..5 → `SetArea(0,0,1)` **literal** en 0x43944E-0x43945C.
11. Orden: antes de `StreamAreaAllocate` (0x5F7BE8) o `ChangeAllocate` (0x5F7F1C) para el modo
    still no hay valor; ambos se invocan desde `GetMemoryInformation` (0x4284AC, 0x428588/0x428594).
12. `dmm.ko` **no interviene** en este tamaño: sirve «units» (`dmm_ctrl_AllocUnit*`, `/proc/udm/*`)
    que libmpr pide por mensajes (`Mem_DmmAccess::SendAndReceiveDmmMsg`, cadenas 0x8DC2C0-0x8DC520).
13. `dmm.ko` carga `DmmConfig=/setting/DmmConfig.bin ` (init de nflasha7, strings 0x29A3/0x29B4) o
    `DmmConfig=/usr/share/dmm/DmmConfig.bin` (libIMDB.so, 0x25B0/0x25BD). **Ninguno existe** en la
    imagen 0700 (`share/dmm` y `setting` están vacíos).
14. Si el fichero no se puede abrir, `dmm_module_GetConfigData` (0x214) devuelve −1 y `init_module`
    llama a `osal_abort` (0x194: mensaje osal cmd 0xE y, si la respuesta es 0, escritura a NULL).
15. No hay *magic* ni CRC del fichero principal (0x370 `crc32` solo se usa en 0x4DC, mapa EXTRA).
    Fallback: `dmm_config_GetConfigData` (0x5140) estado 1 = `ConfigData` integrada en `.rodata`.
16. Conclusión: para que el reproductor pida **0** tiene que estar mal la **tabla de buffers del
    modo** (hueco 13 sin definir para ese sistema/modo, o liberado por `StreamAreaFree`); no es la
    tarjeta, no es la NVRAM del mínimo y no es el DMM.
17. Comprobable sin flashear: subir traza a nivel 5 y buscar en el anillo `CMD(SET_AREA)` (0x93E839),
    `Type2Mode:` (0x8D90C0), `area size failed` (0x8D9E2C) y `StreamAreaFree` (0x8DA930).
18. Todo lo de `dmm.ko` es estático: **NO_VERIFICADO** que la cámara real tenga o no
    `/setting/DmmConfig.bin` y si su contenido es válido.

## 1. Los llamadores de `SetArea` y quién construye el descriptor (objetivo 1)

`SetArea(this=StreamCache*?, …)` se invoca desde estas 10 direcciones (llamadas directas en
`libmpr`):

```
0x330128  0x42d38e  0x42d7d2  0x42d894  0x43945c
0x43f3d0  0x43f472  0x442562  0x44329c  0x759ab4   (0x759ab4 = comando de depuración)
```

Las dos que usan el descriptor `MemInfo` con desplazamiento **+0x138**:

**(a) `ThumbnailRecorder::SetMemoryTable` — función 0x33009C** (comando MPR «setMemTbl»,
tabla de comandos 0x812848 → «Set Memory Table»):

```
330104  ldr r0,=0x00a4b5e8            ; objeto/log
330108  ldr r1,=" type = MemInfo::MEM_TBL_STILL_REC;"
33010a  movs r4,#3                    ; tipo 3 = STILL REC
33010c  bl  0x32ef28                  ; traza
330114  mov r1,r5                     ; 2.º argumento del comando
330116  mov r0,r4                     ; tipo
330118  bl  0x5f8020                  ; MemInfo::ChangeAllocate  -> r0 = MemInfo* (0xA4F368)
33011e  mov r5,r0
330120  ldr.w r0,[r0,#0x138]          ; dirección
330124  ldr.w r1,[r5,#0x140]          ; tamaño
330128  bl  0x7594e0                  ; StreamCache::SetArea(addr,size,save=1)
```

**(b) `SetUpPlayerInstance` — función 0x43910C** (`SetUpPlayerInstance(this, setupMode,
bIsFinalizeMode, mmgrIdForMovie, mmgrIdForStill, …)`; cadenas 0x85AAB7-0x85AB50). El descriptor
llega como **8.º argumento** (`[r7+0x44]` → r5) y la rama que lo usa es la de `setupMode = 2`
(despacho en 0x4391F0, tabla en 0x4391F4; con las otras entradas se usan `+0x108/+0x110` o se salta):

```
4392c6  cmp r5,#0
4392c8  beq.w 0x439460                ; sin descriptor -> no hay SetArea
4392cc  ldr.w r0,[r4,#0xd98]
4392d0  mov r1,r5
4392d2  ldr.w sb,[r5,#0x138]          ; dirección
4392d6  ldr.w r8,[r5,#0x140]          ; tamaño
4392da  bl  0x321f58
439456  mov r0,sb
439458  mov r1,r8
43945a  movs r2,#1
43945c  bl  0x7594e0                  ; SetArea
```

La rama «movie» del mismo `switch` hace lo propio con `[r5+0x108] / [r5+0x110]`
(0x439256-0x43925A → mismo 0x439456). **Quién se lo pasa**: los llamadores de
`SetUpPlayerInstance` guardan ahí el retorno de `GetMemoryInformation` (0x4284AC):

```
4463d6  bl 0x4284ac
4463da  str r0,[r4,#0x34]             ; el MemInfo*
4463e2  str r0,[sp,#0xc]              ; <- 8.º argumento de SetUpPlayerInstance
4463f2  bl 0x43910c
```

y en 0x439694 igual (`str r0,[sp,#0xc]`).

**La cadena que produce el descriptor** (todo en `libmpr`):

| VA | función | qué hace |
|---|---|---|
| 0x4284AC | `GetMemoryInformation(type, contentType, pFlag, modeId)` | traduce `contentType`→`sub` (r6) y salta a una de las dos |
| 0x428588 | `b.w 0x5F7BE8` | si `pFlag != 0` → **StreamAreaAllocate** |
| 0x428594 | `b.w 0x5F7F1C` | si `pFlag == 0` → **ChangeAllocate** |
| 0x5F7BE8 | `MemInfo::StreamAreaAllocate(type,sub,modeId)` | `Type2Mode` (0x5F7C40) → `[0x9DECAC]=areaTblMode` (0x5F7C7A) → `RegistAreaExtList` 0x5F68F8 (0x5F7C7E) → `SetRamMapArea` 0x5F6F28 (0x5F7CB6) → `DistributeBufInfo(areaTblMode, 0xA4F368, [0xA4F0AC])` (0x5F7CEE-0x5F7CF2); éxito → **devuelve 0xA4F368** (0x5F7D26) |
| 0x5F7F1C | `MemInfo::ChangeAllocate(type,sub)` | `Type2Mode` (0x5F7F44); si `[0xA4F0AC]==0` → «cannot change!» (0x8DA8B2) y **devuelve 0** (0x5F7FCC); si no, `DistributeBufInfo` (0x5F7FA0) y **devuelve 0xA4F368** (0x5F7FEA) |
| 0x5F8020 | thunk | `b.w 0x5F7F1C` (el que usa `SetMemoryTable`) |

Es decir: **el descriptor siempre es el mismo objeto global `0xA4F368`**; lo que cambia es qué
entradas quedaron rellenas por la última asignación/cambio de modo.

## 2. De dónde sale el tamaño (objetivo 2)

### 2.1 Formato de la tabla

`DistributeBufInfo(mode, p_bufInfoTbl=0xA4F368, p_RamMapAreaInfo)` (0x5F703C) indexa con
**stride 0x18**:

```
5f71e2  ldr  r0,[r7,#0x30]        ; p_bufInfoTbl
5f71e4  movs r2,#0x18
5f71e6  muls r2,r3,r2             ; índice * 0x18
5f71ea  add.w sl,r0,r2            ; &tabla[idx]
…
5f73be/5f73ce  str  r4|fp,[r2,r1]     ; +0x00 = vAdrs (dirección virtual mapeada)
5f73dc         str.w r8,[sl,#4]       ; +0x04 = pAdrs / offset
5f73e0         str.w r3,[sl,#8]       ; +0x08 = TAMAÑO
5f73c4/5f73d6  strd r0,r1,[sl,#0x10]  ; +0x10 = offset 64 bits
5f73f2-5f7404  bl 0x5f9d8c            ; «set data vAdrs=… pAdrs=… size=… offset=…»
```

El rótulo de los campos lo da el propio `printf` (cadena 0x8D9DCB «set data vAdrs=0x%08lx
pAdrs=0x%08lx size=0x%08lx offset=0x%08lx») y el uso lo confirma: los dos clientes leen
`[X+0x138]` como **dirección** y `[X+0x140]` como **tamaño**, con `0x138 = 13*0x18` y
`0x140 = 13*0x18+8`.

### 2.2 La fuente es una tabla estática, no un cálculo

`MemInfo::Init` (0x5F74D4) fija el índice de tablas de modo:

```
5f755c  ldr r3,=0x00a4f0a4
5f7564  ldr r2,=0x008d87e8        ; mp_modeTblForBufTbl (.rodata)
5f7566  str r2,[r3]               ; [0xA4F0A4] = 0x8D87E8
```

Pares `{puntero a definición, modeId}` en **0x8D87E8**:

| entrada | def | modeId | modo (nombre en 0x9DF090) |
|---|---|---|---|
| 0x8D87E8 | 0x9DE6F0 | 0 | (modo 0) |
| 0x8D87F0 | **0x9DBD20** | **2** | **«Still Pb»** |
| 0x8D87F8 | **0x9DB0E4** | **1** | **«Movie Pb»** |
| 0x8D8808 | **0x9DA8E0** | **4** | **«Still Rec»** |
| … | … | … | hasta modeId 21 «Mass Strage» |

La selección del modo la hace `MemInfo::Type2Mode` (0x5F699C):

```
5f69bc  ldr  r3,[r6]              ; r6 = 0x9DEFE0 -> m_systemType
5f69be  cmp  r3,#1 / cmp r3,#2 / cbnz
5f69c8  …                         ; sysType 0 -> tabla 0x9DE7C8
5f69d2  …                         ; sysType 1 -> tabla 0x9DE898 (y área fija 0x11)
5f69de  …                         ; sysType 2 -> tabla 0x9DEDC0
5f69ea  cmp  sb,r2 / 5f69f4 cmp r8,r2   ; (type, subType); subType==8 = comodín
5f69fc  str  r2,[r4]              ; ramMapAreaMode
5f6a00  str  r3,[r5]              ; areaTblMode
5f6a30  «[MemInfo]not found mode» (0x8D910F)
```

Entradas relevantes de esas tablas (`{type, subType, areaTblMode, ramMapAreaMode}`, terminadas
por `type==0x20`):

| sistema | type | sub | areaTblMode | ramMapAreaMode |
|---|---|---|---|---|
| 0 (0x9DE7C8) | 2 (movie) | 1 | 0x02 | 9 |
| 0 | 3 (still) | 8 | 0x03 | 7 |
| 1 (0x9DE898) | 2 | 1 | 0x01 | 6 |
| **1** | **3** | **8** | **0x03** | **7** |
| 2 (0x9DEDC0) | 2 | 1 | 0x05 | 5 |
| 2 | 3 | 8 | 0x0A | 9 |

Valor de fichero de `[0x9DEFE0]` = **1** (no hay escritura localizable en `libmpr`: se cambia en
tiempo de ejecución; **NO_VERIFICADO** desde dónde).

### 2.3 Las direcciones: mmap, no petición al gestor

`MemConfig::Mmap` (**0x5F6544**) elige dispositivo y hace mmap de una **dirección física dada**:

```
5f6566  ldr r3,=0x00860738        ; "/dev/stream"     (cache: 0x5F6566; noncache: 0x5F6598)
5f657e/0x5f65b0 ldr r3,=0x008d761d ; "/dev/mem"        (alternativa)
5f65d8  blx open                  ; flags 2 = O_RDWR  /  0x1002 = O_RDWR|O_SYNC
5f65c8  «[MemInfo]MemConfig::Mmap() driver open("%s",%d)»
5f65xx  mmap(physAdrs,size)       ; cadenas 0x8D8BCF/0x8D8C0B/0x8D8C53
5f6524  «[MemInfo]MemConfig::Mmap() Fsys_SetStreamArea(vAdrs=0x%08lx,size=0x%08lx)» (0x8D8CAD)
```

El **DMM no aparece en esta ruta**. En `libmpr` el DMM solo se usa para memorias de tipo «unit»:

```
0x8DACEC «[MemInfo]UnitMemAllocate call»      0x8DAD0A  «[MemInfo]DMM Alloc failed...»
0x8DABB8 «[MemInfo]UnitMemShare() call»        0x8DAC1E  «[MemInfo]DMM Reuse failed...»
0x8DC2C0-0x8DC520 «[Mem_DmmAccess][SendAndReceiveDmmMsg] osal_valloc_msg / osal_snd_msg / …»
```

**Respuesta al objetivo 2**: el tamaño procede de una **tabla de configuración estática incluida
en `libmpr`** (por tipo de modelo/sistema de TV y por modo), no de una constante única, **no** de
una petición a `dmm`/`memplus`/`osal` y **no** de un cálculo con parámetros de sesión.

## 3. Rutas en las que el tamaño llega a 0 (objetivo 3)

### 3.1 Estado inicial: la tabla del reproductor nace a cero

`MemInfo::Init` (0x5F74D4, única llamada desde **0x7125CE**) hace, en este orden:

```
5f74dc  mov r8,r0
5f7500  ldr r0,="/dev/stream2" ; open (0x5F7502 movw r1,#0x1002)
5f7566  [0xA4F0A4] = 0x8D87E8          ; tabla de modos
5f7576… recorre [0x9DE788] (áreas FIJAS, entradas 0x10, fin [+8]==-1)
5f75d0  MemConfig::Mmap(addr,size,1,0) ; área fija cache
5f761c  MemConfig::Mmap(addr,size,0,0) ; área fija non-cache
5f7644  mov.w r2,#0x108
5f7648  ldr r0,=0x00a4fd88
5f764a  bl 0x1202e2                    ; memset(0xA4FD88, 0, 0x108)   <- tabla FIJA
5f7652  r2 = r5
5f7654  bl 0x5F703C                    ; DistributeBufInfo(0, 0xA4FD88, lista fija)
5f7666  bl 0x2B1468                    ; [NBL] GetEepData(0x3C01F0)
5f7672  bl 0x5F91E4                    ; fija 4 banderas en 0xA4FFDC/0xA4FFD5/0xA4FFEC/0xA50021
```

**No hay `memset` ni escritura de `0xA4F368` en `Init`**: la tabla del reproductor (0x0A4F368,
entradas 0x18) solo se escribe desde `DistributeBufInfo`, es decir, dentro de
`StreamAreaAllocate`/`ChangeAllocate`. Todo hueco que no se rellene **queda a 0 de `.bss`**.

### 3.2 Liberación: el hueco vuelve a 0 sin invalidar el descriptor

```
StreamAreaFree(unitHandle, subArea)       0x5F802C
5f804e  ldr r0,[r6]                       ; [0x9DECAC] = modo/areaTblMode actual
5f8052  ldr r1,=0x00a4f368                ; tabla de buffers
5f8054  bl  0x5F7EA8                      ; limpia las entradas de esa unidad
```

y en `0x5F7EA8(modeId, tabla, mask)`:

```
5f7eba  ldr r3,=0x00a4f0a4 ; recorre la lista de modos hasta [entrada+4]==modeId
5f7ed8  ldr r0,[r4,#4]
5f7eda  bl  0x5F685C       ; areaType -> máscara (tabla 0x8D9030, índice 0..0xA)
5f7ede  tst r0,r6          ; ¿casa con subArea?
5f7ee2  ldr r3,[r4,#8]     ; índice de la entrada
5f7ee4  movs r0,#0x18
5f7ee6  movs r1,#0
5f7ee8  mla r0,r0,r3,r5    ; &tabla[idx]
5f7eec  bl  0x5F63CA       ; <-- pone a CERO la entrada
```

`0x5F63CA(entry, 0)`:

```
5f63d0  movs r2,#0
5f63d2  movs r3,#0
5f63d4  str r1,[r0]        ; +0x00 = 0
5f63d6  str r1,[r0,#4]     ; +0x04 = 0
5f63d8  str r1,[r0,#8]     ; +0x08 = 0   <-- el TAMAÑO
5f63da  strd r2,r3,[r0,#0x10]
```

Consecuencia clave: tras un `StreamAreaFree` el **puntero sigue siendo válido** (no es NULL), así
que los clientes **sí** llaman a `SetArea` y esta vez con `size = 0` → `BUFFER SIZE TOO SMALL :
00000000` + `C1000002`, y `[0xAD4F94]` queda a 0 → el siguiente `GetArea` da `C1000010`
(«STREAMCACHE NOT SET AREA»).

### 3.3 Modo desconocido o `setupMode` fuera de rango

- Modo desconocido: `Type2Mode` → «not found mode» (0x5F6A30) → `StreamAreaAllocate` falla y
  devuelve **0** (0x5F7D40). Entonces el cliente **no** llama a `SetArea` (comprueba `r5 != 0` en
  0x4392C8) → **este caso no produce el log**.
- `setupMode` fuera de 1..5 (`0x4391EA cmp r3,#4 / bhi.w 0x43944E`) y descriptor no nulo:

```
43944e  cbz r5,0x439460
439450  mov.w r8,#0
439454  mov sb,r8
439456  mov r0,sb ; 439458 mov r1,r8 ; 43945a movs r2,#1
43945c  bl 0x7594e0                 ; SetArea(0,0,1) literal
```

  Esta es la **única** vía en la que el 0 no viene de la tabla sino del código.

### 3.4 ¿Depende del modo de arranque o de algún módulo?

- El área del reproductor depende de **la secuencia de comandos MPR** (`setMemTbl`, entrada/salida
  de modo, `SetUpPlayerInstance`), no del arranque del sistema: `MemInfo::Init` solo prepara el
  stream2 y las áreas fijas.
- Depende del **tipo de sistema** (`m_systemType`, `[0x9DEFE0]`) porque cambia `areaTblMode`. Un
  `m_systemType` distinto del esperado llevaría a **otra** tabla de áreas (y a otro reparto), pero
  entonces lo normal es que el modo no exista y `ChangeAllocate` devuelva 0 (sin log de caché).
- No depende de `dmm.ko` (ver §4).

## 4. `dmm.ko`: qué hace con `DmmConfig.bin` (objetivo 4)

### 4.1 Quién lo carga y con qué ruta

```
nflasha7_unpacked_unpacked/sbin/init (strings):
  29a3  /usr/kmod/dmm.ko
  29b4  DmmConfig=/setting/DmmConfig.bin
nflasha15_unpacked_unpacked/lib/libIMDB.so (strings):
  25b0  /kmod/dmm.ko
  25bd  DmmConfig=/usr/share/dmm/DmmConfig.bin
```

Dos cargadores, **dos rutas distintas** según por dónde arranque la máquina. En la imagen 0700
**no existe ningún `DmmConfig.bin`**: `nflasha15/share` no tiene `dmm/`, y
`nflasha7/setting` y `nflasha7/usr/share` están vacíos. Parámetros del módulo (`__param`, 2
entradas de 16 B): `DmmConfig` (charp, perm 0x124) y `DmmConfigExtra` (string, default
`/setting/DmmConfigExtra.bin`, cadena en `.rodata.str1.1+0x46`).

### 4.2 Secuencia de carga

```
init_module (.init.text 0x0)
0003c  [.data+0x64] = -1
00058  kmalloc/kmem_cache_alloc(0x19000)      ; 100 KiB de buffer de trabajo
00098  [cfg+0x14] = buffer                    ; cfg = .bss+0
000a4  r0 = buffer ; r1 = 0x19000
000ac  bl  dmm_module_GetConfigData            ; 0x214
000b0  cmp r0,#0
000b8  blne osal_abort.clone.1                 ; 0x194  <-- si no hay fichero
000bc  movs r0,#1 ; bl dmm_ctrl_Init           ; 0x7590 -> dmm_config_Init(0x511C)
000c4  bl  dmm_log_lkm_CreateArea
000d4  bl  dmm_udm_procfs_CreateProcfs         ; /proc/udm/dmm_info, dmm_units, dmm_extents…
000ec  bl  dmm_utm_EntryThread
```

`dmm_module_GetConfigData(buf,len)` (**0x214**) — fichero principal:

```
0224  ldr r5,=cfg (.bss+0)       ; +0x10 = charp DmmConfig, +0x14 = buffer, +0x8/+0xc = cursor
0244  ldr r8,[r5,#0x10]          ; ruta
0294  cmp r8,#0
029c  beq 0x334                  ; ruta vacía/NULL -> r4 = 0xffff -> return -1
02a0  mov r0,r8 ; mov r1,#0 ; mov r2,#0
02ac  bl  filp_open
02b0  cmn r0,#0x1000 ; bls 0x2dc ; si error:
02bc  r0=0x61 ; r1=0 ; r2=1 ; r3=«can't open file \"%s\".»  (dmm.ko .rodata.str1.1+0x14, literal 0x368)
02d0  bl  <log>
02d4  str r4,[r5,#0x10]          ; borra la ruta -> no se reintenta
02d8  b   0x334                  ; return -1
02dc  bl  vfs_read(buf,len,&pos)
02ec  cmp r0,#0 ; movle r0,#1 …  ; lectura vacía = error
030c  r3="can't read file."      ; (.rodata.str1.1+0x2a)
0320  movw r4,#0xffff            ; return -1
```

`osal_abort` (**0x194**):

```
01b4  bl osal_valloc_msg_wait(…,&msg,4,1)
01c4  r3 = 0xE ; strh r3,[msg]            ; comando 0xE
01c8  r5 = 0x008F0139                     ; destino (supervisor osal)
01e4  bl osal_snd_sync_msg(r5,msg)
01ec  r4 = status
0200  cmp r4,#0
0204  strbeq r4,[r4]                      ; si status==0 -> escritura a NULL (oops)
```

### 4.3 ¿Valida el contenido?

- **No** para el fichero principal: entre `vfs_read` y el retorno solo se comprueba que se leyó
  algo (>0). No hay *magic*, ni versión, ni CRC. Un `DmmConfig.bin` corrupto se usa tal cual.
- `crc32` (0x370) se llama **una sola vez**, desde `dmm_module_LoadConfigBuf` (0x4DC), que es el
  cargador del mapa **EXTRA** (`DmmConfigExtra`, por defecto `/setting/DmmConfigExtra.bin`),
  invocado desde `dmm_ext_ctrl_LoadExtraMap` (0xD84C → 0xD860). Ahí sí se comparan tamaño y CRC
  con la última carga (`[.data+0x64]`, `[cfg+0x98]`).

### 4.4 Fallback y formato

`dmm_config_GetConfigData(dst,len)` (**0x5140**) es un **lector secuencial** con cursor:

```
515c  ldrsh r5,[r4,#4]           ; estado en .bss+0x30FF4
5160  cmp r5,#1 ; beq 0x517c     ; estado 1 -> sirve la copia INTEGRADA
5168  cmp r5,#2 ; beq 0x520c     ; estado 2 -> sirve el FICHERO
5170  cmp r5,#0 ; beq 0x518c     ; estado 0 -> intenta fichero; si falla pasa a estado 1
5214  movw r0,#0xffff            ; otro estado -> -1
```

- estado 1 copia desde **`ConfigData`**: símbolo `ConfigData` en `.rodata`, VA **0x184**,
  **63976 B**, con la cadena de versión `"for dsc-avip 2011/04/09 19:42:11"` en +0xF9C8
  (15867 B no nulos).
- `dmm_ext_tbl_Init` (**0xEC90**) pide bloques de cabecera de **0x50 B** (0xECEC/0xEE34) y
  registros de **0x14 B** (0xED68/0xED70), termina un grupo cuando `[rec+8] == -1` (0xED80) y
  construye una tabla de extentos `[inicio, inicio+tamaño-1]` (0xEDB0-0xEDD4) según el atributo
  `[rec+0x10] & 0x02000000` (0xEDA8). **Mapeo campo a campo: NO_VERIFICADO.**
- Orden de init: `dmm_ctrl_Init(0x7590)` → `dmm_config_Init(0x511C)`; `dmm_ext_ctrl_Init(0xD48C)`
  → `dmm_ext_tbl_Init(0xEC90)`; `dmm_unit_tbl_Init(0xC2A8)`; `dmm_ext_ctrl_LoadExtraMap(0xD84C)`
  → `dmm_ext_tbl_InitExtra(0xF210)`.

### 4.5 ¿Salen de ahí áreas que consume el userland?

Sí, pero **no las del reproductor**: el DMM reparte «units»/extentos dinámicos
(`dmm_ctrl_AllocUnitNewHdlr`, `AllocUnitShareHdlr`, `FreeUnitHdlr`, `GetUnitInfoHdlr`,
`dmm_unit_tbl_Init`, `/proc/udm/dmm_units|dmm_extents|dmm_info|dmm_reserve`). El consumidor en
`libmpr` es `Mem_DmmAccess::SendAndReceiveDmmMsg` + `UnitMemAllocate/Share/Reuse/Free/Close`
(cadenas 0x8DACEC-0x8DAD28). Las áreas de stream del reproductor son **mmap de direcciones
físicas fijas** (0x5F6544), independientes de `DmmConfig.bin`.

## 5. Conclusión (objetivo 5)

**En una frase**: para que el reproductor pida un área de tamaño 0 tiene que estar mal la
**tabla de buffers del modo** —el hueco 13 del singleton `MemInfo` (`0xA4F368+0x138/0x140`)—, es
decir, que el modo con el que se entra en reproducción no haya definido ese hueco para el
`sistema/modo` con el que corre la cámara, o que algo haya ejecutado `StreamAreaFree` después de
asignarlo y lo haya dejado a cero; no es un cálculo, no es una petición al DMM, no es la tarjeta
ni el mínimo de la NVRAM.

**Qué se puede comprobar sin flashear** (ninguna requiere escribir en la cámara; todas usan el
mismo canal EX-PC de lectura del anillo `0x82DF9300`-`0x82DFC400` ya usado el 20-10):

1. **Subir la traza a nivel 5** (si el monitor EX-PC lo permite) y volcar: aparecerán
   `CMD(SET_AREA): Addr … Size …` (0x93E839/0x93E858), `[MemInfo]StreamAreaAllocate(next)…type=…
   sub=…` (0x8DA503) o `ChangeAllocate(next):` (0x8DA893), `[MemInfo]Type2Mode: type=… subType=…
   / ramMapAreaMode=… / areaTblMode=…` (0x8D90C0) y, si el reparto falla,
   `[MemInfo]DistributeBufInfo -- area size failed` (0x8D9E2C) o
   `bufTbl distribute Failed!` (0x8D9EAF). Con esas cinco líneas se cierra el caso.
2. **Buscar un `StreamAreaFree`** previo al fallo: `[MemInfo]StreamAreaFree(next) unitHandle =…`
   (0x8DA930) o `[MemInfo]StreamAreaFree(next) complite` (0x8DA9EA). Si aparece antes de la línea
   112, la causa es liberación (orden), no tabla ausente.
3. **Repetir la entrada en reproducción** después de grabar/reproducir un vídeo: si el 0
   desaparece o cambia de sitio, es orden de comandos; si sale siempre igual, es la tabla del modo.
4. **Leer `[0x9DEFE0]`** (m_systemType) y `[0x9DECAC]` (areaTblMode actual) por el monitor
   (`md` de sólo lectura). m_systemType distinto de 1 apunta a otra tabla de áreas.
5. **DMM**: leer `/proc/udm/dmm_info`, `/proc/udm/dmm_units` y `/proc/udm/dmm_extents`. Si salen
   vacíos, `DmmConfig.bin` no se cargó; si salen poblados, el DMM está sano y no es la causa.
   Con el mismo canal, `ls -l /setting/DmmConfig.bin` y `/usr/share/dmm/DmmConfig.bin`
   (existencia y tamaño; **no** hace falta leer el contenido).

## 6. Límites (NO_VERIFICADO)

- **NO_VERIFICADO** qué llamada exacta a `SetArea` produjo el 0 en el anillo del 20-10: falta la
  línea verbosa de nivel 5. Por contexto (`EnterStillPb`) y por el despacho de `setupMode`, el
  candidato es la rama still de `SetUpPlayerInstance` (0x43945C); `SetMemoryTable` (0x330128) es la
  alternativa.
- **NO_VERIFICADO** que `0xA4F368+0x138` sea *siempre* el «stream de still»: se deduce del uso
  (índice 13 = 0x138, índice 11 = 0x108) y de que la rama `setupMode=2` de
  `SetUpPlayerInstance` es la del reproductor de fotos; no hay un `enum` en el binario.
- **NO_VERIFICADO** el significado campo a campo de las tablas estáticas de modo (0x9DBD20,
  0x9DB0E4, 0x9DA8E0): sus entradas tienen 0x10 B y la primera de «Still Pb» es
  `{0x01800000, 0x00000000, 0x0000000B, 0x00500000}`; cuál de esos cuatro campos es el tamaño final
  no se ha podido cerrar sin emulación.
- **NO_VERIFICADO** el origen de escritura de `m_systemType` (`[0x9DEFE0]`): en el fichero vale 1 y
  no hay ningún `str` localizable en `libmpr` (probablemente lo fija un constructor o un módulo
  externo).
- **NO_VERIFICADO** si la cámara real tiene `/setting/DmmConfig.bin`, su tamaño y su CRC; y el
  mapeo exacto de los registros de 0x14 B de la configuración del DMM.
- El valor del mínimo de `SetArea` (`[0xAD4F68] = GetEepData(0x3C0057) << 10`) depende de la
  EEPROM de la unidad y no está en los volcados del repositorio (igual que en el informe previo).

## Evidencia

`reports/evidence/film-pb-1-sub-dmm-area-20261126/`

| fichero | contenido |
|---|---|
| `01-setarea-llamadores.txt` | las 10 llamadas a `SetArea`, `SetMemoryTable` (0x330104-0x330128) y las tres ramas de `SetUpPlayerInstance` (0x43924A, 0x4392C6, 0x43944E) |
| `02-meminfo-cadena.txt` | `GetMemoryInformation` 0x4284AC, `StreamAreaAllocate` 0x5F7BE8, `ChangeAllocate` 0x5F7F1C |
| `03-tabla-buffers-0x18.txt` | stride 0x18, escrituras de `DistributeBufInfo`, `0x5F63CA` (puesta a cero), `0x5F7EA8` (limpieza por `areaType`), `StreamAreaFree` 0x5F802C |
| `04-tablas-modo-libmpr.txt` | nombres de modo (0x9DF090), `mp_modeTblForBufTbl` (0x8D87E8), tablas de `Type2Mode` por sistema |
| `05-dmm-modulo.txt` | `init_module`, `dmm_module_GetConfigData`, `dmm_module_LoadConfigBuf`, `dmm_config_GetConfigData`, `dmm_config_Init`, `osal_abort` |
| `06-dmm-config-formato.txt` | `dmm_ext_tbl_Init`, estadística de `ConfigData` (63976 B), símbolos, `__param`, cadenas de los dos cargadores |
