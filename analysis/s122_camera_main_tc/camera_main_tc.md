# S122 — el módulo `[CAMERA_MAIN_TC]` (127 trazas): el consumidor de `[APL]` y el *time compression* de la cámara

**Firmware:** A6000 fw3.21 (`analysis/rea-independent/input/av-cam.bin`, 11 427 236 B)
**Base virtual:** `vaddr = 0x43541000 + file_offset` (verificada en cada cita)
**Método:** solo análisis de bytes (Capstone 5.0.7 + escáner PIC propio). Sin REA/Ghidra, sin
ejecutar firmware, sin cámara, sin red. Escáner bajo la **regla estricta** canónica
(`analysis/s106_imaging_cap/scan_pic_refs_strict.py`): un `add rX,pc` se empareja con el
`ldr rX,[pc,#imm]` **más cercano por detrás del mismo registro** dentro de una ventana de 4 KB, y
solo se aceptan destinos que caigan en el inicio de una cadena, en la etiqueta o en el texto
interior de una de las 127 trazas.

---

## 1. Resumen

* El módulo son **127 cadenas** con la etiqueta `[CAMERA_MAIN_TC]: `, **127 textos distintos**,
  en **6 tramos no contiguos** entre `0x43ca7fd7` y `0x43ccb350`.
* **123 están referenciadas** por código; **4 están muertas** (ni PIC, ni puntero absoluto, ni
  `movw/movt`, y tampoco aparecen en A7S ni en A6300).
* Hay **256 sitios de referencia PIC** repartidos en **41 funciones**; **122 de las 123 trazas
  vivas llevan más de un puntero** (2 en 116, 3 en idx 0 y 4 en los cinco pares) —uno a la cadena
  completa, otro al texto interior— y **cada traza se emite dos veces** (salvo idx 105, que solo
  tiene publicador): una por el publicador OSAL y otra por el `printf` local `0x43902718`.
* Los **emisores de la primera emisión son 17 funciones** con un prólogo **idéntico byte a byte**
  (`0xB408` = `push {r3}`, primer `bl` en `p+0x1e` → `0x435612d0` = `osal_try_valloc_msg`).
* El **despachador del módulo es `ApolloSA_Main` `0x438730b0`** (14 sitios de traza), con un
  `tbb` de **chequeo de rango por modo** en `0x4387333e` y un **`tbh` de 9 casos** en
  `0x4387348e` que reparte el trabajo entre calibración `0x437d48e8`, `JudgeBdroRslt`
  `0x438e8204`, el *tracking* `0x438740c8`, el *motion vector* `0x43874270` y el núcleo
  `0x43872c94`.
* Tiene **solo 2 llamadores**: la **panorámica** (S105) en `0x437f1324` y `0x438bdeac`
  (zona `[IMAGING_CAP]`, con las trazas `Stage_Apollo.cpp` / `Apollo.cpp`).
* Es el **único cliente de `[APL]`** (S119): las 6 funciones `0x438765c8`, `0x438765fc`,
  `0x4387668c`, `0x43876a80`, `0x43876ab4` y `0x43876b74` se llaman **desde dentro** de
  `ApolloSA_Main`.
* **Diferencial A7S fw3.20 / A6300 fw2.01:** **0** apariciones de la etiqueta; **126/127** textos
  interiores presentes literalmente (falta el idx 105, que está vacío) y **119 textos con
  referencias PIC / 123 sitios** frente a 123/256 en la A6000. Idéntico en las dos versiones.
* **No toca la línea del obturador**: 0 apariciones de `shut`, `silent`, `electro`, `mech`,
  `sensor`, `exposure`, `drive`, `readout`, `jpeg`, `movie`, `stc`, `bracket`, `sweep`, `interval`
  en las 127 trazas. **S51 A/B/C = NO se mantiene.**

---

## 2. Qué es `[CAMERA_MAIN_TC]`

### 2.1 El nombre

`TC` **no se expande en ningún byte del firmware**. Lo único que el binario dice del módulo es su
etiqueta de traza y los nombres de sus funciones: `ApolloSA_Main`, `ApolloSA_Fin`,
`ApolloSA_Cancel`, `SA Preload/Acquire/Start/release1/release2`, `ChkExeSeq`, `ChkPrm`,
`MakeLmv`, `LmvlistNum`, `JudgeBrkSmv/Gyro/Gmv`, `JudgeRslt`, `VectTypeAtCoar/Fine`,
`GmvCoarScl/GmvFineScl/GmvStitScl`, `GyroStitScl`, `FinData`, `OutData`, `SMART ZOOM MODE`,
`ARC_*`/`RC_*`, `JudgeBdroRslt`. **No se desarrolla la sigla**: cualquier expansión sería inventada.

