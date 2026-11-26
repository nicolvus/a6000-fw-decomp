# G22-REPRO — La cámara emulada y las fotos de la SD: árbol `AVF_INFO` y reproducción

**Estado (26-11-2026): PARCIAL.** Con `SD_ESTRUCTURA=1` la SD emulada trae ya la estructura que el firmware nombra (`AVF_INFO` con sus ficheros,
`MP_ROOT/100ANV01`) y **el volumen deja de fallar por «no hay `AVF_INFO`»**: medido, `libmpr` consulta `ms:/AVF_INFO` y sigue con los ficheros del índice,
el manejador del recuento (`libmpr+0x620028`) se ejecuta y el montaje del sistema de ficheros termina `OK`.
**No se ha conseguido** que la tecla Reproducción abra la vista ni que el recuento de fotos salga numérico: lo que falta es el **contenido del índice AV**
(no hay ningún volcado real en el repo y no se ha inventado) y, por otro lado, el camino tecla → vista, que sigue sin abrir nada. Diagnóstico exacto en §4.

Sesión: **26-11-2026** (reloj del anfitrión 00:30–01:30, −03). Cámara física: **no usada** (todo en `qemu-system-arm`, perfiles `repro`/`repro2`).
Espacio de direcciones: **VA del ELF** de `libmpr.so` 3.21 (el primero `PT_LOAD` tiene vaddr 0, así que offset de fichero = dirección); `TRACELIB`/`TRACEFN2`
del shim usan el desplazamiento respecto a la base de la biblioteca, que es el mismo número.
Capturas: [disparo](img/g22-repro-disparo.png) · [tras pulsar Reproducción](img/g22-repro-tras-reproduccion.png).

---

## 1. El cambio: qué se construye en la imagen FAT (`scripts/gui/harness/sd_image.py`)

El árbol mínimo anterior (`DCIM`, `DCIM/100MSDCF`, `PRIVATE`, `PRIVATE/M4ROOT`, `PRIVATE/M4ROOT/CLIP`, `PRIVATE/AVCHD`) no traía nada de lo que el firmware
consulta al montar el volumen. `SD_ESTRUCTURA=1` (`completa=True`) añade ahora:

| Entrada | Por qué está (evidencia) |
|---|---|
| `AVF_INFO/` (carpeta) | `Fsys_FindFirst("ms:/AVF_INFO")` es la comprobación que decide «hay medio» en `libmpr+0x1d1774` (§3); cadena `AVF_INFO` en `libmpr+0x7a637f` |
| `AVF_INFO/AVIN0001.INP` | índice AV primario; descriptor en `.data` `0x9d1270` (nombre `0x7a912c`, registro `0x80`, máximo `0x2710`), [film-pb-1-sub-avin](../reports/film-pb-1-sub-avin-20261127.md) |
| `AVF_INFO/AVIN0001.BNP` | respaldo del mismo índice (`0x7a9139`, descriptor contiguo al anterior) |
| `AVF_INFO/AVIN0001.INT` | tabla interna (`0x7a9160`, descriptor propio en `0x9d12c0`) |
| `AVF_INFO/PRV00001.BIN` | pedido por el firmware (§3, medido) y por §5.51 |
| `AVF_INFO/STAT0000.BIN` | **nuevo, medido en esta sesión**: `Fsys_FindFirst("ms:/AVF_INFO/STAT0000.BIN")` (§3). No estaba en ningún informe previo |
| `MP_ROOT/100ANV01/` | `MP_ROOT` en `libmpr+0x7a743a`/`0x7a7ac1`; en la tarjeta real del 25-11 los MP4 vivían en `MP_ROOT/100ANV01` y `MP_ROOT/103ANV01` |

Los cinco ficheros se crean **de 0 B a propósito**: su contenido real no existe en el repo (ni un byte de una `AVF_INFO` de la A6000, ver
[film-pb-1-sub-bd-tarjeta §1](../reports/film-pb-1-sub-bd-tarjeta-20261128.md)), así que el arnés aporta **existencia** y no inventa formato. La SD del invitado
admite escritura (`ioctl 0x110`/`pwrite64` sobre `/sd.img`), así que es la propia cámara la que debería crear/registrar el índice (§4.2).
Los ficheros que el anfitrión ponga en su carpeta **mandan** sobre estos marcadores (`mcopy -o`, cubierto por test).

