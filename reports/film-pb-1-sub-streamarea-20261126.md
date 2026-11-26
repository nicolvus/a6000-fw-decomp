# FILM-PB-1 — Sub-auditoría: `StreamAreaFree` y la liberación del área del reproductor

Fecha: 26-11-2026 (03:05 UTC). Estático. **Sin cámara, sin flashear, sin instalar nada, sin git.**
Objeto único (todo lo que sigue es de este fichero): `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(Thumb-2, stripped, `0x9D7D34` B; `.text` `0x120228`–`0x7A3E84`; `.rodata` `0x7A3E90`–`0x956750`;
`.data` `0x9C42E8`–`0x9DF808`; `.bss` `0x9DF808`–`0xADBB04`).

Herramientas: `python3 /tmp/elfhelper.py` (capstone/Thumb) + scripts de barrido propios descritos en la evidencia.
**No se ha usado `mcp_rea` para binarios.** Evidencia: `reports/evidence/film-pb-1-sub-streamarea-20261126/`.

## Resumen (≤20 líneas)

1. **VAs: los del informe `film-pb-1-sub-dmm-area-20261126.md` sí cuadran.** Auditoría automática de sus 148 VAs: 142 en sección y 6 fuera, y los 6 son triviales o ajenos al ELF (`0x0`, `0xb`, dos tamaños `0x1800000`/`0x2000000` y las dos VA del anillo de RAM `0x82DF9300`/`0x82DFC400`). Ninguno desplazado `0x10000` (`09-auditoria-va.txt`).
2. `StreamAreaFree` = **0x5F802C** (confirmado por sus 4 cadenas), y `0x5F63CA(entry, 0)` pone a cero **`+0x00/+0x04/+0x08/+0x10/+0x14`** de la entrada de `0x18` —incluido el **tamaño en `+0x08`**— y deja **intacto `+0x0C`**.
3. Solo tiene **2 llamadores directos**, y son colas `b.w` desde dos envoltorios: `0x5F8110` (pasa la máscara) y `0x5F8128` (fija `7`). No hay `bl` directo, ni `blx rN`, ni puntero a la función en ningún literal (`03-llamadores-free.txt`).
4. Esos dos envoltorios suman **71 emplazamientos** (2 + 69); los 69 de la máscara fija `7` se reparten en salida/teardown (17), operaciones de volumen Dubbing/Copy/Move/Divide/Delete/DPOF/import/Finalize (48) y entradas de modo (4). Máscara `7` = **todas** las `areaType`, incluido el hueco 11 (`10-resumen-transiciones.txt`).
5. **En arranque normal el hueco 11 NO queda asignado con el área de vídeo.** La tabla `0xA4F368` nace a cero en `.bss` y solo la escribe `DistributeBufInfo`; `MemInfo::Init` rellena la tabla **fija** `0xA4FD88`, no ésta. Y el modo que de verdad se alcanza en esta cámara (`m_systemType=1`) es el **14**, con hueco 11 = **`0x01400000`** (20 MiB); el `0x01C00000` (28 MiB) del modo 1 exige `type=2` y **ningún llamador lo pasa** (§3.1 bis).
6. El primer PlayMovie no asigna nada por sí mismo: la asignación ocurre en la **entrada de modo** `EnterMoviePb` (core `0x437A28`), que es previa al Play en el mismo modo.
7. `EnterMoviePb` llama a `GetMemoryInformation` con el 3.er argumento **`r2=1`**, es decir **siempre `StreamAreaAllocate`**; `ChangeAllocate` no participa en la entrada de vídeo (solo en `EnterRecAtRecovery 0x43F004` y en los caminos de grabador de miniaturas, que pasan el byte `param[+0x64]` como flag).
8. La reasignación del hueco 11 la hacen por tanto `EnterMoviePb`/`EnterMovieThumbnailPb`/`EnterMoviePbStillRec`, cada una dentro de su propia entrada de modo, con `SetArea([0xA4F368+0x108],[+0x110])` en `SetUpPlayerInstance(setupMode=1)`; el tamaño que queda es el del modo alcanzado (14 → `0x01400000`, 8 → `0x01800000`).
9. **Sí existe camino de liberar sin reasignar**, y no hace falta ninguna carrera: (a) toda salida de reproducción libera con máscara `7` y deja el área a cero hasta el siguiente `Enter*Pb`; (b) `ChangeAllocate` **borra con máscara `7` (`0x5F7F94-0x5F7F98`) y luego solo rellena** las `areaType` que encuentre en el *ramMap*; (c) **dos** llamadas a `SetUpPlayerInstance` (`0x43094C` y `0x43530A`) usan un `MemInfo` **cacheado** sin volver a pedirlo (una tercera, `0x439812`, pasa NULL y no llega a `SetArea`).
10. Secuencia observable de ese camino (y la del log real): `StreamAreaFree(next) unitHandle=…, subArea=00000007 !!` → `… complite` → (sin `StreamAreaAllocate`/`ChangeAllocate` entremedias) → `SetUpPlayerInstance … + SetUp mode : N` → `[CACHE]BUFFER SIZE TOO SMALL : 00000000` + `[CACHE]ERROR(C1000002h)` → `[CACHE]ERROR(C1000010h)` en el primer `GetArea`.
11. **Corrección al informe previo (importante):** el `SetArea(0)` del anillo del 20-10 **no es del área de vídeo**. Precede al callback `EnterStillPb` y el `C1000010h` lo emite el `GetArea` del `StillCache`, así que es el camino de **foto** (`setupMode=2`, hueco **13**), no el hueco 11 (`08-anillo-observable.txt`).
12. **Corrección 2:** el "0" tiene una causa que el informe previo no contempla — `DistributeBufInfo` **omite** la entrada si el *ramMap* no tiene esa `areaType` (`0x5F71DE`→`0x5F7444`). La reasignación puede "tener éxito" y no escribir nada (`06-distributebufinfo.txt`).
13. **Corrección 3:** `ChangeAllocate` libera y rellena en la misma función, así que "liberado y no reasignado" también ocurre **dentro** de una reasignación aparentemente correcta.
14. No verificado (necesita traza, no cámara todavía): cuál de los dos sitios con `MemInfo` cacheado aparece en la cámara real, y si el *ramMap* de este modelo tiene `areaType 0` para el modo de vídeo. Discriminadores concretos en §6.

---

## 0. Auditoría de VA (encargo del usuario)

`.text` empieza en `0x120228` y el primer `LOAD` del ELF tiene `Offset 0x0 == VirtAddr 0x0`, así que **en ese segmento VA == offset de fichero** y un VA se puede volcar directamente (`xxd -s 0x5f802c`). El segundo `LOAD` sí va desplazado (`.data`/`.got`: `Offset 0x9BB1C8` vs `VirtAddr 0x9C31C8`, `+0x8000`), y `.bss` es NOBITS.

Repaso automático del informe previo (`09-auditoria-va.txt`):

```
VAs citados: 148 ; fuera de toda seccion: 6 -> 0x0, 0xb, 0x1800000, 0x2000000, 0x82df9300, 0x82dfc400
```

Los dos últimos son las VA del anillo de log en RAM (`ram_0x80000000.bin`), no del ELF; `0x1800000`/`0x2000000` son tamaños de tabla, y `0x0`/`0xb` son constantes. **Ningún VA de código o datos del informe previo está desplazado.** Los 52 VAs que usa *este* informe están verificados uno a uno con su sección en el mismo fichero de evidencia (incluidos `0xA4F368`, `0x9DECAC`, `0x9DEDB6`, `0xAD4F68`, todos dentro de `.bss`/`.data`).

Lo que sí hay en el informe previo son **tres correcciones semánticas** (§5), no de direcciones.

---

## 1. `StreamAreaFree` (0x5F802C) y `0x5F63CA(entry, 0)`

### 1.1 Identificación

`0x5F802C` está dentro de `.text` y es la única función que referencia las cuatro cadenas
`0x8DA930` `"[MemInfo]StreamAreaFree(next) unitHandle =%08x, subArea = %08x !!"`,
`0x8DA972` `"…Mem_NonCache unregistered !!"`, `0x8DA9AD` `"…RegisteredMemory still remain."` y `0x8DA9EA` `"…complite"`.
Firma deducida: `StreamAreaFree(unitHandle /*r0*/, subArea /*r1, máscara*/)`.

```
5f802c  push.w {r4,r5,r6,r7,r8,sb,lr} ; sub sp,#0xc
5f8032  ldr r6,=0x009DECAC            ; modo de bufer ACTUAL
5f8034  r5=r0 (unitHandle) ; 5f8038 r4=r1 (subArea)
5f803a  ldr.w r8,=0x00A4F264
5f803e  bl 0x5F9E0C / 5f8042..5f804a  ; traza "[MemInfo]StreamAreaFree(next) unitHandle…"
5f804e  ldr r0,[r6]                    ; r0 = [0x9DECAC]
5f8052  ldr r1,=0x00A4F368             ; r1 = tabla de 0x18/entrada
5f8050  mov r2,r4                      ; r2 = subArea
5f8054  bl 0x5F7EA8                    ; <-- limpieza por máscara (unico usuario de 0x5F63CA)
5f8058  bl 0x5F6874 (r0=unitHandle, r1=subArea)   ; RemoveAreaExtList
5f8060  if ([0xA4F264]) bl 0x5F7D88(0xA4F368)
5f808a  bl 0x5F6828 (IsRemainMappedMemory)
5f8092  if (r0 == 0):
5f8094    [0x9DEDBC] = 0x20 ; [0x9DEC30] = 8 ; [0x9DECAC] = -1
5f80a8    puntero = [0xA4F0AC]; si !=0 -> bl 0x23FD86 y [0xA4F0AC] = 0   ; suelta el ramMap
5f80c2  traza "…complite" ; 5f80e0 b.w 0x5F9AD4(r0=0x21, unitHandle, subArea>>16, subArea&0xFFFF)
```

`0x5F7EA8(modeId, tabla, máscara)` recorre la lista de modos (`[0xA4F0A4]` = `0x8D87E8`), localiza el
modo cuyo `[+4] == modeId`, y para cada área de ese modo (`{+0=tamaño, +4=areaType, +8=índice}`, paso `0xC`,
fin `[+8]==-1`) comprueba `areaType2mask(areaType) & máscara` (`0x5F685C`, tabla `0x8D9030`) y, si casa,
llama a **`0x5F63CA(&tabla[0x18*índice], 0)`** (`0x5F7EE8 mla` / `0x5F7EEC bl`).

### 1.2 Qué campo pone a cero `0x5F63CA(entry, 0)`

```
5f63ca  push {r7,lr} ; add r7,sp,#0
5f63ce  cbnz r1, 0x5f63de        ; si flag != 0 -> no hace nada
5f63d0  movs r2,#0 ; movs r3,#0
5f63d4  str  r1,[r0]             ; +0x00 = 0   vAdrs   (dirección virtual / identificador del área)
5f63d6  str  r1,[r0,#4]          ; +0x04 = 0   pAdrs   (dirección física)
5f63d8  str  r1,[r0,#8]          ; +0x08 = 0   TAMAÑO  <-- el que se pide en SetArea
5f63da  strd r2,r3,[r0,#0x10]    ; +0x10 y +0x14 = 0   offset de 64 bits
5f63de  pop {r7,pc}
```

**Campos puestos a cero: `+0x00`, `+0x04`, `+0x08`, `+0x10` y `+0x14`.** El dword de **`+0x0C` no se toca**
(la función hermana `0x5F63B0` copia los cinco campos desde un origen, tampoco `+0x0C`).
Consecuencia: tras un `StreamAreaFree` el puntero `0xA4F368` sigue siendo válido y el descriptor sigue teniendo
dirección `0` y **tamaño `0`**; cualquier cliente que lo use directamente llama a `SetArea(0, 0)`.

---

## 2. Todos los llamadores y en qué transición ocurren

### 2.1 Método (para que sea reproducible)

Barrido de media palabra en **todo** `.text` (`0x120228`–`0x7A3E84`) reconociendo los tres formatos de 32 bits:
`bl` (`hw2 & 0xD000 == 0xD000`), `blx imm` (`… == 0xC000`) y cola `b.w` (`… == 0x9000`), más re-verificación
**con capstone de cada acierto** (columna `OK` de la evidencia). Además búsqueda en todo el fichero de punteros
literales a `0x5F802C` y `0x5F802D`: **0 aciertos**, así que la función no es direccionable y no hay `blx rN`.

### 2.2 Llamadores directos: 2, y son colas desde dos envoltorios

| sitio | tipo | destino | qué pasa |
|---|---|---|---|
| `0x5F811E` | `b.w` | `0x5F802C` | en `0x5F8110`: `StreamAreaFree(*(u16*)0x9DEDB6, r0_del_llamante)` |
| `0x5F8136` | `b.w` | `0x5F802C` | en `0x5F8128`: `StreamAreaFree(*(u16*)0x9DEDB6, 7)` |

`0x9DEDB6` es el `unitHandle` que fija `StreamAreaAllocate` en `0x5F7CD6` (`strh r4,[r3]`, `r4 = *[r4]`).

### 2.3 Transitive closure: 2 + 69 emplazamientos

`0x5F8110` (**2** llamadores): `0x43C688` (función `0x43C674`, callback `"CB_REC_START"`) y `0x5F8E88`
(`MEMI … Free [AreaType]`, comando de depuración).
`0x5F8128` (**69** llamadores): listado completo en `03-llamadores-free.txt`, clasificado en `10-resumen-transiciones.txt`.
Agrupado por transición:

| grupo | nº | transición | ¿reasigna después en la misma función? |
|---|---|---|---|
| A | 17 | **salida / teardown**: `ExitThumbnailPb 0x4370D4`, `ExitStillPb 0x439710`, `ClearPlayerInstance 0x4394A4`, `ClearRecorderInstance 0x43F644`, `PlayerCallback` ids `0x00`/`0x20`/`0x21`/`0x60` (`0x438148`, `0x43A6D0`, `0x43A73C`, `0x436FCC`), `SetWaitCoreCtrl 0x429850` (2), `Suspend/ResumeDriveEventCheck`, envoltorio público `0x42898C`, `0x430924` en su rama de fallo, `MEMI Free` | **NO** (por diseño) |
| B | 48 | **operación sobre el volumen**: Dubbing (4), `ChangeRotationAngle`, `DeleteHighlightPL`, `DeleteDirectory`, `Copy`, `Move`, `Divide`, Demo Mode Delete/Protect, `BeginImport`/`EndImport`, `CheckDpofContents`, `WriteDpofFile`, `ClearDpofFile`, `PbStop`, `ProcCbMediaMove/Divide`, `CheckExtDeviceFirmUpConditions`, `UpdateExtDeviceFirmware`, `Enter/ExitMoviePbStillRec` | sí (`GetMemoryInformation` en la misma función) |
| C | 4 | **entrada de modo de reproducción** (`EnterThumbnailPb 0x4366EC`, `EnterAviThumbnailPb 0x436B90`, `EnterMoviePb 0x437A28`, `EnterStillPb 0x4395F8`) — el free está en la **rama de error** (`SetUpPlayerInstance` devolvió 0) | sí, pero ya es un camino de error |

**La máscara `7` no es selectiva.** `areaType2mask` (`0x5F685C` → tabla `0x8D9030`) devuelve
`t0..t2 → 0x2`, `t3..t5 → 0x1`, `t6..t8 → 0x4`, `t9 → 0x1`, `t10 → 0x4`; por tanto `7 == 0x1|0x2|0x4`
**casa con todas** las `areaType` definidas. Como el hueco 11 es `areaType 0`, **cualquiera de los 69 sitios lo
borra** cuando el modo activo es uno de los que lo declaran (todos menos los modos 0 y 17).

---

## 3. ¿Queda asignado el hueco 11 en un arranque normal antes del primer PlayMovie?

### 3.1 El hueco 11 y qué significa "asignado"

Entrada `idx = 11` ⇒ desplazamiento `11 * 0x18 = 0x108`; `+0x108` dirección, `+0x110` tamaño.
En la tabla de modo **1 (Movie Pb)** el hueco 11 es `tamaño 0x01C00000` (28 MiB), `areaType 0`.
Pero **el hueco 11 existe en casi todos los modos, con otro tamaño**: modo 2 (Still Pb) `0x01800000`,
modo 14 `0x01400000`, modo 8 `0x01800000`, modo 10 `0x01200000`… (`05-tablas-modo-y-mascaras.txt`).
Por tanto "asignado" nunca significa "con el área de vídeo": significa *"escrito por el último modo configurado"*.

### 3.1 bis · Qué modo de tabla se alcanza de verdad en esta cámara

`Type2Mode` elige tabla por `m_systemType = [0x9DEFE0]`. En libmpr **no hay ningún `str` a `0x9DEFE0`** (sus 6
referencias son cargas de literal y `MemInfo::Init` no lo escribe), así que en ejecución vale el de fichero: **1**
⇒ tabla `0x9DE898`. Con esa tabla, los `type` que algún llamador pasa de verdad son:

| `type` que llega | de dónde | `m_bufTblMode` | hueco 11 |
|---|---|---|---|
| `0` | `EnterMoviePb 0x437A9A` (tabla `0x85AA54[param[0x10]]`, valor `0`) | **14** | `0x01400000` (20 MiB) |
| `0x18` | el otro valor de la misma tabla | **no existe** en la tabla sys1 → `Type2Mode` falla → `Allocate` = 0 → error 8 | — |
| `4` | `EnterThumbnailPb 0x436728`, `ProcInMakeThumbEnterIPB 0x446BFE` | 8 | `0x01800000` (24 MiB) |
| `1` | `EnterAviThumbnailPb 0x436BFA`, `EnterStillPb 0x43966A`, `ProcInMakeThumbEnterSPB` | 6 | **sin hueco 11** (su lista, `0x9DB75C`, no lo declara) |
| `5` | `DvdEnterFinalize 0x431102` (con `sub = 0` → antes lo rechaza `0x4284D2`: "Parameter is illegal") | 12 | `0x01C00000` |
| `0x0E`/`0x0D`/`0x15` | operaciones de volumen, `PbStop`, salvage/thumb | no existen → `Type2Mode` falla | — |
| `0x10` | `MemInfo::Init`-side / `GetConnectedSNCVAdrs` | 0 | modo 0, sin hueco 11 |

**Consecuencia:** el único camino normal que deja 28 MiB en el hueco 11 es `type = 5` (finalizado de DVD); el
`type = 2` —el único que lleva al modo 1, el «Movie Pb» que citaba el informe previo— **no lo pasa ningún sitio de
libmpr 3.21**, así que esa entrada de tabla no es alcanzable en esta cámara. El área de vídeo que de verdad se
comanda al hueco 11 en reproducción es la del **modo 14** (`0x01400000`, 20 MiB) y, en los caminos de miniaturas,
la del modo 8 (`0x01800000`, 24 MiB).

### 3.2 Nadie escribe la tabla en el arranque

* La tabla `0xA4F368` es `.bss` (NOBITS), nace a cero.
* Referenciada desde 10 literales: solo **escriben** `StreamAreaAllocate 0x5F7BE8` (`0x5F7D74`) y
  `ChangeAllocate 0x5F7F1C` (`0x5F8010`) a través de `DistributeBufInfo 0x5F703C`; el resto son lectores
  (`0x5F6A60`, `0x5F6B50`, `0x5F937C` = volcados/MEMI, `0x5F802C`/`0x5F81E8` = free).
* `MemInfo::Init 0x5F74D4` llama a `DistributeBufInfo` en `0x5F7654` pero con **`r1 = 0x00A4FD88`**: rellena la
  tabla **fija** de áreas, no la del reproductor.
* Los 33 llamadores de `GetMemoryInformation` son todos entradas de modo / callbacks de operación; **ninguno es
  inicialización de sistema**.

### 3.3 El primer PlayMovie

Cadena verificada: `MprIfMcmd::PlayMovie 0x737F38` → `MprIf::PlayMovie 0x722A48`/`0x7229E0` (sobrecargas de
3 y 4 argumentos) → `FeaIf::PlayMovie 0x44EE9C` → `0x4296D0` (guarda los parámetros en `[core+0xA4]`) y publica el
mensaje `0x4000001D`. La asignación del área **no** está en esa cadena: está en la entrada de modo
`EnterMoviePb` core **`0x437A28`**, cuyo único llamador es el despachador `0x429C54` (cada caso del despacho
`0x42A2xx` llama a un core y salta a `0x42ACB0`; `0x42A2FC` es el caso de `0x437A28`).
`NO_VERIFICADO` que ese caso sea exactamente el del mensaje `0x4000001D`.

```
437a92  r0 = tabla[0x85AA54][param[0x10]]      ; 0x85AA54 = {0x00, 0x18}
437a6c  r1 = 0x10 / 0x80 / 0x100 / 8           ; según bits de capacidad [this+0xDB8]
437aa2  movs r2,#1                             ; <<-- fuerza ALLOCATE
437aa4  bl 0x4284AC                            ; GetMemoryInformation(type,sub,1,param[0xC])
437aa8  [this+0xDAC] = resultado               ; MemInfo*
437ac4  bl 0x43910C                            ; SetUpPlayerInstance(setupMode=1,...)
437aca  bl 0x5F8128                            ; SOLO si 0x43910C devolvio 0 (rama de error)
```

`GetMemoryInformation(contentType, subType, force, extList)` (`0x4284AC`) acaba en:

```
42857c  cbz r5 (== force) -> 0x42858C
428588  b.w 0x5F7BE8   ; StreamAreaAllocate(type, sub, extList)   [force != 0]
428594  b.w 0x5F7F1C   ; ChangeAllocate(type, sub)               [force == 0]
```

`0x5F7BE8` → `Type2Mode(type,sub)` (`0x5F699C`; con `m_systemType = [0x9DEFE0] = 1` usa la tabla `0x9DE898`)
→ `SetRamMapArea 0x5F6F28` → **`DistributeBufInfo(modeId, 0xA4F368, ramMap)`** → devuelve `0xA4F368`.
`SetUpPlayerInstance(setupMode=1)` lee entonces `[+0x108]/[+0x110]` (`0x439256/0x43925A`) y llama a
`StreamCache::SetArea(addr,size,1)` en `0x43945C`.

**Respuesta a (3):** en un arranque normal el hueco 11 **no está asignado con el área de vídeo** antes del primer
PlayMovie: el área de 28 MiB entra ahí cuando se ejecuta `EnterMoviePb` (o `EnterMovieThumbnailPb` /
`EnterMoviePbStillRec`), que es la **entrada de modo** previa al Play dentro del mismo modo. Y la reasigna
**siempre `StreamAreaAllocate`**, nunca `ChangeAllocate`, porque `EnterMoviePb` pasa `force = 1` de forma literal.
`ChangeAllocate` solo aparece en `EnterRecAtRecovery` (`0x43F004`, `force = 0`) y en los caminos de grabador de
miniaturas `ProcInMakeThumb*` (`r2 = param[+0x64]`, que puede ser 0), además de la llamada directa por el thunk
`0x5F8020` desde `ThumbnailRecorder::SetMemoryTable` (`0x330118`).

---

## 4. ¿Hay camino en el que se libere y NO se vuelva a asignar?

**Sí, y de tres clases distintas.** Las tres terminan en el mismo sitio: `SetArea` con tamaño 0.

### 4.1 (a) Salida de reproducción — el estado de reposo normal

Los 17 emplazamientos del grupo A liberan con máscara `7` y **no** reasignan. Es el diseño: al salir de
reproducción el área se devuelve y la tabla queda a cero hasta la próxima entrada de modo. En ese intervalo el
descriptor sigue **no nulo** y con tamaño `0`. Cualquier consumidor que no pase por `GetMemoryInformation`
(`0x430924`, `0x43525C`, `0x439794`, y el `SetArea(0,0,1)` literal de `setupMode > 5` en `0x43944E`) lee ceros.

### 4.2 (b) `ChangeAllocate` libera y rellena en la misma función, y el relleno puede no cubrir la entrada

```
5f7f90  ldr r0,[sl]            ; [0x9DECAC] = modo actual
5f7f94  movs r2,#7
5f7f96  ldr r1,=0x00A4F368
5f7f98  bl 0x5F7EA8            ; <<-- borra con mascara 7 (TODAS las areaType) del modo actual
5f7f9c  ldr r0,[r7] ; ldr r1,=0x00A4F368 ; ldr r2,[0xA4F0AC]
5f7fa4  bl 0x5F703C            ; <<-- rellena SOLO lo que el ramMap tenga
```

Y en `DistributeBufInfo`, la entrada de la tabla **solo se escribe si el *ramMap* tiene una entrada con la misma
`areaType`**:

```
5f71d8  r2 = [areaModo+4]      ; areaType declarada por el modo
5f71da  r1 = [ramMap+8]        ; areaType registrada
5f71dc  cmp r1,r2
5f71de  bne.w 0x5f7444         ; <<-- SI NO CASA: no escribe nada y pasa a la siguiente
5f71e6  muls r2, 0x18 ; sl = tabla + 0x18*indice
5f73be/5f73ce  str  -> [+0x00] dirección     5f73dc -> [+0x04] física
5f73e0         str  -> [+0x08] TAMAÑO (de la tabla de modo)
5f73c4/5f73d6  strd -> [+0x10] offset 64 bits
```

Así que una reasignación puede **tener éxito** (`DistributeBufInfo` devuelve distinto de 0) y dejar el hueco a
cero. Esto es una tercera causa del `0`, además de "nunca escrito" y "borrado por `StreamAreaFree`".

### 4.3 (c) `SetUpPlayerInstance` con `MemInfo` cacheado (sin `GetMemoryInformation`)

`SetUpPlayerInstance 0x43910C` recibe el `MemInfo*` como 8.º argumento (`[sp+0x44]` → `r5`) y elige hueco por
`setupMode` (tabla `tbb` en `0x4391F4`: `1→0x4391FA`, `2→0x439264`, `3→0x4392E0`, `4→0x4391FA`, `5→0x439378`,
`>5→0x43944E`):

| setupMode | hueco leído | offsets |
|---|---|---|
| 1 y 4 | **11** | `+0x108` / `+0x110` |
| 2 | **13** | `+0x138` / `+0x140` |
| 3 | 11 o 13 según el 9.º argumento (`cmp r8,#0x40000031` en `0x439312`) | |
| 5 | **11** | `+0x108` / `+0x110` |
| >5 | ninguno: `SetArea(0,0,1)` literal en `0x43944E` | |

De las **12** llamadas, **9** van precedidas de `GetMemoryInformation` en la misma función. Las **3** que no:

| sitio | función | setupMode | `MemInfo` que pasa | ¿llega a `SetArea`? |
|---|---|---|---|---|
| `0x43094C` | `0x430924` (único llamador `0x42B9AC`) | 2 → hueco 13 | `[this+0xDAC]` **cacheado** | sí |
| `0x43530A` | `0x43525C` (`GetMMgrObj for BGM` / `EnterBgmRead`) | 5 → hueco **11** | `[this+0xB0]` | sí, si ese campo no es 0 |
| `0x439812` | `0x439794` `SetPreLoadStill` | 2 → hueco 13 | **0 (NULL)**: `0x4397FE-0x439808` pone a cero `[sp+4..0x10]` | **no**: `0x4392C8 beq 0x439460` lo salta |

Los **dos** candidatos reales son por tanto `0x430924` (hueco 13) y **`0x43525C` (hueco 11)**: usan un `MemInfo`
que no han pedido, y basta con que un `StreamAreaFree(unit,7)` (o un `ChangeAllocate` de §4.2) haya pasado entre
la última asignación y esa llamada. `0x439794` no puede producir el síntoma porque pasa puntero nulo.

### 4.4 Secuencia observable (la que hay que buscar en una traza de nivel 5)

1. `[MemInfo]StreamAreaFree(next) unitHandle =xxxxxxxx, subArea = 00000007 !!` … `[MemInfo]StreamAreaFree(next) complite`
   (`0x8DA930` / `0x8DA9EA`), opcionalmente `… Mem_NonCache unregistered !!` / `… RegisteredMemory still remain.`
2. **Ausencia** de `[MemInfo]StreamAreaAllocate(next):type=…` (`0x8DA503`) y de `[MemInfo]ChangeAllocate Start!!`
   (`0x8DA873`) entre la liberación y el paso 4. Si aparece `ChangeAllocate Start!!`, mirar cuántas líneas
   `**DistributeBufInfo -- areaType…` (`0x8D9A08`) salen y si falta la de `areaType 0`.
3. `SetUpPlayerInstance ... + SetUp mode : N` (`0x85AAB7`). **N=1, 4 ó 5 ⇒ hueco 11**; N=2 ⇒ hueco 13; N>5 ⇒ `SetArea(0,0)`.
4. `[CACHE]BUFFER SIZE TOO SMALL : 00000000` (`0x93E866`) + `[CACHE]ERROR(C1000002h)`.
   El comparador es `0x759562 cmp r4(size), sb([0xAD4F68])` → si `size < mínimo` salta a `0x759566` y devuelve
   `C1000002` **sin dejar el área puesta**.
5. `[CACHE]ERROR(C1000010h)` en el primer `GetArea` (`"STREAMCACHE NOT SET AREA"`).

Los cuatro emparejamientos del anillo real del 20-10 (`08-anillo-observable.txt`):

```
112 [CACHE]BUFFER SIZE TOO SMALL : 00000000
113 [CACHE]ERROR(C1000002h)
114 [MprIf] Callback EnterStillPb
116 [CACHE]ERROR(C1000010h)
```

**Leído con el código: esto es el camino de FOTO, no el de vídeo.** El `SetArea(0)` ocurre *antes* de que se
entregue el callback `EnterStillPb`, y `EnterStillPb` core (`0x4395F8`) usa `setupMode = 2` (`0x439696`), es decir
el **hueco 13** (`+0x138/+0x140`). El `C1000010h` siguiente lo emite el `GetArea` del `StillCache`, que es lo que
provoca el `dfs::seek`/`read` fallido de las líneas 117-126. El hueco 11 no aparece en esas líneas.

---

## 5. Correcciones al informe `film-pb-1-sub-dmm-area-20261126.md`

1. **Falta una tercera causa del `0`.** Ese informe dice "`0` = campo nunca escrito" y "`0` = campo borrado".
   Hay una tercera: **el relleno no escribe la entrada** porque el *ramMap* no tiene esa `areaType`
   (`0x5F71DE`→`0x5F7444`). La reasignación puede devolver éxito y no escribir (§4.2).
2. **`ChangeAllocate` libera antes de rellenar** (máscara `7` en `0x5F7F94-0x5F7F98`). El informe no lo menciona
   y es la vía por la que "liberado y no reasignado" ocurre dentro de una operación que aparenta ser una
   reasignación completa.
3. **`StreamAreaFree` no es invocable desde el reproductor de vídeo "en general"**: solo hay 2 llamadas directas y
   son colas de dos envoltorios; los 69 emplazamientos son todos del subsistema de medios/estado, y **17 de ellos
   son teardown** (liberan y dejan a cero por diseño). Además el free de las entradas de modo está en la **rama de
   error**, no en la buena.
4. **El `SetArea(0)` del log real es del camino de foto (hueco 13), no del hueco 11** (§4.4): sirve como prueba de
   que el mecanismo "descriptor válido con tamaño 0" existe y se dispara de verdad, pero no demuestra nada sobre el
   área de vídeo. Y el anillo **no contiene ni una sola línea `[MemInfo]…`** (ni `StreamAreaAllocate`, ni
   `ChangeAllocate`, ni `StreamAreaFree`), así que con ese log **no se puede decidir** cuál de las tres causas de §4
   produjo el 0 del hueco 13. Ese es exactamente el dato que falta y el que hay que capturar.
5. Detalle menor: `0x5F63CA` **no toca `+0x0C`** de la entrada.

Se mantiene del informe previo (verificado aquí): `0x5F802C` = `StreamAreaFree`; `+0x108/+0x110` = hueco 11;
`+0x138/+0x140` = hueco 13; `0xA4F368` singleton de `.bss` con entradas de `0x18`; `0x8D87E8` = lista de modos
(`{ptr áreas, modeId}`); modo 1 = Movie Pb (`0x9DB0E4`, hueco 11 = `0x01C00000`), modo 2 = Still Pb (`0x9DBD20`),
modo 4 = Still Rec (`0x9DA8E0`); `m_systemType = 1` en fichero y tabla `0x9DE898`; `MemInfo::Init` no toca
`0xA4F368`; el tamaño **no** se pide al DMM.

---

## 6. Qué queda y cómo cerrarlo sin cámara primero

* `NO_VERIFICADO` con binario: si el *ramMap* de este modelo (`SetRamMapArea 0x5F6F28` sobre la lista de unidades
  `[0xA4F0A8]`, filtrada por `m_ramMapAreaMode`) contiene `areaType 0` para el modo alcanzado en reproducción de
  vídeo (modo 14 ⇒ `ramMapAreaMode 3`; modo 8 ⇒ 5; modo 6 ⇒ 4), y lo mismo para el hueco 13 del modo 6 en foto.
  Es el siguiente paso estático y decide si el `0` puede salir **sin** ningún `free` (causa §4.2).
* `NO_VERIFICADO`: cuál de los dos sitios con `MemInfo` cacheado (`0x43094C` hueco 13, `0x43530A` hueco 11) se
  ejecuta en la cámara real. Se distingue en la traza por la línea `+ SetUp mode : N` (§4.4).
* Prueba con la cámara (cuando se autorice): subir traza a nivel 5 y reproducir; con `CMD(SET_AREA)` (`0x93E839`),
  `Type2Mode:` (`0x8D90C0`), `ChangeAllocate Start!!` (`0x8DA873`) y `StreamAreaFree` (`0x8DA930`) se cierra en un
  minuto cuál de las tres clases de §4 es la que aparece, y con qué `+ SetUp mode :` se corresponde.

## 7. Evidencia

| fichero | contenido |
|---|---|
| `01-streamareafree-0x5f802c.txt` | desensamblado completo + las 4 cadenas identificativas |
| `02-zero-entry-0x5f63ca.txt` | `0x5F63CA` con su gemela copiadora y el `mla`/`bl` que la invoca |
| `03-llamadores-free.txt` | barrido: 2 directos + 2 + 69, con función contenedora y verificación capstone |
| `04-asignacion-y-changeallocate.txt` | las dos vías, el thunk `0x5F8020` y los 10 literales de `0xA4F368` |
| `05-tablas-modo-y-mascaras.txt` | lista de modos, listas de áreas (con los huecos 11 marcados), tabla `Type2Mode` sys1 y tabla de máscaras |
| `06-distributebufinfo.txt` | el único escritor: offsets escritos y el filtro por `areaType` |
| `07-setupplayerinstance.txt` | tabla `tbb`, qué hueco lee cada `setupMode`, `SetArea` y su comprobación de tamaño mínimo |
| `08-anillo-observable.txt` | líneas 104-121 del anillo real del 20-10 con la lectura estática de cada una |
| `09-auditoria-va.txt` | los 52 VAs de este informe con su sección, y el repaso de los 148 del informe previo |
| `10-resumen-transiciones.txt` | los 71 emplazamientos agrupados por transición y las 12 llamadas a `SetUpPlayerInstance` |
