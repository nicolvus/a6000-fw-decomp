# S120 — `[IDT_OPD]`: la segunda instancia del módulo IDT (los mapas de imagen del imager)

> Hito de la **línea de ingeniería inversa general** del firmware de la A6000 (fw3.21).
> Verificación **contra los bytes** de `analysis/rea-independent/input/av-cam.bin`
> (11 427 236 B). Convención **vaddr = 0x43541000 + file_offset**.
> Método de referencias: `analysis/s106_imaging_cap/scan_pic_refs_v2.py` (kill analysis
> canónica) **y** `analysis/s120_idt_opd/scan_idt_code_pic.py` (barrido restringido al
> código del módulo + kill analysis **corregida**; ver §5.1), con verificación a mano de
> los sitios que se citan como dato puntual
> (ver `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> No se ha ejecutado firmware, ni se ha usado la cámara, ni la red.

Artefactos: `analysis/s120_idt_opd/`, `docs/capture/s120-idt-opd.md`, `tests/test_s120_idt_opd.py`.

---

## 1. Resumen

| dato | valor | cómo se comprueba |
|---|---|---|
| trazas `[IDT_OPD]` en la A6000 fw3.21 | **274** (274 apariciones del token, 274 textos distintos) | `B.count(b"[IDT_OPD]")` sobre el blob |
| rango de la tabla de cadenas | `0x43cf11f9` … `0x43cf5810` (último token en `0x43cf57f1`) | barrido de bytes |
| gemelos `[IDT]` contiguos | **274 de 274** (cada traza OPD va seguida de su gemelo `[IDT]`) | comparación byte a byte de la tabla |
| funciones que referencian trazas `[IDT_OPD]` | **165** (kill analysis) | mapa PIC + prólogos Thumb |
| sitios PIC (regla kill canónica) | **725** par `(cadena, add)`; 608 `add` distintos; 717 con función atribuida | `scan_pic_refs_v2.py` |
| sitios PIC (kill analysis **corregida**) | **356** — el **mismo** conjunto de 271 cadenas (ver §5.1) | `scan_idt_code_pic.py` |
| trazas con ≥1 referencia | **271 de 274** | idem |
| trazas sin referencia confirmada | **3** (`0x43cf150f`, `0x43cf1557`, `0x43cf274a`) | idem |
| sub-bloques de la tabla | **25** rangos contiguos | §4 |
| código del módulo | `0x439dde84` … `0x439fcf9c` (~127 KB) | mapa función→traza |
| **A7S fw3.20** | **0 trazas `[IDT_OPD]`**, 306 `[IDT]` | bytes del blob de la A7S |
| **A6300 fw2.01** | **0 trazas `[IDT_OPD]`**, 382 `[IDT]` | bytes del blob de la A6300 |

**Idea central (VERIFICADA):** `IDT_OPD` **no es una sigla inventada**: es el nombre de un
**recurso del `SyncResMgr`** (`RESOURCE_IDT_OPD`, `0x43c9c461` en la A6000; offset `0x761b67`
en la A7S) y de una **tarea/comando** (`IDT_OPD_TOP_Sync_OPDAcquire`, `IDT_OPD_TOP_Sync_SetFOPD`).
La fw3.21 de la A6000 es la **única de las tres** que etiqueta sus trazas con el prefijo
`[IDT_OPD]`; la A7S fw3.20 y la A6300 fw2.01 tienen el **mismo recurso y los mismos comandos**,
pero etiquetan todo con `[IDT]`.

## 2. Qué es `[IDT_OPD]`

### 2.1 Es un prefijo de traza, y el bloque de cadenas es una *copia duplicada* del de `[IDT]`

El prefijo `[IDT_OPD]` aparece **274 veces**, todas dentro de un único bloque contiguo de
cadenas (`0x43cf11f9`–`0x43cf5810`). Cada mensaje va **seguido inmediatamente de su gemelo
`[IDT]`**, separado por un NUL:

```
0x43cf11f9  '[IDT_OPD]: SEND MESSAGE alloc ERROR'  (35)  0x00
0x43cf121d  '[IDT]: SEND MESSAGE alloc ERROR'      (31)  0x00
0x43cf123d  '[IDT_OPD]: SEND MESSAGE ERROR'        (29)  0x00
0x43cf125b  '[IDT]: SEND MESSAGE ERROR'            (25)  0x00
0x43cf1275  '[IDT_OPD]: Illegal cap FOPD Call when 1pass %d'
```

Las **274 parejas** son byte a byte idénticas salvo el prefijo (`[IDT_OPD]` = 8 caracteres
frente a `[IDT]` = 5). Esto **confirma y precisa** lo que S89 dejó como
*"casi cada mensaje del módulo aparece dos veces, con prefijo `[IDT_OPD]` y `[IDT]`, y las dos
copias están contiguas"*: la contigüidad es **exacta en los 274 casos**, no "casi".

### 2.2 Las dos etiquetas las emite **el mismo código** (esto NO estaba visto en S89)

El mapa función→traza muestra **135 funciones que referencian las dos variantes** a la vez.
Verificado **a mano** en dos funciones:

**(a) `0x439f85d4`** (volcado de los punteros de mapa, 38 trazas):

```
0x439f85e4:  ldr  r3, [pc, #0x210]      ; pool 0x439f87f8 = 0x002fbf5b
0x439f85e6:  add  r3, pc                ; r3 = 0x43cf4545 = '[IDT_OPD]: 4cmap:%X'
0x439f85e8:  bl   0x439f80b8            ; emisor de mensaje estructurado
0x439f85ec:  ldr  r0, [pc, #0x20c]      ; → 0x43cf4559 = '[IDT]: 4cmap:%X'
0x439f85ee:  ldr  r1, [r4, #0x3c]       ; el valor del campo
0x439f85f0:  add  r0, pc
0x439f85f2:  bl   0x436ce4cc            ; printf de consola
```

**(b) `0x439ee7e8`** (validación del bloque MAP, 53 trazas): mismo patrón,
`[IDT_OPD]: 4cmap.adrs Err:%X` → `bl 0x439ec5b0` y `[IDT]: 4cmap.adrs Err:%X` → `bl 0x436ce4cc`.

**Conclusión (VERIFICADA):** el firmware **duplica la instrumentación**, no el código:
cada evento se registra **dos veces**, una con el prefijo `[IDT_OPD]` (por el canal de
mensajería) y otra con `[IDT]` (por la consola). Los dos "canales" son:

| canal | función | qué hace | reparto de prefijos |
|---|---|---|---|
| mensajería/registro | `0x439f80b8`, `0x439ec5b0` (y gemelas `0x439e0fe0`, `0x439e20d8`, `0x439e7d70`, `0x439f5fc8`, …) | construye un registro de **0x9a bytes** (`movs r2,#0x9a`) con los campos `arg0`(=6), `arg1`(=2), `arg2`(=1) y el texto formateado | casi siempre **`[IDT_OPD]`** |
| consola | `0x436ce4cc` (`printf`-like, usa `vsnprintf` `0x439c5004`) | imprime el texto en la consola | casi siempre **`[IDT]`** |

Recuento de los sitios por canal (heurística "el `bl` siguiente"; verificada a mano en los
dos casos anteriores): `0x436ce4cc` recibe 421 sitios `[IDT]` y 59 `[IDT_OPD]`;
`0x439f80b8` recibe 119 `[IDT_OPD]` y 26 `[IDT]`; `0x439ec5b0` recibe 116 `[IDT_OPD]` y 10 `[IDT]`.

### 2.3 `IDT_OPD` es un **recurso** y un **comando**, no un acrónimo

En la tabla de nombres de recursos del `SyncResMgr` (A6000 `0x43c9b3f9`–`0x43c9c50a`):

```
RESOURCE_UKNOWN  RESOURCE_CAMDEV  RESOURCE_CAMMOV  RESOURCE_SGC  RESOURCE_RCHV
RESOURCE_RCH     RESOURCE_RCV     RESOURCE_VFX
RESOURCE_IDT_OPD   0x43c9c461
RESOURCE_IDT_VOT   0x43c9c472
RESOURCE_IDT_TOP   0x43c9c483
RESOURCE_IMAGER    0x43c9c494
RESOURCE_SRC_*  RESOURCE_IIB_FROM_CAM_/RC_/VFX_/SRC
```

y en la tabla de comandos/recursos de secuencia:

```
0x43c9c2fc  '[CAMERA_MAIN_SYNC]: SyncResMgr::Get: IDT_OPD_TOP_Sync_OPDAcquire error!'
             (el texto 'IDT_OPD_TOP_Sync_OPDAcquire' empieza en 0x43c9c321)
0x43cb0f3e  '[CAMERA_MAIN_SYNC]: SyncResMgr::Get IDT_OPD failure'
             (el texto 'IDT_OPD' está en 0x43cb0f62)
0x43cb2a3f  'b ee IDT_OPD_TOP_Sync_SetFOPD'      0x43cb2a5d  'e ee IDT_OPD_TOP_Sync_SetFOPD'
```

**La misma tabla de recursos, con los mismos nombres, existe en la A7S fw3.20**
(`RESOURCE_IDT_OPD` en el offset `0x761b67`, `IDT_OPD_TOP_Sync_OPDAcquire` en `0x761a63`,
`IDT_OPD_TOP_Sync_SetFOPD` en `0x772de5`) y en la **A6300 fw2.01** (`0x865c1b`, `0x88c56d`,
`0x865d61`), que además añade
`[IDT]:  IDT_OPD_AFMAP_InitAfmap_lower memory_flag = false` (offset `0x8c5a31`),
`IDT_OPD_AFMAP_FreeAfmap_lower` (`0x8c59f7`) e `IDT_OPD_AFMAP_StealDepthMovie` (`0x8c59c9`).

→ **Lo que el prefijo `[IDT_OPD]` etiqueta es la instancia "OPD" del módulo IDT**, que en
la fw3.21 de la A6000 recibe un recurso (`RESOURCE_IDT_OPD`) y una tarea (`IDT_OPD_TOP`)
**propios**, y por eso el firmware la etiqueta con su propio prefijo de traza.
**NO VERIFICADO**: qué hace funcionalmente la OPD que no hace la instancia "IDT"
(el `IDT` normal tiene `RESOURCE_IDT_TOP`); y por qué la A7S/A6300 no la etiquetan.

## 3. La tabla de cadenas: 274 trazas

| | |
|---|---|
| primer token | `0x43cf11f9` = `[IDT_OPD]: SEND MESSAGE alloc ERROR` |
| último token | `0x43cf57f1` = `[IDT_OPD]: MovieDepthRate illegal` (fin de cadena en `0x43cf5810`) |
| textos distintos | 274 (no hay repeticiones) |
| sub-bloques | 25 rangos contiguos (§4) |

Una traza no empieza en el token: `0x43cf274a` es el `[IDT_OPD]` de
`"[IDT_OPD]: CCinitParam addr null"`, precedido por una **tabla de 11 offsets**
(`04 08 0c 10 15 1b 20 24 28 2c 30`) en `0x43cf2740`–`0x43cf274a`; la cadena real empieza en
`0x43cf2750`. Los 274 tokens están cubiertos por los 274 mensajes.

### 3.1 Trazas sin referencia confirmada (3)

| vaddr | texto | nota |
|---|---|---|
| `0x43cf150f` | `[IDT_OPD]: Can't use sync release CB!` | sin referencia en el barrido kill ni en el barrido completo |
| `0x43cf1557` | `[IDT_OPD]: No time for 2imager` | ídem |
| `0x43cf274a` | `[IDT_OPD]: CCinitParam addr null` | ídem (la cadena real en `0x43cf2750` tampoco tiene referencia) |

Las tres son código muerto en la A6000 (su gemelo `[IDT]` sí está referenciado: en la A7S
están vivas, p. ej. `[IDT]: IDT : Init NG : address = %x`).

## 4. Mapa de las 274 trazas por sub-bloque

Los sub-bloques son **rangos contiguos** de la tabla de cadenas (no una taxonomía inventada:
cada rango se comprueba contra los bytes). Los 274 mensajes quedan cubiertos sin huecos.

| # | rango (vaddr) | sub-bloque | n | contenido |
|---|---|---|---|---|
| 1 | `0x43cf11f9`–`0x43cf1aa3` | `driver_canal` | 32 | canal con el gestor de captura: `SEND MESSAGE`, `Cap:`, FOPD, Split, AF, PBL |
| 2 | `0x43cf1aa3`–`0x43cf1d7d` | `driver_modos` | 11 | `IDTdriver overflow`, traducción FRM, `Only vatr is kicked`, `load_delay`, ganancia, distorsión, display |
| 3 | `0x43cf1d7d`–`0x43cf23af` | **`bloque_IE`** | 28 | punteros `ie_miniraw/backImgData/imgmap/ie_out/refmap` y metadatos `tar_num, isSpectRef, isMapOut, r/g/b val, ie_offset, ie_imgwidth/height/addnum, ie_aspect`, `idealWidth/Height`, `mask.x_end/y_end` |
| 4 | `0x43cf23af`–`0x43cf2634` | **`bloque_LC`** | 10 | `lc_miniraw`, `lc_out`, `lc_offset`, `lc_imgwidth/height/addnum`, `lc_aspect`, semáforos LC |
| 5 | `0x43cf2634`–`0x43cf2740` | `RC_del_mapa` | 4 | `Start MapWidthRC/MapHeightRC function`, `leftW,rightW`, `topH,bottomH` |
| 6 | `0x43cf2740`–`0x43cf292a` | `params_sync` | 8 | `CCinitParam`, `ECinitParam`, `CCsyncParam`, `ECsyncParam`, `CCsyncRes`, `ECsyncRes` |
| 7 | `0x43cf292a`–`0x43cf2bb6` | `umbrales_y_regiones` | 11 | `face_use_cc`, `kido_th[%d].up/.dn`, `ratio_wak[%d].up/.dn/.rgt/.lft`, `sel_waku[%d]`, `sel_wak`, `sel_hist`, `sel_sum` |
| 8 | `0x43cf2bb6`–`0x43cf2d56` | **`bloque_MAP`** | 7 | `miniraw`, `shade_map`, `4cmap`, `histmap`, `summap`, `out_opd_cc`, `out_opd_ec` |
| 9 | `0x43cf2d56`–`0x43cf2f5c` | `geometria_MAP` | 11 | `offset`, `imgwidth`, `imgheight`, `imgaddnum`, `aspect`, `x_size`, `y_size`, `x.sel`, `y.sel`, `x.span`, `y.span` |
| 10 | `0x43cf2f5c`–`0x43cf322c` | `regiones_integracion` | 10 | `intn precap/intn cap`, `intWak[%d]`, `histWak[%d]`, `cwaku[%d]`, límites de spec |
| 11 | `0x43cf322c`–`0x43cf3306` | `sync_y_4cmap` | 3 | `CC/EC syncflg set error`, `4cmap aspect error!` |
| 12 | `0x43cf3306`–`0x43cf3588` | `IDTSA` | 9 | `GetIDTSA Unknown aspect`, `AF AE x/y`, `calc_inv(2) 0div`, `Split Coordinate: Async invalid`, `calc SplitIDTSA error`, `IDTSA Invalid Ch select` |
| 13 | `0x43cf3588`–`0x43cf37d6` | `FRM_sync_async` | 8 | `Out of Spec:sync/async FRM_mode`, `sync/async FRM size h 0ch/1ch/v` |
| 14 | `0x43cf37d6`–`0x43cf3ec8` | `DET_HIST_CAE_GLE` | 25 | `DET x/y-size over`, `HIST x/y size not enough`, `CAE x/y size not enough`, `gle *-size error`, `Det1/2`, `Gle1/2`, `HIST min/max`, `CAE cnt_h…`, `total:%dx%d rcout:…`, `det:xs:…` |
| 15 | `0x43cf3ec8`–`0x43cf4090` | `VATR` | 6 | `VATR Error det/gle`, `VATR vld`, `width not 8n or height not 2n`, `VATR size error`, `unknown rate`, `RAW size error` |
| 16 | `0x43cf4090`–`0x43cf431d` | `miniRAW_y_debug` | 8 | `miniRAW Addr`, `width/height`, `DebugGetInfo extraction failed`, `CC EC Result Addr`, `DebugInfo extraction failed` |
| 17 | `0x43cf431d`–`0x43cf44e9` | `tasas_y_AF_param` | 6 | `FRM rate NG`, `FOPD_rate is not correct!`, `Invalid AF_pix/clk`, `8pix/clk`, `AF_param is not correct!` |
| 18 | `0x43cf44e9`–`0x43cf4545` | `AF_param_async` | 1 | `AF_param is not correct async!` |
| 19 | `0x43cf4545`–`0x43cf47f1` | **`volcado_de_punteros`** | 18 | los 18 punteros: `4cmap, hmap, smap, ccout, ecout, shade, input, msain0, msain1, msaout, ieout, p_img_map, p_backImgData, ie_in, mapRC_in, lc_out, lc_in, refmap` |
| 20 | `0x43cf47f1`–`0x43cf4907` | `SGC_y_RefMap` | 4 | `SGC must change w/h`, `IE_RefMap is NULL`, `Can't Get miniRAW Mem` |
| 21 | `0x43cf4907`–`0x43cf4a85` | `memoria_VATR` | 6 | `VATR Mem Get/Mem OK/Mem NG/Mem Release OK/Mem Release NG/IsAlloc` |
| 22 | `0x43cf4a85`–`0x43cf4d51` | `semforos` | 11 | `IDT EC/CC/LC_SEM SIG ERR`, `IDT Get ec/cc/lc_sem`, `time_out`, `EC/CC overflow` |
| 23 | `0x43cf4d51`–`0x43cf4f35` | `load_delay_y_pixclk` | 7 | `invalid load_delay`, `AF invalid rate`, `VATR with 8pix/clk is out of spec`, `unknown pix/clk`, `FOPD rate Convert NG` |
| 24 | `0x43cf4f35`–`0x43cf50ed` | `Request_y_SyncRate` | 5 | `Request Convert NG`, `SelectAF LC request NG`, `Sync rate %d -> %d use:%d mode:%d`, `Async rate %d -> %d` |
| 25 | `0x43cf50ed`–`0x43cf5811` | `modos_FRM_y_EE` | 25 | `Illegal FRM mode for image_param/IDTSA`, `FOPD_MODE error`, `mask%x add%x`, `valid add:%d mask%x`, `0size` (cap/capo/rc/EE/arc), `4pix/clk error`, `FRM width error EE` |

## 5. Funciones que referencian las trazas

165 funciones (kill analysis), código entre `0x439dde84` y `0x439fcf9c`. **Todos** los sitios de
referencia de las 274 trazas están dentro de `0x439d0000`–`0x43a09000` (verificado: un barrido
PIC restringido a ese rango reproduce **exactamente** los 725 sitios del barrido global).
Las funciones que más trazas emiten:

| función | n | primera traza | papel |
|---|---|---|---|
| `0x439ee7e8` | 53 | `[IDT_OPD]: miniraw.adrs Err:%X` | **valida el bloque MAP** (punteros + geometría) |
| `0x439e80c8` | 40 | `[IDT_OPD]: ie_miniraw.adrs Err:%X` | **valida el bloque IE** (`IE_CCinit`) |
| `0x439f85d4` | 38 | `[IDT_OPD]: 4cmap:%X` | **vuelca los 18 punteros** de mapa |
| `0x439f11a4` | 30 | `[IDT_OPD]: idealWidth Err:%d` | geometría / ventanas de detección |
| `0x439e950e` | 23 | `[IDT_OPD]: idealWidth Err:%d` | construcción del bloque LC (array de elementos de **0x60 bytes**) |
| `0x439e2fd6` | 22 | `[IDT_OPD]: AF AE1 %d %d %d %d` | ventanas AF |
| `0x439e2a50` | 19 | `[IDT_OPD]: Illegal Split EE FOPD Call %d` | camino Split/EE |
| `0x439efe10` | 17 | `[IDT_OPD]: idealWidth Err:%d` | idealWidth/Height |
| `0x439f67c4` | 15 | — | mapas |
| `0x439ef11a` | 14 | `[IDT_OPD]: idealWidth Err:%d` | idealWidth |

**Verificación a mano (dato puntual).** Sitio `0x439f85e6`:

```
0x439f85e4  ldr  r3, [pc, #0x210]     → pool 0x439f87f8 = 0x002fbf5b
0x439f85e6  add  r3, pc               → 0x002fbf5b + 0x439f85ea = 0x43cf4545
                                      → '[IDT_OPD]: 4cmap:%X'
```

entre el `ldr` y el `add` no hay ninguna instrucción (nadie escribe `r3`) → la referencia es
segura.

### 5.1 Nota metodológica: la "kill analysis" canónica está **inerte** (VERIFICADO)

Al reimplementar el escáner para este hito (`analysis/s120_idt_opd/scan_idt_code_pic.py`) se
detectaron **dos defectos** en `analysis/s106_imaging_cap/scan_pic_refs_v2.py`:

1. **`md.detail` no está activado.** `_writes_to()` hace `ins.operands`, que con
   `detail=False` lanza `CsError`; la excepción se captura y la función **devuelve siempre
   `False`**. Por tanto **la kill analysis nunca descarta ningún par**: en la práctica el
   escáner v2 aplica la regla **ancha con ventana de 4 KB**.
2. **`op.reg & 0xF` confunde registros.** En Capstone `ARM_REG_Rn == 66 + n`, así que
   `& 0xF` desplaza 2 bits: `r1` (67) se lee como `r3` (67 & 0xF = 3), `r2` como `r4`, etc.
   Con `detail` activado, `movs r1,#2` mataba los pares de `r3` (p. ej. el sitio
   `0x439e10a4` → `0x43cf11f9`, verificado a mano: es **una referencia válida**).

**Efecto sobre este módulo** (barrido restringido `0x439d0000`–`0x43a09000`):

| regla | sitios | cadenas con referencia | cadenas sin referencia |
|---|---|---|---|
| canónica (kill inerte = ancha 4 KB) | 725 | **271** | 3 |
| **kill analysis corregida** (detail activo + nombre de registro) | **356** | **271** | 3 |

→ **El conjunto de cadenas referenciadas NO cambia** (271 de 274) al corregir la regla: sólo
desaparecen 327 sitios falsos. Las 3 cadenas sin referencia son las mismas en ambas reglas,
lo que refuerza que están **muertas** y no que sean un artefacto de la regla.

**Recomendación para los hitos siguientes:** publicar siempre el **número de cadenas**
(estable) y, si se publica el de sitios, indicar **qué** variante de la kill analysis se ha
usado (con `detail` activo y comparación por nombre de registro).

## 6. Estructura de los bloques que entrega el módulo

### 6.1 Bloque IE (`IE_CCinit`) — función `0x439e80c8`, base = puntero recibido en `r0`

| offset | tipo | campo | traza que lo nombra |
|---|---|---|---|
| `0x00` | u16 | `tar_num` | `[IDT_OPD]: tar_num Err:%d` (`0x43cf1eed`) |
| `0x0c` | u8 | `isSpectRef` | `0x43cf1f1d` |
| `0x0d` | u8 | `isMapOut` | `0x43cf1f53` |
| `0x10` | u32 | `refmap` (adrs) | `0x43cf1eb5` |
| `0x16` | u16 | `r.val.high` | `0x43cf1f85` |
| `0x18` | u16 | `r.val.low` | `0x43cf1fbb` |
| `0x1c` | u16 | `g.val.high` | `0x43cf1fef` |
| `0x1e` | u16 | `g.val.low` | `0x43cf2025` |
| `0x22` | u16 | `b.val.high` | `0x43cf2059` |
| `0x24` | u16 | `b.val.low` | `0x43cf208f` |
| `0x54` | u32 | `ie_miniraw` (adrs) | `0x43cf1dc3` |
| `0x58` | u32 | `ie_offset` | `0x43cf20c3` |
| `0x5c` | u16 | `ie_imgwidth` | `0x43cf20f7` |
| `0x5e` | u16 | `ie_imgheight` | `0x43cf212f` |
| `0x60` | u16 | `ie_imgaddnum` | `0x43cf2169` |
| `0x62` | u16 | `ie_aspect` | `0x43cf21a3` |
| `0x70` | u32 | `ie_out` (adrs) | `0x43cf1e7d` |
| `0x74` | u32 | `imgmap` (adrs) | `0x43cf1e45` |
| `0x78` | u32 | `backImgData` (adrs) | `0x43cf1e03` |

(Verificado desensamblando: p. ej. `0x439e80ce: ldr r3,[r0,#0x54]` → `ie_miniraw`;
`0x439e80d4: ldr r2,[r0,#0x78]` → `backImgData`; `0x439e8188: ldrh r3,[r4]` → `tar_num`;
`0x439e81be: ldrb r3,[r4,#0xc]` → `isSpectRef`; `0x439e81c4: ldrb r2,[r4,#0xd]` → `isMapOut`.)

### 6.2 Bloque MAP — función `0x439ee7e8` (base = `r0`)

| offset | tipo | campo | traza |
|---|---|---|---|
| `0x0c` | u32 | `miniraw` (adrs) | `0x43cf2bb6` |
| `0x10` | u32 | `offset` | `0x43cf2d56` |
| `0x14` | u16 | `imgwidth` | `0x43cf2d84` |
| `0x16` | u16 | `imgheight` | `0x43cf2db6` |
| `0x18` | u16 | `imgaddnum` | `0x43cf2dea` |
| `0x1a` | u16 | `aspect` | `0x43cf2e1e` |
| `0x28` | u8 | `x_size` | `0x43cf2e4c` |
| `0x29` | u8 | `y_size` | `0x43cf2e7a` |
| `0x2a` | u16 | `x.sel` | `0x43cf2ea8` |
| `0x2c` | u16 | `x.span` | `0x43cf2f00` |
| `0x2e` | u16 | `y.sel` | `0x43cf2ed4` |
| `0x30` | u16 | `y.span` | `0x43cf2f2e` |
| `0x38` | u32 | `shade_map` (adrs) | `0x43cf2bf0` |
| `0x3c` | u32 | `4cmap` (adrs) | `0x43cf2c2e` |
| `0x40` | u32 | `histmap` (adrs) | `0x43cf2c64` |
| `0x44` | u32 | `summap` (adrs) | `0x43cf2c9e` |
| `0x48` | u32 | `out_opd_cc` (adrs) | `0x43cf2cd6` |
| `0x4c` | u32 | `out_opd_ec` (adrs) | `0x43cf2d16` |

**Coherencia cruzada (VERIFICADA):** el volcado `0x439f85d4` lee del bloque global
`0x43f41b30` los offsets `0x38/0x3c/0x40/0x44/0x48/0x4c` con los nombres
`shade/4cmap/hmap/smap/ccout/ecout` y `0x54 = input`; es **el mismo layout** que el bloque
MAP (`hmap`≡`histmap`, `smap`≡`summap`, `ccout`≡`out_opd_cc`, `ecout`≡`out_opd_ec`).

### 6.3 Los 18 punteros y dónde viven

`0x439f85d4` los reparte en **tres bloques** y **cinco globales sueltos**:

| base | offset | nombre |
|---|---|---|
| `0x43f41b30` | `0x38` / `0x3c` / `0x40` / `0x44` / `0x48` / `0x4c` / `0x54` | `shade` / `4cmap` / `hmap` / `smap` / `ccout` / `ecout` / `input` |
| `0x43f41cbc` | `0x28` / `0x2c` / `0x30` / `0x38` | `ieout` / `p_img_map` / `p_backImgData` / `ie_in` |
| `0x43f418a8` | `0x28` / `0x30` | `lc_out` / `lc_in` |
| `0x43f41bbc` | — | `msain0` |
| `0x43f41ef0` | — | `msain1` |
| `0x43f41ad8` | — | `msaout` |
| `0x43f41f14` | — | `mapRC_in` |
| `0x43f4189c` | — | `refmap` |

### 6.4 Bloque LC

Los campos `lc_*` viven en una **tabla de elementos de 0x60 bytes**
(`0x439e957e: movs r7,#0x60` + `0x439e958a: mla ip,r7,r2,r4` en `0x439e950e`), y
`0x439e86ac: movs r7,#0x8c` marca un segundo array de 0x8c bytes (regiones `waku`).
Del volcado de `0x439e950e` se leen, sobre el bloque LC:
`+0x3c = lc_miniraw` (adrs), `+0x40 = lc_imgwidth` (u16), `+0x42 = lc_imgheight` (u16),
`+0x54 = lc_out` (adrs), más `lc_offset` (u32), `lc_imgaddnum` (u16) y `lc_aspect` (u16).
**NO VERIFICADO**: el layout completo del elemento de 0x60 bytes (el acceso es indexado y el
rastreador lineal no lo resuelve).

### 6.5 Quién escribe y quién lee

- **Escribe**: el propio IDT (las funciones `0x439ee7e8` / `0x439e80c8` / `0x439e950e`
  *validan* los bloques que entrega; los punteros se rellenan en el bloque global
  `0x43f41b30` y en los bloques `0x43f41cbc` / `0x43f418a8`).
- **Publica**: el emisor de mensajes estructurados `0x439f80b8`/`0x439ec5b0` (registro de
  0x9a bytes con `arg0=6`, `arg1=2`, `arg2=1`).
- **Consume**: el `SyncResMgr` (`[CAMERA_MAIN_SYNC]`, S112) reparte el recurso
  `RESOURCE_IDT_OPD`; el `IMAGING_CAP` (S106) dispara el `KickFOPD`; el `CAMERA_MAIN_LC`
  consume el **miniRAW**; el `CAMCORE` libera la memoria del VATR.
- **No hay ningún otro módulo en `av-cam.bin` que nombre estos mapas**: `4cmap` (6
  apariciones), `shade_map` (2), `summap` (2), `histmap` (2), `backImgData` (4),
  `p_img_map` (2), `msain0` (2), `msaout` (2), `ie_out` (2), `refmap` (4), `imgmap` (2)
  aparecen **todas** dentro del bloque `0x43cf11f9`–`0x43cf5810`. → el consumidor final
  (el motor de imagen / DFE) accede a los mapas **por puntero**, no por nombre.

## 7. Relación con los otros hitos

| módulo | vaddr | texto | qué aporta |
|---|---|---|---|
| `[IMAGING_CAP]` (S106) | `0x43cadd2d` / `0x43cadd60` / `0x43cadd8f` | `StartRdraw_Prelight/Read/AfterCap: KickFOPD error` | el gestor de captura **dispara** el IDT en las tres fases de lectura |
| `[CAMERA_MAIN_SYNC]` (S112) | `0x43c9c2fc` | `SyncResMgr::Get: IDT_OPD_TOP_Sync_OPDAcquire error!` | el `SyncResMgr` arranca la **tarea OPD** |
| `[CAMERA_MAIN_SYNC]` | `0x43cb0f3e` | `SyncResMgr::Get IDT_OPD failure` | fallo al adquirir el recurso OPD |
| `[CAMERA_MAIN_SYNC]` | `0x43c9b5ab`, `0x43c9b5f8`, `0x43c9bc5e`, `0x43c9be17` | `IDT_STOP_ERR(VATR)`, `IDT_RELEASE_ERR(VATR)`, `IDT_TOP, IDT_ERR(VATR)`, `MODE_EE(01), IDT_ERR(VATR)` | el VATR es un **recurso** que el gestor de recursos libera/paraliza |
| `[CAMERA_MAIN_SYNC]` | `0x43cb1056`, `0x43cb109a` | `Sync_Kick_IDT: overflow …` | límites de tiempo del kick |
| `[CAMERA_MAIN_SYNC]` | `0x43ca38e2` | `HS3_IDT: process margin warning %dus` | el IDT corre en el **grupo HS3** |
| `[CAM_FUNC_MGR]` | `0x43ca12f6` | `SyncProcMargin[usec] … HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u …` | **el IDT se ejecuta en CPU0 del grupo HS3** |
| `[CAMERA_MAIN_LC]` | `0x43c9c8ba` | `[LC] Movie DM AF cannot get miniRAW Stored memhandle` | el **miniRAW** lo consume el AF híbrido/LC (S75/S71) |
| `[CAMCORE]` | `0x43c90982` | `SplitEEController: Memory Close Error!(VATR)` | el VATR se libera al cerrar la captura partida |
| `[CAM_IMAGER]` (S115) | — | — | **no hay ninguna traza que nombre el IDT**: el driver del sensor no conoce el IDT; la relación es **por puntero/memoria**, no por mensajes |

**Relación con el motor de imagen (S110, `[CAMERA_MAIN_YC]`):** tampoco hay trazas
comunes. Los mapas viajan como **punteros en memoria** (`RESOURCE_IIB_FROM_*` es el camino
`IIB` = *image buffer* en la tabla de recursos del `SyncResMgr`).

## 8. Ficheros fuente

Nombres de fichero embebidos relacionados con el IDT (búsqueda de `*.cpp`/`*.h` en todo el blob):

| vaddr | nombre |
|---|---|
| `0x43cadd17` | `CaptureUtilityIDT.cpp` (utilidad de captura que habla con el IDT) |
| `0x43cc9785` | `Stage_OPD.cpp` (etapa OPD de la tubería de captura) |
| `0x43cef51a` | `FC/Api/fc_api_idt.cpp` (API de caras) |

**Resultado negativo verificado:** en el rango de código del módulo
(`0x439c0000`–`0x43a20000`) **no hay ningún nombre de fichero fuente** (0 coincidencias de
`[A-Za-z0-9_./]+\.(cpp|h)`). Los ficheros fuente del propio IDT **no están embebidos**;
los nombres de arriba pertenecen a los módulos vecinos.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20 (y A6300 fw2.01)

### 9.1 El prefijo

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| apariciones de `[IDT_OPD]` | **274** | **0** | **0** |
| apariciones de `[IDT]` | 298 | 306 | 382 |
| `RESOURCE_IDT_OPD` | sí (`0x43c9c461`) | sí (offset `0x761b67`) | sí (offset `0x865d61`) |
| `IDT_OPD_TOP_Sync_OPDAcquire` | sí | sí | sí |

→ **la A7S y la A6300 tienen la instancia OPD (recurso + comandos) pero no la etiquetan.**
La diferencia de instrumentación es, por tanto, **de etiquetado**, no de funcionalidad.

### 9.2 Comparación texto a texto (sin el prefijo)

| | valor |
|---|---|
| mensajes de la A6000 (`[IDT_OPD]`, texto tras el prefijo) | 274 |
| mensajes de la A7S (`[IDT]`, texto tras el prefijo) | 306 |
| **comunes** | **270** |
| solo en la A6000 | 4 |
| solo en la A7S | 36 |

**Solo en la A6000 (4)** — los cuatro son *reformulaciones* de mensajes que sí están en la A7S:

| A6000 | A7S (equivalente) |
|---|---|
| `: Sync rate %d -> %d use:%d mode:%d %d %d` | `: Sync rate %d -> %d, %d use:%d mode:%d %d %d` |
| `: det:xs:%d xe:%d ys:%d ye:%d ` | `: det:xs:%d xe:%d ys:%d ye:%d fix %d` |
| `: test %d %d %d %d %d %d %d %d %d %d` | `: test %d %d %d / %d %d %d %d %d %d %d %d` |
| `: test2 %d %d %d %d %d %d %d %d` | `: test2 %d %d %d / %d %d %d %d %d %d %d %d` |

**Solo en la A7S (36)** — la A6000 los tiene en otra forma o directamente no los tiene:

*Canal FOPD/PBL por canal (16)*: `: PBL SET_FUNC ERROR. R0./W0./W1./W2.`,
`: PBL SET_LOOP ERROR. R0./W0./W1./W2.`, `: PBL AIF_START ERROR. R0./W0./W1./W2.`
→ en la A6000 existen como `[IDT_OPD]: PBL SET_FUNC_ERROR R0 only` (`0x43cf19c1`) y
`[IDT_OPD]: PBL START_ERROR R0 only` (`0x43cf1a09`), **además** de las variantes por canal
`[IDT]: PBL SET_FUNC ERROR. R0.` etc. en `0x43cfc03f`–`0x43cfc1df`.

*Resto (20)*: `## Error : MemMgrWrapper::Free()/Open()/Close()`, `## Error : No Space to shift`,
`AF_param not correct! %d %d`, `Can't Get Work Mem`, `Cannot Get CapWork MEM`,
`IDT : Init NG : address = %x`, `IDT Async FOPD Sem Get error %x %x %d`,
`IDT Async FOPD Sem Rel error %x %x`, `KICK FOPD %d %d`, `LC force prohibited`,
`NSX BackUp check.`, `RDRAW can't work 8pix/clk %d`, `RDRAW_param not correct! %d %d`,
`Unknown VATR aspect %d`, `addres: %x size: %d`, `arc_target:xs:%d xe:%d ys:%d ye:%d `,
`calc_miniraw cycle err %d %d`, `test %d %d %d / …`, `test2 %d %d %d / …`,
`r0:%02X r1:%02X r2:%02X w0:%02X  [FOPD]r0:%02X w0:%02X w1:%02X w2:%02X  [PRC]r0:%02X w0:%02X`.

**A6300 fw2.01:** 382 mensajes `[IDT]`, **270** comunes con la A6000, 112 propios. La A6300
(que lleva un imager distinto) renombra el bloque de mapas como
`IDT_OPD_AFMAP_InitAfmap_lower` / `…FreeAfmap_lower` / `…StealDepthMovie` y añade
`IDT_OPD_TOP_FastScanFOPD_Acquire error!` — **nunca** usa el prefijo `[IDT_OPD]`.

**Conclusión del diferencial (VERIFICADA):** la A6000 fw3.21 **no tiene un módulo de mapas
nuevo**; tiene la **misma lógica IDT que la A7S**, instrumentada **por duplicado** con el
prefijo `[IDT_OPD]` para la instancia OPD. El conjunto de mensajes es casi el mismo
(270 de 274_common; 4 reformulaciones; 36 mensajes propios de la A7S, 20 de los cuales son
variantes por canal o reescrituras de mensajes que la A6000 sí tiene con otro texto).
**NO VERIFICADO**: por qué la fw3.21 de la A6000 decide etiquetar la instancia OPD y la A7S
no (y si es una decisión de compilación por producto).

## 10. NO VERIFICADO / abierto

1. **Qué hace la instancia OPD que no hace la instancia `IDT`** (mismo recurso y mismos
   comandos en las tres cámaras, pero distinto etiquetado).
2. **Layout completo** del elemento LC de 0x60 bytes y del array de `waku` de 0x8c bytes.
3. **Formato y tamaño en bytes** de cada mapa (`4cmap`, `histmap`, `summap`, `shade_map`,
   `imgmap`, `refmap`, `backImgData`): el firmware solo valida que el puntero no sea nulo y
   comprueba la geometría (`imgwidth`/`imgheight`/`aspect`); el contenido no se nombra.
4. **Significado** de `tar_num`, `isSpectRef`, `isMapOut`, `r/g/b val.high|low`,
   `msain0/1`, `msaout`, `ie_in/ie_out`, `p_img_map`, `p_backImgData`, `mapRC_in`,
   `kido_th`, `ratio_wak`, `sel_hist/sel_sum/sel_wak/sel_waku`, `lc_waku`, `intWak`,
   `histWak`, `cwaku`, `gle`, `SGC`, `IDTSA`.
5. **Quién consume finalmente** los mapas (el DFE / motor de imagen): no hay ninguna traza
   en `av-cam.bin` que los nombre; el acceso es por puntero.
6. Si la **tabla de 11 offsets** en `0x43cf2740` (`04 08 0c 10 15 1b 20 24 28 2c 30`)
   pertenece a `CCinitParam` o es un artefacto de la disposición de la tabla.
7. El **significado de los identificadores** `arg0=6`, `arg1=2`, `arg2=1` del emisor de
   mensajes `0x439f80b8` (¿módulo? ¿comando?).
8. El **recuento de sitios** depende de la regla (725 con la canónica inerte, 356 con la kill
   analysis corregida); el **conjunto de cadenas referenciadas (271 de 274) es estable** en
   ambas reglas.

## 11. Revisión del agente principal

*(vacío — pendiente de revisión)*

## 12. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter

# tabla de referencias PIC (kill analysis, barrido global; ≈6 min)
.venv/bin/python analysis/s106_imaging_cap/scan_pic_refs_v2.py \
    0x43541000 0x44017000 /tmp/opencode/pic_refs_v2.json

# extracción del módulo + diferencial
.venv/bin/python analysis/s120_idt_opd/scan_idt_opd.py
.venv/bin/python analysis/s120_idt_opd/build_idt_opd_json.py

# estructuras de bloque (desensamblado + rastreador de registros)
.venv/bin/python analysis/s120_idt_opd/block_fields.py 0x439e80c8 0x439ee7e8 0x439f85d4
.venv/bin/python analysis/s120_idt_opd/map_block_layout.py

# clasificación de sitios por canal
.venv/bin/python analysis/s120_idt_opd/classify_sites.py

# barrido PIC restringido al módulo (reproduce el canónico y añade la kill corregida)
.venv/bin/python analysis/s120_idt_opd/scan_idt_code_pic.py 0x439d0000 0x43a09000 \
    /tmp/opencode/s120_pic.json
S120_NO_DETAIL=1 .venv/bin/python analysis/s120_idt_opd/scan_idt_code_pic.py \
    0x439d0000 0x43a09000 /tmp/opencode/s120_pic_canonico.json

# tests
.venv/bin/python -m pytest tests/test_s120_idt_opd.py -q
```

### Ficheros de este hito

| fichero | contenido |
|---|---|
| `idt_opd.md` | este informe |
| `idt_opd.json` | datos estructurados (274 trazas, mapa función→traza, sub-bloques, estructuras, diferencial) |
| `scan_idt_opd.py` | extracción de trazas + mapa función→traza + diferencial |
| `scan_idt_code_pic.py` | barrido PIC restringido al código del módulo; reproduce el canónico y permite la kill analysis **corregida** (§5.1) |
| `build_idt_opd_json.py` | genera `idt_opd.json` |
| `classify_sites.py` | reparte los sitios por canal (mensajería vs consola) |
| `block_fields.py` | extrae (cadena, base, offset) → estructura de los bloques |
| `map_block_layout.py` | layout del bloque de 18 punteros |
| `disasm_thumb.py` | desensamblador Thumb mínimo |
| `strings_raw.json`, `func_map.json`, `summary.json` | salidas intermedias |
| `sites_by_callee.json` | sitios con su callee |
| `block_fields.json`, `map_block_table.json` | tablas de campos |

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado:**

1. **Recuento**: 274 apariciones del token `[IDT_OPD]` → **273** cadenas que *empiezan* por él
   (la 274.ª es anidada: `' $(,0[IDT_OPD]: CCinitParam addr null'`). 274 textos distintos.
2. **Gemelos `[IDT]`**: los 274 mensajes `[IDT_OPD]` van seguidos, byte a byte y separados por
   NUL, de su gemelo `[IDT]` → el etiquetado es la **única** diferencia con la A7S.
3. **`IDT_OPD` no es una sigla inventada**: es el nombre de un **recurso del `SyncResMgr`**
   (`RESOURCE_IDT_OPD` `0x43c9c461`, presente también en la A7S) y de **comandos**
   (`IDT_OPD_TOP_Sync_OPDAcquire` `0x43c9c2fc`, `IDT_OPD_TOP_Sync_SetFOPD`).
4. **Diferencial**: 0 trazas `[IDT_OPD]` en la A7S (306 `[IDT]`) y en el A6300 (382 `[IDT]`);
   270 de los 274 mensajes son comunes texto a texto y 4 son sólo de la A6000; 36 son sólo de la
   A7S (16 del tipo `PBL … ERROR. R0./W0./W1./W2.`).

**Corrección de una herramienta del repo (importante):** el subagente encontró que la *kill
analysis* de `analysis/s106_imaging_cap/scan_pic_refs_v2.py` **estaba inerte**: no tenía
`md.detail = True` (con `detail` apagado, `ins.operands` lanza `CsError` y la comprobación
devolvía siempre `False`, es decir, no mataba nada) y además mapeaba los registros con
`op.reg & 0xF`, inválido en Capstone (`ARM_REG_R0 = 66`, así que `& 0xF` confunde r1 con r3).
**Corregido** (detail activado + mapeo explícito `_reg_index`). Con la corrección, la kill
analysis **coincide con la regla estricta** en el conjunto de cadenas referenciadas y en los
recuentos de sitios de los módulos con verdad medida a mano (`[SFRA]` 118, `[AIP]` 37,
`[TRK]` 288) y solo elimina los sitios falsos de las reglas más laxas. La regla canónica sigue
siendo la estricta; la kill analysis corregida queda como herramienta de auditoría. Detalle en
`analysis/s106_imaging_cap/pic_xref_methodology.md` §3.1.
