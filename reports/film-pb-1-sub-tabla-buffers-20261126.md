# FILM-PB-1 (sub) — Tabla de buffers por modo: verificada, con direcciones comprobadas

Fecha: 26-11-2026. **Solo análisis estático** (sin cámara, sin flasheo, sin ejecutar firmware).
Objeto: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(Thumb-2, 10.321.204 B = **0x9D7D34**).
Evidencia: [`reports/evidence/film-pb-1-sub-tabla-buffers-20261126/`](evidence/film-pb-1-sub-tabla-buffers-20261126/).
Herramientas: capstone del `.venv` con `dump.py`/`dis2.py` (copiados en la evidencia). **No se usó
`mcp_rea` para binarios.**

**Corrige y completa** [la sub-auditoría del área del reproductor](film-pb-1-sub-dmm-area-20261126.md):
aquí quedan el formato de la tabla fuente, el de la tabla destino y los tamaños de los huecos 11
(movie) y 13 (still) para los 35 modos.

> **Corregido por** [film-pb-1-sub-modo-camara-20261126.md](film-pb-1-sub-modo-camara-20261126.md) §7: la
> columna «nombre» de §4 y de la evidencia 08 está **desplazada una posición**. El literal real es
> `0x009DF094`, el formato es `{id, ptr}` (no `{ptr, id}`) y `id 0` = `Movie Pb`; además esa tabla nombra
> el argumento **`type`** de `StreamAreaAllocate`, **no** los `modeId` (que no tienen nombres). Los
> **tamaños** de movie/still de §4 **no cambian**; lo que cambia es quién pide cada modo (los cinco con
> movie = 0 son trabajos de **foto**: `Still Rec`, `Still Pb`, `Still Dubbing`, `Still Pb RAW`).

**Regla VA→offset usada y comprobada** (`readelf -lW`, evidencia 03):

| LOAD | offset | VA | filesz | consecuencia |
|---|---|---|---|---|
| 1 | 0x000000 | 0x00000000 | 0x9BB1C8 | **VA == offset** (cubre `.text` 0x120228–0x7A3E84 y `.rodata` 0x7A3E90–0x956750) |
| 2 | 0x9BB1C8 | 0x009C31C8 | 0x001C640 | **offset = VA − 0x8000** (cubre `.data` 0x9C42E8–0x9DF808) |
| — | — | 0x009DF808–0x00ADBA04 | NOBITS (`.bss`) | **no está en el fichero**: 0xA4F368 no se puede volcar en estático |

Corrige el informe previo en un punto que sí importaba: **las tablas por modo viven en `.data`
(0x9DAxxx–0x9DE6F0) y por tanto su VA no es el offset del fichero**; y el "singleton 0xA4F368"
está en `.bss`, así que su contenido solo existe en ejecución.

---

## 0. Resumen (≤20 líneas)
1. **`DistributeBufInfo` = 0x5F703C** (`.text`): prólogo 0x5F703C, epílogo `pop.w {…,pc}` 0x5F74A4, 4 `bl`
   (0x5F7654/0x5F7CF2/0x5F7FA4/0x5F819E) y todas sus cadenas en su pool 0x5F72CC-0x5F74D0 (la de
   `invalid mode`, 0x8D9F24, se carga en **0x5F7088**). La VA del informe previo era correcta.
2. **Tabla fuente:** por modo, entrada **0xC B** `{+0 size, +4 mt_order, +8 idx}`; terminador `+8 == -1`
   (0x5F712C/0x5F71A8); clave `ldr r3,[r5,#8]` (**0x5F71A6**); tamaño `ldr r3,[r5]` (**0x5F73DA**).
3. **Lista de modos: 0x8D87E8** (`.rodata`), pares `{ptr, modeId}` de 8 B, terminador `ptr==0`; puntero
   publicado en `.bss` 0xA4F0A4 (**0x5F7566**). **35 modos**; **faltan 0x0F y 0x10** (→ `invalid mode`).
