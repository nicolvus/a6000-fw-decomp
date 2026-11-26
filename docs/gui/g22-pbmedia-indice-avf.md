# G22-PBMEDIA — el modelo de contenidos de la reproducción: formato de `AVF_INFO`, generador de tarjeta y el eslabón medido

**Estado (26-11-2026, sesión G22-PBMEDIA, sin cámara): PARCIAL con el eslabón nuevo medido.** Se ha deducido y
documentado el **formato de `AVF_INFO\AVIN0001.INP`** con bytes y direcciones (§2), se ha escrito el **generador**
`SD_MEDIA=1` que mete en la imagen FAT32 una **foto JPEG real con EXIF** y un **índice coherente con ella** (§3, con
tests sin QEMU), y se ha **medido en el invitado** que con esa tarjeta el modelo sigue en **0** (§4). Pero el motivo
**no** es el contenido del índice: en los tres arranques medidos el invitado **no llega a leer ni un sector de datos**
de `AVF_INFO` (traza `SDIO`, §4.2) y `Fsys_FindFirst` (`libmpr+0x13e474`) **no se dispara ni una vez**. El eslabón
medido está antes: la secuencia de arranque del medio (`DefObjMedia`) **rechaza la tarjeta 1 s antes de que se monte**
—`SetInhStatus() [INH_INVALID_INFO_FS]` → `ChangeInhFactors(177)` → `RejectMedia()` a los **65,03 s**, y `FsysMount
/dev/mmca` recién a los **65,98 s** (`ClearInhStatus [INH_INVALID_INFO_FS]` a los 66,26 s)—(§4.1).

Direcciones = **VA del ELF** de `libmpr.so`/`libObj.so` 3.21 (en `libmpr`, REA/Ghidra = VA + 0x10000). Se etiqueta
**V** = verificado en bytes/instrucciones · **M** = medido en el invitado · **D** = deducido · **NV** = no verificado.
Evidencia: [`reports/evidence/g22-pbmedia-20261126/`](../../reports/evidence/g22-pbmedia-20261126/).

---

## 1. Lo que ya estaba medido (no se repite) y lo que añade esta sesión

De [`g22-pbvista-carga-bajo-demanda.md`](g22-pbvista-carga-bajo-demanda.md): `O view/INDEX_PLAYBACK 0` carga
`viewUnified3.so` y la vista pide `getModelInfo(@M00A = model/MEDIA, 0) -> 0`, `(…, 64) -> 0`, con `model/ROOT, 6 -> 1`;
la SD emulada estaba vacía y `AVF_INFO` se creaba con ficheros de 0 B. De
[`film-pb-1-sub-avin`](../reports/film-pb-1-sub-avin-20261127.md): descriptor `0x80`/`0x2710` y una rejilla de registro
**deducida** (sin ningún byte real en el repo).

Lo que añade esta sesión:

| # | Resultado | Etiqueta | Dónde |
|---|---|---|---|
| 1 | El registro de `AVIN0001.INP` mide **0x80 B** y sus campos caen en **+0x00/+0x12/+0x20/+0x28/+0x2c/+0x30/+0x38** según el volcado propio de `libmpr` en `0x1de030` | **V** | §2.2 |
| 2 | El tamaño **máximo** del índice es **`0x138800` = 10 000 × 0x80**, devuelto por el *getter* `libmpr 0x6800e4` (**sin** cabecera) | **V** | §2.3 |
| 3 | El *file ID* de 16 B del descriptor (`+0x28`) **no está referenciado** por ningún literal de `.text` ni de `.data`, igual que los nombres `AVIN0001.INP/.BNP/.INT` (0 referencias en un barrido lineal del 99,8 % de `.text`) | **V** | §2.4 |
| 4 | `SD_MEDIA=1` mete una foto JPEG real (294 771 B, 1616×1080, **con EXIF**) en `DCIM/100MSDCF/DSC00001.JPG` y un `AVIN0001.INP` de **384 B = 0x100 + 1×0x80** coherente con ella | **V** (anfitrión) | §3 |
| 5 | Con esa tarjeta, `getModelInfo(model/MEDIA, 0)` sigue devolviendo **0** (a 57,8 s, 87,0 s y 103,9 s del invitado) | **M** | §4.1 |
| 6 | El medio se **rechaza a los 65,03 s**, antes de que el volumen esté montado (65,98 s): `[ObjMedia]SetInhStatus() [INH_INVALID_INFO_FS]` → `RejectMedia()` | **M** | §4.1 |
| 7 | El invitado **no lee ningún sector de datos** de la SD en 367 s: 34 lecturas, todas en el rango de la FAT (`sec=32…7968`, 256 sectores cada una) | **M** | §4.2 |
| 8 | `Fsys_FindFirst` (`libmpr+0x13e474`) **no se dispara** en 367 s con la trampa armada (`TRACELIB=libmpr.so TRACEFN2=13e474`) | **M** | §4.2 |
| 9 | Los tres arranques en frío de esta sesión se quedaron en la firma de **G22-CUELGUE** (2 listas, opacos 0,0046) | **M** | §5 |

---

## 2. Formato de `AVF_INFO\AVIN0001.INP`

### 2.1 Descriptor en `.data` (V)

`libmpr.so` lleva el descriptor del fichero en `.data` VA **`0x9d1270`** (0x50 B; el descriptor de `.INT` empieza justo
después, en `0x9d12c0`). Volcado literal (`reports/evidence/g22-pbmedia-20261126/formato-avin-estatico.txt`):