Tests sin QEMU: `tests/test_gui_sd_image.py` (5 casos: lista de entradas con y sin estructura, imagen base sin `AVF_INFO`, imagen completa con los cinco
ficheros a 0 B y `MP_ROOT/100ANV01`, y que un `AVF_INFO` del anfitrión se copia encima sin romper `mkfs.vfat`/`mmd`/`mcopy`).

---

## 2. Cómo se mide (comandos exactos)

```sh
# perfil propio, puerto 8650, SD de la carpeta del configurador (con DSC00001.JPG de 1536x1024 dentro)
HOME=/tmp/g22/home SD_ESTRUCTURA=1 \
SHIMEXTRA="WAITLOG=5000 TRACELIB=libmpr.so TRACEFN2=13e474,620028 TRACEDEREF=d0:0:18 TRACEREP=1 TRACEMAX=32" \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir repro --puerto 8650 --config /tmp/g22/config-repro.json
```

- `TRACEFN2` relativo a `libmpr.so`; `TRACEDEREF=d0:0:18` vuelca 18 palabras desde `r0` **sin desreferenciar** (la cadena de ruta que llega a
  `libmpr+0x13e474`, el envoltorio de `MprFileIf::FindFirst`).
- `WAITLOG=5000` reenvía al anfitrión las líneas `efp` (trazas) a `live/<perfil>/shim.log`; **`WLALL=1` no hace falta** para las trazas (`efp` reenvía
  con `wl_on()`) y solo añade ruido y lentitud.
- Arranque en frío ≈ 250 s hasta la pantalla; el primer fotograma llega ≈ 240 s con tres VM en el anfitrión.

---

## 3. Medición: el firmware SÍ ve `AVF_INFO` y sigue con el índice (VERIFICADO)

Arranque con `SD_ESTRUCTURA=1` y `DCIM/100MSDCF/DSC00001.JPG` (73 359 B, JPEG real de 1536×1024, generado con PIL) en la carpeta del configurador.
`live/<perfil>/shim.log`, traza de `libmpr+0x13e474` (24 disparos, cadena de `r0` decodificada):

```
348.03  TRACE 13e474 n=1  r0=62989bd8 -> "ms:/AVF_INFO"                    <- comprobación de volumen (la que daba 0x2109)
386.06  TRACE 13e474 n=2  r0=62989aec -> "ms:/AVF_INFO/PRV00001.BIN"
386.06  TRACE 13e474 n=3  r0=86bd026c -> "ms:/AVF_INFO"
386.06  TRACE 13e474 n=4  -> "ms:/AVF_INFO/AVIN0001.INP"
386.06  TRACE 13e474 n=5  -> "ms:/AVF_INFO/AVIN0001.BNP"
386.06  TRACE 13e474 n=6  -> "ms:/AVF_INFO/AVIN0001.INT"
386.06  TRACE 13e474 n=10 -> "ms:/AVF_INFO/STAT0000.BIN"   <- no documentado antes
397.04  TRACE 620028 n=1  (manejador del recuento de fotos)  <- se ejecuta
404.73  TRACE 620028 n=2
413.06  TRACE 620028 n=4
```

- **El montaje no es el problema** (ya lo decía §5.14): `[ObjMedia]StartFsysMount`, `FsysMount /dev/mmca` y
  `[ObjMedia]Fsys_MountAsync("/dev/mmca") OK 'A'` a los 107–108 s del invitado, y el estado pasa por `MSGID_FILESYSTEM_MOUNT_EVT`.
- El orden de las consultas importa: **primero** `ms:/AVF_INFO` (a los 348 s del invitado, antes de cualquier otra ruta `ms:`), después
  `PRV00001.BIN` y las tres tablas del índice. Es decir, `AVF_INFO` es la puerta y este arranque la pasó.
