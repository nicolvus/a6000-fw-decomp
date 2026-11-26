# G22-REPRO — La cámara emulada y las fotos de la SD: árbol `AVF_INFO` y reproducción

**Estado (26-11-2026, sesión G22-REPRO-3): PARCIAL, corte localizado un tramo más adelante.** Con `SD_ESTRUCTURA=1` la SD emulada trae la estructura que el firmware nombra
(`AVF_INFO` con sus ficheros, `MP_ROOT/100ANV01`) y **el volumen deja de fallar por «no hay `AVF_INFO`»**: medido, `libmpr` consulta `ms:/AVF_INFO` y sigue con los ficheros del índice,
el manejador del recuento (`libmpr+0x620028`) se ejecuta y el montaje del sistema de ficheros termina `OK`.
**No se ha conseguido** que la tecla Reproducción abra la vista ni que el recuento de fotos salga numérico.
La sesión G22-REPRO-3 **corrige y avanza el corte** (§8): la tecla **sí** sale del driver — `0x1f7` → `InfraInput` → `snd_InfraInputEvent_to_InputServant` →
`InputService::createEvent(0x150100f2 pulsación / 0x150100f1 suelta)` → `InputService::pushFilterEvent` — y lo que no ocurre **ni para la Reproducción ni para ninguna otra tecla**
es el paso siguiente: `ActionEventMapBase::DispatchEvent` (`libObj+0xf59f0`) no recibe **ningún** evento `0x1501xxxx` y `ActionCheckerListBase::execAction` no se ejecuta nunca.
El invitado lo dice él mismo: `[FMWK] EventQueue pile count: 100` en el mismo instante de la pulsación (§8.3). Abrir la vista por la ruta del arnés sigue siendo posible pero **no pinta miniatura** (§8.4).
**G22-PBVISTA (26-11-2026)**: el módulo de la vista **sí** se carga bajo demanda (`dlopen(viewUnified3.so)` al abrir
`view/INDEX_PLAYBACK`); el eslabón que falta para pintar es el **modelo de contenidos** (`getModelInfo(@M00A =
model/MEDIA, 0) -> 0`) → [g22-pbvista-carga-bajo-demanda.md](g22-pbvista-carga-bajo-demanda.md).

Sesión: **26-11-2026** (reloj del anfitrión 02:30–05:30, −03). Cámara física: **no usada** (todo en `qemu-system-arm`, perfiles `repro`, `repro2`, `repro3`, `repro4` y `repro5`, puertos 8660/8661/8670/8671).
Espacio de direcciones: **VA del ELF** de `libmpr.so`/`libObj.so`/`viewUnified2.so` 3.21 (el primer `PT_LOAD` tiene vaddr 0; el segundo de `viewUnified2.so` lleva +0x8000,
por eso `.data` se cita por VA y no por desplazamiento de fichero); `TRACELIB`/`TRACEFN2` del shim usan el desplazamiento respecto a la base de la biblioteca.
Capturas: [disparo](img/g22-repro-disparo.png) · [tras pulsar Reproducción](img/g22-repro-tras-reproduccion.png) · [G22-REPRO-2 sin av-cam](img/g22-repro2-disparo.png) ·
[tras `O view/SINGLEPB`](img/g22-repro2-singlepb.png) · **G22-REPRO-3** [disparo con av-cam y la foto en la SD](img/g22-repro3-disparo.png) ·
[`O view/INDEX_PLAYBACK` en blanco](img/g22-repro3-indexpb-en-blanco.png).

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
- **Actualizado en G22-REPRO-2 (§7)**: medido, la clave `0x1f7` **sí** es la del firmware (`KEY_TACT_PLAY`) y su evento `0x150100f0` sale de la tabla de la vista;
  el mapa de teclas del arnés es correcto y el corte está **después** (acción 4 → `viewManagerIf::openView`, que no se llama). La inferencia de arriba sobre el
  índice de teclas queda **descartada**; la de que el recuento depende del índice AV sigue en pie.

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

| 12 | La clave que manda el arnés (`0x1f7`, índice `0x1f`) es la del firmware y se llama `KEY_TACT_PLAY` | **VERIFICADO** | `libObj` VA `0x10a6054`: `{0x1f7, puntero a "KEY_TACT_PLAY"}` (§7.1) |
| 13 | La vista registra `0x1f7` con el evento `0x150100f0` (y `0x1f0`→`0x15010050`, `0x3`→`0x15010070`) | **VERIFICADO** | tripletes `{0x7ffffffe, clave, evento}` en `viewUnified2.so` VA `0x4aa844` (§7.1) |
| 14 | Una tabla estática de `viewUnified2.so` manda el evento `0x150100f0` a la **acción `4`** (19 entradas) | **VERIFICADO** | tabla `.rodata` `0x3a03d4` + búsqueda `viewUnified2+0x1906a8` (desensamblado, §7.1) |
| 15 | `view/INDEX_PLAYBACK` se resuelve como `viewIndexPb.so` + `ViewIndexPbToInstance`; ese nombre de biblioteca no existe como fichero, y el símbolo solo lo exporta `viewUnified3.so` | **VERIFICADO** (triplete y símbolo) / **NO_VERIFICADO** (cómo resuelve el cargador: ningún nombre lógico de la tabla existe como fichero) | `viewUnified2.so` `.rodata` `0x3a14c1`/`0x3a14d5`/`0x3a14e4`; `dynsym` de las 157 bibliotecas (§7.1) |
| 16 | Al pulsar Reproducción, `viewManagerIf::openView` **no se llama** (el contador de la traza no sube) | **VERIFICADO** | `TRACEFN=1251fc` + `TRACEDEREF`: 2 pulsaciones, contador 3→3 (§7.2) |
| 17 | `openView("view/SINGLEPB")` y `openView("view/INDEX_PLAYBACK")` en caliente **entran** pero no vuelven en ≥5 s, y la pantalla queda en blanco (`0 listas`) | **VERIFICADO** | `TRACE 1251fc n=3/n=4` con la cadena en `r0`; sin línea `OPENHOT`; [captura](img/g22-repro2-singlepb.png) (§7.2) |
| 18 | El modelo, la indexación y la miniatura de la reproducción existen en el firmware (`ModelIndexPbToInstance`, `ModelSinglePbToInstance`…) | **VERIFICADO** | `dynsym` de `libObj.so` (§7.1) |
| 19 | La tecla `0x1f7` **despierta** al hilo `I-InputRecv` de la cola `0x7a0020`, pero no produce `[INPUTSERVICE] … key_code=0x1f7` ni llega a `DispatchEvent` como `0x150100f0` | **VERIFICADO** | `WAITLOG … tras 42758 ms` en 133.95 vs `tecla 0x1f7` en 133.91; 19 disparos de `libObj+0xf59f0` sin ese evento (§7.3) |
| 20 | En un arranque sin ciclo de cámara (`av-cam`), el manejador del recuento `libmpr+0x620028` **no se ejecuta** en 630 s del invitado (con la biblioteca cargada a los 37 s y las trampas armadas) | **VERIFICADO** | `TRACELIB libmpr.so base 0xad34d000` en 37.47 y 0 disparos de `620028`/`620262`/`62059c` (§7.3) |