4. **Tabla destino: 0xA4F368 + idx·0x18**, entrada 0x18 B `{+0 vAdrs, +4 pAdrs, +8 size, +0x10 offset}`;
   `muls r2,r3,#0x18` (0x5F71E6) y **`dst+8 = [src+0]`** en **0x5F73E0**. Hueco **11 = movie**
   (`+0x108/+0x110`), **13 = still** (`+0x138/+0x140`); base 0xA4F368 (retorno de 0x5F7BE8 en 0x5F7D26).
5. **Tabla completa** (35 modos → movie/still) en **§4**: 21 con movie>0, **5 con movie=0 y still>0**,
   3 con movie presente pero 0 (0x21/0x22/0x24) y 6 con los dos a 0.
6. **Sí existe tal modo: cinco** — 0x03 (24 MiB), 0x06 (22), 0x12 (24), 0x13 (16), 0x20 (3 MiB); con
   `m_systemType=1` alcanzables 0x03, 0x06, 0x12 y 0x20 (§5).
7. **Conclusión (§6):** el 0 no es un cálculo, es una fila de la tabla. **NO_VERIFICADO** qué modo
   (0x9DECAC) se usa en el fallo real.
8. **En cámara (§7):** leer **0x9DECAC**, **0xA4F478** (movie) y **0xA4F4A8** (still), y la línea
   `StreamAreaAllocate(next): complete ret=%ld` (0x8DA720) para separar «tabla» de «fallo de allocate».

---

## 1. Qué se comprobó de las direcciones del informe previo

| VA del informe previo | ¿Cae en sección real? | Veredicto |
|---|---|---|
| 0x8D9F24 (cadena `invalid mode`) | `.rodata` (0x7A3E90–0x956750) | ✅ correcta, `VA == offset` |
| 0x5F703C `DistributeBufInfo` | `.text` (0x120228–0x7A3E84) | ✅ correcta (§2) |
| 0x5F74D4 `MemInfo::Init` | `.text` | ✅ correcta (prólogo distinto, cadena `memInfo::Init insmod"stream2 driver"` en 0x8D9F59) |
| 0x8D87E8 `mp_modeTblForBufTbl` | `.rodata` | ✅ correcta, pero **no es una tabla de nombres**: es la lista `{ptr, modeId}` (§3.1) |
| 0x9DBD20 / 0x9DB0E4 / 0x9DA8E0 | `.data` (0x9C42E8–0x9DF808) | ⚠️ VA correcta, **pero offset = VA − 0x8000**; leer con la VA como offset da basura |
| 0xA4F368 | `.bss` | ⚠️ **no existe en el fichero**: no se puede volcar en estático (solo su *layout* por código) |
| 0x9DF090 "nombres de modo" | `.data` | ⚠️ sí hay nombres (**§4**, evidencia 08), pero **ninguna referencia literal** en `.text` de libmpr ⇒ tabla de depuración, nombres **indicativos** |
| 0x5F73BE/0x5F73CE/0x5F73DC/0x5F73E0 (escrituras al destino) | `.text` | ✅ correctas, confirmadas una a una (§3.3) |

Ninguna VA de este informe se ha usado sin comprobar antes la sección; las de `.data` se leen con
`offset = VA − 0x8000` y las de `.bss` no se leen.

---

## 2. `DistributeBufInfo` = 0x5F703C (prueba)

* Cadena `"[MemInfo]DistributeBufInfo() invalid mode !:mode=%ld"` en **0x8D9F24** (`.rodata`).
  Su único literal de 32 bits en todo el fichero está en **0x5F72D4**, y lo carga la instrucción
  **`ldr r2,[pc,#0x248]` en 0x5F7088**, dentro de 0x5F703C–0x5F74A4.
* Prólogo `push.w {r4,r5,r6,r7,r8,sb,sl,fp,lr}` + `sub sp,#0x5C` en 0x5F703C.
  Epílogo `pop.w {r4,r5,r6,r7,r8,sb,sl,fp,pc}` en **0x5F74A4** (la función acaba ahí;
  0x5F74A8–0x5F74D2 es su pool de literales y 0x5F74D4 es ya `MemInfo::Init`).
