# FBM · tabla de pares `(userID,mediaID)→sector` y su cruce con la Sector Manager Info Table

26-11-2026 · `libmpr.so` fw 3.21 (SHA-256 `9a74a3bb…4c30`) · volcado `ram-servicio-20261020/ram_0x80000000.bin` (1 GiB, física `0x80000000`)
y `nand-20261020/dev_nflasha4.bin` · **todo estático, cámara no tocada, sin `git`**.
Evidencia reproducible: [reports/evidence/fbm-pares-video-20261126/](evidence/fbm-pares-video-20261126/INDEX.md).

## Resumen (15 líneas)

1. **La tabla de pares no está en `0x8B0023FC`.** En ese dump la VA `0x9D23FC` vive en `.data` y aparece como página *file-backed* en
   **`0x88F3A3FC`** (idéntica al `.so`) y en **`0x8BB3E3FC`**; en `0x8AF9D3FC` (= `0x8A5CB000`+`0x9D23FC`) hay **ceros**, no la tabla.
   Se conserva `VA&0xFFF = físico&0xFFF = 0x3FC`, así que la identificación es inequívoca.
2. Filas de **0x18 B, 37 filas**, terminador `+0 == 0` (`0x2B2B50`): `+0` userID · `+4` mediaID · `+8` fileType (=sector) · `+0xC` OM ·
   `+0x10` función registrada · `+0x14` dato de esa función (cabecera del comando `View`, `0x7E6AAA`).
3. La SMT de `0xA3699C` **sí** está en `0x8B00199C` (única copia en 1 GiB): 30 × `0x14` = `+0` sector · `+4` handle · `+8` válido · `+0xC` · `+0x10`.
4. `0x9D2380` = lista de los **30 sectores** (u32 + terminador `-1` en `0x9D23F8`), justo antes de la tabla de pares; el índice es la posición.
5. Cruce completo (30 filas) y las 37 parejas, abajo. **4 de 30 con handle**: `0x30`(4) · `0x62`(3) · `0xA0`(1) · `0xB2`(5).
6. Esos 4 son exactamente los 4 pares `(0x10,3)` `(0x20,3)` `(0x22,8)` `(0x23,3)`, y son también las **4 únicas filas** con `+0x10/+0x14` no cero
   en la copia viva `0x8BB3E3FC` (`diff_copias.txt`). `0x2B1E34` los pone a 0 al liberar la pareja.
7. `0x10100001` sólo se produce con **índice válido y `[entrada+4]==0`** (`0x2B39EC`→`0x2B39EE`→`0x2B3A28`).
8. ⇒ **El par que falla no es ninguno de esos 4.** En particular `(0x22,8)→0xA0` **tiene** handle: si el vídeo usara ese par no fallaría.
9. **Sí existe al menos un par de vídeo con handle**: `(0x22,8)→0xA0` h=1 y `(0x23,3)→0xB2` h=5 (ambos `+8`=1).
   Por tanto la cadena «todos los de vídeo a 0» **no se cierra con este volcado**: el par de vídeo que falla tiene que ser otro.
10. Si el vídeo va por `(0x23,m)` (`MSV`, `0x3AF686` lee `userID=[cliente+0x3c]`, `mediaID=[cliente+0x40]`), entonces `m ≠ 3` ⇒
    `0xB1` `0xB3` `0xB8` `0xBC` `0xBD`, todas a 0. El candidato natural es **`(0x23,7)→0xBD` (handle 0)**.
11. No hay **ningún** `str [X+0x4088]`/`[X+0x408c]` en los 6,8 MB de `.text` (0 aciertos): el par entra por construcción del objeto de medio
    y se lee en `0x35E0EC`/`0x35E0F0`. El `mediaID` es el campo `+0x40` del objeto cliente (`0x388A2C`, `0x3AF688`).