---

## 6. Reproducir

```sh
mkdir -p ~/A6000-SD/DCIM/100MSDCF   # + una foto DSC00001.JPG (p. ej. 1536x1024 con PIL; en G22-REPRO-2: 222 164 B)
echo '{"sd":{"carpeta":"'$HOME'/A6000-SD"}}' > /tmp/cfg.json
SD_ESTRUCTURA=1 .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness \
  --perfil-dir repro --puerto 8650 --config /tmp/cfg.json
# a los ≈240 s: GET /eventos (PNG), POST /tecla {"k":"reproduccion","v":1|0}, POST /sd-volcado, POST /salir
```

`SD_ESTRUCTURA=1` es opt-in: sin la variable la imagen que recibe el invitado es **la de siempre** (el test lo fija).
Medido en este equipo con `amontonamiento` de VM (hasta 3 `qemu-system-arm` de otros perfiles): un arranque en frío tardó 250 s en dar la primera pantalla
y otro se quedó en 2 fotogramas sin av-cam — **INFERENCIA**: sin `--avcam` el ciclo de cámara no arranca y la UI no se pinta; no se atribuye al árbol FAT.

---

## 7. G22-REPRO-2: el camino de la tecla, estático y medido

Segunda sesión del pendiente (perfiles `repro2`/`repro3`, puertos 8660/8661). Objetivo: seguir `0x1f7` desde `InputService` hasta la acción que abre la vista de
reproducción y medir en el invitado dónde se corta. **Resultado**: el grafo estático queda cerrado hasta la **acción `4`** y el corte medido está **entre esa acción y
`viewManagerIf::openView`**, que no se llama. La vista en sí tampoco pinta en este arnés (§7.4).

### 7.1 Estático (VA del ELF; instrucciones leídas de los binarios, no de decompilador)

**(a) La clave.** `libObj.so`, tabla `{clave, nombre}`: en VA `0x10a6054` hay `{0x000001f7, puntero}` y el puntero apunta a la cadena `KEY_TACT_PLAY` (VA `0xd93851`).
Es la misma clave que `live.py` manda para el botón Reproducción (`TECLAS["reproduccion"] = (0x1F7, 0x1F)`), así que **el mapa de teclas del arnés no se toca**.

**(b) La clave → evento.** `viewUnified2.so`, `.data` (VA): la tabla de registro de `InfraInput` es una lista de tripletes `{0x7ffffffe, clave, evento}`; en `0x4aa844`
está `{0x7ffffffe, 0x000001f7, 0x150100f0}`. Los vecinos cuadran con las teclas ya medidas: `{0x7ffffffe, 0x1f0, 0x15010050}` (MOVIE) y `{0x7ffffffe, 0x3, 0x15010070}` (arriba).
Otra entrada compuesta, `{0x7ffffffe, 0x0a000022, 0x150100f0}`, manda al mismo evento.

**(c) El evento → acción.** `viewUnified2.so` tiene una tabla de 19 pares `{evento, acción}` en `.rodata` VA `0x3a03d4`, y la primera entrada es
`{0x150100f0, 4}`. La consume una búsqueda lineal en `viewUnified2+0x1906a8`:

```
1906a8  push {r4,r5,r7,lr}
1906ae  ldr  r2,[pc,#0x20]
1906b2  add  r2,pc                 ; r2 = 0x3a03d4 (tabla)
1906b4  ldr.w r5,[r2,r3,lsl #3]    ; evento de la entrada i
1906b8  cmp  r5,r0                 ; ¿es el evento pedido (r0)?
1906ba  bne  0x1906c6
1906bc  adds r2,r2,r4              ; entrada i
1906be  movs r0,#1
1906c0  ldr  r3,[r2,#4]            ; acción
1906c2  str  r3,[r1]               ; *out = acción
1906c4  pop  {r4,r5,r7,pc}         ; return 1
1906c6  adds r3,#1
1906c8  cmp  r3,#0x13              ; 19 entradas
1906ca  bne  0x1906ae
1906cc  movs r0,#0                 ; no encontrado
```