* Cuatro `bl` la llaman: 0x5F7654 (`MemInfo::Init`, con `r1 = 0xA4FD88`, la tabla de áreas fijas),
  **0x5F7CF2 (`StreamAreaAllocate`, `r1 = 0xA4F368`)**, **0x5F7FA4 (`ChangeAllocate` 0x5F7F1C,
  `r1 = 0xA4F368`)**, **0x5F819E (`ExtraStreamAreaAllocate`, `r1 = 0xA4F368`)**.
* Firma deducida de las cadenas: `int DistributeBufInfo(int mode, void* p_bufInfoTbl,
  void* p_RamMapAreaInfo)`; devuelve 1 en 0x5F749C (éxito) y 0 en 0x5F7498 (fallo).

Convención de nombres: las cadenas del propio binario llaman `p_bufInfoTbl` a 0xA4F368 y
`p_RamMapAreaInfo` al tercer argumento.

---

## 3. Formato de las tablas (con instrucciones y VA)

### 3.1 Selección de la tabla del modo

```asm
005f705e: ldr  r3,[pc,#0x270]   ; [005f72d0] = 00A4F0A4   <- global .bss con el puntero a la lista
005f7060: ldr  r2,[r3]          ; r2 = *(0xA4F0A4) = 0x008D87E8   (lo fija 0x5F7566)
005f7062: movs r3,#0
005f7064: b    0x5f707a
005f7066: adds r0,r2,r3         ; entrada = lista + i*8
005f7068: ldr  r4,[r7,#0x34]    ; r4 = mode (arg0)
005f706a: adds r3,#8            ; stride = 8
005f706c: ldr  r0,[r0,#4]       ; +4 = modeId (campo clave)
005f706e: cmp  r0,r4
005f7070: bne  0x5f707a
005f7072: str  r1,[r7,#0x44]    ; guarda la tabla del modo
005f707a: ldr  r1,[r2,r3]       ; +0 = puntero a la tabla del modo; terminador: == 0
005f707c: cmp  r1,#0
005f707e: bne  0x5f7066
```

* Lista de modos: **0x008D87E8** (`.rodata`), entrada **8 B** `{+0 ptrTabla, +4 modeId}`,
  terminador `ptr == 0` en **0x8D8900** ⇒ **35 modos**.
  El puntero se publica en `.bss` **0xA4F0A4** en el init: `str r2,[r3]` en **0x5F7566**
  (0x8D87E8 cargado en 0x5F7564).
* Si el modo no está en la lista: cadena `"[MemInfo]DistributeBufInfo() invalid mode !:mode=%ld"`
  (0x8D9F24) y salto al epílogo **sin escribir ninguna entrada** (0x5F7090-0x5F7092).

### 3.2 Tabla fuente por modo (la que se pide en el objetivo 2)

Entrada de **0xC bytes**, tres campos de 32 bits:

| offset | campo | evidencia |
|---|---|---|
| `+0x0` | **size** (bytes del área) | `ldr r3,[r5]` en **0x5F73DA**, justo antes de `str.w r3,[sl,#8]` en **0x5F73E0** |
| `+0x4` | **mt_order** (se compara con `[rammap+8]`) | `ldr r2,[r5,#4]` en 0x5F71D8 vs `ldr r1,[r6,#8]` en 0x5F71DA, `cmp`+`bne` en 0x5F71DC-0x5F71DE |
| `+0x8` | **índice en la tabla destino** (campo clave) | `ldr r3,[r5,#8]` en **0x5F71A6** → `muls r2,r3,#0x18` en **0x5F71E6** |

* Recorrido: `adds r4,#0xC` (**0x5F7124**), `adds r1,r5,#0xC` (**0x5F7448**).
* Terminador: **`[entrada+8] == 0xFFFFFFFF`** (`cmp.w r3,#-1` en 0x5F712C y 0x5F71A8).
* Cuenta de entradas: bucle 0x5F744E-0x5F745C; se compara con las realmente repartidas en
  `"[MemInfo]**DistributeBufInfo --bufTbl item count = %d / defined count = %d"` (0x8D9E64)
  y si no cuadran (y el modo no es 6 ni 0x20) se registra
  `"[MemInfo]**DistributeBufInfo --bufTbl distribute Failed!"` (0x8D9EAF).
