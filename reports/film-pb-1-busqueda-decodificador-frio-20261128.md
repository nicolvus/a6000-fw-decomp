# FILM-PB-1 — por qué el decodificador H.264 no arranca en frío y sí en caliente

Fecha: 28-11-2026. **100 % estático**: la cámara estaba apagada y desconectada; no se usó telnet, USB,
SWD, `adb` ni `pmca-console`, no se construyó ni se instaló nada. Todo lo que exige la cámara está en
[§7](#7-peticiones-para-la-próxima-sesión-física) como petición con su comando exacto, **sin ejecutar**.

Evidencia: [`reports/evidence/film-pb-1-busqueda-decodificador-frio-20261128/`](evidence/film-pb-1-busqueda-decodificador-frio-20261128/).
Continúa [sector31-resultado §12](film-pb-1-sector31-resultado-20261126.md#12-resultado-del-control-av-instalado),
[arranque WBI](film-pb-1-sub-arranque-wbi-20261128.md), [decodificador](film-pb-1-sub-decodificador-20261128.md)
y [auditoría del CFW](film-pb-1-auditoria-cfw-20261127.md).

---

## 0. Respuesta en una página

| # | Pregunta | Respuesta | Estado |
|---|---|---|---|
| 1 | ¿Dónde falla? | El core AV contesta al comando **movie decoder start** (mensaje `0x2003`) con estado ≠ 0. `libmpr` traduce ese estado a `0x1600F101`, lo rotula `E_AVCON_MOVIE_CODEC_STOP`; `MDecI/F` lo convierte en `0x16001001` = `ER_MOVIE_DECODE_FAILED` y `libObj` acaba en `ER_FAILED` → «No se puede visualizar». | **VERIFICADO** contra bytes |
| 2 | Corrección al informe anterior | El `00002003h` del anillo **no es un código de error**: es el **id del mensaje** (3.er argumento del log). El nombre `E_AVCON_MOVIE_CODEC_STOP` corresponde a la palabra **ya traducida** `0x1600F101`. | **VERIFICADO** |
| 3 | ¿Lo rompe el CFW? | **No.** A es el tar de fábrica 3.21 con **un solo miembro menos** (`0700_part_image/dev/nflasha5`); los otros 71 son idénticos byte a byte, y B es el tar de fábrica íntegro. La rotura es del **camino de arranque en frío del propio 3.21 de Sony**. | **VERIFICADO** |
| 4 | ¿Qué cambia en frío? | (a) Loader3 carga **6** ficheros RAMCFG en vez de 2 (`sa_dfdet.bin`, `kemco.txt`, `initrd.img`, `vmlinux.bin` de más); (b) **no se restaura la instantánea**: el estado de MPR/`libmpr`/`libObj` y las 12 regiones `wbimem=` se construyen desde cero; (c) `im.elf` **vuelve a pedir la carga** de `av-cam.bin`. | **VERIFICADO** |
| 5 | ¿Qué NO cambia? | La imagen del core AV (`av-cam.bin` tiene **0 de 2 200 páginas** dentro del WBI ⇒ es la misma en ambos modos), cmdline, módulos, montajes, `DmmConfig.bin` y el microcódigo de `/usr/sabin`. | **VERIFICADO** |
| 6 | ¿Cuál es la causa? | **No demostrada.** Quedan tres mecanismos vivos (§4) y un experimento de 4 bytes que los separa (§7, E2). | — |

**Lectura corta:** el decodificador no está «roto»; en frío nadie completa el estado con el que el
core AV arranca su unidad de decodificación, y el primer comando que lo pide se rechaza con «codec
parado». En caliente ese estado no hace falta construirlo: la instantánea lo devuelve.

---

## 1. La cadena exacta, contra bytes

`libmpr.so` del 3.21 (`firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/lib/libmpr.so`, VA = offset
de fichero, primer `PT_LOAD` a base 0; Thumb). Todo lo de esta sección está desensamblado en
[`03-libmpr-cadena-decodificador.txt`](evidence/film-pb-1-busqueda-decodificador-frio-20261128/03-libmpr-cadena-decodificador.txt).

| VA | Qué es | Detalle |
|---|---|---|
| `0x2C111C` | despachador de mensajes de codec | `movw r3,#0x200E`; `r0`=id, `r1`=payload |
| `0x2C11F8` | selección del caso | `movw r3,#0x2003` · `cmp` · `beq 0x2C1916` |
| `0x2C1916` | lectura del estado | `ldr r2,[r1,#8]` · `cmp r2,#0` · `bne 0x2C1974` |
| `0x2C1920` | rama OK | nombre del msg `0x1004` = «Movie Decoder Start», texto `0x7EE09C` = «Dec start complete» |
| `0x2C1974` | rama de error | `add.w r0,r1,#8` → `bl 0x2C0E88` **traduce el estado en sitio** |
| `0x2C1988` | log | literal `0x7ED455` = «Dec start complete error!!», módulo 4 = `CodecDrv` |
| `0x2C0E88` | traductor de códigos del AV-Codec | búsqueda binaria sobre el pool `0x2C1040…0x2C109C`; `0xF1000001` (`subs r2,#1` en `0x2C0EC4`) y `0xFB050001` (`0x2C0F50`) van **los dos** a `0x1600F101` (`0x2C0FB0`, literal `0x2C10C4`) |
| `0x2D7B40` | emisor del log de error | `[Error]` (0x7F6531) + `[módulo]` (tabla `0x2D0BB0`; 4=`CodecDrv`) + **nombre del código** (`0x2D06C8`) + `( %08X )` con **`r5` = id del mensaje** |
| `0x2D0B44` | nombre | slot → `0x7F325A` = `E_AVCON_MOVIE_CODEC_STOP` |
| `0x462E2C` | `MDecI/F` | compara con `0x1600F300/F000/F200/F600/F800/F500`; si no es HW, deja `0x16001001` (`0x4630F8`) en `this+0x88C` y registra `ER_MOVIE_DECODE_FAILED` (`0x2D0AD0`) |
| `0x2C0AD0`… | `libObj` | `mp4FileLib_Play` `0xB0F2000A`, `PlayMovie` → `ER_FAILED` |

**La línea del anillo, despiezada** (`8-anillo-variante-A.txt:120`):

```
[CodecDrv][Error] E_AVCON_MOVIE_CODEC_STOP (00002003h)
   ↑módulo   ↑nombre de 0x1600F101   ↑id del mensaje (no es un código de error)
```

Consecuencia que cambia el trabajo pendiente: **el log no puede decir qué palabra original llegó**
(`0xF1000001` de la familia *movie codec* o `0xFB050001` de la familia `FB05`), porque la traducción
sobrescribe `+8` en el mismo sitio. Y el estado lo escribe **el core AV**: `libmpr` sólo lo lee, lo
traduce, lo registra y devuelve 1; en la cadena `0x2C111C…0x2C305C` y `0x462E0C` no hay ni una lectura
de cmdline, `nflasha5` ni nada del arranque (comprobado: `libmpr` no importa símbolos de `dmm`/`stream`
en esa ruta; el transporte es `osal`/`uipc`).

---

## 2. Qué cambia de verdad con el arranque en frío

Detalle completo en [`04-frio-vs-caliente.txt`](evidence/film-pb-1-busqueda-decodificador-frio-20261128/04-frio-vs-caliente.txt).

### 2.1 Loader3 (BootMode 1) carga cuatro ficheros más que en caliente (VERIFICADO)

| N | Ruta RAMCFG | Destino | Modos que la cargan |
|---:|---|---|---|
| 0 | `\sabin\idt_cam.bin` | `0x83501000` | `0x1000000` (frío) y `0x4000000` (caliente) |
| 1 | `\sabin\sa_dfdet.bin` | `0x96800000` | **sólo frío** |
| 2 | `\av-cam.bin` | `0x83541000` | frío y caliente |
| 3 | `\kemco.txt` | `0x80033000` | **sólo frío** |
| 4 | `\initrd.img` | `0x80628000` | **sólo frío** |
| 5 | `\vmlinux.bin` | `0x80038000` | **sólo frío** |

Medido en el propio cargador (log SWD del 3.52 en frío, `analysis/camera-dumps/20261108-swd-352/loader-log-0xc0060000.txt`):

```
BOM:<<BootMode: 1>>
LD3:Run Config(load:1000000)
CFG:Parse file [P=0x3:A=0x83501000:E=0x83540FFF:C=0x5000000:\sabin\idt_cam.bin]
CFG:Parse file [P=0x3:A=0x96800000:E=0x9682FFFF:C=0x1000000:\sabin\sa_dfdet.bin]
```

⇒ El `C=` de cada entrada **es** el argumento de la selección por modo, y `sa_dfdet.bin` es el único
programa de DSP que el arranque en frío coloca y el caliente no.

### 2.2 El WBI es una suspensión de RAM, y no lleva el core AV (VERIFICADO)

`nflasha5` = `WBI1`, `numSections=0x48C` (1 164), `flag=9` (WBI + LZ77), `dataSize=41 993 728 B`,
`oDataSize=172 998 656 B`; cada sección es un chorro LZ77 de 4 096 B exactos (42 236 páginas). Contiene
las **páginas en uso** del nodo 0 (imagen del kernel, *page cache* de `/usr` y memoria de los procesos
MPR/`libmpr`/`libObj`) más las 12 regiones `wbimem=` de la cmdline.

- **No contiene `av-cam.bin`: 0 de 2 200 páginas.** La ventana del core AV
  `0x834C0000-0x84141000` (boottime + `klog` + `idt_cam` + `av-cam`) queda fuera ⇒ **la imagen que
  ejecuta el core AV es idéntica en frío y en caliente**; se recarga del flash en ambos modos.
- Sí contiene `libObj.so` (994/4 254 páginas), `im.elf` (5/5), `viewUnified2.so` (50/1 209),
  `CautionConfig.so` (12/409) y el TOC TPZL de `/usr` materializado en `0x8D3B8000`.

⇒ La diferencia no puede ser «el código del decodificador»: es **estado**.

### 2.3 En frío, `im.elf` vuelve a pedir la carga de `av-cam.bin` (VERIFICADO)

`/usr/bin/im.elf` (sólo se ejecuta desde `/sbin/init` → `bootin.elf`):
`0xB368`: `Backup_read(0x00fa007c)` → `snprintf("fn=/system/av-cam.bin load=1 debug=1 adr=0x%x …")`
(cadena en `0x43B3`) → `mmap` + `syscall(0x80)` (el mismo mecanismo con el que `init` inserta los `.ko`).
En caliente `im.elf` **no** se ejecuta y nadie hace esa segunda petición.

### 2.4 La asimetría medida más concreta: `sa_dfdet.bin` (VERIFICADO el hecho, INFERENCIA el efecto)

Sobre el volcado de RAM real de la cámara en marcha (`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`,
1 GiB desde `0x80000000`, arranque normal = caliente):

- `sa_dfdet.bin` está **íntegro en `0x96600000`** (bloque no nulo `0x96600000-0x96627000` = 159 744 B ≈
  los 155 780 B del fichero; coinciden los tramos `+0x0`, `+0x2000`, `+0x8000`, `+0x20000`).
- En **`0x96800000`** —la dirección que declara RAMCFG— hay **192 KiB a cero**.
- `0x96600000-0x96800000` es una de las 12 regiones `wbimem=` (`wbimem=0x200000@0x96600000`) ⇒ **sólo
  existe si se restaura la instantánea**; en frío Loader3 escribe el fichero en `0x96800000` y no deja
  nada ahí.

[`02-ram-medida-96600000.txt`](evidence/film-pb-1-busqueda-decodificador-frio-20261128/02-ram-medida-96600000.txt).
Es el único trozo de carga de DSP que se ha podido medir en RAM, y su colocación **depende del modo**.

### 2.5 La plataforma de medios tiene un camino explícito de reanudación (VERIFICADO que existe)

`libmpr`: `MprIf::SnapShotBootInit(SnapShotBootInitParam*)` `0x71CE64`, `MprIf::Resume(bool, MPR::BootType)`
`0x722BA4`, `FlashLib::WarmBootInit()` `0x2B6788`, textos «SnapShot mode» `0x9003F6`, «AVI Warm boot Init»
`0x8E93E1`, «bootType = [%x]» `0x905579`. `libObj` tiene la orden de consola «Usage : Resume [cold/hot/ssb]».
**NO VERIFICADO** que esa rama sea la que programa el decodificador.

---

## 3. Esto no es un fallo del CFW (y lo que implica)

**VERIFICADO.** El par de la bisecta no aísla un parche: aísla el modo de arranque.

| | A | B |
|---|---|---|
| `container.json` | `"sin_wbi": true` | `"sin_wbi": false` |
| `0700_part_image/dev/nflasha5` | ausente | presente (WBI de fábrica, sha `fe080cda…`) |
| resto del tar (71 miembros) | idéntico byte a byte | idéntico byte a byte |
| Loader3 | `BootMode 1` → modo RAMCFG `0x1000000` | `BootMode 11` → `0x4000000` |
| Reproduce | **no** | **sí** |

Y A **es** el 3.21 de fábrica sin el miembro del WBI: no lleva Silent, ni EFCS, ni AV-CAM parcheado
(`/system/AV-CAM.BIN` md5 `ef2e3003…` = fábrica en ambos).

**Implicación (INFERENCIA fuerte):** en el campo la cámara prácticamente nunca arranca en frío. El
actualizador oficial sí invalida el WBI (`ud_wbi_drop.elf` escribe 512 ceros sobre `/dev/nflasha5`,
`us_mkfs.sh:106`) **pero acto seguido reescribe el miembro `0700_part_image/dev/nflasha5` del propio
paquete de Sony** ⇒ tras cualquier actualización de Sony el arranque vuelve a ser caliente. El frío
queda como camino rara vez ejercitado, y ahí el decodificador no arranca. Por eso el proyecto llevaba
tres versiones sin explicación: nunca estaba mirando el camino caliente de Sony, sino un camino que
Sony no recorre.

**Consecuencia práctica para el proyecto:** la vía «CFW con WBI» no es un compromiso, es la única que
reproduce; y como el WBI **no** contiene `av-cam.bin` (0/2 200 páginas), los parches que viven en
`/system` (Silent/EFCS sobre `av-cam.bin`, Darwin) **sí** se aplican en caliente. Lo que no se aplica
en caliente es `/usr` (`libObj.so`, `CautionConfig.so`, `viewUnified*`, `.uxc`), que es donde vive el
menú. [Detalle](film-pb-1-sub-arranque-wbi-20261128.md#6-riesgo-de-conservar-el-wbi-lo-que-documenta-el-proyecto).

---

## 4. Causas candidatas ordenadas

Ninguna está demostrada. El orden es por cuánto explica y por cuánto costaría refutarla.

### C1 — La unidad de decodificación del core AV no se carga/programa en frío (principal)

*Qué sostiene:* (i) el estado lo produce el core AV, no Linux (§1); (ii) la imagen del core AV es la
misma en ambos modos (§2.2), así que lo que falta es **estado**, no código; (iii) el único payload de
DSP medido en RAM (`sa_dfdet` en `0x96600000`) existe **sólo** por restauración (§2.4); (iv) el único
camino que en frío toca el core AV y en caliente no existe es la segunda carga de `av-cam.bin` por
`im.elf` (§2.3).
*Qué la refutaría:* que la palabra original sea `0xFB050001` (familia baseband/refcode, ajena a la
unidad de vídeo) — entonces el que rechaza no es el decodificador.
*Estado:* **INFERENCIA**.

### C2 — El mapa de buffers/recurso que MPR entrega al codec está incompleto en frío

*Qué sostiene:* las tablas de buffers del reproductor son estáticas de `libmpr` (`0x8D87E8` →
«Movie Pb» `0x9DB0E4`), las regiones de dispositivo `0x8E680000`, `0x8F708000`+59 MiB, `0x9334F000`,
`0x93383000`, `0x933AD000`, `0x96083000`, `0x96600000`, `0x96800000` son `wbimem=` (se restauran) y en
frío nacen del `bootmem` a cero; el anillo del MPR (`0x82DF9000`) es la prueba visible de que esa
memoria vuelve con contenido de la sesión anterior.
*Qué la refutaría:* `0x1600F104` (`E_AVCON_MOVIE_CODEC_BADARG`) en vez de «codec parado», o que
`/proc/udm/dmm_units`/`extents` sean iguales en A y B (§7-E1).
*Estado:* **INFERENCIA**.

### C3 — Reparto de memoria del `dmm.ko` reconstruido en frío

*Qué sostiene:* es el único módulo con estado heredable (`dmm_module_BootCore`, `Suspend/Resume`,
`dmm_ext_tbl_GetSuspendAreaStart/EndAddr`, «FATAL! MEMORY MAP TABLE FIXED, BUT NEEDS RESTART!»).
*Qué la debilita:* `DmmConfig.bin` no viaja en el paquete (es el mismo fichero en A y B), `dmm` está
cargado en ambos y los buffers del codec **no** se piden al DMM ni al *buddy*: son `mmap` de físicas
fijas de una tabla estática. MemTotal, `memrsv`, `secgrp` y `page_alloc.minkb=256` son iguales.
*Estado:* **NO VERIFICADO**; es la hipótesis viva más débil de las tres, pero es la única barata de
cerrar con dos lecturas.

### C4 — El frío deja el área ZIT en otra dirección (§2.4) y la primera carga de unidad falla

Subcaso de C1 con la única evidencia positiva de contenido que existe. **INFERENCIA**.

---

## 5. Descartes, con razón

| Hipótesis | Por qué se descarta |
|---|---|
| Silent / EFCS / Darwin v3 / AV-CAM 233 B / parches de `libObj` | A **es** el 3.21 de fábrica sin el WBI: no lleva ninguno de esos parches y falla. `darwin_v3=false` en los dos paquetes; `/system/AV-CAM.BIN` md5 `ef2e3003…` = fábrica en A y B |
| `0xB051000B` de `ff4PlayIf` (1084/1028/967) | Está también en B, que reproduce y acaba en `ER_STREAM_END` |
| Sector FBM `0x31`, IFO, `Err RcsBackupTblData`, `0xB0800001`, `0x31000007`, `MS IDs are not same` | Los mismos errores están en B (que reproduce). A cambia de estado de tarjeta entre sus dos arranques y falla igual. `A-frio/ring.txt` y `B-caliente/ring.txt` difieren por primera vez **después** de `EnterMoviePb` |
| Guardas `Pb Disable!!` (`0x437C0A`) y `Detect UnSupported Content` (`0x437C3C`) | En el anillo de A **no aparecen** (0 aciertos): no dispararon. El fallo está dentro de `PbStart` |
| Selector PAL/NTSC / `isSupportContent` `0x61A8F0` | B es igual de NTSC y reproduce; en A no hay rastro de la guarda. (Además: `0x61A8F0`, `0x60945C` y la vtable `0x8E6E58` están en **`libmpr`**, no en `libObj`) |
| `/tmp` en flash, `swap_prepare.sh`, `mkdosfs` | `/tmp` = `nflasha10` vfat **en ambos**; los otros dos sólo corren con `upm_bootmode == BIS` |
| Módulos y su orden | `init` no tiene ramas por modo; los 38 `insmod` y sus parámetros son estáticos; 3 ficheros ni existen y `main` ignora los fallos; `/proc/udm/drivers` no lo crea nadie (el `write("set")` falla en todos los arranques) |
| `/dev/ldec` como decodificador | Es el descompresor **LZ77 por hardware** (`ux4core::Lz77Decoder` en `libObj`); el kernel no tiene ningún nodo de códec (75 nodos de `devno.ko`) |
| `vmlinux`/`initrd`/`rootfs` distintos | Idénticos a fábrica en A y B |
| Reprogramación del sub-CPU «desde cero» como causa aislada | El core AV se recarga en **ambos** modos (av-cam 0/2 200 páginas en el WBI) ⇒ no es una diferencia |
| «El arranque en frío no afecta» ([sub-motor §3](film-pb-1-sub-motor-20261127.md)) | Contradicho por la medición A/B: es la **única** variable |

---

## 6. Límites

- **La causa no está demostrada.** Lo demostrado es *dónde* falla (el core AV rechaza el arranque del
  decodificador) y *qué* cambia (frío frente a caliente, §2). El «por qué» último necesita una medida
  en cámara: la palabra cruda `+8` y/o el estado de las unidades del DSP.
- El valor original que devuelve el core AV **no se puede deducir del log** (la traducción sobrescribe
  `+8`). Las dos palabras posibles están en el traductor: `0xF1000001` y `0xFB050001`.
- No hay volcado de `0x82D90000-0x84141000` ni del *heap* de MPR en frío, así que no se puede decir
  qué estructura concreta falta.
- `Loader3` es binario no disponible: el modelo de «en caliente no se ejecuta `/sbin/init`» es
  **INFERENCIA** apoyada en `warm.c` y en la medición A/B (arranque rápido, sin mensajes de `init`).
- La rama REA no estuvo utilizable esta sesión (socket ocupado); todo se verificó contra bytes con
  Capstone 5.0.7, `strings`, `readelf` y los volcados. `sa_dfdet` en `0x96600000` es medición directa;
  su **significado** es inferencia.

---

## 7. Peticiones para la próxima sesión física

Ordenadas por coste. Ninguna se ha ejecutado.

### E1 — Sólo lecturas, sin cambiar firmware (≈5 min). Cierra C3 y acota C1/C2

En **A** (con el fallo) y en **B** (que reproduce), tras un intento de PLAY fallido/correcto:

```sh
busybox cat /proc/udm/upm_bootmode
busybox dd if=/dev/nflasha5 bs=16 count=1 2>/dev/null | busybox od -c   # ¿sigue el WBI a cero en A?
busybox cat /proc/meminfo | busybox grep -E 'MemTotal|MemFree|VmallocTotal'
busybox cat /proc/udm/dmm_info;  busybox cat /proc/udm/dmm_units
busybox cat /proc/udm/dmm_extents; busybox cat /proc/udm/dmm_reserve
busybox dd if=/dev/mem bs=4096 skip=536057 count=4 2>/dev/null           # anillo MPR (ya usado)
busybox dd if=/dev/nflasha11 2>/dev/null | busybox strings | busybox grep -iE 'codec|avcd|ZIT|unit'
```

Criterio: si `dmm_*` y `MemFree` coinciden en A y B ⇒ **C3 muerta** y queda el core AV. Si en `/log`
aparece un fallo de carga de unidad **al arrancar** (no al pulsar PLAY) ⇒ **C1 confirmada**.

### E2 — Decisiva, requiere construir un paquete (offline). Separa C1 de «otra cosa»

Sobre el paquete **A** (que ya falla), parche en `libmpr.so` **copiando la palabra cruda antes de
traducirla**: en `0x2C1974` está `add.w r0,r1,#8` → `bl 0x2C0E88`. Sustituir el `bl` por una cueva que
(i) lea `[r0]`, (ii) la guarde en la zona libre `wbimem=0x8000@0x82EAE000` (relleno `0x5A`, no la usa
nadie), (iii) ejecute el cuerpo de `0x2C0E88` y vuelva. Después de un PLAY fallido:

```sh
busybox dd if=/dev/mem bs=1 skip=$((0x82EAE000)) count=16 2>/dev/null | busybox od -An -tx4
```

- `f1000001` ⇒ **familia movie codec** (C1/C2/C4).
- `fb050001` ⇒ **familia FB05 / baseband-refcode**: el que rechaza no es la unidad de vídeo y hay que
  reescribir §4 entera.

Alternativa sin cueva (2 bytes): poner `0x4770` (`bx lr`) al principio de `0x2C0E88` y leer **el nombre**
del código en el anillo; si cambia de `E_AVCON_MOVIE_CODEC_STOP` a otro rótulo, se conoce la familia.

### E3 — La pregunta que puede arreglarlo todo sola (1 minuto, gratis)

`im.elf` escribe **`"warm"`** en `/sys/power/state` en cada arranque en frío (`cmdline: warm.mode=2`,
`im.elf 0x9FB4` → `0x9FCA-0xA018`), es decir: la cámara debería **regenerar su propio WBI** al apagarse.
No lo hace: A siguió arrancando en frío dos veces. Comprobar, tras un apagado **normal** desde A:

```sh
busybox dd if=/dev/nflasha5 bs=16 count=1 2>/dev/null | busybox od -c
```

- Sigue a cero ⇒ la generación falla; mirar el `klog`/`/log` en busca de `WARM(warm_count=…)` o
  `SUS(warm_count=…)` y de errores de `nand.ko`.
- Empieza por `W B I 1` ⇒ **el arreglo es automático en el segundo encendido**: la cámara estaría en
  caliente *con el `/usr` del CFW*, y con ello se resolverían a la vez la reproducción y el menú.

### E4 — Experimento de control (sólo si E1-E3 no bastan)

Construir **A + `nflasha5` = B** ya está hecho. Lo que falta es el control inverso: **B con el `/usr`
del CFW** (`build_package_nflasha15.py` sin `--sin-wbi`, `sin_wbi=False` por defecto). Si reproduce,
el WBI y los parches de `/usr` conviven mejor de lo que dice [§6 del informe del WBI](film-pb-1-sub-arranque-wbi-20261128.md#6-riesgo-de-conservar-el-wbi-lo-que-documenta-el-proyecto);
si no reproduce, se confirma el riesgo de mezcla.

---

## 8. Reproducibilidad

```bash
# 1. Selección de ficheros de Loader3 por modo (RAMCFG)
sed -n '41,60p' docs/capture/e26-r14-ramcfg-bos-analysis.md
grep -a "BootMode\|CFG:Parse file" analysis/camera-dumps/20261108-swd-352/loader-log-0xc0060000.txt

# 2. WBI: cabecera, secciones y cobertura
xxd -l 64 firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5
.venv/bin/python3 references/fwtool/fwtool/sony/wbi.py --help      # lector (no hay escritor)

# 3. sa_dfdet en RAM (0x96600000) frente a la dirección de RAMCFG (0x96800000)
.venv/bin/python3 - <<'PY'
import mmap
f=open('analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin','rb')
m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
df=open('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/sabin/sa_dfdet.bin','rb').read()
for off in (0,0x2000,0x8000,0x20000):
    n=df[off:off+48]; h=[]; k=m.find(n)
    while k!=-1 and len(h)<4: h.append(hex(k+0x80000000)); k=m.find(n,k+1)
    print(hex(off), h)
print('0x96800000 a cero:', not any(m[0x16800000:0x16800000+0x30000]))
PY

# 4. Cadena del decodificador en libmpr (desensamblado con Capstone 5.0.7, Thumb)
.venv/bin/python3 /tmp/armdis.py 0x2c1916 0x40 thumb
.venv/bin/python3 /tmp/armdis.py 0x2c0e88 0x50 thumb
```

### Ficheros de evidencia

| Fichero | Contenido |
|---|---|
| `01-ramcfg-y-modos.txt` | tabla RAMCFG con destinos/ventanas/flags, selección por modo, log de Loader3 en frío, las 12 regiones `wbimem=` |
| `02-ram-medida-96600000.txt` | medida sobre el volcado de 1 GiB: `sa_dfdet` íntegro en `0x96600000`, `0x96800000` a cero |
| `03-libmpr-cadena-decodificador.txt` | cadenas, manejador `0x2C1916`, traductor `0x2C0E88`, pools de constantes y tabla de nombres |
| `04-frio-vs-caliente.txt` | resumen citado de todo lo que cambia y lo que no, con las rutas de cada prueba |
