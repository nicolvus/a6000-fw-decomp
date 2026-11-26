# FILM-PB-1/sub — Qué tocan exactamente los parches de código del `av-cam` del CFW (26-11-2026)

Informe de análisis estático. No se ha tocado la cámara, no se ha instalado nada.
Evidencia: `reports/evidence/film-pb-1-sub-avcam-parches-20261126/`.

## 0. Respuesta en una línea

**NO**: ninguno de los 25 parches de código del `av-cam` (más 2 cuevas de código) cae en el
códec, el muxer, el decodificador, el control de *framerate*/resolución ni en el marco IFO de
reproducción. Todos están en la cadena de **color/gamma/APC** o en el **transporte de ajustes
de captura**. La reproducción se rompe en `libObj`/`libmpr` (IFO), no aquí. Las dos salvedades que sí
podrían morder están en §5 y ninguna sostiene el síntoma actual (§6).

## 1. Método y comprobación de direcciones (el aviso de VA)

1. `av-cam` instalado = `build/cfw_func393/pp/base-film.tar` → `0700_part_image/dev/nflasha3`
   → TPZL (`scripts/e25_27/tpzl.py`) → FAT16 (`fatimg.py`) → `AV-CAM.BIN`. Es determinista y
   da siempre el mismo binario (SHA-256 en `00-leer.txt`).
2. Se compara byte a byte con el `av-cam.bin` de fábrica 3.21.
3. **VA = 0x43541000 + desplazamiento**. Comprobado: `analysis/av-cam-analysis-view.elf` tiene
   una sola sección `.text` en VA `0x43541000`, fichero `0x1f0`, tamaño `0xAE5DA4` = el
   binario entero ⇒ la correspondencia offset↔VA es exacta y **todos** los VA de este informe
   caen dentro de `.text` (`0x43541000..0x44026DA3`). Aquí **no** hay que restar `0x10000`:
   esa corrección es del ELF de `libmpr`, no de este.

## 2. Cifras medidas (y corrección de las del enunciado)

| Medida | Valor |
|---|---|
| bytes distintos 3.21 → instalado | **34 013** |
| tramos exactos de bytes distintos (sin tolerancia) | **659** |
| rangos si se unen huecos ≤ 16 B (la cifra «33» del informe anterior) | 33 |
| sitios lógicos (un parche = un sitio) | **33** (25 de código + 2 cuevas de código + 6 de datos) |
| bytes «integrados» (3.21 → base del CFW, sin PP) | **233 B en 24 tramos** |
| bytes de los parches PP/S-Log3/B&N/Silent (base → instalado) | **33 780 B en 635 tramos** |

Corrección al enunciado: el av-cam instalado no lleva «40 B integrados», lleva **233 B**.
El «~40 B» encaja con el parche E25-24 solo (selector EFCS: 51 B distintos), pero la base
instalada lleva además los **tres estados** (`patch_tristate`) y el gancho **Silent r5**
(`patch_silent_r5`): 8 sitios, 233 B. Y las tablas no son «~32 084 B»: son **32 437 B de
curvas** + **1 164 B de código nuevo** en las cuevas D4/D5 + **72 B de ganchos** + **107 B de
datos** (punteros, selectores, matrices) = 33 780 B.

## 3. Lista EXACTA de los sitios de código

Convenio: VA, bytes distintos (no el *span*), y la función que los contiene. Los tramos
exactos de bytes, uno a uno, están en `01-diff-321-vs-cfw.txt`; el desensamblado lado a lado
de cada sitio, en `desasm/`.

### 3.1 Integrados (ya venían en la base del CFW; 233 B)