Los nombres `ApolloSA_*` son los mismos que S119 encontró del lado de `[APL]`: es el mismo
subsistema visto desde sus dos mitades (el cliente y el coprocesador). El binario nombra además
los ficheros fuente `Apollo.cpp` (`0x43cc6e15`) y `Stage_Apollo.cpp` (`0x43cc6e0f`), ambos en la
zona de cadenas de `[IMAGING_CAP]`.

### 2.2 Dónde vive

Las 127 cadenas **no son un bloque contiguo**: son 6 tramos separados por las cadenas de otros
módulos (`[CAMERA_MAIN_YC]` de S110, `[CAMERA_MAIN_SYNC]` de S112, `[CAM_IMAGER]` de S115…).

| # | bloque (contenido) | idx | n | rango | sitios | refs | funciones |
|---|---|---|---|---|---|---|---|
| 1 | GYRO/CALIB | 0–31 | 32 | `0x43ca7fd7`–`0x43ca84c3` | 65 | 32 | 7 |
| 2 | DIST | 32–44 | 13 | `0x43ca8547`–`0x43ca884b` | 26 | 13 | 3 |
| 3 | APL/ApolloSA | 45–91 | 47 | `0x43cb6a67`–`0x43cb72a9` | 88 | 43 | 21 |
| 4 | SMART ZOOM | 92–107 | 16 | `0x43cb72d5`–`0x43cb74fe` | 31 | 16 | 1 |
| 5 | DDT | 108–125 | 18 | `0x43cb7524`–`0x43cb796c` | 44 | 18 | 8 |
| 6 | JudgeBdroRslt | 126 | 1 | `0x43ccb350` | 2 | 1 | 1 |
| | **total** | | **127** | | **256** | **123** | **41** |

La partición es **por contenido** (suma exacta, ninguna función en dos bloques) y está fijada en
`scan_tc.py` (`subblocks_content`). Se conserva además una **capa léxica secundaria por prefijo**,
que no coincide con la de contenido: `TC (varios)` 57, `TC:APL:Err` 25, `TC:DDT:Err` 18,
`SMART ZOOM` 14, `TC:DIST:Err` 13. La diferencia está en el bloque 4: por prefijo solo entran 14
cadenas (idx 0, 66, 68 y 92–104 sin 93/95/105/106/107), mientras que por contenido son 16.

---

## 3. Anatomía de una traza: doble emisión con dos punteros

La pauta general es **dos registros** por traza, con dos punteros distintos a la misma cadena
(idx 105 es la excepción: solo publicador, ver §3.2):

```
0x437d1b78  ldr r3, [pc, #...]   ; pool -> 0x43ca7ffb (base de la cadena)
0x437d1b7a  add r3, pc           ; r3 -> "[CAMERA_MAIN_TC]: TC:APL:Err: LmtGyroVect Denom=0 %d %d %d %d"
0x437d1b82  bl  0x437d19c4       ; publicador OSAL (valloc + snd_msg)
0x437d1b86  add r0, pc           ; r0 -> "TC:APL:Err: LmtGyroVect Denom=0 %d %d %d %d" (texto interior)
0x437d1b8a  bl  0x43902718       ; printf local
```

Consecuencia: el destino de **cada uno de los 127 `inner`** vive exactamente **18 bytes** después
del inicio de su cadena (`strlen("[CAMERA_MAIN_TC]: ")` = 18), verificado en **127/127**
referencias (`inner == vaddr + 18`, `string == vaddr_string + 0`).

### 3.1 Recuento de punteros

| tipo de puntero | n | qué apunta | destino |
|---|---|---|---|
| `string` | 127 | inicio de la cadena (a veces 3 B antes, ver §3.2) | publicador |
| `prefix` | 2 | la etiqueta `[CAMERA_MAIN_TC]: ` | publicador |
| `inner` | 127 | el texto interior (+18) | `printf` `0x43902718` |
| **total** | **256** | | |

Reparto por traza: **115** con `(1 string, 0 prefix, 1 inner)`, **5** con `(2,0,2)` (idx 46, 108,
109, 110, 118), **4** muertas con `(0,0,0)`, idx 0 con `(1,1,1)` (tres punteros), idx 32 con
`(0,1,1)` (dos: etiqueta + interior) e idx 105 con `(1,0,0)`. La suma cuadra:
115·2 + 5·4 + 3 + 2 + 1 = **256**.

### 3.2 Los tres casos especiales

* **idx 0** (`0x43ca7fd7`, `GyroStitScl %d %d`) tiene **tres** punteros y una particularidad: la
  cadena está precedida por los bytes imprimibles `<20` en `0x43ca7fd4`, que **no forman parte del
  texto**. El sitio `0x437d07be` carga ese `0x43ca7fd4` y lo usa como **tabla de bytes**
  (`ldrb r1,[r3,r2]` en `0x437d07c0`), **no** como formato: es el único `string` del módulo que no
  emite. El prefijo `0x43ca7fd7` (`add` en `0x437d1ade`) y el interior `0x43ca7fe9`
  (`add` en `0x437d1af0`) sí emiten.