Las otras entradas de la tabla son las teclas de disparo (`0x15010020` semipulsación→1, `0x150102b0` S1→2, `0x15010030` S2→3, `0x15010050` MOVIE→6, `0x15010110` MENU→7,
`0x15040010`→8, diales `0x15070050`→5, cruceta `0x15020030/80/90/c0`→0x9d/0x9b/0x9e/0x9c, `0x15050040/50`→12). Que la reproducción sea la **acción 4** es el dato que
faltaba en §4.1.

**(d) La acción → vista.** El `ViewManager` guarda su mapa como tripletes de cadenas contiguas en `.rodata` de `viewUnified2.so` (102 tripletes):
`0x3a14c1 "view/INDEX_PLAYBACK"` → `0x3a14d5 "viewIndexPb.so"` → `0x3a14e4 "ViewIndexPbToInstance"`. Dos hechos que corrigen la hipótesis de §4.1:

- **Ninguno** de los nombres de biblioteca de los 102 tripletes existe como fichero en `/usr/lib` (157 ficheros, ninguno `view*Pb*.so` ni `viewFormat.so`…), y sin embargo
  `view/STLREC` sí abre en el invitado (§7.2). Es decir, **el nombre lógico no es el fichero**: la resolución real (¿`dlopen` con otro nombre?, ¿`dlsym(RTLD_DEFAULT)`
  sobre lo ya cargado?) **queda NO_VERIFICADA** y no se puede afirmar que la biblioteca «falte».
- Los **símbolos** sí están: `ViewIndexPbToInstance` lo exporta solo `viewUnified3.so` (398 464 B) y `ViewSinglePbToInstance` / `ViewSinglePb4KToInstance` los exporta
  el propio `viewUnified2.so`. Los modelos, en `libObj.so`: `ModelIndexPbToInstance`, `ModelSinglePbToInstance`, `ModelScrollSinglePbToInstance`, `ModelDlnaSinglePbToInstance`.
  Es decir, **no falta código del firmware**: falta saber quién llama a `openView` con esos nombres y con qué condición.

**(e) Quién debería abrirla.** Por partes, con lo medido:

- `viewUnified2.so` **no llama nunca** a `viewManagerIf::openView` ni a `ViewBase::openView`: de 59 182 llamadas a la PLT (1 478 destinos distintos, mapa
  `.rel.plt` → stub verificado), **cero** van a los stubs `0xe6724` (`openView(const char*, int)`) y `0xe5cc8` (`ViewBase::openView`). La vista **no** abre por su cuenta.
- El despachador está en `libObj.so` y sí tiene símbolos: `DefRootView::ActionEventMapBase::DispatchEvent(unsigned long)` = `libObj+0xf59f0` y
  `DefRootView::ActionCheckerListBase::execAction(int)` = `libObj+0x11817e` (`dynsym`, Thumb). El camino esperado es **evento → `DispatchEvent` → acción (4) →
  `execAction` → acción concreta de la vista → `openView` con el nombre del mapa**, y la condición para llegar es que la acción 4 esté registrada/en disposición
  (`IsReadyExec`) en la vista activa. Este tramo es **INFERENCIA** con el despachador **VERIFICADO como símbolo**, no como flujo.
- El llamador concreto de `openView` **no se ha localizado**: no hay referencia literal (ni `ldr` de pool, ni `movw/movt`, ni `add pc`) desde `.text` a las cadenas del
  `ViewManager`, así que la tabla se consume por índice/estructura (probablemente desde `initializeViewConfig`), y la función `0x1906a8` no recibe ningún `bl` directo.

### 7.2 Medido en el invitado (perfil `repro2`, puerto 8660, arranque en frío 155 s)

```sh
HOME=/tmp/g22r/home SD_ESTRUCTURA=1 \
SHIMEXTRA="WAITLOG=5000 TRACEFN=1251fc,114104 TRACEDEREF=d0:0:18 TRACEREP=1 TRACEMAX=8 \
TRACELIB=libmpr.so TRACEFN2=620028,620262,62059c GMILOG=1 SETLOG=1" \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir repro2 --puerto 8660 --config /tmp/g22r/config-repro2.json
```

`libObj+0x1251fc` es `viewManagerIf::openView(const char*, int)`; `TRACEDEREF=d0:0:18` vuelca 18 palabras desde `r0`, que es la cadena del nombre:

```
570.48  TRACE 1251fc n=1  r0=13752f0  r1=0    -> DEREF "view/ROOT"        (arranque, OPENVIEW)  OPENVIEW view/ROOT -> 0
586.76  TRACE 1251fc n=2  r0=13752fa  r1=3    -> DEREF "view/STLREC"      (arranque)            OPENVIEW view/STLREC -> 20502056
643.10  WAITLOG 173.60 tecla 0x1f7            (pulsación Reproducción)
644.24  WAITLOG 174.74 tecla 0x1f7            (suelta)
697.04  WAITLOG 225.28 tecla 0x1f7            (segunda pulsación)
698.15  WAITLOG 226.39 tecla 0x1f7
626.44  TRACE 1251fc n=3  r0=13e0b18  r1=0    -> DEREF "view/SINGLEPB"    (orden «O» en caliente)
671.93  TRACE 1251fc n=4  r0=13e2430  r1=0    -> DEREF "view/INDEX_PLAYBACK" (orden «O» en caliente)
```

- **La tecla llega**: dos líneas `tecla 0x1f7` por pulsación (bajada y suelta) en la cola del driver `0x7a0020`.
- **Y no abre nada**: el contador de `openView` se queda en 3 entre las dos pulsaciones (líneas 143 y 155, antes y después de las teclas de 643/697). **Medido**: la
  cadena se corta **antes** de `viewManagerIf::openView`, no en el `ViewManager`.