| # | VA (bytes) | B | Función / sitio | Qué hace |
|---|---|---:|---|---|
| T1 | `0x43841472..0x43841487` | 16 | `0x43841070`, constructor del paquete `0x0c` de la foto (llamado desde `CaptureUtilityModuleAPI` `0x437f87ac`) | `and r0,r0,#3` / `and r1,r1,#1` (EFCS fijo) → `ldrb.w r3,[sb,#0x41d]` + extracción de bits reescrita (`lsls r0,#30; lsrs r0,#27` = `(r0&3)<<3`); el byte `pkt[0x0e]` pasa a ser el estado **electrónico** |
| T2 | `0x4384219E` | 1 | idem (`0x43842158`) | lector Sony `ldr.w r1,[r7,#0x41c]` → `ldrb.w` (compara `==1`) |
| T3 | `0x43842270` | 1 | idem | idem para `r2` |
| T4 | `0x43845F2E..0x43845FA3` | **83** (en 118 B) | `0x43845840` (llamado por `0x43a8e694`) | copiador de ajustes a `cap+0x41c/0x41d`: añade `cap+0x41d = [ajustes+0x238]` (Silent) y **quita 5 recargas `ldr r3,[r5]`** para ganar sitio |
| T5 | `0x438C82FE..0x438C8301` | 4 | `0x438C828C`, paso 0 de la secuencia de foto | `bl 0x436d6118` (imager) → cueva |
| T6 | `0x43FB7E00..0x43FB7E69` | 103 | cueva de T5 | repite `bl 0x436d6118`; si `[0x43EDF8BC]==1` lee Tv de ajustes, limita a `0x1400..0x1e00`, lo pasa a µs (`0x4382fa94`) y escribe `cap+0x64c` y `cap+0x655=0` |
| T7 | `0x438D01A2` | 1 | `0x438D0064` (`CaptureUtilityCAIF.cpp`), constructor del envío | `cbnz r6` → `0x438d01aa` |
| T8 | `0x438D01AA..0x438D01C1` | 24 | idem | `pkt[0x0e] = [0x43EDF684+0x238]` (Silent en vivo) |

### 3.2 Parches del proyecto — color/gamma (17 sitios, 72 B de ganchos)

