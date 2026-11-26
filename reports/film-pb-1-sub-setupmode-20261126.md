# FILM-PB-1 — Sub-auditoría: `SetUpPlayerInstance` (0x43910C) y qué es `setupMode`

Fecha: 26-11-2026. Estático, sin cámara, sin flashear. Objeto único:

- `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
  (ELF32 ARM, Thumb-2; **VA = offset de fichero** en el primer LOAD: `.text` 0x120228-0x7A3E84,
  `.rodata` 0x7A3E90-0x956750, `.data` 0x9C42E8-0x9DF808, `.bss` 0x9DF808-0xADBB04; fichero 0x9D7D34 B).
- Cruzado con `libObj.so` (0x8CC954) sólo para el extremo de la cadena del MP4.

Herramientas: `python3 /tmp/elfhelper.py` (capstone, Thumb), un decodificador de `.ARM.exidx`
para límites de función y barridos de patrones BL/B.W y de accesos a campo (`+0x1F8`, `+0x1F0`).
**No se ha usado `mcp_rea` para binarios.**

## Resumen (≤20 líneas)

1. `SetUpPlayerInstance` = **0x43910C-0x4394A4** (`.ARM.exidx`; código hasta el epílogo 0x439486;
   literales 0x4393D8-0x4393FC y 0x4394A0). Cadena `" SetUpPlayerInstance ..."` en **0x85AAB7**,
   referenciada desde el pool **0x4393D8**.
2. Firma (9 args): `bool SetUpPlayerInstance(FeaCore*, int setupMode, bool bIsFinalizeMode,
   uint mmgrIdForMovie, uint mmgrIdForStill, uint mmgrIdForIndex, uint mmgrIdForAudio,
   MemInfo* pMemInfo, uint cmdIdOfIndex)`. Devuelve 1 = hecho, 0 = fallo de reserva/`GetMemoryInformation`.
3. `setupMode` **no se calcula dentro**: es un selector de "qué reproductor se instancia".
   `ldr r2,[r7,#4]; subs r3,r2,#1; cmp r3,#4; bhi.w 0x43944E; tbb` → **sólo 1..5 tienen rama**.
4. Clase que construye cada valor (por el `new ...!!` del constructor interno):
   **1 y 4 → MoviePlayer** (0x307E44/0x307878), **2 → StillPlayer** (0x321EC8/0x320074),
   **3 → IndexPlayer** (0x2FE0D4/0x2FC268), **5 → AudioPlayerIf** (0x2F699C).
5. 1 y 4 comparten rama (0x4391FA) y sólo divergen después, en el despacho de órdenes por
   `[FeaCore+0x1F8]`: con la misma orden, 0x42BD0C salta a 0x438148 si el modo es 1 y 0x42BD1C a
   0x438D00 si es 4.
6. **12 llamadas directas** (12 BL, 0 B.W, 0 punteros en `.text`/`.data`); **todas pasan una
   constante inmediata**: 1 → 2 sitios, 2 → 4, 3 → 4, 4 → 1, 5 → 1. Ninguna >5.
7. Quién las hace: `EnterMoviePb`(1), `EnterStillPb`+`SetPreLoadStill`+`ProcInMakeThumbEnterSPB`(2),
   `EnterThumbnailPb`+`EnterAviThumbnailPb`+`ProcInMakeThumbEnterIPB`+`DvdEnterFinalize`(3),
   `EnterMoviePbStillRec`(4), `EnterHighlightPb`(5).
8. **`setupMode` se guarda** en `[FeaCore+0x1F8]` (0x439466) en todas las ramas de modo, incluida
   la de fuera de rango (los retornos de error 0x43946C-0x439478 sí se lo saltan); el campo nace a 0
   en el constructor de FeaCore (0x42928E) y se limpia en las salidas (`ClearPlayerInstance` 0x43957A,
   `ExitHighlightPb` 0x431B3E/0x431B8A).
9. **`>5` (y también 0) → 0x43944E**: `SetArea(0,0,1)` **literal**, y sólo si `pMemInfo != 0`
   (`cbz r5`); después cae al mismo epílogo y **devuelve 1** (éxito) con el área a cero.
10. **En fw 3.21 ese camino es defensivo**: al no haber ningún llamador con valor fuera de 1..5 ni
    llamadas indirectas, la rama >5 **no es alcanzable** por las rutas de este binario.
11. **No depende del fichero**: el tipo de contenido (MP4/AVCHD/STILL/DVD/DV/XAVC/WAV) no entra en la
    elección; entra *antes*, en `GetMemoryInformation` (0x4284AC) para elegir tabla de memoria
    (`type`/`sub`) y llega ya resuelto como `pMemInfo`.
12. **No hay comprobación de capacidad** en la función ni en sus llamadores: no lee NVRAM, tarjeta,
    IFO ni flags de modelo.
13. Dependencia real: **qué API de reproducción se invocó** (modo de cámara/feature: película, foto,
    índice/miniaturas, movie+stillrec, highlight/BGM). Es un enum de *feature*, no de contenido.
14. Única variación en tiempo de ejecución dentro de la función: en `setupMode==3`, si
    `cmdIdOfIndex == 0x40000031` (`MprIf::EnterAviThumbnailPb`) usa el área **still** (`+0x138/+0x140`);
    con cualquier otro `cmdId` usa la **movie** (`+0x108/+0x110`).
15. **Un MP4 normal NO cae en `setupMode>5`**: `MprIf::EnterMoviePb` (0x7231B0/0x723214, opcode
    **0x40000017**) → `FeaIf::EnterMoviePb` 0x44F2F4 → despacho 0x429C54 (caso 0x42A2F2) →
    `EnterMoviePb` 0x437A28 → `SetUpPlayerInstance(..., setupMode=1, ...)`.
16. Consecuencia para el caso de la traza del 20-10: el reproductor de MP4 usa la **entrada 11**
    (`0xA4F368+0x108/+0x110`), no la 13 del informe de área; la rama `>5` no puede ser la causa del
    `SetArea(0,0,*)` de un MP4.
17. `bIsFinalizeMode` se imprime (`0x439160`) y, **sólo en `setupMode==3`**, se reenvía como 3.er
    argumento al arranque del IndexPlayer (`0x439360 ldr r2,[r7]` → 0x2FE128). En 1/2/4/5 no se usa.
18. `pMemInfo` es el 4.º argumento de pila (`[sp+0xC]`); todos los llamadores guardan ahí el retorno
    de `GetMemoryInformation` (0x4284AC) en `[FeaCore+0xDAC]`.

## 1. Localización, firma y contrato

La cadena `" SetUpPlayerInstance ..."` está en **0x85AAB7** (`.rodata`), seguida del bloque de trazas
`" + SetUp mode     :"` (0x85AAD0), `" + bIsFinalizeMode:"` (0x85AAE4), `" + mmgrIdForMovie :0x"`
(0x85AAF8), `" + mmgrIdForStill :0x"` (0x85AB0E), `" + mmgrIdForIndex :0x"` (0x85AB24),
`" + mmgrIdForAudio :0x"` (0x85AB3A) y `" + cmdIdOfIndex   :0x"` (0x85AB50). Su único xref es el
literal **0x4393D8**, dentro de la función.

Límites por `.ARM.exidx` (no por olfato): la entrada que cubre 0x43910C da
**0x43910C-0x4394A4**; la siguiente función empieza en **0x4394A4** (`ClearPlayerInstance`, cadena
`" ClearPlayerInstance ... mode:"` 0x85AB66). Dentro del rango: código 0x43910C-0x439486, *landing
pads* de excepción 0x439488-0x43949E y dos pools de literales.

```
43910c  push.w {r4-r8,sb,sl,fp,lr}      ; 9 registros = 0x24
439110  sub    sp,#0x1c
439112  add    r7,sp,#8                 ; marco local
439114  mov    r4,r0                    ; r4 = this (FeaCore*)
439116  mov    r6,r3                    ; r6 = mmgrIdForMovie
439118  ldr    r0,[r0,#0xc]             ; this->log
43911a  str    r1,[r7,#4]               ; [r7+4] = setupMode      (arg 2)
43911c  str    r2,[r7]                  ; [r7]   = bIsFinalizeMode (arg 3)
43911e  ldr.w  fp,[r7,#0x38]            ; arg de pila 1 = mmgrIdForStill  ([sp+0x40])
439122  ldr.w  sb,[r7,#0x3c]            ; arg de pila 2 = mmgrIdForIndex  ([sp+0x44])
439126  ldr.w  sl,[r7,#0x40]            ; arg de pila 3 = mmgrIdForAudio  ([sp+0x48])
43912a  ldr    r5,[r7,#0x44]            ; arg de pila 4 = pMemInfo        ([sp+0x4c]) -> r5
43912c  ldr.w  r8,[r7,#0x48]            ; arg de pila 5 = cmdIdOfIndex    ([sp+0x50])
439130  bl     0x6830e4                 ; log->enabled ([log+8])
439134  cmp    r0,#0
439136  beq    0x4391e6                 ; sin traza -> directo al switch
```

Firma resultante (los 9 argumentos se usan exactamente así: los cuatro primeros en registros y los
cinco restantes en pila a partir de `[sp+0]`, con `r7 = sp+8`):

```c
bool SetUpPlayerInstance(FeaCore* this,        // r0
                         int      setupMode,   // r1 -> [r7+4]
                         bool     bIsFinalizeMode, // r2 -> [r7]  (sólo traza)
                         uint32_t mmgrIdForMovie,  // r3
                         uint32_t mmgrIdForStill,  // [sp+0x00]
                         uint32_t mmgrIdForIndex,  // [sp+0x04]
                         uint32_t mmgrIdForAudio,  // [sp+0x08]
                         MemInfo* pMemInfo,        // [sp+0x0C]
                         uint32_t cmdIdOfIndex);   // [sp+0x10]
```

- **Retorno**: `r8` al epílogo 0x43947C. Vale **1** por la vía normal (0x439462) y también en la rama
  de `setupMode` fuera de rango; vale **0** cuando `GetMemoryInformation`/`operator new` fallan
  (0x43946C, 0x439470, 0x439474, 0x439478). Es un `bool` de éxito, no un código de error.
- **Efecto lateral obligatorio**: `[this+0x1F8] = setupMode` en 0x439466 (común a todas las ramas).
- `pMemInfo` se usa sólo como descriptor: `[r5+0x108]/[r5+0x110]` (entrada 11, "movie") o
  `[r5+0x138]/[r5+0x140]` (entrada 13, "still").
- `bIsFinalizeMode` se lee dos veces: en la traza (0x439160) y en la rama 3 (0x439360), donde se
  pasa al arranque del IndexPlayer. En las demás ramas no interviene.

## 2. Desensamblado comentado (completo)

El listado íntegro, instrucción a instrucción, está en
`reports/evidence/setupmode/00-setupplayerinstance.dis.txt`. Aquí va la estructura con los saltos.

### 2.1 Bloque de traza (0x439138-0x4391E4) — prescindible para el flujo

Imprime los 7 campos en orden: `SetUp mode` (arg2), `bIsFinalizeMode` (arg3), `mmgrIdForMovie` (r6),
`mmgrIdForStill` (fp), `mmgrIdForIndex` (sb), `mmgrIdForAudio` (sl) y `cmdIdOfIndex` (r8), con los
helpers de log 0x68323C (cadena), 0x6831B8/0x6831F8 (hex) y 0x683118 (fin de línea).

### 2.2 Selección de modo (0x4391E6)

```
4391e6  ldr  r2,[r7,#4]      ; setupMode
4391e8  subs r3,r2,#1        ; r3 = setupMode-1
4391ea  cmp  r3,#4
4391ec  bhi.w 0x43944e       ; (unsigned) setupMode==0 || setupMode>=6
4391f0  tbb  [pc,r3]         ; PC=0x4391F4
4391f4  .byte 0x03,0x38,0x76,0x03,0xC2
```

| setupMode | destino | clase instanciada |
|---|---|---|
| 1 | 0x4391FA | `MoviePlayer` (ctor 0x307E44, objeto en `[this+0xD94]`) |
| 2 | 0x439264 | `StillPlayer` (ctor 0x321EC8, `[this+0xD98]`) |
| 3 | 0x4392E0 | `IndexPlayer` (ctor 0x2FE0D4, `[this+0xD9C]`) |
| 4 | **0x4391FA** (idéntica a 1) | `MoviePlayer` |
| 5 | 0x439378 | `AudioPlayerIf` (ctor 0x2F699C, `[this+0xDA0]`) |
| 0 ó ≥6 | 0x43944E | ninguna; `SetArea(0,0,1)` |

Los constructores son envoltorios ("If") que crean el motor real: 0x307878 imprime
`"new MoviePlayer!! ( this = 0x"`, 0x320074 `"new StillPlayer!! ( this = 0x"`, 0x2FC268
`"new IndexPlayer!! ( this = 0x"`, 0x2F699C `"new AudioPlayerIf!! ( this = 0x"`. Todos usan el mismo
patrón: `operator new` → ctor → llamada virtual de arranque con un código propio
(0x1040 movie, 0x1050 still, 0x1060 index, 0x1080 audio) y `0x428BAD` como callback.

### 2.3 Cuerpo común de las ramas 1 y 4 (0x4391FA-0x439262)

```
439202  ldr.w r0,[r4,#0x1ec]     ; gestor de MMgr
439206  mov   r1,r6              ; mmgrIdForMovie
439208  str   r8(=0),[r7,#0xc]   ; local out-param
43920c  bl    0x447810           ; busca/crea el MMgr del movie
439210  bne   0x43947c           ; error -> devuelve 0
439216  adds  r0,#8  ; blx _Znwj ; new(8)
43921e  bl    0x307e44           ; MoviePlayerIf::MoviePlayerIf()
439222  str   r8,[r4,#0xd94]
...
439238  blx   r6                ; vtable: arranque(0x1040, 0x428BAD, this)
439246  bl    0x307e88           ; 2.ª parte del arranque (usa [r7+0xc])
43924a  cmp   r5,#0
43924c  beq   0x439460           ; sin MemInfo -> no toca área, pero SÍ guarda el modo
439250  ldr   r0,[r4,#0xd94]
439254  mov   r1,r5
439256  ldr.w sb,[r5,#0x108]     ; dirección  (entrada 11 = movie)
43925a  ldr.w r8,[r5,#0x110]     ; tamaño
43925e  bl    0x307e96           ; SetMemoryTable(pMemInfo)
439262  b     0x439456           ; -> SetArea(sb,r8,1)
```

### 2.4 Rama 2 — StillPlayer (0x439264-0x4392DE)

Mismo esqueleto con `[r4,#0xD98]`, ctor 0x321EC8, arranque `0x321F28(obj, [r7+0xC], 2, 1)`
(nótese el **2** literal: subtipo still, y el `1` de saveCache), y área **`[r5+0x138]/[r5+0x140]`
(entrada 13)** en 0x4392D2/0x4392D6, `SetArea` en 0x439456. Además `0x321F58(obj, pMemInfo)` y, en el
llamador 0x430924, `0x321F80` (DoStillZoom) al terminar.

### 2.5 Rama 3 — IndexPlayer (0x4392E0-0x439376) y la única decisión en tiempo de ejecución

```
439312  ldr  r3,=0x40000031      ; opcode MprIf::EnterAviThumbnailPb
439314  cmp  r8,r3               ; r8 = cmdIdOfIndex
439316  bne  0x439328
439318  cbz  r5,0x439338
43931a  ldr  sb,[r5,#0x138]      ; AVI thumb -> área STILL (entrada 13)
43931e  mov  fp,#1               ; (flag 1 al arranque 0x2FE128)
439322  ldr  r8,[r5,#0x140]
439328  cbz  r5,0x43933e
43932a  ldr  sb,[r5,#0x108]      ; resto de miniaturas -> área MOVIE (entrada 11)
43932e  mov  fp,#0
439332  ldr  r8,[r5,#0x110]
439344  blx  vtable: Init(0x1060, 0x428BAD, this)
439356  movs r3,#3
439358  bl   0x2FE128(obj, fp /*área still?*/, bIsFinalizeMode, local, 3)
439372  bl   0x2FE156(obj, pMemInfo)
439376  b    0x439456           ; -> SetArea(sb,r8,1)
```

### 2.6 Rama 5 — AudioPlayerIf (0x439378-0x439404)

Igual patrón con `[r4,#0xDA0]`, `operator new(0x63DC)`, ctor 0x2F699C, arranque `0x2F6A74(obj,
0x1080, 0x428BAD, this)` y `0x2F6AA8`/`0x2F6AD8` (SetMMgrInfo / SetMemoryTable / Enter, cadenas
`"SetCallback"`, `"SetMMgrInfo"`, `"SetMemoryTable"`, `"Enter"`). Área: entrada 11 (movie) porque
`sb/r8` se cargan de `[r5+0x108]/[r5+0x110]` en 0x4393CA/0x4393CE.

### 2.7 Rama por defecto `>5` / `0` y epílogo (0x43944E-0x439486)

```
43944e  cbz  r5,0x439460        ; pMemInfo == NULL -> ni SetArea
439450  mov.w r8,#0
439454  mov  sb,r8
439456  mov  r0,sb              ; dirección = 0
439458  mov  r1,r8              ; tamaño    = 0
43945a  movs r2,#1              ; saveCache = 1
43945c  bl   0x7594e0           ; StreamCache::SetArea(0,0,1)   <-- literal
439460  ldr  r3,[r7,#4]         ; setupMode
439462  mov.w r8,#1             ; retorno = 1
439466  str.w r3,[r4,#0x1f8]    ; [FeaCore+0x1F8] = setupMode  (se guarda SIEMPRE)
43946a  b    0x43947c
43947c  mov  r0,r8
43947e  add.w r7,r7,#0x14
439482  mov  sp,r7
439484  pop.w {r4-r8,sb,sl,fp,pc}
```

`0x7594E0` es `StreamCache::SetArea` (cadena `"CMD(SET_AREA): Addr "` en 0x93E839): queda confirmado
que la llamada es a `SetArea`, con los tres argumentos a 0/0/1.

## 3. Qué es `setupMode`: valores, quién lo pasa y cuándo es >5

**Qué es**: el discriminante con el que `FeaCore` decide *qué interfaz de reproductor* se instancia y
se guarda en `[FeaCore+0x1F8]` para el resto de la sesión. No es el tipo de contenido, ni el modo de
cámara, ni un tamaño: es la "personalidad" del reproductor.

**Valores con rama** (1..5) y qué API lo pasa — 12 llamadas directas, todas con constante:

| # | setupMode | Llamador (VA) | Función / API | Opcode MPR | Clase |
|---|---|---|---|---|---|
| 1 | 1 | 0x437AC4 | `EnterMoviePb` | 0x40000017 | MoviePlayer |
| 2 | 1 | 0x446E02 | `ProcInMakeThumbEnterMPB` | (interno de grabación) | MoviePlayer |
| 3 | 2 | 0x4396A6 | `EnterStillPb` | 0x4000001B | StillPlayer |
| 4 | 2 | 0x439812 | `SetPreLoadStill` | (interno) | StillPlayer |
| 5 | 2 | 0x4463F2 | `ProcInMakeThumbEnterSPB` | (interno) | StillPlayer |
| 6 | 2 | 0x43094C | callback del reproductor still (sin xref directo: se invoca por tabla) | — | StillPlayer |
| 7 | 3 | 0x436752 | `EnterThumbnailPb` | 0x4000002E | IndexPlayer |
| 8 | 3 | 0x436C1C | `EnterAviThumbnailPb` | **0x40000031** | IndexPlayer (área still) |
| 9 | 3 | 0x446C1A | `ProcInMakeThumbEnterIPB` | (interno) | IndexPlayer |
| 10 | 3 | 0x431184 | `DvdEnterFinalize` | 0x40000039 | IndexPlayer |
| 11 | 4 | 0x438E90 | `EnterMoviePbStillRec` | 0x40000019 | MoviePlayer |
| 12 | 5 | 0x43530A | `EnterHighlightPb` | 0x40000062 | AudioPlayerIf |

Barrido de `.text` completo con los patrones BL **y** B.W: **12 BL, 0 B.W**; `xref` del valor
0x43910C/0x43910D en todo el fichero: **cero** punteros (no está en ninguna vtable ni tabla). No hay
pues llamada indirecta.

**Cuándo es >5**: nunca en fw 3.21. La comparación es *unsigned* sobre `setupMode-1`, de modo que
caen en 0x43944E los valores **0 y ≥6**. Es una **guarda defensiva** (el binario la conserva para un
llamador que no existe en esta imagen). Si algún día se alcanzara:

- sólo actúa si `pMemInfo != NULL` (`cbz r5`);
- deja el área del reproductor en **(0,0)** con `saveCache=1`;
- **no falla**: guarda el modo y devuelve 1.

## 4. ¿Depende del tipo de contenido, del modo de cámara o de una capacidad?

**Del tipo de contenido: NO.** Ningún llamador calcula `setupMode` a partir de nada: los 12 emiten
`movs r1,#N` / `mov.w r1,#N` justo antes del `bl`. El tipo de contenido (MP4/AVCHD/STILL/DVD/DV/XAVC/
WAV, cadenas de `GetMemoryInformation` en 0x857BD2) influye **antes**, en
`GetMemoryInformation` (0x4284AC), que elige la tabla de memoria (`type`, `sub`, `modeId`) y
devuelve el `MemInfo*` que llega como 4.º argumento de pila. Ese descriptor sí varía con el
contenido; `setupMode` no.

**Del modo de cámara (foto/vídeo): SÍ, pero por identidad de la API.** Cada entrada de reproducción
tiene su constante: película → 1, foto → 2, índice/miniaturas/DVD → 3, película durante grabación de
foto → 4, highlight/BGM → 5. Es decir, el "modo" que selecciona `setupMode` es el *feature* que entra
en reproducción, decidido por la capa de aplicación/`MprIf` al elegir la API (y su opcode), no por un
campo del fichero ni por el modo de la cámara leído en tiempo de ejecución. Prueba: la misma función
`EnterMoviePb` sirve para cualquier `contentTypes` y siempre pasa 1.

**De una capacidad: NO.** `SetUpPlayerInstance` no lee NVRAM, EEPROM, tarjeta, IFO, `/dev/*` ni flags
de modelo/capacidad; sólo despacha y llama a `StreamCache::SetArea`. Tampoco hay chequeo de capacidad
en los 12 llamadores antes del `bl` (lo que hay es `GetMemoryInformation` y la búsqueda del MMgr).

**Única variación en tiempo de ejecución**: `setupMode==3` y `cmdIdOfIndex == 0x40000031`
(`EnterAviThumbnailPb`) → área still (entrada 13). Para `0x4000002E` (`EnterThumbnailPb`) o
cualquier otro `cmdId` → área movie (entrada 11). El `cmdId` viene del primer campo del payload
(0x44DE8A en `FeaIf::EnterThumbnailPb`, 0x44DBB2 en `FeaIf::EnterAviThumbnailPb`).

## 5. ¿El camino normal de reproducción de un MP4 cae en `setupMode>5`?

**No.** Cadena completa (cada salto verificado en bytes; listados en
`reports/evidence/setupmode/03-mp4-chain.txt`):

```
libObj.so 0x8CC954   blx  MprIf::EnterMoviePb(mm,color*,mm,MoviePbType,StillPlayOutputMode)
libmpr 0x7231B0/0x723214  MprIf::EnterMoviePb   -> opcode 0x40000017 (traza MprIfLog::AsyncApiCall)
libmpr 0x44F2F4      FeaIf::EnterMoviePb       -> payload 0x18 B: [+0]=mmgrIdForMovie, [+4]=contentTypes,
                                                  [+8]=muteColor, [+0xC]=modeId, [+0x10]=moviePbType,
                                                  [+0x14]=stillPlayOutputMode; encola 0x40000017
libmpr 0x429C54      FeaCore command dispatch -> caso 0x40000017: 0x429D26 beq 0x42A2F2 -> 0x42A2FC
libmpr 0x437A28      EnterMoviePb (handler)    -> guarda [this+0xDC0]=mmgrId, [this+0xDB8]=contentTypes
                     GetMemoryInformation(type=tbl[moviePbType]∈{0,0x18}, sub=8/0x10/0x80/0x100,
                                          flag=1, modeId=[payload+0xC]) -> [this+0xDAC] = MemInfo*
libmpr 0x43910C      SetUpPlayerInstance(setupMode = 1)   <-- constante
```

Es decir, el reproductor normal de película entra **siempre por `setupMode==1`**, sea MP4 (contentType
6 "CONTENT_MP4(AVC)" en la tabla de la app) o cualquier otro tipo de película; la diferencia de
contenido sólo cambia `contentTypes`/`moviePbType`, que van a `GetMemoryInformation`, no a
`setupMode`.

**Corolario para el caso del 20-10**: la rama `>5` no puede explicar el área a 0 de un MP4. Con
`setupMode==1` el par que se pasa a `SetArea` es **`[0xA4F368+0x108] / [0xA4F368+0x110]`** (entrada
11, "movie"), no `+0x138/+0x140` (entrada 13, "still") que es la que subraya el informe de
`dmm-area`. Si el área del MP4 sale 0, hay que mirar la entrada 11 de la tabla del modo movie (o su
liberación por `StreamAreaFree`), no la rama defensiva.

## 6. Comprobación de los VA del informe `film-pb-1-sub-dmm-area-20261126.md`

Se han extraído los 148 valores con forma de VA de ese informe y clasificado contra las secciones de
`libmpr.so` (`reports/evidence/setupmode/04-va-check.txt`): **140 caen dentro** (84 `.text`,
34 `.rodata`, 11 `.data`, 11 `.bss`) y **8 no son VA**:

`0x0`, `0xB`, `0x19000`, `0x30FF4`, `0x1800000`, `0x2000000`, `0x82DF9300`, `0x82DFC400`
(dos tamaños, dos flags y dos patrones de bytes; no direcciones).

Los VA que usa este informe, verificados uno a uno:

| VA | sección | qué es |
|---|---|---|
| 0x43910C | `.text` | `SetUpPlayerInstance` |
| 0x4391F0 / 0x4393D8 / 0x43944E / 0x439456 / 0x439466 | `.text` | tabla TBB, pool de la cadena, rama >5, `SetArea`, guardado del modo |
| 0x7594E0 | `.text` | `StreamCache::SetArea` (`"CMD(SET_AREA)"` 0x93E839) |
| 0x4284AC | `.text` | `GetMemoryInformation` (`" GetMemoryInformation, type:"` 0x857C02) |
| 0x42B9AC | `.text` | despacho de órdenes que lee `[FeaCore+0x1F8]` |
| 0x85AAB7..0x85AB66 | `.rodata` | cadenas de `SetUpPlayerInstance` y `ClearPlayerInstance` |
| 0x7231B0 / 0x723214 / 0x44F2F4 / 0x437A28 | `.text` | cadena del MP4 |
| 0xA4F368 | `.bss` | singleton `MemInfo` (no está en fichero: es NOBITS, por eso "no cuadra" contra el tamaño) |

Conclusión de la comprobación: **ningún VA de `libmpr` de ese informe necesita el ajuste −0x10000**.
Lo que no encaja son (a) las direcciones de `dmm.ko` (`0x214`, `0x194`, `0x370`, `0x4DC`, `0x5140`,
`0x29A3`…) y de `libIMDB.so` (`0x25B0`…), que son **offsets de sección de otros binarios**, y (b) los
campos de `.bss` (`0xA4F368`, `0xA4FD88`, `0x9DEFE0`), que están más allá del final del fichero por
diseño.

## 7. Límites (NO_VERIFICADO)

- Todo es estático: no se ha observado la cámara ejecutando esta función. Que la traza del 20-10 no
  muestre `SetUpPlayerInstance` es coherente con que el bloque de traza esté tras el gate de nivel.
- No se ha identificado el nombre simbólico del enum de `setupMode` (el binario está *stripped*; sólo
  quedan `.dynsym`). La nomenclatura 1..5 de arriba se deduce de la API llamadora y de la clase que
  construye cada rama, no de un símbolo.
- No se ha seguido el ciclo completo de `[FeaCore+0x1F8]` fuera de `libmpr` (posibles lecturas en
  `libObj.so`), ni se ha verificado si el valor llega a verse en la UI.
- No se ha comprobado en runtime que la entrada 11 del `MemInfo` (`0xA4F368+0x108/+0x110`) valga 0 en
  la cámara del usuario; eso sigue siendo la hipótesis abierta del informe de área.

## Evidencia

`reports/evidence/setupmode/`:

- `00-setupplayerinstance.dis.txt` — desensamblado íntegro 0x43910C-0x4394A2 con cabecera de firma.
- `01-callsites.txt` — las 12 llamadas: ventana de instrucciones, función contenedora y valor de
  `setupMode`; incluye el resultado del barrido BL/B.W.
- `02-modos.txt` — tabla TBB, decodificación de destinos, constructores y cadenas `new ...!!`,
  despacho por `[FeaCore+0x1F8]` (0x42B9AC) y ciclo de vida del campo.
- `03-mp4-chain.txt` — cadena MP4: 0x7231B0 → 0x44F2F4 → 0x429C54 → 0x437A28 → 0x43910C, con el
  detalle del payload y de `GetMemoryInformation`.
- `04-va-check.txt` — clasificación de los 148 VA del informe de `dmm-area` contra las secciones.
- `05-opcodes.txt` — stubs `MprIf::*` con el literal del opcode y el `b.w` al `FeaIf::*` que encola.