- Con la estructura, el **manejador del recuento se ejecuta periódicamente** (`libmpr+0x620028`, ≈ cada 8 s) — sin ella se quedaba en la comprobación de medio.
- La UI queda sana: 50–64 fotogramas a 1,0–1,5 fps, 33–35 listas por fotograma, OSD poblada (modo P, 3:2 24M FINE, AF-S, AWB, DRO, ISO).

### 3.1 Estático que explica la puerta (VERIFICADO en instrucciones)

`libmpr+0x1d1774` (consulta de volumen, llamada desde `+0x14f1cc`):

```
1d185a  bl 0x13e474                 ; FindFirst(ruta = r0)
1d185e  movw r3,#0x2109
1d1862  cmp  r0,r3
1d1866  beq  1d1964                 ; 0x2109 -> sin medio (falla)
1d1868  cbz  r0,1d18d8              ; 0     -> sigue
1d18d8  str r3(=1),[fp]             ; salida «hay medio» = 1, y copia tamaño/libre/sector del volumen
```

Es decir: **«hay medio» = 1 si y sólo si `FindFirst("ms:/AVF_INFO")` devuelve 0** (encontrado); `0x2109` (no existe) y cualquier otro código
(`0x2008` = carpeta vacía, medido en §5.51) lo dejan en 0. Los códigos forman parte de las tablas de parejas `(código mpr, código fsys)` de `.data`
`0x7a8780` (`0x2008↔0x1d`) y `0x7a88d0` (`0x2109↔0x1009`); **INFERENCIA**: son la traducción de errores de `libInfraFsys` a `libmpr` — el nombre humano
de cada código no está en el binario (no hay tabla de textos de error).

---

## 4. Lo que sigue sin funcionar, y por qué

### 4.1 La tecla Reproducción no abre ninguna vista (VERIFICADO: sigue igual)

Con la SD estructurada y una foto real dentro, `POST /tecla {"k":"reproduccion","v":1}` (+ suelta) **no cambia la vista**: comparando
[antes](img/g22-repro-disparo.png) y [después](img/g22-repro-tras-reproduccion.png) solo cambia `AF-S`→`MF` (efecto colateral del índice de tecla) y
`SteadyState OFF`; la pantalla sigue siendo la de disparo y el invitado repinta sin abrir nada nuevo. Coincide con lo medido el 26-11 en
[film-pb-1-sub-arnes-galeria §0](../reports/film-pb-1-sub-arnes-galeria-20261126.md): «la tecla Reproducción (`0x1f7`) llega al shim y **no abre ninguna vista**»
y las vistas `view/INDEX_PLAYBACK` / `view/SINGLEPB` se abren y se cierran solas. **No es un problema del árbol FAT**: la cadena de la tecla termina
antes de consultar el índice.

- **INFERENCIA**: el índice que usa la tecla no es el `AVF_INFO` del volumen sino la tabla de acciones de `InputService` → `viewManagerIf::openView`;
  el `AF-S`→`MF` demuestra que la pulsación **sí** se entrega y que el índice físico `0x1f` del shim cae en otra entrada de la tabla (o en un
  `KEY_*` con acción distinta a la de Reproducción).
- **Siguiente paso concreto (G22-REPRO-2)**: `TRACEFN2` sobre el despachador de acciones de `viewUnified2` (`ViewStlrec` usa el mismo patrón que §5.6:
  `+0x147fd4`, `switch` de ranuras) y sobre `viewManagerIf::openView`, pulsando `0x1f7`, para leer qué acción/índice sale; y comparar con el volcado de la
  tabla de teclas que el shim ya registra al arrancar (`InfraInput`, §5.18z¹²). Sin ese dato no se toca el mapa de teclas.

### 4.2 El recuento de fotos no sale numérico (PARCIAL: la comprobación de medio pasa, falta el dato del índice)

Con la estructura, el manejador `libmpr+0x620028` corre, pero la OSD **no muestra número** y el aviso `ERROR` de tarjeta sigue ahí
([captura](img/g22-repro-disparo.png)). Estructura estática del manejador (VERIFICADO, desensamblado Thumb):