* **Excepción única**: sólo en los modos **0x21, 0x22 y 0x24** (seleccionados en 0x5F70D2-0x5F70DE)
  el tamaño de las claves **11, 7 y 0** se **sobreescribe** con `[rammap+0xC]`
  (`ldr r3,[r2,#0xc]` + `str r3,[r4]` en 0x5F7106-0x5F7108, log
  `"[MemInfo]**DistributeBufInfo -- Movie Stream or ES size=0x%08lx"` en 0x8D98E7).
  En esos tres modos la tabla estática **pone 0** y el tamaño llega en ejecución.

### 3.3 Tabla destino (singleton 0xA4F368)

Entrada de **0x18 bytes**:

| offset | campo | escritura |
|---|---|---|
| `+0x00` | **vAdrs** (dirección virtual del área) | `str r4,[r2,r1]` en **0x5F73BE** / `str.w fp,[r2,r1]` en **0x5F73CE** |
| `+0x04` | **pAdrs** (dirección física) | `str.w r8,[sl,#4]` en **0x5F73DC** |
| `+0x08` | **size** (bytes) = `[src+0]` | `str.w r3,[sl,#8]` en **0x5F73E0** |
| `+0x0C` | (no escrito aquí) | — |
| `+0x10` | **offset** de 64 bits | `strd r0,r1,[sl,#0x10]` en **0x5F73C4** / **0x5F73D6** |

Dirección de la entrada: `sl = p_bufInfoTbl + idx·0x18` (**0x5F71E2-0x5F71EA**), con
`p_bufInfoTbl = 0xA4F368` (literal `00a4f368` en 0x5F7D74, usado en 0x5F7CF0 y 0x5F7D26).
Se escribe **sólo** si el `mt_order` de la fuente aparece en el `p_RamMapAreaInfo`; si no aparece,
la entrada **queda con lo que tuviera** (0 en `.bss` recién cargada).

Longitud de la tabla: la clave máxima usada es **0x59 = 89** ⇒ 90 entradas × 0x18 = **0x870**, es
decir 0xA4F368–**0xA4FBD8**, y justo en 0xA4FBD8 empieza otro global (2 referencias literales:
0x5F756E, 0x5F8672). Consistencia extra: `DfsAllocate` lee `[0xA4F368+0x7D0]` como tamaño máximo
(0x5F6AC6, 0x5F6BAC) y **0x7D0 = 83·0x18+8**, o sea el campo *size* del índice **0x53**. Encaja al byte.

### 3.4 Qué offset lee cada rama del reproductor

| sitio | setupMode | lee | área |
|---|---|---|---|
| `ThumbnailRecorder SetMemoryTable` 0x330120 / 0x330124 (nombre en la cadena 0x812B3F) | (type 2/3) | `+0x138` / `+0x140` | **still (13)** |
| `SetUpPlayerInstance` 0x439256 / 0x43925A | 1 y 4 | `+0x108` / `+0x110` | **movie (11)** |
| `SetUpPlayerInstance` 0x4392D2 / 0x4392D6 | 2 | `+0x138` / `+0x140` | **still (13)** |
| `SetUpPlayerInstance` 0x43931A-0x439336 | 3 | `+0x138` si `r8 == 0x40000031`, si no `+0x108` | **still o movie según el valor** |
| `SetUpPlayerInstance` 0x4393CA / 0x4393CE | 5 | `+0x108` / `+0x110` | **movie (11)** |
| `SetUpPlayerInstance` 0x43944E-0x43945C | `setupMode` fuera de 1..5 **o** puntero base = 0 | literal `mov r8,#0; mov sb,r8; SetArea(sb,r8,1)` | **SetArea(0,0,1)** |

`SetArea` recibe `(vAdrs, size, 1)`: `r0 = sb = [base+0x108|0x138]`, `r1 = r8 = [base+0x110|0x140]`.
La constante **0x40000031** (`[0x4393FC]`) decide entre los dos huecos en setupMode 3.

---

## 4. TABLA COMPLETA: modo → tamaño movie (11) / still (13)