* **idx 32** (`0x43ca8547`, `TC:DIST:Err:SetDistMode1ForSync aspect, %d`) está precedido por
  ` &08@` en `0x43ca8542`; el `ldr` de `0x437d713c` carga esa base, pero el **sitio PIC** es el
  `add` de `0x437d71a2`, que deja el puntero en `0x43ca8547` (prefijo), más un interior en
  `0x43ca8559`. Por eso idx 32 tiene **dos** sitios `(0,1,1)` y **no** hay sitio `string`.
* **idx 105** (`0x43cb74cd`) tiene el texto interior **vacío**: en `vaddr+18` (`0x43cb74df`) hay
  un `0x0a` (salto de línea), no texto imprimible; el `": "` visible está en `vaddr+16`
  (`0x43cb74dd`) y forma parte de la propia etiqueta. Solo se referencia la cadena completa, y
  por eso su traza tiene 1 sitio en lugar de 2.

### 3.3 Cadenas muertas

| vaddr | texto |
|---|---|
| `0x43cb6c6f` | `[CAMERA_MAIN_TC]: ApolloSA_Cancel(start) %d` |
| `0x43cb6c9b` | `[CAMERA_MAIN_TC]: ApolloSA_Cancel(end) %d` |
| `0x43cb717a` | `[CAMERA_MAIN_TC]: TC:APL:Err: Cancel SeqNG` |
| `0x43cb71a5` | `[CAMERA_MAIN_TC]: TC:APL:Err: SA Cancel %d` |

Comprobado (`scan_dead_check.py`, `dead_check.json`): **0** punteros absolutos en el pool, **0**
`addw rX,pc`, **0** pares `movw/movt` hacia esas direcciones; y **0** apariciones de esos textos en
A7S fw3.20 y A6300 fw2.01. Coherente: las cuatro son del camino de **cancelación**, y la función
`ApolloSA_Cancel` **no existe como tal** en el binario (ningún prólogo ni llamador con ese nombre);
la cancelación se hace por las funciones `SA release*`/`SA Cancel` que sí emiten.

---

## 4. Los emisores

### 4.1 Los 17 publicadores OSAL

Los 256 sitios se reparten entre **17 funciones publicadoras** y el `printf` `0x43902718`
(ya documentado en S119). Los 17 tienen el **mismo prólogo, byte a byte**:

`0xB408` (`push {r3}`) y primer `bl` en `p+0x1e` → `0x435612d0` = **`osal_try_valloc_msg`**
(S109/S20/S41), seguido en el cuerpo de `blx 0x439c5a04` (`memset`), `bl 0x43561244`,
`bl 0x439c5004` (formateo tipo `vsnprintf`) y, en la ruta de error, `bl 0x435612ec`
(`osal_free_msg`).

| publicador | sitios | publicador | sitios |
|---|---|---|---|
| `0x437d4828` | 26 | `0x43872894` | 3 |
| `0x43878570` | 23 | `0x43874700` | 3 |
| `0x43876c08` | 15 | `0x437d19c4` | 2 |
| `0x4387651c` | 14 | `0x43875188` | 2 |
| `0x437d6cf4` | 13 | `0x437d5090` | 1 |
| `0x43873004` | 9 | `0x438758a4` | 1 |
| `0x438737a4` | 4 | `0x438e8158` | 1 |
| `0x4387401c` | 4 | | |
| `0x43874ba4` | 4 | **total** | **128** |
| `0x437d373c` | 3 | | |

`0x43873004` es el publicador propio de `ApolloSA_Main`/`ApolloSA_Fin`: se llama desde **9 sitios**,
7 en `0x438730b0` (`0x438731ba`, `0x43873232`, `0x43873286`, `0x438732f2`, `0x438733b4`,
`0x43873580`, `0x438735c2`) y 2 en `0x43873646` (`0x43873668`, `0x43873690`).

El prólogo `push {r3}` **no se detecta como inicio de función** con la regla de prólogos del repo
(`h & 0xFF00 == 0xB500` con bit 8); por eso `0x43875878` se atribuye a `0x43875604` y los 17
publicadores se listan por su dirección real. Análogamente, **dos entradas reales empiezan 2 B
antes del `push`**: `0x43872c94` (`cmp r0,#2`; prólogo en `0x43872c96`) y `0x43873644`
(`ldr r3,[pc,#0x58]`; prólogo en `0x43873646`). En `tc_map.json` se conservan las claves de
prólogo (`0x43872c96`, `0x43873646`) y aquí queda dicha la salvedad.

### 4.2 Lectura estructural de los 256 sitios

La clasificación **exacta** no depende de heurísticas, sino del **tipo de puntero**:

| lectura estructural | n | sitios |
|---|---|---|
| sitios que **publican** (OSAL) | **128** | 126 `string` + 2 `prefix` |
| sitios que **imprimen** (`printf`) | **127** | los 127 `inner` |
| sitio que **no emite** (tabla de bytes) | **1** | idx 0, `0x437d07be` |
| **total** | **256** | |

Esto se apoya en que **ningún `inner` apunta a un publicador** (siempre `+18`, el texto sin
etiqueta) y en que los 128 sitios de cadena/etiqueta van a uno de los 17 publicadores.

### 4.3 La heurística "primera llamada directa" y sus anomalías

Para no fiarse solo del tipo de puntero se clasificó también cada sitio por la **primera llamada
directa** (`bl`) que le sigue en una ventana de 40 instrucciones (`scan_emitters.py`):

| clase heurística | n | desglose |
|---|---|---|
| `publisher` | 128 | 125 `string` + 2 `prefix` + **1 `inner`** |
| `printf` | 115 | 114 `inner` + **1 `string`** |
| `other` | 9 | 8 `inner` + 1 `string` |
| `none` | 4 | 4 `inner` (cola `b.w`/`bx lr`) |

Las dos discrepancias están identificadas y explicadas:

* **`0x43876fcc` (idx 95, `string`)**: el `add sb,pc` carga en el registro **`sb`**, no en `r0`.
  Su `ldr` es el más cercano de `sb` y su destino se consume en el publicador `0x43876ffe`
  (`mov r3,sb` → `bl 0x43876c08`): **sí publica** (de ahí 126 `string` publicadores). Su interior
  `0x43876fce` (`add sl,pc`) se consume en `0x43877004` → `bl 0x43902718`.
* **`0x43879274` (idx 121, `inner`)**: hace `b 0x43879296` → `bl 0x43902718`: **imprime**, pero la
  llamada no es la primera de la ventana. (Su pareja `string`, `0x4387926a`, va a
  `bl 0x43878570`.)

Además, **los 13 `inner` que la heurística no marca como `printf`** (idx 0, 43, 45, 46, 60, 68, 72,
73, 74, 86, 87, 121 y 124) **alcanzan `0x43902718` dentro de la misma función** —por cola `b.w` o
tras llamadas intermedias, con un máximo de **251 instrucciones**—, y un barrido que trata `bx lr`
como tope da **0** casos sin alcanzarlo. Ejemplo de cola: `0x437d1af0` termina en
`add r0,pc; add sp,#0xc; vpop {d8}; pop.w {r4,r5,lr}; b.w 0x43902718`.

Por eso la cifra que se usa en todo el informe es la **estructural (128/127/1)** y la heurística se
conserva solo como capa de contraste.

---

## 5. El despachador: `ApolloSA_Main` `0x438730b0`

```
0x438730b0  2de9f04f   push.w {r4,r5,r6,r7,r8,sb,sl,fp,lr}
0x438730b4  9fb0       sub    sp,#0x7c
0x438730be  fff7e3fb   bl     0x43872888          ; contexto/registro del módulo
0x438730c6  5ffa85fa   uxtb.w sl,r5            ; sl = modo & 0xFF
0x43873338  082d       cmp    r5,#8
0x4387333a  00f23281   bhi.w 0x438735a2          ; modo > 8 -> error
0x4387333e  dfe805f0   tbb    [pc,r5]            ; tabla 0x43873342
0x4387348e  dfe815f0   tbh    [pc,r5,lsl #1]     ; tabla 0x43873492
0x4387359e  bde8f08f   pop.w  {…,pc}
```

### 5.1 `tbb` de `0x4387333e`: chequeo de rango, no despacho

Tabla `0x43873342`: `05 05 09 14 14 0d 0f 0d 0f`; destino = `PC (0x43873342) + 2·byte`:
0/1→`0x4387334c`, 2→`0x43873354`, 3/4→`0x4387336a`, 5→`0x4387335c`, 6→`0x43873360`,
7→`0x4387335c`, 8→`0x43873360`. Cada rama hace un `cmp` y salta al `bhi.w` común de `0x43873366`
**conservando las flags**, así que el `tbb` no elige operación: valida el parámetro
`[r4,#0x2c]` contra un rango distinto por modo —(x−1)≤0xA para 0/1, (x−1)≤1 para 2, x==0x95 para
5/7, (x−1)≤0x94 para 6/8— y, si no cuadra, salta a `0x438735a8` (`mov.w r8,#2` + traza) frente a
`0x438735a2` (`mov.w r8,#4`) para el modo fuera de tabla.

### 5.2 `tbh` de `0x4387348e`: los 9 casos

Tabla `0x43873492`: `09 00 09 00 0e 00 a3 00 25 00 15 00 1d 00 15 00 1d 00`;
destino = `PC (0x43873492) + 2·halfword`:

| modo | destino | qué hace |
|---|---|---|
| 0, 1 | `0x438734a4` | `ldr.w r0,[fp,#4]` + `bl 0x43875878` |
| 2 | `0x438734ae` | `mov r0,r6 / r1,r4 / r2,fp / r3,r7` + `bl 0x438e8204` (`JudgeBdroRslt`) |
| 3 | `0x438735d8` | punto de unión: `bl 0x43872c94` en `0x438735e2` |
| 4 | `0x438734dc` | `mov r0,fp / r1,r4` + `bl 0x437d48e8` (calibración, 52 sitios) |
| 5, 7 | `0x438734bc` | `bl 0x438740c8` (`VectTypeAtCoar`) |
| 6, 8 | `0x438734cc` | `bl 0x43874270` (`FinData`/`OutData`/`VectTypeAtFine`) |

Las cinco ramas terminan en `b 0x438735d8`; allí (`mov r0,r5; mov r1,r6; mov r2,r4;
ldr r3,[sp,#0x6c]; str r7,[sp]`) se hace `bl 0x43872c94` en **`0x438735e2`** (el núcleo),
`mov sb,r0` y `b 0x438734e6`, donde sigue el camino común (`bl 0x43876b74` = `SA Vect Close`, la
publicación de `0x43873004` en `0x43873580`, el segundo `printf` en `0x43873596` y el
`pop.w {…,pc}`). Es decir: **`0x438735d8` es a la vez destino del caso 3 y punto de unión**
de las cinco ramas restantes.

### 5.3 Qué imprime `ApolloSA_Main`

14 sitios = 7 trazas × 2:

* `ApolloSA_Main(start) %d %d %d %d %d %d %d %d 0x%X 0x%X` `0x43cb6ac7`
* `APL_MEM_INFO 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X` `0x43cb6b10` (8 punteros)
* `APL_IMG_INFO %d %d %d %d %d %d %d` `0x43cb6b57`
* `APL_PANORAMA_INFO %d %d %d %d 0x%X 0x%X %d 0x%X 0x%X 0x%X 0x%X` `0x43cb6b8b`
* `TC:APL Err: ChkExeSeq %d %d %d` `0x43cb6bdc`
* `ApolloSA_Main(end) %d %d %d %d %d` `0x43cb6c0d`
* `TC:APL:Err: ChkPrm %d %d %d` `0x43cb6c41`

Los nombres `APL_MEM_INFO` / `APL_IMG_INFO` / `APL_PANORAMA_INFO` son la prueba textual de que este
módulo **empaqueta las tres cosas para la APL**: el mapa de memoria, la imagen y el estado de
panorámica. El doble camino se ve en el arranque: `0x438731b4`/`0x438731b8` → publicador
`0x438731ba: bl 0x43873004`, y `0x438731d0` (interior `0x43cb6ad9`) → `0x438731f4:
bl 0x43902718`.

### 5.4 `ApolloSA_Fin` y el núcleo

* **`ApolloSA_Fin` `0x43873644`** (4 sitios = 2 trazas): `ldr r3,[pc,#0x58]` en `0x43873644`,
  `push {r0,r1,r2,r4,r5,lr}` en `0x43873646`, `ldr r5,[r3,r2]` en `0x4387364e` (contexto global),
  `ldrb r3,[r5,#9]` / `tst.w r3,#1` en `0x43873650`/`0x43873652` y publicación en `0x43873668`.
  Emite `ApolloSA_Fin(start) %d` `0x43cb6cc5` y `ApolloSA_Fin(end)` `0x43cb6cee`.
* **`0x43872c94`** (4 sitios): `cmp r0,#2` en `0x43872c94` y `push.w {r4,r5,r6,r7,r8,lr}` en
  `0x43872c96`; filtra modos (0–2, 6 y 8; el resto va a `0x43872fdc`) y emite
  `TC:APL:Err: MakerNote:GetTagPt %d` `0x43cb6a93`, que implica que el núcleo **rellena el
  MakerNote EXIF** de la imagen.

---

## 6. Llamadores y relaciones

### 6.1 Solo dos llamadores de `ApolloSA_Main`

| llamador | contexto | evidencia |
|---|---|---|
| `0x437f1324` | **panorámica** (`ExecutePanoramaTC1ST`, S105) | `bl 0x438730b0` tras `cmp r7,#2` |
| `0x438bdeac` | zona `[IMAGING_CAP]`, función `0x438bddf0` | 3 llamadores: `0x438be0de`, `0x438be302`, `0x43b1d74e` |

La función `0x438bddf0` (prólogo `70b5`) referencia las trazas
`[IMAGING_CAP]: ApolloNrBase err:0x%x ` `0x43cc6db8`, `Stage_Apollo.cpp` `0x43cc6e0f` y
`Apollo.cpp` `0x43cc6e15`: es el **puente entre el gestor de captura y el módulo TC**.

### 6.2 La cadena de la panorámica (S105)