- **En caliente sí se llama**: `O view/SINGLEPB` y `O view/INDEX_PLAYBACK` entran en `openView` con la cadena correcta (arriba). Pero **no hay línea `OPENHOT`** (el shim la
  escribe al volver de la llamada) ni 5 s después, y la pantalla pasa a **`0 listas` / PNG en blanco** ([captura](img/g22-repro2-singlepb.png)) mientras el invitado sigue
  pintando a 1,5 fps: es decir, `openView` **no vuelve** en esas condiciones (INFERENCIA: espera a que la vista se construya y algo no llega).
- **Aviso de comparabilidad**: en este worktree **no está `analysis/rea-independent/input/av-cam.bin` ni `liro.ko`**, así que `avcam_disponible()` es falso y `live.py`
  arrancó **sin av-cam**. El OSD sale casi vacío ([captura](img/g22-repro2-disparo.png): solo el icono `P` y un icono, **2 listas**) frente a las 33–35 listas del registro
  de §3; por eso el efecto colateral `AF-S`→`MF` de [film-pb-1-sub-arnes-galeria](../reports/film-pb-1-sub-arnes-galeria-20261126.md) **no se ha reproducido aquí** y
  queda NO_VERIFICADO en esta sesión. La conclusión de (c) no depende de eso: el corte está antes de `openView` en ambos casos.

### 7.3 Medido con las tres trampas y `WLALL=1` (perfil `repro3x`, puerto 8665, invitado hasta 630 s)

El arranque bueno para diagnóstico es con `TRACEFN=f59f0,11817e,1251fc` (`libObj`: despachador de acciones, `execAction` y `openView`), `TRACELIB=libmpr.so
TRACEFN2=620028,620262,62059c` (recuento), `TRACEDEREF=d0:0:18 TRACEREP=1 TRACEMAX=16 WLALL=1 GMILOG=1 SETLOG=1`. Lo medido:

```
37.45  dlopen(libmpr.so) -> 0x1d3c4f0
37.47  TRACELIB libmpr.so base 0xad34d000          <- las trampas del recuento se arman al cargar la biblioteca
70.38  FsysMount /dev/mmca ... Fsys_MountAsync("/dev/mmca") OK 'A'
91.07  [INPUTSERVICE] toActive:3515 insert key_code=0x00000002 event_code=0x15010010   <- entrada activa (tecla de encendido)
133.91 tecla 0x1f7                                   (pulsación Reproducción, escrita en la cola 0x7a0020)
133.95 WAITLOG fin tid 282 I-InputRecv uipc7 id=0x7a0020 tmo=-1 tras 42758 ms   <- la espera del hilo de entrada TERMINA con la tecla
135.03 tecla 0x1f7                                   (suelta)
         sin línea [INPUTSERVICE] con key_code=0x1f7
         19 × TRACE f59f0 (DispatchEvent): r1 = 2, 8, 0x23, 0x2a, 0x11012001, 0x11014001, 0x11012004 … ninguna 0x150100f0
         0 × TRACE 11817e (ActionCheckerListBase::execAction) en 630 s
         0 × TRACE 620028 / 620262 / 62059c en 630 s
```

- **La tecla llega al firmware**: el hilo `I-InputRecv` estaba esperando en la cola `0x7a0020` y su espera **acaba en el mismo instante** en que el shim escribe la tecla
  (`tras 42758 ms` en 133.95 frente a `tecla 0x1f7` en 133.91). No es un problema de entrega del arnés.
- **Pero no se traduce**: no aparece la línea `[INPUTSERVICE] … key_code=0x1f7` que sí sale con la tecla de encendido (`0x2`), y el despachador de acciones
  (`libObj+0xf59f0`, `DispatchEvent`) recibe eventos internos (`2`, `8`, `0x23`, `0x2a`, `0x1101xxxx`) **nunca `0x150100f0`**. El corte medido está, por tanto,
  **entre el hilo de entrada y el despachador**, antes de la acción 4. `r1` es el evento en esa función (el `r0` es `this`): dato para la próxima traza.
- **`execAction` no se usa en este arranque** (0 disparos): el camino de acciones de `DefRootView` que se suponía en §7.1(e) **no se ejecuta** con esta UI.
- **El recuento tampoco**: con `libmpr` cargada a los 37 s y las tres direcciones armadas, **ninguna dispara en 630 s**, mientras que en el arranque de §3
  (mismo árbol de SD, con ciclo de cámara) `620028` salía a los ≈397 s. Es decir: en este perfil el manejador del recuento **no llega a ejecutarse**; la diferencia
  medida entre los dos arranques es el ciclo de cámara (`av-cam`), que aquí no está (INFERENCIA). Sigue sin medirse si la fórmula `0x620262`/`0x62059c` corre.

### 7.4 La vista de reproducción: qué haría falta (medido + estático)

- `openView("view/INDEX_PLAYBACK")` y `openView("view/SINGLEPB")` **se aceptan** (la llamada entra con el nombre correcto) y la pantalla queda en blanco: la vista no
  llega a pintar ni una lista. Con `GMILOG=1` **no aparece ni una sola petición `getModelInfo`** de esa vista, así que se descarta que se quede esperando un modelo por
  nombre: sale antes de pedirlo.
- El índice AV sigue siendo el candidato para el contenido: `AVF_INFO/AVIN0001.INP`, `.BNP`, `.INT`, `PRV00001.BIN` y `STAT0000.BIN` los crea hoy el arnés **de 0 B** y la
  cámara no los rellena (§4.2, volcado del disco del invitado). Sin un índice real no hay «contenidos» que listar; **no se ha inventado formato**.