```
62022e  b   6206ec          ; salida temprana: recuento 0
620242  bl  615928          ; comprobación de medio (§5.51: devolvía 0 -> salida)
620250  bl  64c298
620262  bl  3bb438          ; tamaño/espacio libre (§5.51)
620294  bl  11e4bc
6202b0  bl  74a274 ...      ; ramas que salen por 620762
```

- **VERIFICADO** que el manejador entra; **NO VERIFICADO** si llega a `0x620262`/`0x62059c` (la división libre/tamaño). El intento de armar esas
  direcciones en caliente (`POST /linea "E TRACEFN2=…"`) no dejó línea de confirmación en `shim.log` (el `LOG` de rearme no se reenvía sin `WLALL`),
  así que **no se afirma** que la fórmula no corra: queda como medición pendiente con trazas armadas en el arranque.
- **Lo que sí está descartado midiendo**: (a) el montaje (arriba), (b) que la tarjeta no tenga el árbol (`AVF_INFO` presente y consultado),
  (c) que la cámara escriba el índice sola: el volcado del disco del invitado (`POST /sd-volcado` → `sd-volcado.img`, 8 515 584 B = exactamente la
  cabeza de la imagen) muestra `AVF_INFO` **igual que al arrancar**: los cinco ficheros siguen a 0 B y `STAT0000.BIN` **no** se ha creado. La foto está
  intacta (`DSC00001.JPG 73359`), libre 4 286 435 328 B. Es decir, **la cámara lee el índice pero no lo repara ni lo crea** en este arranque.
- **INFERENCIA (la más probable)**: el recuento y la lista de reproducción salen del **índice AV**, y un índice de 0 B es «0 contenidos». El `ERROR`
  de tarjeta apunta a lo mismo: falta la base (`AVF_INFO`) con contenido válido o el fichero de estado que el propio firmware pide (`STAT0000.BIN`).

---

## 5. VERIFICADO / INFERENCIA / NO_VERIFICADO

| # | Afirmación | Etiqueta | Evidencia |
|---|---|---|---|
| 1 | El firmware consulta `ms:/AVF_INFO` y a continuación `PRV00001.BIN`, `AVIN0001.INP/.BNP/.INT` y `STAT0000.BIN` | **VERIFICADO** | 24 disparos de `TRACE 13e474` con la ruta decodificada (§3) |
| 2 | «Hay medio» en `libmpr+0x1d1774` ⇔ `FindFirst("ms:/AVF_INFO") == 0`; `0x2109` falla | **VERIFICADO** | desensamblado `0x1d185a–0x1d18dc` (§3.1) |
| 3 | El montaje del FS del invitado termina OK y no es el bloqueo | **VERIFICADO** | `Fsys_MountAsync("/dev/mmca") OK 'A'` (§3), coincide con §5.14 |
| 4 | Con `SD_ESTRUCTURA=1` el manejador del recuento se ejecuta y la UI queda sana (50+ fotogramas, OSD poblada) | **VERIFICADO** | `TRACE 620028` n=1,2,4; `/estado` 64 fotogramas (§3) |
| 5 | La tecla Reproducción no abre la vista de reproducción ni con la SD estructurada y una foto real | **VERIFICADO** | capturas antes/después (§4.1) |
| 6 | La cámara no crea ni repara `AVF_INFO` en este arranque (no hay ninguna escritura nueva en `/sd.img`) | **VERIFICADO** | `sd-volcado.img` = cabeza original, cinco ficheros a 0 B, sin `STAT0000.BIN` (§4.2) |
| 7 | `0x2109`/`0x2008` son códigos `libmpr` traducidos de `libInfraFsys` (`0x1009`/`0x1d`); su nombre humano no está en el binario | **INFERENCIA** | tablas `0x7a8780`, `0x7a88d0` (§3.1) |
| 8 | El recuento y la lista de reproducción necesitan contenido válido del índice AV (los ficheros a 0 B son «0 contenidos») | **INFERENCIA** | §4.2 + [film-pb-1-sub-avimmgr](../reports/film-pb-1-sub-avimmgr-20261127.md) |
| 9 | El manejador del recuento llega o no a la fórmula (`0x620262`/`0x62059c`) en este arranque | **NO VERIFICADO** | rearme en caliente sin confirmación (§4.2); falta arranque con `TRACEFN2=615928,620246,620262,62059c` |
| 10 | Formato y contenido reales de `AVIN0001.INP/.BNP/.INT`, `PRV00001.BIN` y `STAT0000.BIN` | **NO VERIFICADO** | no hay ni un byte real en el repo ([film-pb-1-sub-bd-tarjeta §1](../reports/film-pb-1-sub-bd-tarjeta-20261128.md)) |
| 11 | Qué índice/acción sale de la tecla `0x1f7` y por qué no abre `view/INDEX_PLAYBACK` | **NO VERIFICADO** | traza pendiente (§4.1) |