12. `nflasha4` (D1): los **30** sectores están formateados (estado 0, firma `0x004A004A`, 2-5 registros de 8 B, trailer `draCNV4'` en `+0x3AB`),
    incluidos todos los de vídeo. Los 4 con handle no se distinguen por contenido.
13. `0x30`→off `0xC000`, `0x62`→`0x18800`, `0xA0`→`0x28000`, `0xB2`→`0x2C800`: **sin rutas ni nombres**; sólo el trailer.
    Las únicas 5 rutas `ms:/DCIM/…` de la partición están en los sectores 0x2501/0x2504/0x251E/0x2529/0x252C (carga útil).
14. Único rastro en el flash que separa sectores: `0xBC` y `0xBD` llevan el primer registro con flag `0x00` (`{00 01 03 ff}`) en vez de `0x01`.
15. **Falta** para cerrar la cadena: el `mediaID` real en `[obj+0x408c]` del MP4 (campo `+0x40` del objeto cliente). Con eso, el par sale de la
    tabla de arriba y se sabe si es `0xBD` (handle 0) u otro.

---

## 1. Dirección real de la tabla de pares (corrección)

| dirección | contenido en el volcado |
|---|---|
| `0x8B0023FC` (VA supuesta) | **no es la tabla**: datos binarios ajenos (`43 04 00 00 00 00 00 02 43 a8 03 00 …`) |
| `0x8AF9D3FC` = `0x8A5CB000`+`0x9D23FC` | **ceros** (la `.data` file-backed de ese proceso no está mapeada ahí) |
| **`0x88F3A3FC`** | tabla de pares, **idéntica** al `.so` (37 filas + terminador) |
| **`0x8BB3E3FC`** | la misma tabla, con **4 filas** con `+0x10`/`+0x14` escritos |
| `0x8B00199C` | Sector Manager Info Table (`0xA3699C`), **única** copia en 1 GiB |

El volcado es RAM **física**: las páginas de un `.so` mapeado desde fichero (XIP) caen donde el kernel quiere, pero el
offset dentro de página se conserva. Las dos copias cumplen `& 0xFFF == 0x3FC` = `0x9D23FC & 0xFFF`, y sus filas casan
byte a byte con el `.so` salvo el estado de runtime. La lista de 30 sectores (`0x9D2380`, `& 0xFFF == 0x380`) aparece en
`0x88F3A380` y `0x8BB3E380`.

## 2. Geometría deducida del código (no de suposiciones)

```
GetFileType 0x2B2B18              ; (userID, mediaID) -> *fileType
002b2b4c  ldr  r2,=0x9D23FC
002b2b4e  ldr  r0,[r2,r3]         ; +0x00 userID
002b2b50  cmp  r0,#0
002b2b52  bne  0x2B2B2E           ; fin de tabla = userID 0
002b2b2e  cmp  r0,r4              ; == userID arg
002b2b34  ldr  r0,[r0,#4]         ; +0x04 mediaID
002b2b42  ldr  r3,[r2,#8]         ; +0x08 fileType (=sector)  -> *out

GetOperationModeFromUserIDAndMediaID 0x2B2DF4
002b2e24  ldr  r3,[r2,#0xc]       ; +0x0C operation mode

GetSectorManagerInfoTableIndexFromUserID 0x2B2F48
002b2f8e  ldr  r2,=0xA3699C ; 0x14*idx
002b2f96  ldr  r3,[r2,r3]         ; +0x00 == fileType  ->  idx
002b2fae  cmp  r5,#0x1e           ; 30 entradas

ReadFirstPackData 0x2B39B8
002b39e0  movs r1,#0x14 ; muls    ; idx*0x14
002b39e8  ldr  r0,=0xA3699C
002b39ec  ldr  r2,[r2,#4]         ; +0x04 HANDLE
002b39ee  cbz  r2,0x2B3A28        ; handle 0 -> error
002b39f6  ldrh r1,[r0,r1]         ; +0x00 sector (16 b) -> out+0
002b39fe  str  r2,[r3,#4]         ; out+4 = handle
002b3a28  ldr.w sb,=0x10100001    ; el error que ve el IFO
```