- Lo que **no** falta: los símbolos de las vistas y los modelos están en el firmware (§7.1d).

### 7.5 Lo que queda por medir (siguiente paso exacto)

1. **¿Se genera el evento, y qué acción se ejecuta?** Arranque en frío con `TRACEFN=f59f0,11817e,1251fc TRACEDEREF=d0:0:18 TRACEREP=1 TRACEMAX=8` (`TRACEFN` es de
   `libObj`) y pulsar Reproducción. `libObj+0xf59f0` = `DefRootView::ActionEventMapBase::DispatchEvent` (`r0` = evento), `libObj+0x11817e` =
   `ActionCheckerListBase::execAction` (`r0` = acción) y `libObj+0x1251fc` = `viewManagerIf::openView` (`r0` = nombre). Los tres juntos dicen en una sola pasada si el
   evento llega a la vista, qué acción sale y si se acaba abriendo; si `DispatchEvent` no recibe `0x150100f0`, el corte está antes, en `InfraInput`/`InputService`
   (`libObj+0x114104`, `+0x113d2c` `activate`, `+0x113c1c` `UpdateInputTable`). En esta sesión se intentó **en caliente** (`E TRACELIB`/`E TRACEFN2` sobre
   `viewUnified2+0x1906a8`) y no hubo confirmación de armado (el `LOG` del rearme no se reenvía sin `WLALL`), así que el intento **no cuenta como medición**.
2. **Contenido del índice AV**: hace falta un `AVIN0001.INP` de una tarjeta real de A6000 (no hay ni un byte en el repo) o que el propio MPR lo genere
   (`FormatCmd`/«Formatear», §5.46/§5.50). Con eso se repite `O view/INDEX_PLAYBACK` y se compara.
3. **`openView` que no vuelve**: repetir `O view/SINGLEPB` con `WATCH=1251fc`/`DUMPAT` y `RCVSTACK=1` para ver en qué cola se queda (la orden «O» se lanza en su propio
   hilo, así que el bloqueo no rompe la UI).
4. **El recuento (`0x620262`/`0x62059c`)**: en la sesión `repro2` se armaron `TRACEFN2=620028,620262,62059c` con `TRACELIB=libmpr.so`, pero **`libmpr.so` no llegó a
   mapearse**: no hay línea de armado `TRACELIB … base …` ni ningún disparo, porque la sesión terminó a los ≈230 s del invitado y las consultas de `libmpr` empiezan a los
   ≈348 s (§3). No es un negativo: es una medición **no hecha**. El arranque que la cierra es el mismo de §7.2 con `WLALL=1` (para ver la línea de armado) y dejándolo correr
   hasta los ≈450 s del invitado.

---

## 8. G22-REPRO-3: la tecla sale del driver y muere en la cola de eventos de `InputService`

Tercera sesión (perfiles `repro4`/`repro5`, puertos 8670/8671; `--avcam` **activo**: el worktree enlaza `analysis/rea-independent/input/av-cam.bin` y
`analysis/camera-extract/usr/kmod/liro.ko`, que no se versionan). Objetivo: cerrar el tramo que §7.3 dejaba abierto. **Resultado**: el corte medido se mueve **un eslabón más adelante**
y deja de ser específico de la Reproducción; la vista de reproducción se abre por la ruta del arnés pero **no pinta**.

### 8.1 Estático nuevo (VA del ELF, leído de los binarios)

**(a) Las listas de teclas y sus grupos.** `viewUnified2.so` describe sus listas de `_InfraInputKeyList` en una tabla de descriptores de **20 B** en `.data` VA **`0x4aa59c`**:
`{puntero a la lista, callback, nº de entradas, 0, 0}`. El **índice** de esa tabla es el *grupo* que se pasa como primer argumento de
`InfraInput::SetEventKeyList(int grupo, _InfraInputKeyList*, int n)` (`libObj+0x806140`):

| grupo | lista | callback | entradas | contenido (12 B por entrada) |
|---|---|---|---|---|
| 7 | `0x4aa914` | `0x1816d5` | 202 | lista de la vista de disparo: `[0]={0xa7,0x15010030}`, `[1]={0x2,0x15010010}`, `[2]={0x1f1,0x15010020}` … **sin `0x1f7`** |
| 8 | `0x4aa87c` | `0x1816b5` | 8 | teclas de mando: `{0x708d,0x15060010}`, `{0x18000001,0x150700c0}` … |
| 0xf | `0x4aa848` | `0x181a3d` | 4 | **grupo de la Reproducción**: `{0x1f7,0x150100f0,0x7ffffffe}`, `{0x7095,0x15010120,…}`, `{0xa000022,0x150100f0,…}`, `{0xa00001c,0x15010120,…}` |

La cuenta de los descriptores coincide **una a una** con las llamadas medidas en el invitado (§8.2): grupos 7→202, 8→8, 9→5, 0xa→6, 0xb…0xe→1, 0xf→4, 0x10→1, 0x11→1.

**(b) CORRECCIÓN de §7.1(b).** La entrada de `_InfraInputKeyList` es **`{clave, evento, máscara}`** (12 B), no `{máscara, clave, evento}`. El triplete `{0x7ffffffe, 0x1f7, 0x150100f0}` que cita §7.1 está
desplazado una palabra: `0x7ffffffe` es la **máscara final de la entrada anterior** (lista del grupo 8, en `0x4aa844`) y la entrada de la Reproducción empieza en `0x4aa848`, con la máscara `0x7ffffffe` en
la **tercera** palabra. `0x7ffffffe` = «sin condición» y lo llevan las cuatro entradas del grupo `0xf`.