---

## 6. Reproducir

```sh
mkdir -p ~/A6000-SD/DCIM/100MSDCF   # + una foto DSC00001.JPG (p. ej. 1536x1024 con PIL)
echo '{"sd":{"carpeta":"'$HOME'/A6000-SD"}}' > /tmp/cfg.json
SD_ESTRUCTURA=1 .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir repro --puerto 8650 --config /tmp/cfg.json
# a los ≈240 s: GET /eventos (PNG), POST /tecla {"k":"reproduccion","v":1|0}, POST /sd-volcado, POST /salir
```

`SD_ESTRUCTURA=1` es opt-in: sin la variable la imagen que recibe el invitado es **la de siempre** (el test lo fija).
Medido en este equipo con `amontonamiento` de VM (hasta 3 `qemu-system-arm` de otros perfiles): un arranque en frío tardó 250 s en dar la primera pantalla
y otro se quedó en 2 fotogramas sin av-cam — **INFERENCIA**: sin `--avcam` el ciclo de cámara no arranca y la UI no se pinta; no se atribuye al árbol FAT.

---

## PARA PENDIENTES.md

| ID | Estado | Resumen | Criterio de cierre |
|---|---|---|---|
| G22-REPRO | EN CURSO (abierto 26-11-2026, tarea G22-REPRO) | **Árbol de la SD con `AVF_INFO` (opt-in `SD_ESTRUCTURA=1`)**: `sd_image.py` crea `AVF_INFO/{AVIN0001.INP,AVIN0001.BNP,AVIN0001.INT,PRV00001.BIN,STAT0000.BIN}` (0 B, contenido no inventado) y `MP_ROOT/100ANV01`; tests en `tests/test_gui_sd_image.py`. **MEDIDO**: `libmpr` consulta `ms:/AVF_INFO` (24 disparos de `FindFirst`, con `STAT0000.BIN` no documentado antes) y el manejador del recuento `libmpr+0x620028` se ejecuta con la UI sana (`Fsys_MountAsync OK`). **Sigue fallando**: (a) la tecla Reproducción no abre ninguna vista (solo cambia AF-S→MF; `INDEX_PLAYBACK`/`SINGLEPB` ya se cerraban solas, film-pb-1-sub-arnes-galeria §0) — falta medir acción/índice de `0x1f7` en InputService→`viewManagerIf::openView`; (b) el recuento de fotos sigue sin número y el aviso `ERROR` de tarjeta persiste; la cámara **no** crea ni repara el índice (volcado del disco del invitado idéntico, cinco ficheros a 0 B); falta medir si `0x620028` llega a la fórmula (`0x620262`/`0x62059c`) con trazas armadas en el arranque. **NO VERIFICADO**: contenido real de los cinco ficheros del índice (no hay volcado de tarjeta en el repo). | PNG de `view/INDEX_PLAYBACK` (o `SINGLEPB`) con la miniatura de `DSC00001.JPG` de la SD emulada **y** OSD de disparo con recuento numérico (sin `ERROR`); si el índice es imprescindible, con un `AVIN0001.INP` cuyo contenido venga de una tarjeta real (o generado por el propio MPR, p. ej. arreglando «Formatear»/`FormatCmd`, §5.46/§5.50) y no inventado |
