# ¿Funciona el camino de ESCRITURA de un clip nuevo después de crear el sector FBM `0x31`?

**Fecha:** 26-11-2026 · **Ámbito:** QEMU (perfil `nf4`, `NFLASH4=1`) sobre **copias** de
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin`. La cámara no se ha tocado y no se ha usado
`mcp_rea`. **Evidencia:** [`reports/evidence/clip-write-cs-wpb-20261126/`](evidence/clip-write-cs-wpb-20261126/README.md)
(sonda `nf4clip.c` → `nf4clip.so` `3cce22fc…`, lanzador `pb_run_clip.py`, cinco `run*/consola.log`,
`dis-escritura.txt`). Las cinco pasadas salen del **mismo** `.so` y del mismo lanzador.

## Resumen (≤15 líneas)

1. **Antes** (prístina `a5ab15ca…`, tabla 1/30): `ChangeSector(4,3)` = `0x10100006`, `WritePackBegin(4,3,0,0x800,&pack,0,0)` = `0x10100001`, **0 B** escritos (`runPre/consola.log`).
2. **Después** (`6d2ab43a…` = sector `0x31` creado y persistido, al arrancar `idx10 h1 esto1 om6` sin escribir nada): `ChangeSector(4,3)` = `0x10800010`, `WritePackBegin` = `0`, `WritePackAdd` = `0`, `WritePackEnd` = `0x10800020` y **0 B** en nflasha4 en todos los diffs; el relleno `0x5a` del payload no aparece (`runPost/consola.log`).
3. Los dos son fallos **reales**, no artefactos de llamar sin el objeto `m2psIfo_Backup`: esas rutinas sólo usan sus argumentos y las tablas `0xA3699C`/`0x9D23FC` (ver `dis-escritura.txt`), y la fila `0x9D23FC[13]` tiene `fn = 0` **medido en el invitado recién arrancado**.
4. Fallo 1, punto exacto: `0x2B4232` ← `0x2B4030` ← `0x2B3000`, que salta las filas con `fn == 0` (`cbz r2`, `0x2B301A`) y devuelve `0x10800010` en `0x2B2FF8`.
5. Fallo 2, punto exacto: `WritePackEnd 0x2B3C18` → `0x2B25D0` → `GetSectorInfo` da `validDataSize=0xffffffff` ≠ `currentSeekPoint=0xa` → rama «Seek position error» (`0x2B25F8`) → `ChangeSeekPoint` → `0x2B242C` traduce el código crudo `0x11` = **`FBS_UNCERTAIN_WRITE_POINT`** a `0x10800020` (el mismo `0x11` da la sonda directa `FlashLib::WriteSector(1,0x10)`).
6. **Falta X:** el registro de `fn` en `0x9D23FC[13]` (`u04/m3/ft031/om6`), lo que hace `FBM EWBDFD 4 3 0` — y que **sólo vive en RAM**; con sector + `fn`: `ChangeSector(4,3)=0`, `WritePackBegin/Add/End = 0` y **4 770 B** escritos, payload `0x5a` en `0x3A0206` (`runFnPost/consola.log`).
7. **Conclusión (una línea):** *no, falta X — el `fn` de `0x9D23FC[13]` (lo que registra `EWBDFD`, sólo en RAM): con el sector `0x31` persistido y `fn=0`, `ChangeSector` da `0x10800010` y `WritePackEnd` `0x10800020` (`FBS_UNCERTAIN_WRITE_POINT`) sin escribir nada; con `fn` presente, el clip queda registrado (4 770 B medidos).*

## 1. Qué se ha llamado, y la firma real

Todo por dirección dentro del propio `im.elf` del invitado (2º `.so` precargado; la base de `libmpr`
se obtiene con `dladdr` sobre un símbolo exportado de `FlashLib`, como en el arnés anterior):

| llamada | dirección | firma real | de dónde sale |
|---|---|---|---|
| `ChangeSector` | `0x2B41B4` | `unsigned ChangeSector(unsigned userID /*r0*/, unsigned mediaID /*r1*/)` | su propio log: `"ChangeSector(userID,mediaID)"` en `0x7E7BA5`; `r0`→`0x2B3094`, `0x2B2BCC` (OM) y `0x2B4030`; `r1` = mediaID |
| `WritePackBegin` | `0x2B3D24` | `unsigned WritePackBegin(unsigned userID /*r0*/, unsigned mediaID /*r1*/, unsigned dataID /*r2*/, unsigned dataSize /*r3*/, RWBPACK *pack /*[sp+0]*/, unsigned /*[sp+4]: no se lee*/, unsigned operationMode /*[sp+8]*/)` | cuerpo completo + log `"[FBM]<RWB>WritePackBegin userID[0x%x]mediaID[0x%x]dataID[0x%x]operationMode[0x%x]"` (`0x7E7879`) + sus dos llamantes |
| `WritePackAdd` | `0x2B3C64` | `unsigned WritePackAdd(RWBPACK *pack, unsigned char *data, unsigned len)` | log `"WritePack"`; `[pack+0x22]==0xffff` ⇒ `0x10100006` |
| `WritePackEnd` | `0x2B3B94` | `unsigned WritePackEnd(RWBPACK *pack)` | log `"WritePackEnd"`; exige `curDL == totalDL` |

`pack` es un struct de 0x28 B **del llamante** (`0x2B38B4` = `<RWB>GetRWBuffer` le da índice de búfer
en `+0x22`, `0xFFFF` si no hay ninguno). El llamante real del clip (`m2psIfo_Backup.cpp`, **dentro de
`libmpr`**, cadena en `0x8C5B54`) lo deja claro:

```
0x5C9F7C  movs r0, #4                 ; userID = 4
0x5C9F7A  ldr  r1, [r4, #0xC]         ; mediaID
0x5C9F7E  bl   0x2B41B4               ; ChangeSector(4, mediaID)       [m2psIfo_Backup.cpp:0x3ea]

0x5CA158  movs r0, #4                 ; userID = 4
0x5CA152  ldr  r1, [r4, #0xC]         ; mediaID
0x5CA154  mov  r2, sl                 ; dataID  (2.º argumento de la función)
0x5CA162  mov  r3, r6                 ; dataSize (longitud; si es impar se redondea a par)
0x5CA15A  str  r3, [sp]               ; [sp+0] = &pack local
0x5CA15E  str  r3, [sp, #4]  (=0)     ; [sp+4] = 0  (no se lee)
0x5CA160  str  r3, [sp, #8]  (=0)     ; [sp+8] = 0  operationMode
0x5CA164  bl   0x2B3D24               ; WritePackBegin                 [m2psIfo_Backup.cpp:0x48e]
0x5CA186  bl   0x2B3C64               ; WritePackAdd(&pack, data, len) [m2psIfo_Backup.cpp:0x493]
0x5CA1A2  bl   0x2B3B94               ; WritePackEnd(&pack)            [m2psIfo_Backup.cpp:0x499]
```

El otro llamante, `WriteSectorManagerInfo 0x2B3EF8`, usa `userID = 0x80` (`UID_BACKUP_MANAGER`) y
`[sp+8] = operationMode`: confirma el reparto de los tres argumentos de pila.

## 2. Valores exactos antes y después de crear el sector `0x31`

`dataID = 0`, `dataSize = 0x800`. «Antes» = imagen prístina; «después» = la imagen del parche C /
`EWBDFD`+`InitB` **tras reiniciar** (sector persistido, `fn` otra vez a 0).

| paso | **antes** `a5ab15ca…` | **después** `6d2ab43a…` (`idx10 h1 esto1 om6`) |
|---|---|---|
| `ChangeSector(4,3)` | **`0x10100006`** | **`0x10800010`** |
| diff tras `ChangeSector` | 0 B | 0 B |
| `WritePackBegin(4,3,0,0x800,&pack,0,0)` | **`0x10100001`** (`bufferIndex=0xffff`) | **`0`** — `pack`: `sector=0x31 handle=0x1 totalDL=0x800 hdrDL=0x800` |
| diff tras `WritePackBegin` | 0 B | 0 B |
| `WritePackAdd(&pack, buf 0x5a, 0x800)` | no se llama (falló Begin) | **`0`** (`curDL=0x800`) |
| diff tras `WritePackAdd` | — | 0 B |
| `WritePackEnd(&pack)` | — | **`0x10800020`** |
| diff tras `WritePackEnd` (y +2 s) | — | **0 B** / 0 B · `patron(0x5a×32) = -1` (no está en la imagen) |
| `FlashLib::GetSectorInfo(handle)` | `0x9 FBS_INVALID_PARAM` (handle 0) | **`0`**: `name=0x31 status=3 validDataSize(@+4)=0xffffffff currentSeekPoint(@+0xc)=0xa` |
| `FlashLib::WriteSector(handle,0x10,…)` | `0x9` | **`0x11` crudo** (`FBS_UNCERTAIN_WRITE_POINT`), `written` intacto |
| diff total al final | **0 B** | **0 B** |

En «después» se comprobó además que los atajos de `ChangeSector` **sí** pasan:
`0x2B2B18(4,3)→0 fileType=0x31`, `0x2B2F48(4,3)→0 idx=0xa`, `0x2B3094(4,3)→0 handle=0x1`,
`0x2B2BCC(4)→0 operationMode=0x6`, `0x2B1DCC(6)=0`; lo que falla es el paso siguiente:
`0x2B3000(6,3) → 0x10800010` y `BackupMgr::WriteBaseData(6,3) → 0x10800010`.

## 3. Punto exacto de cada fallo

### 3.1 `ChangeSector(4,3) = 0x10800010`

```
0x2B41D8  bl 0x2B3094      ; userID/mediaID -> índice (0x2B2F48) -> handle de 0xA3699C
0x2B41EC  cbnz r3          ; handle != 0   (si 0: 0x10100006 en 0x2B41F4 — el fallo de ANTES)
0x2B41FC  bl 0x2B2BCC      ; userID -> operationMode = 6
0x2B420E  bl 0x2B1DCC      ; (OM-7<=1)? no
0x2B422E  bl 0x2B4030      ; BackupMgr::WriteBaseData(OM=6, mediaID=3)
0x2B4232  mov r4, r0       ; <-- aquí se devuelve 0x10800010
```

Dentro de `WriteBaseData`, `0x2B3000` recorre `0x9D23FC` y **salta** la fila si `fn == 0`
(`0x2B301A: cbz r2`), acabando en `0x2B2FF8` con `0x10800010`. La fila que toca es
`[13] u04/m3/ft031/om6/fn0/arg0`, `fn = 0` tanto en el fichero `libmpr.so` como en la tabla viva
(`[NF4] tabla 0x9D23FC: … [13]u04/m3/ft031/om6/fn0/arg0`, en los cinco `run*/consola.log`).

### 3.2 `WritePackEnd = 0x10800020`

```
0x2B3C18  bl 0x2B25D0                      ; escritura real del pack
  0x2B25EA bl 0x2B2480                     ; GetSectorInfo(handle) -> FBS_INFO
  0x2B25F2 ldr r1,[r7,#8]    ; validDataSize   = 0xffffffff
  0x2B25F4 ldr r2,[r7,#0x10] ; currentSeekPoint = 0xa
  0x2B25F8 beq 0x2B2612                    ; NO salta (son distintos) -> rama «Seek position error!!»
  0x2B2606 blx 0x11E8D0                    ; FlashLib::ChangeSeekPoint(handle, 0, 0xffffffff)
  0x2B260A bl 0x2B242C                     ; traduce el código FBS
  0x2B244A ldr r4,[pc] = 0x10800020        ; «cualquier otro código» -> 0x10800020
```

El código crudo traducido es **`0x11` = `FBS_UNCERTAIN_WRITE_POINT`** (tabla de cadenas en `0x7E9488`,
`FlashLib::GetErrorString 0x2B6114`); el mismo `0x11` devuelve la llamada directa al símbolo
exportado `FlashLib::WriteSector(1,0x10,…)`. Traducción: **el sector `0x31` existe y se puede abrir,
pero su punto de escritura no está asentado** (`validDataSize = 0xffffffff`), así que el pack del
clip nunca llega al NAND.

## 4. ¿Segundo fallo real o artefacto de llamar sin el módulo `m2psIfo_Backup` vivo?

**Real, no artefacto.** Cuatro medidas:

1. `ChangeSector` (`0x2B41B4`) y `WritePackBegin` (`0x2B3D24`) **no leen estado de instancia**: sus
   únicos datos son `r0..r3` más uno/dos argumentos de pila (desensamblado completo en
   `dis-escritura.txt`). El `this` de `m2psIfo_Backup` sólo se usa en el llamante (`0x5C9F48`,
   `0x5CA134`). Además `m2psIfo_Backup.cpp` está **dentro de `libmpr.so`**: el código sí existe en el
   arnés; lo que no hay es una instancia, y estas dos funciones no la necesitan.
2. La fila `0x9D23FC[13]` tiene `fn = 0` **en el invitado recién arrancado** (las 38 filas volcadas
   en cada pasada; `runPre`, `runPost`, `runBoth`, `runFn`, `runFnPost`): ningún módulo lo registra
   en un arranque completo.
3. **Control con un sector que siempre tuvo handle**: `ChangeSector(0x22,8)` (fileType `0xA0`,
   `idx 0x17 h1`) devuelve **`0x10800010`** igualmente, con `0x2B3000(9,8) = 0x10800010`
   (`runPre/consola.log`). El fallo es de la tabla, no del sector recién creado.
4. `FBM InitB 6 3` **solo** (imagen prístina, `runBoth/consola.log`) devuelve `1` pero **no crea
   nada**: `idx10 h0`, 0 B. El `1 300 B` del estado previo lo aporta `EWBDFD 4 3 0`, que es quien
   registra `fn`.

## 5. Qué falta (X), demostrado con la matriz 2×2

Se escribió el campo `fn` de la fila `[13]` desde la sonda (stub propio que devuelve 0: misma
semántica que el `fn` que registra `EWBDFD`) y se repitieron las llamadas con y sin el sector creado:

| `0x31` creado | `fn` en `[13]` | `ChangeSector(4,3)` | `WritePackBegin` | `WritePackAdd` | `WritePackEnd` | bytes nuevos en `nflasha4` | evidencia |
|---|---|---|---|---|---|---|---|
| no | 0 | `0x10100006` | `0x10100001` | — | — | 0 | `runPre/` |
| **sí** | **0** | **`0x10800010`** | **`0`** | **`0`** | **`0x10800020`** | **0** | `runPost/` |
| no | sí | `0x10100006` | `0x10100001` | — | — | 0 en esas llamadas; `WriteBaseData(6,3)=0` crea el sector (**1 300 B**) y deja `GetSectorInfo` con `validDataSize=0x200`; `WriteSector(3,0x10)=0` (16 B, diff \(1812-1300=512\) B) | `runFn/` |
| sí | sí | **`0`** | **`0`** | **`0`** | **`0`** | **4 770 B**, payload `0x5a` en `0x3A0206` | `runFnPost/` |

Lectura: `ChangeSector` **no** crea el sector (con `fn` y sin sector sigue dando `0x10100006`: el
handle es precondición); lo que hace el `fn` es permitir que `WriteBaseData` **asiente** el sector
(crea y cierra: `CreateSector32` → alta en `0xA3699C` → `fn` → `ChangeSectorToValid` →
`TermSectorData`), y sólo entonces `FlashLib` conoce el punto de escritura y el pack del clip entra.

Matiz importante: `0x9D23FC` es `.data` de `libmpr`, así que **el `fn` que registra `FBM EWBDFD 4 3 0`
no persiste**; el sector `0x31` sí (lo reabre `FBM::Init`). Por eso el clip funciona en el mismo
arranque en que se lanzó `EWBDFD` (o el parche C con `fn`), y deja de funcionar tras reiniciar.

## 6. Conclusión

> **No, falta X:** con el sector FBM `0x31` creado y persistente, un clip nuevo **no** queda
> registrado: `ChangeSector(4,3)` da `0x10800010` en `0x2B4232` (fila `0x9D23FC[13]` con `fn=0`,
> `0x2B301A`) y `WritePackEnd` da `0x10800020` = `FBS_UNCERTAIN_WRITE_POINT` (`0x11`, `0x2B260A`)
> porque el sector no tiene punto de escritura (`validDataSize=0xffffffff`) — **0 bytes** llegan a
> `nflasha4` (`runPost/consola.log`). Falta el `fn` de `0x9D23FC[13]` (lo que registra
> `FBM EWBDFD 4 3 0`, **sólo en RAM**); con él y el sector, `ChangeSector(4,3)=0`,
> `WritePackBegin/Add/End=0` y el clip se escribe (**4 770 B**, payload `0x5a` en `0x3A0206`,
> `runFnPost/consola.log`).

## 7. Ficheros de esta medición

- Informe: este fichero.
- Evidencia: [`evidence/clip-write-cs-wpb-20261126/`](evidence/clip-write-cs-wpb-20261126/README.md) —
  `nf4clip.c`, `pb_run_clip.py`, `comando.sh`, `dis_escritura.py`, `dis-escritura.txt` y
  `runPre/`, `runPost/`, `runBoth/`, `runFn/`, `runFnPost/` (cada uno con su `consola.log`).
- Imágenes: prístina `a5ab15ca…` (volcado del repo) y «sector `0x31` creado» `6d2ab43a…`
  (reconstruida con `evidence/fbm-sector31-c-20261126/reconstruye_imagen.py`; los 10 MiB no se versionan).
- Sonda: `nf4clip.so` → `3cce22fc8aa8f556333bcf1555b5ac16461f441575c2b58b1adb3f6f3d40edaa`.