```
0x437f1ac4  ExecutePanoramaTC1ST
   -> 0x437f10d4
        0x437f12f6  cmp r7,#2
        0x437f1314  bl 0x43873644   ; ApolloSA_Fin   (si r7 == 2)
        0x437f1324  bl 0x438730b0   ; ApolloSA_Main  (si r7 != 2)
        0x437f1368  bl 0x43902718   ; error: imprime y sigue
```

El error de la panorámica es la cadena `0x43cacf9c`
(`[IMAGING_CAP]: ApolloSA_Main: err[0x%02x]`): sitios `ldr`/`add` en `0x437f1352`/`0x437f135a`
→ `0x43cacf9c` e interior `0x437f1362`/`0x437f1366` → `0x43cacfab`. **Rectificación**: S105 citaba
`0x43cacf9b`, que es un byte NUL; el inicio real de la cadena es `0x43cacf9c`.

Con esto, el barrido de S105 queda enlazado por código: el **barrido/panorámica** es el único
consumidor de primer nivel del módulo TC que se ha podido verificar, y el módulo TC es el que
decide entre `Fin` y `Main` según `r7 == 2`.

### 6.3 El enlace con `[APL]` (S119)

Las 6 funciones cliente de `[APL]` se llaman **solo desde dentro de `0x438730b0`**, verificado por
destino de `bl` y por unicidad de llamador:

| función `[APL]` | sitio de llamada | traza del cliente |
|---|---|---|
| `0x438765c8` | `0x43873378` (modo 5/7) | `TC:APL:Err: SA Preload %d` `0x43cb700e` |
| `0x438765fc` | `0x438733e6` | `TC:APL:Err: SA Acquire %d` `0x43cb703a` |
| `0x4387668c` | `0x43873418` | `SA Start %d %d` `0x43cb7092` (+ `SA Prm Close1`, `SA release1`, `SA Rslt`, `SA ChkRslt`) |
| `0x43876a80` | `0x4387352c` | `TC:APL:Err: SA release2 %d` `0x43cb714d` |
| `0x43876ab4` | `0x4387343a` | `SA Prm Open2`, `SA Rslt Open`, `SA Vect Open` |
| `0x43876b74` | `0x438734e8` | `SA Prm Close2`, `SA Rslt Close`, `SA Vect Close` |

Así se cierra el circuito que S119 dejó abierto: **TC → APL** es la única arista de entrada a la
capa APL, y la APL es el coprocesador de imagen (HW + SA) de este módulo.

### 6.4 Las otras funciones

* **`0x437d48e8` (calibración)**: **52 sitios / 26 etiquetas** (`zoom_pos_id`, `err_flg`,
  `init_valid_num`, `tar_remove_num`, `sad_remove_num`, `total_loop_count`, `final_valid_num`,
  `final_max_err`, `final_ave_err`, `param_d/e/f/j/k/l`, `square_a,b,c,d`, `square a*b,c*d`,
  `center_x/y`, `calibration_x/y/r/z`, `reliablity_lvl`, `main_temp`, `sub_temp`). Único llamador:
  `0x438734e0`, el **caso 4** del `tbh`. Es el volcado de la calibración del **estabilizador**
  (centro, radio, fiabilidad, temperaturas de los dos sensores) junto al `GyroStitScl` de idx 0.
* **`JudgeBdroRslt` `0x438e8204`**: caso **2** del `tbh` (llamada en `0x438734b6`). Emite
  `JudgeBdroRslt %d %d %d %d %d %d %d %d %d %d` `0x43ccb350` (10 enteros) en `0x438e84f8` y el
  interior `0x43ccb362` en `0x438e850c` (publicador `0x438e8158`).
* **`0x43876ea4` (SMART ZOOM, 31 sitios)**: único llamador `0x4354af32` (función `0x4354a678`),
  fuera de la zona TC. Emite el bloque `SMART ZOOM MODE = %x`, `ARC_ValidSize`, `RC_ValidSize`,
  `ARC_UnitPix`, `ClipRatio`, `StblzRatio`, `TargetSizeRatio`, `TargetOffsetRatio`, `ARC.Size`,
  `ARC.Offset`, `RC.Size`, `RC.Offset`, `=== X ===`, `=== Y ===`.
* **DDT (18 sitios, 8 funciones)**: `0x43878620` (4 sitios, `push {r0..r6,lr}`, a su vez emisor
  OSAL con `bl 0x435612d0` en `0x4387863a`, 4 llamadores), `0x438786c4` (18 sitios), `0x43879050`
  (4), `0x43879104` (4, solo desde `0x438120a4`), `0x43879180` (4, solo desde `0x438120aa`),
  `0x43879204`, `0x438792dc` y `0x4387938e` (sin llamadores `bl`/`blx` directos). Contenido:
  `Osal Valloc/Snd/Rsv Msg`, `Not Reg L Img addr`, `Req SA Stt1/2`, `Write MS`, `Snd Dst Addr`,
  `SA Acq`, `SA Stt … Rls`, `Snd SA Rslt`, `Mem not open/AllocNew/Size/Close/Free`, `Req Init SA`.