Volcado literal de la fuente en la evidencia 02 (todas las entradas de los 35 modos, con `size`,
`mt_order` e índice). `AUSENTE` = no hay entrada con esa clave en la tabla del modo ⇒ la posición
0xA4F368+idx·0x18 **no se escribe** y se queda a 0.

| modo | nombre (0x9DF090, indicativo) | tabla src | n | hueco 11 movie (+0x108) | hueco 13 still (+0x138) |
|---|---|---|---|---|---|
| 0x00 | — | 0x009DE6F0 | 11 | AUSENTE (0) | AUSENTE (0) |
| 0x01 | Movie Pb | 0x009DB0E4 | 22 | 0x01C00000 (28 MiB) | AUSENTE (0) |
| 0x02 | Still Pb | 0x009DBD20 | 24 | 0x01800000 (24 MiB) | 0x00600000 (6 MiB) |
| 0x03 | Movie Rec | 0x009DB444 | 6 | AUSENTE (0) | 0x01800000 (24 MiB) |
| 0x04 | Still Rec | 0x009DA8E0 | 14 | 0x01200000 (18 MiB) | AUSENTE (0) |
| 0x05 | Index Pb | 0x009DBE4C | 14 | 0x01200000 (18 MiB) | AUSENTE (0) |
| 0x06 | I-Pic Rec | 0x009DB75C | 9 | AUSENTE (0) | 0x01600000 (22 MiB) |
| 0x07 | Dual Rec | 0x009DAF7C | 29 | 0x01400000 (20 MiB) | AUSENTE (0) |
| 0x08 | Dmy Dual | 0x009DA994 | 9 | 0x01800000 (24 MiB) | AUSENTE (0) |
| 0x09 | Pb Capture | 0x009DB348 | 20 | 0x00A00000 (10 MiB) | AUSENTE (0) |
| 0x0A | File Copy Dubbing | 0x009DAE44 | 25 | 0x01200000 (18 MiB) | AUSENTE (0) |
| 0x0B | Re-Mux Dubbing | 0x009DC23C | 25 | 0x00900000 (9 MiB) | 0x00400000 (4 MiB) |
| 0x0C | Still Dubbing | 0x009DBA14 | 23 | 0x01C00000 (28 MiB) | AUSENTE (0) |
| 0x0D | Down Convert | 0x009DC11C | 23 | 0x00C00000 (12 MiB) | AUSENTE (0) |
| 0x0E | Thumb Rec | 0x009DB8F4 | 23 | 0x01400000 (20 MiB) | AUSENTE (0) |
| 0x0F | Content Edit | **no existe** | — | **invalid mode** | **invalid mode** |
| 0x10 | Highlight Pb | **no existe** | — | **invalid mode** | **invalid mode** |
| 0x11 | Create | 0x009DB1F8 | 4 | AUSENTE (0) | AUSENTE (0) |
| 0x12 | Multi Rec HDHD | 0x009DB234 | 8 | AUSENTE (0) | 0x01800000 (24 MiB) |
| 0x13 | Multi Rec HDSD | 0x009DC584 | 12 | AUSENTE (0) | 0x01000000 (16 MiB) |
| 0x14 | Smth Slow | 0x009DAAE4 | 19 | 0x01000000 (16 MiB) | AUSENTE (0) |
| 0x15 | Mass Strage | 0x009DC620 | 19 | 0x01000000 (16 MiB) | AUSENTE (0) |
| 0x16 | Idle | 0x009DC710 | 13 | AUSENTE (0) | AUSENTE (0) |
| 0x17 | Create Movie | 0x009DB744 | 1 | AUSENTE (0) | AUSENTE (0) |
| 0x18 | Movie Rec 3D | 0x009DABD4 | 23 | 0x01000000 (16 MiB) | AUSENTE (0) |
| 0x19 | Movie Pb 3D | 0x009DB6D8 | 8 | AUSENTE (0) | AUSENTE (0) |
| 0x1A | Highlight Pb 3D | 0x009DB2A0 | 3 | AUSENTE (0) | AUSENTE (0) |
| 0x1B | OUCranc Rec | 0x009DC374 | 43 | 0x01000000 (16 MiB) | AUSENTE (0) |
| 0x1C | Still Pb RAW | 0x009DB498 | 23 | 0x01C00000 (28 MiB) | AUSENTE (0) |
| 0x1D | Multi Rec DVDV | 0x009DACF4 | 27 | 0x01400000 (20 MiB) | AUSENTE (0) |
| 0x1E | Multi Rec AVCHDMP4 | 0x009DBB34 | 40 | 0x01400000 (20 MiB) | AUSENTE (0) |
| 0x1F | Multi Rec XAVCMP4 | 0x009DAA0C | 17 | 0x03000000 (48 MiB) | AUSENTE (0) |
| 0x20 | Reserve | 0x009DB2D0 | 9 | AUSENTE (0) | 0x00300000 (3 MiB) |
| 0x21 | — | 0x009DB5B8 | 23 | **0x00000000 (presente, 0)** | AUSENTE (0) |
| 0x22 | — | 0x009DB7D4 | 23 | **0x00000000 (presente, 0)** | AUSENTE (0) |
| 0x23 | — | 0x009DA6D0 | 43 | 0x01C00000 (28 MiB) | AUSENTE (0) |
| 0x24 | — | 0x009DBF00 | 44 | **0x00000000 (presente, 0)** | AUSENTE (0) |