`0x2B2E54` (`GetNewSectorManagerInfoTableIndexFromUserID`) recorre la misma tabla saltando las **ocupadas**
(`+8 != 0` → `0x10800010`), y `0x2B31F0` (`GetRemainSize`) devuelve también `0x10100001` con `[+4]==0`.

## 3. Tabla cruzada — 30 filas (índice = posición en `0x9D2380` = índice en `0xA3699C`)

`handle` / `valido` leídos de `0xA3699C` en `0x8B00199C`; `pares` de las 37 filas de `0x9D23FC`.

| idx | sector | pares `(userID,mediaID)` | handle | válido | `+0xC` | `+0x10` |
|---|---|---|---|---|---|---|
| 0 | `0x10` | `(0x10,1)` | 0 | 0 | 0 | – |
| 1 | `0x11` | `(0x02,1)` | 0 | 0 | 0 | – |
| 2 | `0x12` | `(0x03,1)` | 0 | 0 | 0 | – |
| 3 | `0x20` | `(0x10,2)` | 0 | 0 | 0 | – |
| 4 | `0x21` | `(0x04,2)` `(0x21,2)` | 0 | 0 | 0 | – |
| 5 | `0x28` | `(0x10,5)` | 0 | 0 | 0 | – |
| 6 | `0x29` | `(0x04,5)` `(0x21,5)` | 0 | 0 | 0 | – |
| 7 | `0x2C` | `(0x10,6)` | 0 | 0 | 0 | – |
| 8 | `0x2D` | `(0x04,6)` `(0x21,6)` | 0 | 0 | 0 | – |
| **9** | **`0x30`** | **`(0x10,3)`** | **4** | **1** | `0x04` | – |
| 10 | `0x31` | `(0x04,3)` `(0x21,3)` | 0 | 0 | 0 | – |
| 11 | `0x38` | `(0x10,4)` | 0 | 0 | 0 | – |
| 12 | `0x39` | `(0x04,4)` `(0x21,4)` | 0 | 0 | 0 | – |
| 13 | `0x40` | `(0x01,1)` `(0x30,1)` | 0 | 0 | 0 | – |
| 14 | `0x60` | `(0x20,1)` | 0 | 0 | 0 | – |
| 15 | `0x61` | `(0x20,2)` | 0 | 0 | 0 | – |
| 16 | `0x68` | `(0x20,5)` | 0 | 0 | 0 | – |
| 17 | `0x6C` | `(0x20,6)` | 0 | 0 | 0 | – |
| **18** | **`0x62`** | **`(0x20,3)`** | **3** | **1** | `0x07` | – |
| 19 | `0x63` | `(0x20,4)` | 0 | 0 | 0 | – |
| 20 | `0x90` | `(0x10,7)` | 0 | 0 | 0 | – |
| 21 | `0x91` | `(0x04,7)` `(0x21,7)` | 0 | 0 | 0 | – |
| 22 | `0x92` | `(0x20,7)` | 0 | 0 | 0 | – |
| **23** | **`0xA0`** | **`(0x22,8)`** | **1** | **1** | `0x09` | `0x08` |
| 24 | `0xB1` | `(0x23,2)` | 0 | 0 | 0 | – |
| **25** | **`0xB2`** | **`(0x23,3)`** | **5** | **1** | `0x0A` | – |
| 26 | `0xB3` | `(0x23,4)` | 0 | 0 | 0 | – |
| 27 | `0xB8` | `(0x23,5)` | 0 | 0 | 0 | – |
| 28 | `0xBC` | `(0x23,6)` | 0 | 0 | 0 | – |
| 29 | `0xBD` | `(0x23,7)` | 0 | 0 | 0 | – |

Volcado literal de `0xA3699C` (30 × `0x14`, en `0x8B00199C`) y las 37 filas de `0x9D23FC`: `tabla_pares.txt`.