| # | VA (bytes) | B | Función | Qué hace |
|---|---|---:|---|---|
| P1 | `0x437A2728..0x437A2743` | 24 (en sitio) | `0x437A24FC`, `CAMERA_MAIN_CC` («LUT Write Cnt»), llamado por `0x43aeb654` (sus ancestros llevan cadenas `[CAMERA_MAIN_CC] ExtractCaptureData()`/`AfterOPDAfterNR()`; grafo aproximado, §7) | monocromo = `(tipo Color Mode == 8)` en vez de `caps[3]&2` **y** saturación < −7. Cadenas: `LUT Write Cnt:%d`; constantes `#8`, `ctx+0x31`, `ctx+0x88` |
| P2 | `0x437A44D2` | 1 | `0x437A44D0`, buscador de **conjuntos de deltas** de color (7 llamadores) | `cmp r1,#0x18` → `#0x1a` (acepta los conjuntos 0x18/0x19) |
| P3 | `0x437A44FA` | 4 | idem | `cmp r4,#0x18 / beq` → `b.w 0x43FB74D0` (cueva de deltas) |
| P4 | `0x437A4B42` | 1 | `0x437A4B40`, buscador de **matriz 3×3** (3 llamadores) | `cmp r1,#0xf` → `#0x11` |
| P5 | `0x437A4B62` | 4 | idem | `cmp r1,#0xf / beq` → `b.w 0x43FB7490` (cueva de matrices) |
| P6 | `0x437A4DB2` | 4 | `0x437A4CD4`, `switch` id de Color Mode (TBH de 0x15 casos) | caso por defecto `bhi.w 0x437a4f7e` → `b.w 0x43FB7450`: si id==0x17 → matriz 0x10/conjunto 0x19; si id==0x18 → matriz 0x11/conjunto 0x19; si no, al caso por defecto original |
| P7 | `0x437AA816` | 1 | `0x437AA65C` (`CAMERA_MAIN_CC`), tabla tipo→id de Color Mode | `cmp r0,#6` → `#0xa` (7 → 11 tipos) |
| P8 | `0x437AAFE0` | 3 | `0x437AAA78` | literal `0x004FBED0` → `0x0080CBDE`: apunta a la tabla de tipos de la cueva `0x43FB7400` |
| P9 | `0x43802B64` | 4 | `0x43802B14`, módulo `Function/FunctionSetParam.cpp` (CAM_FUNC_MGR) | `ldrb.w r2,[r0,#0x35]` → `b.w 0x43FB7528`: copia `msg[0x17..0x26]` del LIRO `0x4066` al snapshot `pp` |
| P10 | `0x43853226` | 4 | `0x43853200`, constructor de la LUT de 96 puntos (llamado por `0x43854718`, `0x43854a28`, `0x43854f78`; 3 niveles arriba: `YC::api_YC_SetSaCamDsp`, `ModuleAPI_SA_Develop`) | `ldr.w r3,[r3,r1,lsl#2]` → `bl 0x43FB7550` (tramplín → `pp_curve`) |
| P11 | `0x4385392E` | 4 | `0x438538E4`, idem | idem → `0x43FB7564` |
| P12 | `0x43853C8E` | 4 | `0x43853C70`, idem | idem → `0x43FB7578` |
| P13 | `0x4386783A` | 1 | `0x4386781E`, clase de proceso por gamma | `cmp r5,#2` → `#3`: en modo `[+0x193]`=2, 0x14..0x17 comparten rama |
| P14 | `0x43867924` | 1 | `0x438678AC`, selector de clase por gamma (TBH de 0x1c casos) | `blo 0x4386794c` → `blo 0x43867932`: la gamma 0x17 (S-Log3) cae en la clase de S-Log2 |
| P15 | `0x438B172C` | 4 | `0x438B11F0` (cadena `SHD::job_YC_SetParam`, `CAMERA_MAIN_YC`) | literal GOT `0x000073A0` → `0xFFF903AC` = `0x43FAF290 − GOT` (`GOT=0x4401EEE4`): la lectura de la bandera Hi-Light pasa a una tabla propia con `T[0]=1` |
| P16 | `0x438B336E` | 4 | **`Camera::YC::job_apc_coring_stl`** (`0x438B3298`) | `add.w r4,r7,#0x760` → `bl 0x43FB75A0` (tramplín que repite la instrucción y llama a `pp_coring`) |
| P17 | `0x438B3D52` | 4 | **`Camera::YC::job_apc_gain_stl`** (`0x438B37CE`) | `add.w r6,r5,#0x760` → `bl 0x43FB758C` (tramplín → `pp_gain`) |

### 3.3 Tablas, datos y cuevas (8 sitios, 33 708 B)

| # | VA | B distintos | Qué |
|---|---|---:|---|
| D0 | `0x43FB7400..0x43FB744F` | 49 | datos de color: tabla tipo→id de 11 entradas, matrices S-Gamut3 (9×s16) y S-Gamut3.Cine, deltas de 24 B |
| D1 | `0x43BC868C` | 1 | tabla de clase por gamma: `[0x17] 0 → 8` (igual que S-Log2 0x14) |
| D2 | `0x43CB56EA..0x43CB56FD` | 17 | tabla selector→gamma (13 entradas de 2 B): 0x17/0x17, 0x16/0x16, 0x18..0x1b, 0x14/0x15 |
| D3 | `0x43FAF290..0x43FAF2B3` | 9 | datos de Hi-Light de la cueva (puntero a `T` + `T[0]=1`, `T[0x1b..0x1f]=0,6,12,18,24`) |
| D4 | `0x43FB7450..0x43FB74EF` | 132 | cueva de código del switch/matrices/deltas de Color Mode |
| D5 | `0x43FB7528..0x43FB7981` | 1032 | cueva de tono: gancho asm del `0x4066` + `pp_curve` / `pp_gain` / `pp_coring` compilados (`pp_tone.bin`, 969 B) |
| D6 | `0x43FAF300..0x43FB73FF` | 32 437 | 8 curvas de gamma de `0x101A` B (0x16, 0x18–0x1b, 0x14, 0x15, 0x17) |
| D7 | `0x440014A8..0x440014E3` | 31 | punteros de curva escritos en la tabla `0x44001404` (índices 0x14..0x17 y su modo vídeo) |