Notas de lectura de la tabla:

* **Modos 0x0F y 0x10**: los produce la tabla de tipos —0x0F con `type=13 sub=8` en la **activa**
  (0x9DE898), 0x10 con `type=13 sub=8` en la de systemType 2 (0x9DEDC0)— pero **no tienen tabla de
  buffers** ⇒ `DistributeBufInfo` registra `invalid mode` y **no reparte nada**.
* **0x21/0x22/0x24**: la clave 11 existe con `size = 0` y el tamaño real se toma del
  `RamMapAreaInfo` (§3.2). Si el rammap no trae ese `mt_order`, **se queda 0**.
* Las claves altas (0x52–0x59) son áreas especiales que conviven en el mismo espacio de índices
  0..89 de 0xA4F368: 0x55 = IFO WorkCache y 0x56 = Effect WorkCache (comprobado por las
  comparaciones `cmp r3,#0x55` en 0x5F7212 y `cmp r3,#0x56` en 0x5F72AA), 0x53 = área que
  `DfsAllocate` usa como límite (por `[0xA4F368+0x7D0]`, §3.3) y 0x59 = relleno/alineación que
  aparece repetido tras varias entradas (su valor exacto es **NO_VERIFICADO**).

---

## 5. ¿Existe un modo con movie = 0 y still > 0?

**Sí. Cinco, y cuatro son alcanzables en este firmware.**

| modo | nombre | movie (11) | still (13) | alcanzable con `m_systemType = 1` |
|---|---|---|---|---|
| 0x03 | Movie Rec | 0 (ausente) | 24 MiB | sí — `type=3 sub=8` |
| 0x06 | I-Pic Rec | 0 (ausente) | 22 MiB | sí — `type=1 sub=8` |
| 0x12 | Multi Rec HDHD | 0 (ausente) | 24 MiB | sí — `type=11 sub=8` |
| 0x13 | Multi Rec HDSD | 0 (ausente) | 16 MiB | no (no aparece en 0x9DE898) |
| 0x20 | Reserve | 0 (ausente) | 3 MiB | sí — `type=27 sub=8` |

Caso simétrico (movie presente pero **0**, todavía sin still): **0x21, 0x22, 0x24**, que es donde el
tamaño del movie llega del `RamMapAreaInfo`.

Y el caso opuesto (still = 0 con movie > 0) es el más común: 0x01, 0x04, 0x05, 0x07, 0x08, 0x09,
0x0A, 0x0C, 0x0D, 0x0E, 0x14, 0x15, 0x18, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x23.

**Por qué esto basta para «fotos sí, vídeo no»**: la miniatura de foto usa el hueco 13
(`ThumbnailRecorder SetMemoryTable` 0x330120 lee `+0x138/+0x140`) y el reproductor de vídeo usa el
hueco 11 (`SetUpPlayerInstance` 0x439256 lee `+0x108/+0x110`). Si el modo activo está en una fila
con movie = 0 y still > 0, el reproductor pide `SetArea(vAdrs, 0)` y las miniaturas siguen teniendo
sus 22-24 MiB. **No hace falta ninguna otra causa.**