**(c) CORRECCIÓN de §7.1(e)/§7.3.** `DefRootView::ActionEventMapBase::DispatchEvent(unsigned long)` (`libObj+0xf59f0`) es un **thunk virtual de 12 B**: la conversión evento → acción **no** está en
`libObj`, la hace la implementación virtual que registra la biblioteca de la vista (`evento` en `r1`, `this` en `r0`):

```
f59f0  ldr r3,[r0]        ; vtable del objeto
f59f2  push {r7, lr} / add r7, sp, #0
f59f6  ldr r3,[r3,#8]     ; ranura +8
f59f8  blx r3             ; implementación real (viewUnified2/viewUnified3)
```

**(d) El log `insert key_code=…` no es por pulsación.** `InputService::UpdateInputTable` (cuerpo en `0x113718`) llama a `SetEventKeyList` en `0x113c1c` y recorre las entradas de la lista; la línea
`[INPUTSERVICE] toActive:3515 insert key_code=0x%08x event_code=0x%08x` (`0x113c72`) **solo se imprime para entradas cuyo primer campo vale 2** (`cmp r3,#2` en `0x113c46`) y se emite **al registrar** la
lista. Su ausencia con `0x1f7` (§7.3) **no** prueba que la tecla no llegue.

### 8.2 Medido: la tecla SÍ sale del driver y llega a `InputService` (VERIFICADO)

Perfil `repro5`, puerto 8671, SD con `AVF_INFO` y `DSC00001.JPG` (1536×1024, 51 356 B), arranque en frío 132 s hasta la primera pantalla, 4,5 fps:

```sh
HOME=/tmp/g22r3/home SD_ESTRUCTURA=1 SHIMEXTRA="WAITLOG=5000 \
TRACEFN=806140,805804,110138,1106b8,110a04,110b14,1117f4,f59f0,11817e,1251fc TRACEREP=1 TRACEMAX=12 WLALL=1 GMILOG=1 SETLOG=1" \
  .venv/bin/python scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir repro5 --puerto 8671 --config /tmp/g22r3/config.json
```

```
616.10 TRACE 806140 n=7  r1=7 r3=ca       <- grupo 7, 202 entradas (desde libObj+0x113c20 = UpdateInputTable)
616.11 TRACE 806140 n=8…n=10 r1=8,9,a  r3=8,5,6
616.14 TRACE 806140 n=11…n=14 r1=b,c,d,e r3=1,1,1,1
616.25 TRACE 806140 n=15 r1=f r3=4        <- ¡el grupo 0xf (la Reproducción) SÍ queda registrado!
616.28 TRACE 806140 n=16,n=17 r1=10,11 r3=1,1
668.71 WAITLOG 135.24 tecla 0x1f7         <- pulsación Reproducción
668.71 TRACE 110138 n=2 r1=0 r2=4   lr=libObj+0x11303c   <- snd_InfraInputEvent_to_InputServant
668.71 TRACE 1106b8 n=2 r1=150100f2 r2=4                 <- InputService::createEvent (pulsación, estado 2)
668.71 TRACE 1117f4 n=2 r1=…                             <- InputService::pushFilterEvent
668.72 135.79 TRAZA # [FMWK] EventQueue pile  count: 100  <- el propio invitado: cola de eventos llena
668.72 WAITLOG 135.75 tecla 0x1f7         <- suelta
668.72 TRACE 110138 n=3 · TRACE 1106b8 n=3 r1=150100f1 (suelta) · TRACE 1117f4 n=3
```

Con `O view/INDEX_PLAYBACK` abierta la pulsación se repite igual (755.34 → `0x150100f2`, 755.73 → `0x150100f1`). **Control con otras teclas** (misma sesión): `arriba` (`0x3`) → `createEvent 0x15010072` y
`0x15010071`; `menu` (`0x1ab`) → `0x15010074`. La conversión clave → evento funciona para todas y el evento es `0x150100f0 + estado` (`…f1` suelta, `…f2` pulsación; `…71/72` para `0x3`).

Extractos versionados de estas dos medidas (el `shim.log` completo son 2,3 MB y no se versiona):
[`trazas-tecla-repro5.txt`](../../reports/evidence/g22-repro3-20261126/trazas-tecla-repro5.txt) y
[`registro-listas-repro5.txt`](../../reports/evidence/g22-repro3-20261126/registro-listas-repro5.txt).

### 8.3 Dónde se corta ahora (VERIFICADO)

- `DispatchEvent` (`f59f0`) se dispara 64+ veces en 800 s y **ninguna** con un evento `0x1501xxxx`: `r1` = `0x42,0x43,0x44,0x45,0x46,0x47,0x54,0x5a` (identificadores pequeños, de la vista),
  `0x2,0x23,0x2a` y `0x11012001,0x11012007,0x11014001`, siempre desde `viewUnified2.so+0x198450` (una vez desde `viewUnified2.so+0x17e068`). A `DispatchEvent` le llegan
  **identificadores internos de la vista**, no eventos de `InputService`.
- `ActionCheckerListBase::execAction` (`libObj+0x11817e`): **0 disparos** con cualquier tecla.
- El corte medido está **entre `InputService::pushFilterEvent` (`0x1117f4`) y la vista**: el evento se construye (`createEvent`) y se encola, y no hay quien lo despache. El invitado lo dice él mismo
  (`[FMWK] EventQueue pile count: 100`, cadena en `libObj` VA `0xd8810a`) en el mismo instante de la pulsación — **INFERENCIA**: la cola del framework está saturada y el alta se descarta.
- **CORRECCIÓN de §7.3**: no es cierto que la tecla muera «entre el hilo de entrada y el despachador»; el hilo `I-InputRecv` la entrega, `InfraInput` la convierte y `InputService` la encola. Y **no es
  específico de la Reproducción**: ninguna tecla llega al mapa de acciones.