* **DIST (13 sitios, 3 funciones)**: `0x437d713c` (10 sitios, `SetDistMode1ForSync`),
  `0x437d7478` (12, `SetDistModeForCapture`/`SetModeForCapture`) y `0x437d765c` (4,
  `WriteRawAppliTagValue1/2`). Los campos que valida son `aspect`, `imager_type`, `crop_type`,
  `dual_cam_mode`, `dist_corr_sw`, `on_still`: el bloque apunta a **corrección de distorsión**
  (el firmware no expande `DIST`, pero los nombres de campo son literales).

---

## 7. Qué dice y qué no dice el módulo

**Vocabulario presente** en las 127 trazas: `ApolloSA` 6, `SA ` 22, `DDT` 18, `TC:` 58, `Dist` 9,
`Gmv` 4, `Gyro` 3, `Lmv` 2, `Raw` 2, `dist` 2, `PANORAMA` 1, `Exif` 1, `SMART ZOOM` 1, `zoom` 1,
`still` 1, `Vect` 5, `Judge` 5, `Stit` 2.

**Vocabulario ausente (0 apariciones)**: `shut`, `silent`, `electro`, `mech`, `sensor`,
`exposure`, `drive`, `readout`, `jpeg`, `movie`, `stc`, `bracket`, `sweep`, `interval`.

Conclusión para la línea del obturador: el módulo es el **pipeline de estabilización /
*time compression* / panorámica** (gyro, vectores, *stitch*, smart zoom, EXIF, SA), no un módulo de
exposición ni de mecanismo. **Ninguna de las 127 trazas distingue obturador mecánico de
electrónico**; el módulo no aporta ningún indicio nuevo a favor o en contra del obturador
electrónico. **S51 A/B/C = NO se mantiene.**

Nota de nomenclatura: la etiqueta `SMART ZOOM/STC` que aparecía en un borrador **no tiene base
textual** (ninguna cadena contiene `STC`); la etiqueta correcta es **`SMART ZOOM`** y así se fijó
en `tc_map.json`.

---

## 8. Diferencial A7S fw3.20 y A6300 fw2.01

| métrica | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| apariciones de `[CAMERA_MAIN_TC]` | 127 | **0** | **0** |
| textos interiores localizados literalmente (de 127) | **126** | **126** | **126** |
| textos con referencias PIC | **123** | **119** | **119** |
| sitios PIC | 256 | **123** | **123** |

El único texto interior **no localizable** en A7S/A6300 es el del **idx 105**, que está vacío (no
hay nada que buscar). Las dos versiones antiguas tienen **casi una referencia por traza**: 115 con
1 sitio, 8 con 0 y 4 con 2. Las **cuatro con 2 sitios** son idx 46, 109, 110 y 118, en estas
direcciones:

| idx | A7S | A6300 |
|---|---|---|
| 46 | `0x4386f142`, `0x4386f1ee` | `0x43928c2a`, `0x43928cd6` |
| 109 | `0x4380d1b8`, `0x4380daea` | `0x4386e688`, `0x4386efba` |
| 110 | `0x4380d218`, `0x4380d3f4` | `0x4386e6e8`, `0x4386e8c4` |
| 118 | `0x4380db32`, `0x4380db8c` | `0x4386f002`, `0x4386f05c` |

**Tres trazas pierden sus sitios** (idéntico en A7S y A6300):

| idx | texto | A6000 (sitios de publicación) | A7S/A6300 |
|---|---|---|---|
| 2 | `calib_r_ave     ` `0x43ca8039` | 1 | **0** |
| 32 | `TC:DIST:Err:SetDistMode1ForSync aspect, %d` `0x43ca8547` | 1 | **0** |
| 108 | `TC:DDT:Err: Osal Valloc Msg %d` `0x43cb7524` | 2 | **0** |

La columna A6000 cuenta sitios de **publicación** (`string`/`prefix`), que es lo comparable con la
referencia al literal interior en las otras versiones; el total de punteros de esas tres trazas en
la A6000 es **2/2/4**, porque cada emisión lleva además su `inner` (§3.1).

Lectura: la fw3.21 **instrumenta** el módulo con una emisión doble (publicador + `printf`) y añade
tres trazas nuevas; el **código de fondo** (calibración, DIST, DDT, ApolloSA, SMART ZOOM) existe en
las tres versiones. La etiqueta `[CAMERA_MAIN_TC]` es **exclusiva de la fw3.21 de la A6000**.

---

## 9. NO VERIFICADO

1. Por qué `idx 2`, `idx 32` e `idx 108` **pierden sus sitios** en A7S/A6300 (¿se eliminó la
   emisión, se movió a otra función o cambió el texto?). No se ha decompilado el código equivalente.