## 4. ¿Hay algún parche en código de vídeo?

**No.** El mapa de módulos (`06-modulos.txt`) sitúa el vídeo muy lejos de todos los sitios:

| Ventana | Contenido | Bytes parcheados |
|---|---|---:|
| `0x435C–0x435D` | `McAvcDecVDisplayBase`, `McAvcDec60I50IVDisplay` (decodificador + presentación) | **0** |
| `0x4360–0x4361` | `cdcMgr/cdcMgrEnc/*` (gestor del códec), mux/MP4 | **0** |
| `0x4390–0x4391` | `video/enc/avcEncVideoStateIdle.cpp`, `video/dec/avcDecVideoZimaAccessor.cpp`, `MojitoAvcEncoder` | **0** |
| `0x4392` | `MpgPinConverter` (mux de *pins*) | **0** |
| `0x4393` | `pcpCtrl` (control de presentación) | **0** |
| `0x4394–0x4395` | `RcDriver`/`api_rc`/`RcResize` (escalado y resolución) | **0** |
| `0x4398` | `nalSepTop/nalSepApp` (separador NAL) | **0** |

Las únicas ventanas con bytes distintos son `437a 4380 4384 4385 4386 438b 438c 438d
43bc 43cb 43fa 43fb 4400` (`08-ventanas.txt`).

Matiz importante y honesto: **sí hay parches que afectan a la imagen que se graba en vídeo**.
La tabla de curvas se indexa `TAB[gamma·2 + modo]` con **modo 1 = vídeo**, y la tabla
selector→gamma y la de clases por gamma se usan igual al grabar. Es decir: P7/P8/D1/D2/D6/D7
y los tramplines de LUT (P10–P12) **sí** pueden cambiar el aspecto del vídeo grabado. Lo que
ninguno toca es el *contenedor*, el *encoder*, el *decoder* ni el *framerate*.

El único byte dentro de una ventana que también contiene cadenas de códec es `0x43CB56E6`
(tabla D2). No es código: es una tabla de 2 B por entrada (`000a 000a …`), y sus vecinos son
datos y cadenas de `CAMERA_MAIN_YC`, no instrucciones.

## 5. Riesgos reales de estos parches (lo que sí podría romper algo)

1. **El hueco de 40 020 B** `0x43FAF28C..0x43FB8EDF` es el destino de las 8 curvas y de las
   cuevas D0/D3/D4/D5. En 3.21 está **todo a cero** y no tiene referencias válidas: las 5
   coincidencias de 32 bits dentro del rango (`07-hueco.txt`) son bytes de datos o de código
   mal alineado, no punteros (comprobado desensamblando `0x4365F814`, `0x436E2CDE`,
   `0x439EE6FA`, `0x43FCFF7A`, `0x43FF0012`). Conclusión: **no se pisa código ni datos de
   fábrica**. Lo que no se puede demostrar en estático es que el cargador o el *heap* del
   núcleo no usen esa RAM en ejecución; si la usaran, se corromperían curvas y cuevas →
   Picture Profile mal o salto a basura **con PP activo**, no un fallo de reproducción.
2. **T4 (118 B de span, 83 B distintos; el «112 B» del enunciado es el tramo unido) asume que `[r5]` no cambia** entre las 6 lecturas que el original repetía
   (`ldr r3,[r5]` ×6 → ×1). Si el puntero cambiara a mitad, el bloque de ajustes de captura
   quedaría con campos viejos. Afecta a la captura; no al IFO.