## 4. Los 4 pares con estado de runtime (`0x8BB3E3FC` frente al `.so`)

| fila | userID | mediaID | sector | `+0x10` en RAM | `+0x14` en RAM |
|---|---|---|---|---|---|
| 12 | `0x10` | 3 | `0x30` | `0x070481D1` | `0x252ACD38` |
| 24 | `0x20` | 3 | `0x62` | `0x06E31009` | `0x19C293F0` |
| 30 | `0x22` | 8 | `0xA0` | `0x06E2FD39` | `0x19C293F0` |
| 32 | `0x23` | 3 | `0xB2` | `0x06E64A79` | `0x25332180` |

Son los mismos 4 sectores con handle. Interpretación (la cabecera de `View` llama a esas columnas
`[WriteBaseDataFunction] [Funciton DATA]`): `+0x10` = puntero a función registrada (los cuatro son impares ⇒ *thumb*),
`+0x14` = dato de esa función; `0x19C293F0` se comparte entre las filas 24 y 30. La copia `0x88F3A3FC` es idéntica al `.so`
(nadie registró nada aún en ese proceso).

## 5. Foto, vídeo y tarjeta: qué está probado y qué no

**Probado hoy:**

* No existe **ningún** store directo a `[X+0x4088]`/`[X+0x408c]` en `.text` (0 aciertos con capstone `skipdata` sobre 6,8 MB); el par se lee en
  `0x35E0EC`/`0x35E0F0` y lo pone la construcción del objeto de medio (`busqueda_4088.md`).
* El `mediaID` es **un campo del objeto cliente** (`+0x40`), compartido por foto y vídeo:
  `0x388A2C ldr r1,[r5,#0x40]` (DCF, `(0x20, [cliente+0x40])`), `0x388A48 movs r0,#0x22; movs r1,#8` (DCF, `(0x22,8)` fijo),
  `0x3AF686 ldr r0,[r4,#0x3c]; 0x3AF688 ldr r1,[r4,#0x40]` (MSV/vídeo, `(userID, mediaID)` del cliente).
* **Inferencia** (por la etiqueta de las trazas, no por nombres de símbolo): foto/DCF = userID `0x20` y `0x22`
  (sectores `0x60`…`0x6C` y `0xA0`); vídeo/MSV = userID `0x23` (sectores `0xB1` `0xB2` `0xB3` `0xB8` `0xBC` `0xBD`).
  Los userIDs `0x10`, `0x04`, `0x21` no aparecen en ningún `Clear`.
* Las 4 filas registradas son 3 de mediaID **3** más el `(0x22,8)` fijo ⇒ **indicio** de que el medio montado en ese arranque
  es el mediaID 3 (tres clientes distintos registraron el 3 y ninguno otro). No es prueba del mapeo mediaID↔ranura.

**NO probado:** que el `mediaID` de la tarjeta SD sea 7 (hipótesis de `film-pb-1-sub-mp4ifo-1749-20261126.md` §158/§270) o 3.
El volcado no contiene el valor de `[obj+0x408c]` del objeto del MP4 (su `.data` no está mapeada), y no hay `GetDeviceInfo`/`MountCmd`
en la cadena estática de `libmpr`. **Es el dato que falta** y el que decide el punto 6.

## 6. ¿Existe algún par de vídeo con handle ≠ 0? (respuesta con datos)

**Sí.** Dos filas de la familia de vídeo están registradas y válidas:

* `(0x22,8) → 0xA0`, idx 23, **handle 1**, `+8`=1, `+0xC`=`0x09`, `+0x10`=`0x08` (es el "índice compartido" que registra DCF con `mediaID=8` fijo, `0x388A48`).
* `(0x23,3) → 0xB2`, idx 25, **handle 5**, `+8`=1, `+0xC`=`0x0A`.

Consecuencia lógica, sin depender de nombres: el error `0x10100001` exige handle 0 en una entrada **existente**, luego