### 8.4 La vista de reproducción por la ruta del arnés (abre; no pinta)

`O view/INDEX_PLAYBACK` en caliente: `TRACE 1251fc n=3` (entra en `viewManagerIf::openView`) y la pantalla pasa a **0 listas** y un PNG de **un solo color**
([captura](img/g22-repro3-indexpb-en-blanco.png)). `O view/SINGLEPB`: `OPENHOT view/SINGLEPB 0 -> 33156776` (**esta vez sí vuelve**, al contrario que en §7.2) y también queda en blanco. En los dos casos,
con `GMILOG=1`, la vista **no pide ni un `getModelInfo`**: no se queda esperando un modelo por nombre, no llega a pintar. **Conviene decirlo claro: este camino es del arnés** (`openhot` llama a
`viewManagerIf::openView` desde un hilo del shim), **no de la cámara**. La miniatura de `DSC00001.JPG` **no se ha conseguido**; el candidato sigue siendo el contenido del índice AV (§4.2, §7.4), del que no
hay ni un byte real en el repo.

### 8.5 Trampa de medición que hay que evitar (VERIFICADO)

`TRACEDEREF` vuelca palabras desde un registro **sin comprobar que sea un puntero**. En el perfil `repro4` se armó `E TRACEDEREF=d2:0:27` y la traza siguiente fue `110138` con `r2=4`: el volcado leyó en la
dirección 4 dentro del manejador de SIGILL, el invitado quedó congelado (`sig 11 tid 476 I-InputEvent`, 9 fotogramas y el `shim.log` sin una línea más) y hubo que repetir el arranque en frío.
Regla para esta ruta: **sin `TRACEDEREF`**, o con un registro que siempre sea un objeto (`r0` = `this`).

### 8.6 Afirmaciones nuevas

| # | Afirmación | Etiqueta | Evidencia |
|---|---|---|---|
| 21 | `_InfraInputKeyList` es `{clave, evento, máscara}` de 12 B y el grupo `0xf` de `viewUnified2.so` es la lista de la Reproducción (`0x1f7`→`0x150100f0`) | **VERIFICADO** | tabla de descriptores `.data` VA `0x4aa59c` (§8.1a) |
| 22 | El invitado **registra** el grupo `0xf` y los demás (17 llamadas, grupos 1…0x11) y las cuentas coinciden con los descriptores | **VERIFICADO** | `TRACE 806140 n=7…n=17` (§8.2) frente a §8.1a |
| 23 | Pulsar Reproducción produce `InputService::createEvent(0x150100f2)` + `pushFilterEvent`; la suelta, `0x150100f1` | **VERIFICADO** | `TRACE 1106b8`/`1117f4` en 668.71/668.72 y 755.34/755.73 (§8.2) |
| 24 | `DispatchEvent` no recibe **ningún** evento `0x1501xxxx` y `execAction` no se ejecuta nunca, tampoco con otras teclas | **VERIFICADO** | 64+ disparos de `f59f0` con ids internos; 0 de `11817e` (§8.3) |
| 25 | El invitado avisa de la cola de eventos llena en el instante de la pulsación | **VERIFICADO** | `[FMWK] EventQueue pile count: 100` (§8.3) |
| 26 | Quién vacía esa cola y por qué no lo hace en este arnés | **NO VERIFICADO** | — |
| 27 | `DispatchEvent` es un thunk virtual de 12 B: la conversión evento→acción vive en la biblioteca de la vista | **VERIFICADO** | desensamblado `libObj+0xf59f0…0xf59fa` (§8.1c) |
| 28 | `O view/INDEX_PLAYBACK` y `O view/SINGLEPB` abren pero no pintan ni piden modelo | **VERIFICADO** | PNG de un color, `OPENHOT … -> 33156776`, 0 `getModelInfo` (§8.4) |
| 29 | La miniatura de la foto de la SD pintada por la vista de reproducción | **NO VERIFICADO** | no se ha logrado por ninguna de las dos rutas (§8.3, §8.4) |

### 8.7 Siguiente paso exacto

1. **Quién vacía la cola de eventos.** `pushFilterEvent` (`0x1117f4`) encola con `bl 0x127bb6` y notifica con `0x127bc4`; el consumidor está al otro lado. Medir con
   `TRACEFN=127bb6,127bc4,1114b0,11113e,f59f0` (sin `TRACEDEREF`) y comprobar si el consumidor se ejecuta; si no, identificarlo por el nombre de hilo en los `WAITLOG` con `WLALL=1`
   (en el informe de pila de §8.5 aparece `I-InputEvent`) y ver en qué cola espera.
2. **La cola llena.** Localizar el código de `[FMWK] EventQueue pile count: %d` (cadena en `libObj` VA `0xd8810a`, **sin** xref literal: se llega por tabla; usar REA o `TRACEFN` sobre el
   framework de eventos) y leer el máximo (100) y qué condición la descarga.
3. Cuando drene, repetir la pulsación y leer `TRACE f59f0 … r1=150100f0` y `TRACE 1251fc` con `r0` = `view/INDEX_PLAYBACK`: eso cierra el tramo de la tecla.

---

## PARA PENDIENTES.md