3. **P9 se ejecuta en el desempaquetador del `0x4066`** (arranque/ajustes): un fallo ahí sería
   global, no «sólo reproducción».
4. **`pp_curve` es no-op con PP por defecto**: `if (!orig || !sel) return orig;` y `pp` está a
   cero hasta que llega el `0x4066` ⇒ sin PP activo los tres tramplines devuelven el puntero
   original.

## 6. Conclusión: ¿puede alguno romper la reproducción manteniendo la foto?

**NO**, con la evidencia disponible:

1. **Reparto**: de los 34 013 B, 233 B son transporte de ajustes de captura y 33 780 B son
   color/gamma/APC + tablas. Cero bytes en el código de códec, muxer, decodificador,
   presentación, escalado o NAL (§4).
2. **El fallo está antes de decodificar**: el log del 20-10 muestra que **no se carga ningún
   IFO** (`CreateAndLoad Error` en AVCHD/XAVC/MP4) y que `StreamCache::SetArea` se pide con
   tamaño 0. Eso ocurre en el marco IFO (`libObj`/`libmpr`), que no ejecuta nada del `av-cam`
   parcheado: si no hay metadatos de IFO, no hay ni miniatura ni reproducción — que es
   exactamente el cuadro observado (miniatura de foto sí, de vídeo no).
3. **El `av-cam` de vídeo es byte a byte el de fábrica**: 0 bytes distintos en `0x435C–0x4361`
   y en `0x4390–0x4398`.
4. **Los parches de imagen sólo cambian valores con PP activo** (§5.4).

Salvedades (no sostenidas por la evidencia, pero medibles en una sesión con cámara):

- Si el hueco de 40 KB fuera memoria viva del decodificador, el síntoma sería distinto
  (curvas/cuevas corruptas, no «ningún IFO cargado»). Comprobación barata: leer
  `0x43FAF290` y `0x43FB7528` en RAM al arrancar y después de intentar reproducir; si cambian,
  el hueco está vivo.
- Si la reproducción usara el mismo constructor de LUT con PP activo, el vídeo se vería mal,
  pero seguiría reproduciendo (no explica `0x1A`/IFO).

Por tanto el siguiente paso no está en `av-cam`: sigue en el marco IFO / `AviMMgr`
(`film-pb-1-sub-ifoframework-20261126.md`, `film-pb-1-sub-decodificador-20261128.md`).

## 7. Límites de este informe

- El grafo de llamadas sale de `BL`/`BLX` directos verificados con capstone; los llamadores
  **indirectos** (tablas de despacho LIRO) no se enumeran: P9, T4, T6, D4 y D5 no tienen
  llamador directo verificado.
- «No hay referencias al hueco» es cierto para referencias de 32 bits alineadas; un cálculo
  de dirección por suma de offsets en ejecución no se puede descartar en estático.
- No se ha ejecutado nada en la cámara (por indicación expresa).

## 8. Ficheros

- `reports/evidence/film-pb-1-sub-avcam-parches-20261126/00-leer.txt` — entradas y SHA-256.
- `…/01-diff-321-vs-cfw.txt` — 659 tramos exactos.
- `…/02-diff-321-vs-base.txt`, `…/03-diff-base-vs-pp.txt` — el reparto integrados / PP.
- `…/04-sitios.tsv`, `…/sitios.json` — los 33 sitios con sus tramos exactos.
- `…/05-funciones.tsv` — función contenedora, llamadores verificados y cadenas.
- `…/06-modulos.txt`, `…/08-ventanas.txt` — mapa de módulos y ventanas tocadas.
- `…/07-hueco.txt` — tramos a cero y referencias al hueco de 40 KB.
- `…/desasm/` — desensamblado lado a lado de los 27 sitios de código (25 en sitio + 2 cuevas).
- `…/scripts/` — herramientas usadas (`atlas.py`, `avcdis.py`, `callers.py`, `sites.py`, …).