2. **Llamada por puntero** a `0x438786c4` y a `0x43879204`/`0x438792dc`/`0x4387938e`: no tienen
   llamadores `bl`/`blx`; puede haber una llamada indirecta a través de una tabla. La búsqueda de
   punteros absolutos no está cerrada para estas cuatro.
3. Significado de **`TC`**, **`DDT`**, **`DIST`**, **`STC`**, **`ARC`**, **`RC`**, **`Gmv`**,
   **`Lmv`**: el firmware **no expande ninguna** de estas siglas. Para `DIST` hay solo la
   inferencia por los nombres de campo (`dist_corr_sw`, `SetDistMode`), no una expansión textual.
4. La **estructura de los 17 publicadores en A7S/A6300**: el diferencial se ha hecho por texto y
   referencia PIC, no por comparación de prólogos ni del cuerpo de los publicadores.
5. La etiqueta `[CAMERA_MAIN_TC]` en **A7S fw3.21**: solo se han comparado A7S fw3.20 y A6300
   fw2.01; no hay una A7S fw3.21 en el repo.
6. El **pipeline interno** de los subsistemas de calibración, DIST, DDT y SMART ZOOM más allá de
   sus trazas (a qué SA/HW llaman, qué buffers manejan) no se ha reconstruido: este hito cierra el
   **vocabulario y la topología de emisión**, no la semántica completa de cada bloque.
7. El **significado de `r7 == 2`** en la cadena de la panorámica (`0x437f12f6`): se sabe que
   selecciona `ApolloSA_Fin` frente a `ApolloSA_Main`, no qué estado representa.
8. Los **campos** que se imprimen (`APL_MEM_INFO`, `APL_IMG_INFO`, `APL_PANORAMA_INFO`,
   `JudgeBdroRslt` de 10 enteros): se conoce su número y su orden de emisión, no su significado
   ni el offset de origen de cada uno.

---

## 10. Reproducibilidad

| script | qué produce |
|---|---|
| `scan_tc.py` | inventario de las 127 cadenas, 6 sub-bloques por contenido, `tc_map.json` |
| `scan_refs_targeted.py` | los 256 pares PIC con su `kind` (`refs_targeted.json`) |
| `scan_emitters.py` | clasificación de los 256 sitios y los 17 publicadores (`emitters.json`) |
| `scan_diff_versions.py` | diferencial A7S/A6300 (`diff_versions.json`) |
| `scan_dead_check.py` | evidencia de las 4 cadenas muertas (`dead_check.json`) |
| `build_report_json.py` | agrega los JSON anteriores y fija despacho, llamadores y vocabulario (`camera_main_tc.json`) |
| `callers.py`, `disasm.py` | verificación a mano (llamadores `bl`/`blx`, ventanas Capstone) |

**Validación de la regla**: el escáner dirigido (`scan_refs_targeted.py`) reproduce **127
referencias `string` comparables, 0 discrepancias y 0 sitios estrictos ausentes** frente a la
regla estricta canónica aplicada a ciegas sobre la imagen.

Tests: `tests/test_s122_camera_main_tc.py` (bytes reales: recuentos, direcciones, pares PIC,
las 4 muertas, los 17 publicadores, el despacho `tbb`/`tbh`, los 2 llamadores y el diferencial).

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado:**

1. **Recuento**: 127 tokens `[CAMERA_MAIN_TC]` (127 textos distintos) en 6 tramos entre
   `0x43ca7fd7` y `0x43ccb350`; 123 vivas y **4 muertas**; 256 sitios PIC en **41 funciones**
   (regla estricta, la canónica del repo).
2. **`tbb` del despachador**: la tabla en `0x4387333e` es `dfe805f005050914140d0f0d` (rango
   `0xdfe` + 9 casos) → coincide con lo que el subagente describe.
3. **17 publicadores** con prólogo `push {r3}` y `bl` a `osal_try_valloc_msg` `0x435612d0` →
   patrón de publicación uniforme (cola OSAL), y **`ApolloSA_Main` `0x438730b0`** como
   despachador con `tbh` de 9 casos y **6 clientes de `[APL]`** (S119) con un único llamador
   cada uno — encaja con lo que S119 había medido.
4. **Diferencial**: 0 apariciones del token en la A7S fw3.20 y en el A6300 fw2.01, con
   126/127 textos interiores literales y 123 sitios frente a los 256 de la A6000 → **el módulo
   existe en las tres cámaras con otro etiquetado**; la fw3.21 de la A6000 es la que etiqueta.

**Aclaración sobre S51**: el informe dice «S51 A/B/C = NO se mantiene», es decir, **la decisión
de S51 sigue vigente** (A/B/C = NO): el módulo no aporta ningún indicio nuevo a favor ni en
contra del obturador electrónico (0 apariciones de `shut`, `silent`, `electro`, `mech`, `sensor`,
`exposure`, `drive`, `readout`, `jpeg`, `movie`, `bracket`, `sweep`, `interval` en sus 127 trazas).