| ID | Estado | Resumen | Criterio de cierre |
|---|---|---|---|
| G22-REPRO | EN CURSO (abierto 26-11-2026; **2.ª sesión G22-REPRO-2 y 3.ª G22-REPRO-3, 26-11-2026**) | **Árbol de la SD con `AVF_INFO` (opt-in `SD_ESTRUCTURA=1`)**: `sd_image.py` crea `AVF_INFO/{AVIN0001.INP,AVIN0001.BNP,AVIN0001.INT,PRV00001.BIN,STAT0000.BIN}` (0 B, contenido no inventado) y `MP_ROOT/100ANV01`; tests en `tests/test_gui_sd_image.py`. **MEDIDO (1.ª sesión)**: `libmpr` consulta `ms:/AVF_INFO` y el manejador del recuento `libmpr+0x620028` se ejecuta con la UI sana (`Fsys_MountAsync OK`). **NUEVO (2.ª sesión, estático VERIFICADO)**: el camino de la tecla queda cerrado hasta la acción: `0x1f7` = `KEY_TACT_PLAY` (`libObj` VA `0x10a6054`) → evento `0x150100f0` (`viewUnified2.so` `.data` VA `0x4aa844`) → **acción 4** (tabla `.rodata` `0x3a03d4`, búsqueda `viewUnified2+0x1906a8`); el `ViewManager` da `view/INDEX_PLAYBACK` → `viewIndexPb.so` + `ViewIndexPbToInstance` (símbolo exportado solo por `viewUnified3.so`; los 102 nombres de biblioteca de la tabla **no** son ficheros de `/usr/lib`, resolución NO_VERIFICADA) y los modelos están en `libObj` (`ModelIndexPbToInstance`, `ModelSinglePbToInstance`). **MEDIDO (2.ª sesión, invitado)**: la tecla llega a la cola `0x7a0020` (2 líneas `tecla 0x1f7`) y **`viewManagerIf::openView` no se llama** (contador `TRACE 1251fc` 3→3); `O view/SINGLEPB` y `O view/INDEX_PLAYBACK` **entran** en `openView` con la cadena correcta pero **no vuelven** en ≥5 s (sin línea `OPENHOT`) y la pantalla queda en blanco (`0 listas`). En este worktree no hay `av-cam.bin`/`liro.ko`: el OSD sale con 2 listas y el efecto `AF-S`→`MF` no se ha reproducido (no comparable con §3). **Sigue fallando**: (a) el tramo acción 4 → `openView` (no localizado el llamador; no hay referencia literal a las cadenas del `ViewManager` desde `.text`); (b) el recuento de fotos sin número y el aviso `ERROR` de tarjeta; falta medir si `0x620028` llega a la fórmula (`0x620262`/`0x62059c`) con `TRACEFN2` armado en el arranque; (c) el contenido real del índice AV. **MEDIDO (3.ª pasada, `repro3x`, `WLALL=1`, tres trampas)**: la tecla **despierta** al hilo `I-InputRecv` de `0x7a0020` (`WAITLOG … tras 42758 ms` en 133.95 vs `tecla 0x1f7` en 133.91) pero **no** produce `[INPUTSERVICE] … key_code=0x1f7` ni llega a `DispatchEvent` (`libObj+0xf59f0`, 19 disparos con eventos internos, ninguno `0x150100f0`; el evento va en `r1`), así que el corte medido está **entre el hilo de entrada y el despachador**, antes de la acción 4; `execAction` (`libObj+0x11817e`) no se llama en ese arranque. Sin ciclo de cámara el recuento **no llega a ejecutarse**: `620028`/`620262`/`62059c` armadas a los 37 s y 0 disparos en 630 s, frente a los ≈397 s del arranque de §3 (la diferencia medida es `av-cam`, sin verificar). Tests nuevos sin QEMU: `tests/test_g22_repro.py` (8 casos). **MEDIDO (3.ª sesión, `repro5`, puerto 8671, con `av-cam`)**: la tecla **sí** sale del driver — `0x1f7` → `InfraInput` → `snd_InfraInputEvent_to_InputServant` → `InputService::createEvent(0x150100f2)` / `(0x150100f1)` → `pushFilterEvent` — y el corte medido está **después** de `InputService`: `DispatchEvent` (`libObj+0xf59f0`) 64+ disparos, **ninguno** con evento `0x1501xxxx`, y `execAction` (`+0x11817e`) **0** disparos, igual con `arriba` y `menu` (no es específico de la Reproducción); el invitado registra el grupo de teclas `0xf` (`TRACE 806140 n=15 r1=f r3=4`) y avisa `[FMWK] EventQueue pile count: 100` en el instante de la pulsación. **Estático nuevo**: la tabla de descriptores de `_InfraInputKeyList` de `viewUnified2.so` está en `.data` VA `0x4aa59c` (20 B por entrada, el índice es el grupo; grupo 7 = 202 entradas de la vista de disparo, grupo `0xf` = 4 entradas con `{0x1f7,0x150100f0,0x7ffffffe}`) y la entrada es **`{clave, evento, máscara}`** (corrige §7.1b); `DispatchEvent` es un thunk virtual de 12 B (corrige §7.1e); el log `insert key_code=…` se emite al **registrar** la lista y solo para entradas con primer campo 2 (corrige §7.3). `O view/INDEX_PLAYBACK` y `O view/SINGLEPB` abren por la ruta del arnés (`OPENHOT … -> 33156776`) y **no pintan** (PNG de un color, 0 `getModelInfo`): ese camino es del arnés, no de la cámara. Tests nuevos sin QEMU: `tests/test_g22_repro.py` (13 casos). | PNG de `view/INDEX_PLAYBACK` (o `SINGLEPB`) con la miniatura de `DSC00001.JPG` de la SD emulada **y** OSD de disparo con recuento numérico (sin `ERROR`); si el índice es imprescindible, con un `AVIN0001.INP` cuyo contenido venga de una tarjeta real (o generado por el propio MPR, p. ej. arreglando «Formatear»/`FormatCmd`, §5.46/§5.50) y no inventado |