Matiz importante para no engañarse: en el camino *normal* de reproducción de vídeo de esta cámara
(`m_systemType = 1`, `type=2 sub=1..6`) el modo es **0x01 = Movie Pb** y el movie son **28 MiB**
> 0. Para que el 0 sea de tabla, el modo tiene que ser uno de los cuatro de arriba o 0x21 (sub=7).

---

## 6. Conclusión (una frase)

**La tabla es determinista y el 0 no es un cálculo: es una fila.** Para cada `areaTblMode` (0x9DECAC)
la tabla de 0x8D87E8 elige una lista de 0xC B por entrada y `DistributeBufInfo` (0x5F703C) copia
`src+0` en `0xA4F368+idx·0x18+8`; el hueco 11 es movie y el 13 es still, así que **existen cinco
modos (0x03, 0x06, 0x12, 0x13, 0x20) en los que el área de movie vale 0 y la de still no**, y ese
único hecho explica «fotos sí, vídeo no» sin tocar nada más.

---

## 7. Cómo comprobarlo en cámara (sin flashear)

1. **Modo activo**: leer la palabra de **0x9DECAC** (`areaTblMode`) durante la reproducción de vídeo.
   Se escribe en `str r2,[r3]` de **0x5F7C7C** con la salida de `Type2Mode` 0x5F699C.
   Esperado en vídeo: **0x01**; si sale **0x03 / 0x06 / 0x12 / 0x20**, el 0 es de tabla y este
   informe es la explicación completa. Si sale **0x0F** (o 0x10), el log dirá `invalid mode`.
2. **Área resultante**: leer 4 bytes en **0xA4F478** (size del movie, = 0xA4F368+11·0x18+8) y en
   **0xA4F4A8** (size del still, = 0xA4F368+13·0x18+8). Con modo 0x01: 0x01C00000 / 0. Con modo
   0x02: 0x01800000 / 0x00600000. Con un 0 en 0xA4F478 y ≠0 en 0xA4F4A8, caso cerrado.
3. **Log del propio `libmpr` (nivel verboso)** — estas seis líneas, en este orden, cuentan la historia
   completa (`VA` de la cadena entre paréntesis):
   * `[MemInfo]Type2Mode(): type=%d /subType=%d / ramMapAreaMode=%ld / areaTblMode=%ld` (0x8D90C0)
   * `[MemInfo]StreamAreaAllocate(next) : type=%ld /subType=%ld /m_ramMapAreaMode=%ld /m_bufTbl…` (0x8DA590)
   * `[MemInfo]StreamAreaAllocate(next): complete ret=%ld` (0x8DA720) ← **si `ret=0`, no hay base y
     el `SetArea(0,0,1)` es literal (0x439460)**: es la otra causa posible, distinguible aquí
   * `[MemInfo]DistributeBufInfo() mode !:mode=%ld p_bufInfoTbl=0x%08lX p_RamMapAreaInfo=0x%08lx` (0x8D9854)
   * `[MemInfo]**DistributeBufInfo -- set data vAdrs=0x… pAdrs=0x… size=0x… offset=0x…` (0x8D9DCB)
     ← aquí se ve el `size` de cada hueco al escribirse
   * `[MemInfo]**DistributeBufInfo --bufTbl item count = %d / defined count = %d` (0x8D9E64)
4. **Desambiguar las dos rutas**: si aparece `complete ret=0` → el fallo es de `StreamAreaAllocate`,
   no de la tabla. Si `ret=1` y aun así `size=0` en el hueco que pide el reproductor → es la fila del
   modo (§5).
5. Repetir lo mismo en reproducción de foto (debe dar otro modo, p.ej. 0x02/0x03) para confirmar
   que vídeo y foto eligen modos distintos: ahí está el «fotos sí, vídeo no».

---

## 8. Límites (NO_VERIFICADO)

* **NO_VERIFICADO en cámara qué `areaTblMode` (0x9DECAC) se usa en el fallo del 20-10, ni qué
  `ramMapAreaMode`/`p_RamMapAreaInfo` hay en ese momento.** Todo este informe es estático.