```
0x009d1270  41 56 49 4e 30 30 30 31 2e 49 4e 50 00 00 00 00  AVIN0001.INP....
0x009d1280  80 00 00 00 10 27 00 00 ff ff ff ff 01 00 00 00  .....'..........
0x009d1290  b0 04 00 00 86 00 00 00 ff 06 75 81 fa 7b e2 90  ..........u.{..
0x009d12a0  45 27 84 b0 5e 61 10 ad 46 60 02 00 00 00 00 00  E'..^a..F`......
0x009d12b0  00 01 00 00 04 00 00 00 04 00 00 00 04 00 00 00  ................
```

| offset | tipo | valor | lectura |
|---|---|---|---|
| `+0x00` | `char[16]` | `AVIN0001.INP` | nombre del fichero |
| `+0x10` | `u32` | `0x80` | **tamaño de registro** |
| `+0x14` | `u32` | `0x2710` | **nº máximo de registros** (10 000) |
| `+0x18` | `u32` | `0xffffffff` | centinela de «vacío» |
| `+0x1c` | `u32` | `1` | versión / nº de ficheros del juego |
| `+0x20` | `u32` | `0x4b0` | NV (¿tope de otra tabla?) |
| `+0x24` | `u32` | `0x86` | NV |
| `+0x28` | `u8[16]` | `ff067581fa7be920452784b05e6110ad` | **file ID** del índice (`GETAVINDEXFILEID`) |
| `+0x38` | `u32` | `0x26046` | NV |
| `+0x3c` | `u32` | `0` | NV |
| `+0x40` | `u32` | `0x100` | **candidato a cabecera de fichero** (§2.3) |
| `+0x44`/`+0x48`/`+0x4c` | `u32` | `4` | NV |

### 2.2 Registro: 0x80 B, con los offsets que lee el propio firmware (V)

`libmpr 0x1de030…0x1de110` vuelca un struct cuya base está en **`r7+0xb8`**; cada campo se pasa a la macro de traza con
su nombre `[AVI][MON]`:

```
0x1de066  ldr r2,[pc,#0x160] / add.w r3,r7,#0xb8 / …   → cDirPath        (base+0x00)
0x1de082  add.w r3,r7,#0xca   …                         → cFileName       (base+0x12)
0x1de09c  ldr.w r3,[r7,#0xd8] …                         → nFileSize       (base+0x20)
0x1de0b6  ldr.w r3,[r7,#0xe0] …                         → nWidth          (base+0x28)
0x1de0d0  ldr.w r3,[r7,#0xe4] …                         → nHeight         (base+0x2c)
0x1de0e4  ldr.w r3,[r7,#0xe8] …                         → duración (ms)   (base+0x30)
0x1de104  ldr.w r3,[r7,#0xf0] / cmp r3,#2 …             → códec (4 = AVC) (base+0x38)
```

Δ = `0xca−0xb8 = 0x12` (cDirPath) y `0xd8−0xca = 0x0e` (cFileName) ⇒ la rejilla que ya había deducido
[`film-pb-1-sub-avin`](../reports/film-pb-1-sub-avin-20261127.md) queda confirmada en instrucciones. Rejilla completa
que escribe el generador (`scripts/gui/harness/sd_media.py`):

| off | tipo | campo |
|---|---|---|
| `+0x00` | `char[0x12]` | `cDirPath` (`DCIM/100MSDCF`) |
| `+0x12` | `char[0x0e]` | `cFileName` (`DSC00001.JPG`) |
| `+0x20` | `u32` | `nFileSize` |
| `+0x24` | `u8` | `bIsValid` = 1 (**D**) |
| `+0x28` | `u32` | `nWidth` |
| `+0x2c` | `u32` | `nHeight` |
| `+0x30` | `u32` | duración ms (0 en foto) |
| `+0x34` | `u32` | duración 90 kHz (0 en foto) (**D**) |
| `+0x38` | `u32` | `emVideoCodec` (4 = AVC; 0 en foto) |
| `+0x3c` | `u32` | `emProfileIndication` (0) |

**Qué necesita el parser para aceptar una entrada** (lo que se puede afirmar con bytes): un registro de **0x80 B** con
`cDirPath` y `cFileName` en `+0x00`/`+0x12` apuntando a un fichero que exista en la tarjeta, su `nFileSize` en `+0x20` y
la geometría en `+0x28`/`+0x2c`; el total de registros sale del tamaño del fichero (no hay contador visible). **NV**: si
el parser exige además un recuento en la cabecera o un CRC.

### 2.3 Tamaño máximo y cabecera (V el número; D la consecuencia)

`libmpr 0x6800e4` es un *getter* de 8 bytes que devuelve la constante `0x138800`:

```
0x6800e4  80 b5      push {r7,lr}
0x6800e6  00 af      add  r7,sp,#0
0x6800e8  00 48      ldr  r0,[pc,#0]        ; slot 0x6800ec = 0x00138800
0x6800ea  80 bd      pop  {r7,pc}
```

`0x138800 = 0x2710 × 0x80` = 10 000 × 128 B **exactamente**, sin sumando de cabecera ⇒ argumento fuerte de que el
fichero es **un vector puro de registros** (cabecera 0). En cambio el descriptor guarda `0x100` en `+0x40`, que es lo
único parecido a una cabecera. Por eso el generador deja el tamaño de cabecera **parametrizable**
(`SD_MEDIA_CAB`, por defecto `0x100`) y el *file ID* conmutable (`SD_MEDIA_ID=0`): la próxima sesión decide con una
medida, no con una suposición.

### 2.4 Por qué el nombre del fichero no resuelve el eslabón

Barrido lineal de `.text` (99,8 % de 0x683c5c B decodificados, 2 615 201 instrucciones) buscando literales y
`movw/movt`: **0 referencias** a `AVIN0001.INP` (`0x7a912c`), `.BNP` (`0x7a9139`), `.INT` (`0x7a9160`), al descriptor
`0x9d1270` y al *file ID* (`0x7a909c` y su copia `0x9c9298`). Las que sí aparecen (p. ej. `AVF_INFO` `0x7a637f`, 10
sitios) confirman que el método encuentra xrefs normales. Es decir: el nombre del índice **no se materializa como
literal** en esta biblioteca (lo más probable: el descriptor se alcanza por una estructura intermedia y el nombre se
compone en tiempo de ejecución). Consecuencia práctica: **no se puede “arreglar” el índice desde el nombre**; hay que
medir qué lee el invitado (§4.2) o instrumentar el lector.

---

## 3. Generador: `SD_MEDIA=1`

`scripts/gui/harness/sd_media.py` (nuevo) + `sd_image.construye(..., media=True)` + una línea en `live.py`
(la del montaje de la SD, **no** la página ni su JS):

```sh
SD_MEDIA=1 .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir pbmedia --puerto 8693 --config /tmp/final/cfg.json
```

Qué mete en la imagen (mapa real de una construcción, `SD_MEDIA_MAPA=1` lo imprime):

```
{'foto': 'DCIM/100MSDCF/DSC00001.JPG', 'foto_bytes': 294771, 'ancho': 1616, 'alto': 1080, 'exif': True,
 'cabecera': 256, 'registro': 128, 'registros': 1, 'indice_bytes': 384, 'offset_registro0': 256,
 'id_indice': 'ff067581fa7be290452784b05e6110ad'}
```

* **Foto**: la primera JPEG con EXIF del repo (`analysis/camera-dumps/**`, `reports/evidence/**`; `SD_MEDIA_FOTO`
  fuerza otra): 294 771 B, 1616×1080, EXIF **sí** (se comprueba con la firma `Exif\0\0`). Si no hubiera ninguna, se
  genera una sintética y el mapa lo delata.
* **Índice**: `AVF_INFO/AVIN0001.INP` y `.BNP` **iguales** (384 B = 0x100 cabecera + 1 registro de 0x80), con
  `cDirPath`/`cFileName`/`nFileSize`/`nWidth`/`nHeight` **calculados del JPEG que se acaba de escribir** (no se
  inventan), y `AVIN0001.INT`/`PRV00001.BIN`/`STAT0000.BIN` a **0 B** (contenido real desconocido: no se inventa).
* Opt-in: sin `SD_MEDIA=1` la imagen es la de siempre (`SD_ESTRUCTURA` sigue igual). `media=True` implica la
  estructura de carpetas de `SD_ESTRUCTURA` y **sustituye** los cinco ficheros vacíos por los reales.
* `SD_MEDIA` entra en el `SHIMENV` solo como marca (`SDMEDIA=1`), para que cambiar de tarjeta **invalide el estado
  guardado** (`estado.zst` incluye la huella del `SHIMENV`) y no se restaure una VM con la tarjeta vieja.

Tests sin QEMU: `tests/test_g22_pbmedia.py` (8 casos) — offsets del registro, truncado de nombres, cabecera/recuento,
coherencia con el JPEG, foto con EXIF, cableado de `entradas()` y, si está `libmpr.so`, que el descriptor dice `0x80`
y el mismo *file ID* que escribe el generador. Más `tests/test_gui_sd_image.py` (5) siguen verdes.

---

## 4. Medido en el invitado

### 4.1 El medio se rechaza 1 s antes de montarse (M)

Perfil `pbmedia2`, puerto 8693, `SHIMEXTRA='WAITLOG=3000 WLALL=1 GMILOG=1 SDIO=20000 TRACELIB=libmpr.so TRACEFN2=13e474'`
(traza completa en [`pbmedia2-trazas.txt`](../../reports/evidence/g22-pbmedia-20261126/pbmedia2-trazas.txt)):

```
64.91  [ObjMedia]onStarting
64.95  [ObjMedia]RegistInput()
65.01  [ObjMedia]SetInhStatus() [INH_INVALID_INFO_FS]
65.01  [ObjMedia]ChangeInhFactors() factorID = 177
65.03  [ObjMedia]RejectMedia()                       <- el medio queda rechazado
65.03  [ObjMedia]SetInhStatus() [INH_MEDIA_MOUNT]
65.07  [ObjMedia]SendToAppEvent() -> MSGID_DETECT_REJECT_EVT
65.12  [ObjMedia]ChangeInhFactors() factorID = 174    <- añade INH_INVALID_INFO_FS (tabla .data libObj 0x10a76f8)
65.12  [ObjMedia]onStarting End
65.98  FsysMount /dev/mmca                            <- el volumen se monta DESPUÉS
66.26  [ObjMedia]ClearInhStatus() [INH_INVALID_INFO_FS]
66.31  [ObjMedia]FsysMountNotify()
```

El factor `174` es la entrada `{0xae, 0xdefc03, 0x200}` de la tabla `.data` de `libObj` **`0x10a76f8`** =
`INH_INVALID_INFO_FS` (V: los 12 B `ae 00 00 00 03 fc de 00 00 02 00 00`), es decir «la información del sistema de
ficheros no es válida»: a los 65 s **el volumen todavía no está montado**. El montaje posterior *limpia* el inhibidor,
pero el evento de rechazo ya se había emitido.

Y el modelo, en el mismo arranque:

```
57.83  getModelInfo(model/MEDIA, 0) -> 0
87.00  getModelInfo(model/MEDIA, 0) -> 0
88.22  getModelInfo(model/ROOT,  6) -> 1     <- el modelo de raíz sí responde
103.88 getModelInfo(model/MEDIA, 0) -> 0
```

**Nuevo respecto al repo**: el diagnóstico anterior atribuía el 0 al **contenido** del índice. Aquí el 0 aparece
**antes** de que se lea nada de la tarjeta y **también después** de montarla, con una foto real y un índice de 384 B en
su sitio.

### 4.2 El índice no se lee: ni un sector de datos, ni un `FindFirst` (M)

Dos instrumentos independientes, mismo arranque (367 s de invitado):

| instrumento | qué mide | resultado |
|---|---|---|
| `SDIO=20000` (nuevo, `sonyshim.c`) | cada lectura de sectores de `/dev/mmca` (`ioctl 0x10f`) | **34 lecturas**, sectores `32, 288, 544, … 7968` (256 sectores cada una ≈ 4 MiB de la zona de **FAT**). **Ninguna** en la zona de datos, donde está `AVF_INFO` (§3: el `file ID` del índice cae en el sector **16488**) |
| `TRACELIB=libmpr.so TRACEFN2=13e474` | entrada de `Fsys_FindFirst` | **0 disparos** (la traza sí se armó: `TRACELIB libmpr.so base 0xad3ac000` a los 46,50 s) |

Conclusión medida: en estos arranques **el camino del índice AV no se ejecuta**, así que el formato del `AVIN0001.INP`
—por muy correcto que sea— **no puede** ser todavía la causa del 0. El experimento `MEDIADELAY` (§4.3) ataca
exactamente el orden medido en §4.1.

### 4.3 Intento de invertir el orden (`MEDIADELAY`): el parche entra, el orden no se puede mover así (M)

`sonyshim.c` gana `MEDIADELAY=n`: parchea la entrada de `ObjMedia_Create` (`libObj` **0x93d2cc**; símbolo de `.dynsym`
`ObjMedia_Create` = `0x93d2cd`, bit Thumb) con `ldr.w pc,[pc,#0]` + un trampolín que **copia los 12 B del prólogo**
(`push {r3-r7,lr}; mov r6,r0; add r7,sp,#0; mov.w r0,#0x3c0; mov r5,r1`), llama a una espera **de una sola vez** y
vuelve a `+0x0c`. Objetivo: que `FsysMount` (65,98 s) llegue antes que `onStarting` (65 s).

| intento | qué pasó | evidencia |
|---|---|---|
| trampolín de 10 B (sin `mov r5,r1`) | **SEGV del invitado** (`IMEXIT im_s 139`) a los 79,96 s: la función escribía por `r5` basura | `mediadelay-intento.txt` §2 |
| trampolín de 12 B, `MEDIADELAY=4`, espera solo en la 1.ª llamada | el parche se aplica (`ObjMedia_Create en 0xae81d2cc parcheada (una sola espera)`) y la espera se toma (`62,51 s, 4 s`), pero a los **228 s** el invitado **no ha llegado ni a `onStarting` ni a `FsysMount`** (sin parche llegaban a 65/66 s) y no hay ni un fotograma | `mediadelay-intento.txt` §1 |

Lectura: dormir dentro de `ObjMedia_Create` **no es un retardo inocuo** — esa llamada está en el camino de arranque del
contador/MPR y bloquea la secuencia que se quería adelantar. El orden `montaje → onStarting` hay que conseguirlo por
otra vía (adelantar el montaje, o una espera fuera de `ObjMedia_Create`), no durmiendo ahí. **No se ha demostrado**
que el rechazo temprano sea la causa del 0; sigue siendo la hipótesis con más apoyo (§4.1).

---

## 5. Límites de la sesión

### 5.1 Los tres arranques en frío se quedaron en la firma de G22-CUELGUE (M)

| perfil | `SHIMEXTRA` | `/estado` a los ~150 s | lecturas de datos de la SD |
|---|---|---|---|
| `pbmedia1` | `WAITLOG=3000 WLALL=1 GMILOG=1 SDIO=20000` | 2 fotogramas · 2 listas · **opacos 0,0046** | ninguna |
| `pbmedia2` | + `TRACELIB=libmpr.so TRACEFN2=13e474` | 2 fotogramas · 2 listas · **opacos 0,0046** | ninguna |
| `pbmedia3` | `GMILOG=1 SDIO=20000` | 2 fotogramas · 2 listas · **opacos 0,0046** | ninguna |

Es la misma firma que [`g22-cuelgue-navegacion.md`](g22-cuelgue-navegacion.md) y que §8 de
[`g22-pbvista-carga-bajo-demanda.md`](g22-pbvista-carga-bajo-demanda.md): **el arranque no llega a pintar la OSD**. Se
borró `live/<perfil>` entre intentos (los tres son arranques en frío de verdad) y aun así no pintó ninguno; con dos
`qemu-system-arm` en la máquina (el otro agente) el invitado va a ~1/3 de velocidad, lo que alarga todo.

### 5.2 Qué NO se ha podido afirmar

* Que `getModelInfo(model/MEDIA, 0)` devuelva **1**: no se ha dado el caso (§4.1).
* Que la rejilla de `view/INDEX_PLAYBACK` se pinte: no hay OSD (§5.1) y el modelo está en 0.
* Si la cabecera del índice es `0`, `0x100` u otra: hay dos indicios contradictorios (§2.3) y ninguna lectura medida
  de la que deducirlo.
* El significado de `+0x24`, `+0x34`, `+0x3c` del registro, de `0x4b0`/`0x86`/`0x26046` del descriptor y del formato de
  `.INT`, `PRV00001.BIN` y `STAT0000.BIN`: siguen **NV**; el generador los deja a 0 B o a cero.

### 5.3 Siguiente paso concreto

1. Conseguir que el **montaje preceda a `onStarting`** con un mecanismo que no duerma dentro de `ObjMedia_Create`
   (§4.3): o adelantar el montaje (la traza `MediaMount /dev/mmca` marca el disparo), o esperar **fuera** de esa
   llamada (p. ej. en el hilo que la invoca). Si `FsysMount` precede a `onStarting`, comprobar si desaparece
   `RejectMedia()` y si `getModelInfo(model/MEDIA, 0)` pasa a 1.
2. Si sigue en 0 con el medio aceptado, repetir el arranque con `SDIO=20000` y buscar lecturas en el sector del
   índice (el generador imprime su sector: `mdir` + `img.find(ID)`); con eso se decide la cabecera (`SD_MEDIA_CAB=0`
   frente a `0x100`) sin adivinar.
3. Si el medio se acepta pero el índice no se lee, el siguiente eslabón es quién dispara el lector
   (`CS_AviFileIf`: `smf_avi_*` en `libmpr 0x1d13xx`, `IsExistAVIndexDirectory` con xref en `0x13c0e8`).

---

## 6. Comandos reproducibles

```sh
# formato: descriptor, getter del tamaño máximo y campos del registro
cd analysis/gui/g22/harness/stage/cam/usr/lib && python3 - <<'PY'
import struct, capstone
D=open('libmpr.so','rb').read()
o=0x9bb1c8+(0x9d1270-0x9c31c8)                       # VA→offset del 2.º PT_LOAD
print(D[o:o+0x50].hex(' '))                           # descriptor de AVIN0001.INP
md=capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
print([f'{i.mnemonic} {i.op_str}' for i in md.disasm(D[0x6800e4:0x6800ec],0x6800e4)])   # getter 0x138800
PY

# generador: mapa de lo que se mete en la tarjeta
SD_MEDIA_MAPA=1 .venv/bin/python -c "
import sys; sys.path.insert(0,'scripts/gui/harness')
import sd_media, tempfile, pathlib
print(sd_media.construye(pathlib.Path(tempfile.mkdtemp()) / 'sd'))"

# imagen + contenido, sin QEMU
.venv/bin/python - <<'PY'
import sys; sys.path.insert(0,'scripts/gui/harness')
import sd_image, sd_media, pathlib
t=pathlib.Path('/tmp/pbmedia'); t.mkdir(exist_ok=True)
sd_image.construye(pathlib.Path('/nonexistent'), t/'sd.head', 4.0, media=True)
d=(t/'sd.head').read_bytes(); print('sector del AVIN0001.INP:', d.find(sd_media.ID)//512)
PY
MTOOLS_SKIP_CHECK=1 mdir -i /tmp/pbmedia/sd.head -/ ::/AVF_INFO

# invitado (con la máquina libre de otros qemu)
SD_MEDIA=1 SHIMEXTRA='WAITLOG=3000 WLALL=1 GMILOG=1 SDIO=20000' \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir pbmedia \
  --puerto 8693 --config /tmp/final/cfg.json
grep -a 'ObjMedia\]onStarting\|RejectMedia\|ClearInhStatus\|FsysMount /dev/mmca\|getModelInfo(model/MEDIA' \
  analysis/gui/g22/harness/live/pbmedia/shim.log
grep -ac 'SDIO rd' analysis/gui/g22/harness/live/pbmedia/shim.log
curl -s http://127.0.0.1:8693/estado
curl -s -X POST http://127.0.0.1:8693/salir
```

## 7. Evidencia

| fichero | qué es |
|---|---|
| [`formato-avin-estatico.txt`](../../reports/evidence/g22-pbmedia-20261126/formato-avin-estatico.txt) | descriptor `0x9d1270` volcado, getter `0x6800e4 = 0x138800`, desensamblado de `0x1de030` con los offsets del registro |
| [`pbmedia2-trazas.txt`](../../reports/evidence/g22-pbmedia-20261126/pbmedia2-trazas.txt) | ciclo de `[ObjMedia]` (rechazo y limpieza), `getModelInfo(model/MEDIA,*)`, 34 lecturas `SDIO` con sus sectores, 0 disparos de `13e474` |
| [`mediadelay-intento.txt`](../../reports/evidence/g22-pbmedia-20261126/mediadelay-intento.txt) | los dos intentos de `MEDIADELAY`: el SEGV del trampolín corto y la espera de 4 s que deja el arranque sin `onStarting` ni `FsysMount` |
| [`mapa-sd-media.txt`](../../reports/evidence/g22-pbmedia-20261126/mapa-sd-media.txt) | `mdir` de la imagen con `SD_MEDIA=1` (foto 294 771 B, índice 384 B) y el sector del *file ID* |
| [`00-antes.png`](../../reports/evidence/g22-pbmedia-20261126/00-antes.png) · [`01-index.png`](../../reports/evidence/g22-pbmedia-20261126/01-index.png) | fotogramas antes y después de `O view/INDEX_PLAYBACK 0` (idénticos: el arranque no pinta, §5.1) |