> el par que falló **no** es `(0x10,3)`, ni `(0x20,3)`, ni `(0x22,8)`, ni `(0x23,3)`.

Por tanto **no se puede cerrar** "todos los pares de vídeo están a 0": `0xA0` y `0xB2` no lo están. El par de vídeo que falla es
uno de `(0x23,m)` con `m ≠ 3` ⇒ `0xB1` `0xB3` `0xB8` `0xBC` `0xBD`, todos con handle 0. El candidato coherente con el resto de la
investigación (medio de la tarjeta = 7) es **`(0x23,7) → 0xBD`, idx 29, handle 0, `+8`=0**.

Para decidirlo hace falta leer `[obj+0x408c]` del objeto que llama a `0x35E0F4` (o el `mediaID` `+0x40` del cliente MSV) — no está en
este volcado por ser `.data` de otro proceso, y no hay store estático que lo delate.

## 7. `nflasha4` (D1) — los 4 sectores con handle

Partición de 10 MiB = 10 240 sectores de 1 KiB; 765 no blancos (9 475 totalmente `0xFF`). Los **30** sectores de la lista
`0x9D2380` están presentes y formateados, no sólo los 4 con handle:

| sector | offset | estado | firma | registros (`u32 longitud`/flags) | handle |
|---|---|---|---|---|---|
| `0x30` | `0x00C000` | 0 | `0x004A004A` | `81/010103`, `a0/000101` | 4 |
| `0x62` | `0x018800` | 0 | `0x004A004A` | `81/010103`, `a0/000101`, `62/000607`, `b2/000507` | 3 |
| `0xA0` | `0x028000` | 0 | `0x004A004A` | `81/010103`, `a0/000101`, `62/000607`, `30/000507`, `b2/000507` | 1 |
| `0xB2` | `0x02C800` | 0 | `0x004A004A` | `81/010103`, `a0/000101`, `62/000607`, `b2/000507`, `30/000507` | 5 |
| `0xBD` | `0x02F400` | 0 | `0x004A004A` | `81/000103`, `a0/000101`, `62/000607`, `b2/000507` | 0 |

* **Nada legible**: sólo el trailer `draCNV4'` en `+0x3AB`. Ninguna ruta `ms:/`, ningún nombre de fichero, ningún `DCIM`.
* Las 5 únicas rutas de la partición están en sectores de carga útil:
  `0x2501 ms:/DCIM/141MSDCF/DSC00003.JPG`, `0x2504 …/DSC00010.JPG`, `0x251E ms:/DCIM/14240101/DSC03043.JPG`, `0x2529 …3044.JPG`, `0x252C …3045.JPG`.
* Los registros `81`, `a0`, `62`, `30`, `b2` son **longitudes** (129/160/98/48/178 B) y se repiten en casi todos los sectores:
  coinciden con los ids `0x30/0x62/0xA0/0xB2` pero **no** son ids; no sirven para explicar los handles.
* Único rasgo diferencial en el flash: `0xBC` y `0xBD` llevan `{00 01 03 ff}` en el primer registro (flag `0x00`) en lugar de `{01 01 03 ff}`.
* ⇒ el contenido de `nflasha4` **no** explica por sí solo que 26 sectores queden sin handle: los 30 existen. La causa hay que
  buscarla en el estado que ve `FlashLib::CheckExistSector`/`OpenSector32` en runtime (o en el límite de sectores abiertos), no en la ausencia de datos.

## 8. Siguiente paso (una sola lectura)

Leer en el arnés `[obj+0x408c]` (o `[cliente MSV+0x40]`) en el instante del `bl 0x2B39B8` de `0x35E0F4`: si vale `7`, el par es
`(0x23,7)→0xBD` (handle 0) y la cadena queda cerrada con el dato de §6; si vale `3`, el fallo **no** es del FBM y hay que buscar
otro par (p. ej. `(0x10,3)`/`(0x20,3)` usados con otro `userID`).