* **NO_VERIFICADO el significado literal de «11 = movie» y «13 = still»**: no hay `enum` en el
  binario. Se deduce de (a) `ThumbnailRecorder SetMemoryTable` 0x330120 usando `+0x138` con
  `MemInfo::MEM_TBL_STILL_REC` (cadena 0x812B84), (b) las ramas de `SetUpPlayerInstance`
  0x439256/0x4392D2, y (c) la cadena `Movie Stream or ES size` (0x8D98E7) asociada a la clave 11.
  Consistente, pero es inferencia de uso.
* **NO_VERIFICADO que la tabla de 0xA4F368 acabe exactamente en 0xA4FBD8**: se deduce de la clave
  máxima (0x59) y de que 0xA4FBD8 es el siguiente global con referencias propias. No hay `memset`
  localizado con el tamaño de la tabla.
* **NO_VERIFICADO el nombre de los modos 0x21-0x24** (la tabla de nombres 0x9DF090 sólo llega a 0x20)
  ni que esa tabla de nombres sea la del mismo `enum`: **no tiene ninguna referencia literal en
  `.text`**.
* **NO_VERIFICADO el `mt_order`**: se sabe que se compara con `[rammap+8]` (0x5F71DA-0x5F71DE), no
  qué enum representa; en consecuencia, **si el `RamMapAreaInfo` no trae ese id, la entrada del
  destino no se escribe** (queda 0) aunque la tabla diga 24 MiB.
* **NO_VERIFICADO el sentido de 0x40000031** ([0x4393FC]) que en setupMode 3 elige entre `+0x138`
  y `+0x108`.
* Mismos límites heredados del informe previo sobre `m_systemType` (`[0x9DEFE0] = 1` en fichero, sin
  origen localizable en libmpr) y sobre el valor de `[0xAD4F68]` (mínimo de `SetArea`, depende de
  EEPROM).

---

## 9. Evidencia

`reports/evidence/film-pb-1-sub-tabla-buffers-20261126/`

| fichero | contenido |
|---|---|
| `01-distributebufinfo-0x5F703C.txt` | desensamblado completo 0x5F703C–0x5F74A6 (447 líneas), incluido el pool de literales con todas las cadenas |
| `02-tabla-por-modo-dump.txt` | los 35 modos: resumen (movie/still) + **volcado crudo** de cada entrada con `size`, `mt_order`, índice y terminador |
| `03-secciones-elf-y-regla-va-offset.txt` | `readelf -h/-S/-l` + la regla VA→offset aplicada (y por qué `.bss` no se puede volcar) |
| `04-globals-bss-y-referencias.txt` | todas las referencias literales reales a 0xA4F200–0xA50000 y el mapa de índices (11→0xA4F470, 13→0xA4F4A0, 0x53→0xA4FB30, 0x59→0xA4FBC0, fin 0xA4FBD8) |
| `05-setarea-offsets-108-138.txt` | los sitios de `SetArea` con `+0x138/+0x140` y `+0x108/+0x110`, el `tbb` de setupMode y el `SetArea(0,0,1)` literal |
| `06-streamareaalloc-retorno-a4f368.txt` | la cadena `GetMemoryInformation`→`StreamAreaAllocate`→**retorno 0xA4F368** (0x5F7D26) y los 4 llamadores de `DistributeBufInfo` |
| `07-type2mode-y-tablas-por-sistema.txt` | `Type2Mode` 0x5F699C y las tres tablas `{type, subType, modeId, ramMapAreaMode}` (0x9DE7C8 / **0x9DE898 activa** / 0x9DEDC0) |
| `08-nombres-de-modo-0x9DF090.txt` | tabla de nombres de modo (id 0x00–0x20) con su aviso de que no tiene xref |
| `09-formato-tabla-instrucciones.txt` | las instrucciones clave del formato (selección, recorrido 0xC, clave, tamaño, escritura, contador) + volcado de 0x9DBD20 y 0x9DB0E4 |
| `dump.py`, `dis2.py` | scripts usados (lectura por VA y desensamblado tolerante a pools de literales) |
