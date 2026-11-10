# G22-B — Arnés de la UI: `im.elf` de la cámara bajo QEMU

**Estado (09-11-2026): PARCIAL, reproducible.** El userland de la A6000 (firmware 3.21: `nflasha7` + `/usr` = `nflasha15`) arranca en
`qemu-system-arm` con un kernel genérico y una capa `LD_PRELOAD` (`sonyshim.so`) que sustituye los módulos de kernel de Sony. `im.elf`
vive > 2 min, carga 47 módulos (hasta `libSyncAndroid`) y recibe respuesta del servicio `0xd9016e`; **no llega a `appFw.so` ni dibuja**:
`grm_init` (libObj) espera a un trabajador que inicializa la pila EGL/GLES del GPU de DMP, inexistente en QEMU (§5).

Fuente de detalle histórico: entradas «G22-B avance 1–17» del registro de cambios de [PENDIENTES](../PENDIENTES.md). Este documento
las consolida, registra la auditoría del 09-11-2026 (§6) y fija el plan para completar el arnés (§7).

## 1. Para qué sirve

Ejecutar la interfaz real de la cámara sin cámara: probar los `nflasha15` modificados (menú Silent G10, Picture Profile G15–G27,
secciones nuevas G12) antes de instalarlos, observar qué pide la UI al «kernel» y, cuando se resuelva §5, capturar la pantalla
emulada. Es el único camino para verificar menús sin arriesgar la unidad (cada instalación fallida costó una recuperación: G11).

## 2. Arquitectura (VERIFICADO en ejecución, 09-11-2026)

| Pieza | Qué es | Fichero |
|---|---|---|
| Máquina | `qemu-system-arm -M virt -cpu cortex-a15 -smp 8 -m 1536`, consola `ttyAMA0`, `-no-reboot`; `-smp > 8` no arranca (GICv2) | `scripts/gui/harness/run.py` |
| Kernel + initrd | Instalador *netboot* de Debian 13 (trixie) armhf: `vmlinuz` 6.12.107+deb13-armmp e `initrd.gz` (busybox + módulos). El `init` se sustituye: monta `proc/sys/dev`, los *bind-mounta* en `/cam`, `tmpfs` en `/cam/tmp`, ejecuta `/cam/harness.sh` y apaga | `build_base.py` |
| Rootfs de la cámara | `/cam` = `nflasha7_unpacked_unpacked` con `/usr` = `nflasha15_unpacked_unpacked` (fw 3.21, `libObj.so` md5 `eb12512e…`); enlaces de *soname* que el extractor no conserva, bit de ejecución restaurado, `ld-linux.so.3 → ld-2.11.2.so` | `build_base.py` |
| Overlay | cpio.gz concatenado al base: `/cam/harness.sh` (guion), `/cam/harness.env` (`SHIMENV`), `/cam/usr/lib/sonyshim.so`, `/cam/usr/share/bk.tbl` | `run.py`, `setup.sh` |
| Shim | `sonyshim.c` compilado con `clang --target=armv7-linux-gnueabi -mfloat-abi=softfp`, cabeceras Debian (`libc6-dev` 2.44, `linux-libc-dev` 7.3.3) y **enlazado contra la glibc 2.11.2 de la cámara** (`-nostdlib`, `-l:libc-2.11.2.so`…) | `shim/build.sh` |
| Datos de NVRAM | `bk.tbl` = registros `{id, len, datos}` generados del volcado `20261105-volcado-total-nvram/backup_flash.bin` con `pmca.backup` | `gen_bk.py` |

### 2.1 Qué sustituye el shim

`libosal_uipc.so` es la OSAL de usuario: las colas con bit `0x8000` viven en memoria compartida (futex); las demás van al kernel por
`ioctl` sobre `/dev/uipc`. El shim abre `/tmp/uipc.shm` (512 KiB, `[+0x10]=8` hilos proxy) en lugar de `/dev/uipc` y atiende los índices:

| idx | Operación | Modelo |
|---|---|---|
| 0x10 | connect | `{0x80000, 0x20000, 0x8000, 0}` (valores de `__k_4u_connect`) |
| 0 / 1 / 2 | stat / wai / sig sem | Semáforos propios (cuenta inicial 1; `0x83037a` = señal de salida de `im.elf`, inicial 0); aviso `BLOQUEO sem` tras 8 s sin señal |
| 3 | stat_msgq | devuelve 0 y lo registra |
| 4 | snd_msg | `0x8f0139/a` trazas (texto) · colas con callback registrado → se entrega a un hilo proxy (idx 13) · `ACKQ` (por defecto `d9016e,7a0029,61003c`): acuse genérico a la cola dinámica que viaja en el cuerpo (cabecera `0x61003c`, estado 0) · resto: descartado y registrado |
| 5 | snd_sync_msg | colas con callback registrado → devuelve `{cb,arg}` y el emisor llama `cb(msg,arg)` en su hilo (`__osal_finish_sync_cb` lo cierra con la 2.ª llamada) · `0x8f013a` trazas · `0x3e014d` **backup** (op 0 tamaño, 3 lectura, 4 lectura de 4 B, 8 escritura descartada; datos de `bk.tbl`) · `0x14c0424` **dmm** (código 7: área por nombre → phys desde `0x80000000`, 64 MiB por área) |
| 6 | snd_sync_direct | responde 0 (`0x910042`… sin modelar) |
| 7 | rcv_msg | colas dinámicas (`dynamic_id` tipo `0x2a`) leen su buzón con el *timeout* pedido; las demás «duermen» y devuelven `E_TMOUT` |
| 10 / 11 | valloc / free | reserva `tamaño+0x240` con cabecera de 0x20; `free` no libera (fuga aceptada) |
| 12 | dynamic_id | tipo `0x32` semáforo y `0x2a` cola: id `(grupo<<16)|n` |
| 8 / 9 | reg / unreg_msg_queue_cb | tabla `cbs[]`: `(qid, arg=t[0], cb=t[1])`; el registro **síncrono** (`t[3]==1`) lleva el argumento en `t[2]` (`MWF::EventWrapper`) |
| 13 | wait_cb | el proxy espera una entrega y vuelve con `{cb, arg, msg}` (`libosal_uipc` llama `cb(msg, arg)`) |

Índices medidos en `libosal_uipc.so` (Thumb): 0 stat_sem · 1 wai_sem · 2 sig_sem · 3 stat_msgq · 4 snd_msg · 5 snd_sync_msg · 6 snd_sync_direct · 7 rcv_msg · 8 reg_msg_queue_cb · 9 unreg · 0xa valloc · 0xb free · 0xc dynamic_id · 0xd wait_cb · 0xe/0xf modos de cola · 0x10 connect. Sin servicio (descartados): colas `0x7a0020` (input.ko), `0x5700f9`, `0x5a0048`, `0x16f4010`, `0x61003c`; backup `op 1`/`op 5`.

Otros ganchos: cualquier otro `/dev/*` → fd inerte sobre `/dev/null` con `mmap` anónimo (`/dev/mem`, `/dev/stream*`, `/dev/nflasha4`…);
`/proc/modules` simulado con `grm_ma`/`grm_gles`; `dlopen`/`system`/`fopen`/`munmap` registrados; `abort()` vuelca `r4–r8/lr`;
`SIGSEGV/BUS/ILL/ABRT` imprimen la pila (direcciones resueltas por `/proc/self/maps`) y dejan el *core*.

### 2.2 Variables del shim (se pasan con `SHIMENV` de `run.py`)

| Variable | Efecto |
|---|---|
| `WAIT` / `TAILN` | `im.sh`: segundos de espera (50) y líneas finales mostradas (40) |
| `FULLLOG=1` | `im.sh`: trae el registro completo del guest al anfitrión (`DIR_TRABAJO/guest.log`, gzip+base64 por la consola) |
| `ACKQ=hex,hex,…` | colas de kernel que reciben acuse genérico (por defecto `d9016e,7a0029,61003c`) |
| `DEVSTACK=1` | pila del llamador en la 4.ª repetición de cada ioctl de un dispositivo genérico (los ioctl genéricos se registran las 5 primeras veces y cada 4096, con módulo+offset del llamador) |
| `VERB=1` | muestra valloc/free/direct, `MSGHEX` de envíos a colas de kernel y `LOGRAW` |
| `TIDLOG=1` | antepone el tid a cada línea |
| `BKV=1` | registra cada petición al backup (por defecto solo los ids ausentes) |
| `CVWAIT=s` | tope en el `pthread_cond_wait` de `grm_init` (`libObj+0x719ee1`); `0` = sin tope |
| `POKE=dir` | escribe la dirección de `malloc` en `libObj+dir` (asignador del GPU: `fef348`) |
| `SKIPFN=dir[=v],…` | sustituye funciones Thumb de `libObj` por `movs r0,#v; bx lr` |
| `TRACEFN=dir,…` / `TRACEPEEK=dir,…` | traza única de entrada (`r0–r3`, `lr`) mediante UDF + `SIGILL`; `TRACEPEEK` lee palabras de `libObj` en cada traza |
| `WATCH=dir` | hilo que sondea cada ms `libObj+dir` y registra cambios |
| `DUMPAT=n` | a los n s manda `SIGUSR1` a cada hilo: pila con nombre |
| `MEMSCAN=1` | con `DUMPAT=n`: por área de dispositivo, páginas no nulas (¿ha escrito algo la UI?) |
| `STACKQ=qid` | pila del emisor en el 3.er envío síncrono a esa cola |
| `GPUIRQ_MS=n` | periodo de la IRQ simulada de la GPU (20 por defecto; 0 = GPU ociosa) |
| `RCVSTACK=1` | pila de cada `rcv_msg` nuevo con espera infinita |

## 3. Reproducir desde cero

```sh
sh scripts/gui/harness/setup.sh analysis/gui/g22/harness          # descarga, extrae, construye base + shim + bk.tbl (ignorado por git)
SHIMENV='WAIT=60 CVWAIT=0 POKE=fef348' python3 scripts/gui/harness/run.py analysis/gui/g22/harness scripts/gui/harness/im.sh 115
python3 -m pytest -q tests/test_gui_harness.py                     # formato de bk.tbl y compilación del shim
```

Descargas (sha256 del 09-11-2026, `dl/SHA256SUMS`): `vmlinuz` `b508abca3127cb0d…` (6 046 208 B), `initrd.gz` `e7ca77e9dfd998ef…`
(25 985 449 B), `libc6-dev_2.44-3_armhf.deb` `a6afc8308abc26f6…`, `linux-libc-dev_7.3.3-1_all.deb` `0ae575f92986cf32…`. La ruta
`installer-armhf/current` cambia con cada versión puntual de trixie: si el kernel deja de ser 6.12 armmp, fijar la URL con fecha.
Requisitos del anfitrión: `qemu-system-arm` (probado 11.1.3), `clang`+`lld`, `bsdtar`, `cpio`, `curl`, `readelf`, Python 3 con
`references/pmca`. Un `setup.sh` con las descargas ya hechas tarda ≈ 5 s; el arranque completo ≈ 15 s y la ejecución la fija `WAIT`.

Resultado de referencia (09-11-2026, tras la auditoría §6): `alive=<pid> threads=49 lineas=1542 modulos=47`,
`snd_msg 0xd9016e -> respuesta`, sin `ABORT`/`EXIT`. Tras el avance 18 (callbacks): `threads=49 modulos=46`, `guest.log` ≈ 3 000 líneas sin `VERB` (`FULLLOG=1` lo trae al anfitrión).

## 4. Camino recorrido (avances 1–17, condensado)

| Avance | Hito |
|---|---|
| 1–2 | Userland glibc 2.11.2 corre en QEMU; `im.elf` sale con `open /dev/uipc error`; ~20 módulos de kernel Sony a sustituir; `libosal_uipc.so` = OSAL de usuario |
| 3–5 | `/dev/uipc` modelado (connect, semáforos, colas, `dynamic_id`); trazas `0x8f013a` legibles; **backup real** desde NVRAM (`0xfa0028`=`0x82df9000`, `0xfa005d`=`0x7c000`); `InitParameterControl OK`, `senif_init done` |
| 6 | `gl_common`: las áreas de memoria se piden por `snd_sync_msg` a `0x14c0424`, no por ioctl a `dmm.ko`; `im.elf` deja de abortar |
| 7–8 | Estable > 110 s; `/dev/fb0` solo existe en `libObj` (la pantalla no es un framebuffer); bucles HDMI/WLAN silenciados; `appFw.so` (etapa 4) nunca llega |
| 9–10 | Causa: `grm_init` (`libObj+0x616778`) publica una orden síncrona `0x8001` en el pool B (`0x719e10`) y espera en `0x719ee1`; con `CVWAIT` toma la rama de error: **la orden falla** |
| 11–12 | La orden es la **init EGL/GLES de DMP embebida en libObj** (`0x717830 → 0x716800 → 0x6cd970 eglChooseConfig → 0x6cf120 eglCreateContext → 0x6c96c0`); saltarla aborta con «grm_ma is not installed» |
| 13–15 | El asignador del GPU (`libObj+0xfef348`) nunca se instala (`blx` a 0); `POKE=fef348` y `/proc/modules` simulado pasan `grm_ma`; la aserción `MMapBase.h` es de la limpieza, no de `gl_common` |
| 16–17 | El trabajador B entra en el despachador `0x719950` y no vuelve; `0x6a272c` crea una cola de respuesta (`dynamic_id 0x2a`) y bloquea en `rcv_msg` de `0xd9016e`: **ya se responde**; el sistema sigue hasta `libSyncAndroid` y vuelve a esperar (segunda llamada, cola `0xaf404a`) |

## 5. Bloqueo vigente

`THREAD_INFRA0` espera en `grm_init` a que el trabajador B termine la orden `0x8001`. El trabajador queda dentro de `0x6a272c`
(envío síncrono a servicios del «kernel»): la primera petición a `0xd9016e` ya recibe respuesta; la segunda (cola `0xaf404a`,
traza `0x6a22d4`: `osal_wai_sem_tmo(obj+0x10, 0)` ocupado → error `0xfffffc00` y luego espera `−1`) no la recibe porque el shim no
sabe qué servicio la atiende ni qué respuesta espera. Hay no determinismo entre ejecuciones (a veces el primer envío no llega en 55 s).
Sin `POKE`, el asignador nulo hace fallar `0x71e890`. INFERENCIA: el asignador real lo instala `dmp_allocator_lib_init` (`0x6c70f0`)
con pools `mpool_0x10` (`libObj+0x65f420`), y los *callbacks* del controlador GL (`0x1016f38+0x34/+0/+4/+0x38`) los provee el módulo
`grm_gles.ko` (dispositivo `/dev/dmpgles2`), que no existe en QEMU.

### 5.1 Avance 18 (09-11-2026): callbacks de cola y protocolo de `0x61003c`

- `idx 8/13/5` modelados: antes las colas con callback (MWF, HDMI `0x9c015b`, etc.) no recibían nada; ahora hay ≈ 300 entregas asíncronas por arranque y `libMWF` (`EventWrapper::CallBackPoint`) responde. Corregido en el camino el orden de argumentos del registro (`t[0]`=arg, `t[1]`=cb) y el argumento del registro síncrono (`t[2]`).
- Referencia nueva: `threads=49 modulos=46` (+`libMWF`, `libmpr*`, `MediaMount/Detect`), sin `ABORT` ni `ioctl ignorada`.
- El trabajador B (`THREAD_INFRA0`) espera en `rcv_msg` de una cola dinámica tras enviar a **`0x61003c`** (`m[0]=1, m[1]=0x000e1700, m[3]=-1, m[4]`=cola de respuesta; cabecera `m[-4]`=cola): orden de `dmpNative::InternalCmd` (`int_cmd.cpp`). Con `ACKQ=d9016e,7a0029,61003c` la respuesta pasa la aserción `int_cmd.cpp:171` (`req_id` en `+6` debe ser **0**; medido con `TRACEFN=6a2612`: `r2=0xe` copiado frente a `r3=0` esperado) y el sistema avanza hasta `DataflowInfraPin::RequestDisconnect` (`libObj+0x6a7f60`), que aborta con «invalid phys 0x01704021»: recibe nuestro acuse (cola de respuesta en `m[4]`) donde espera una dirección física. Esto se resolvió en el avance 19 (§5.2); `61003c` ya está en el `ACKQ` por defecto.
- Siguiente (F2): modelar el protocolo de pines de `stream.ko` (`DataflowInfraPin::Request*`, `_MSG_PIN_REQUEST_*`): desensamblar `0x6a7968`/`0x6a7f60` y fabricar respuestas con direcciones físicas de las áreas `dmm`.

### 5.2 Avance 19 (09-11-2026): órdenes de `InternalCmd`, backup `nread`, GPU de DMP y dmm 1/9

Cadena resuelta, en el orden en que cada tramo bloqueaba el arranque (todo medido con el registro del guest, `TRACEFN` y desensamblado):

1. **`0x61003c` = alloc de `dmpNative::InternalCmd`**: petición `{1, tamaño=0xe1700, 0, -1, cola, ?:req_id}` (cabecera `m[-4]`=cola); respuesta `+6`=`req_id` (= `m[5]&0xffff`: 0,1,2,3 en las 4 peticiones), `+0x10`=phys, `+0x14`=tamaño (leídos por `libObj+0x6a2626` → `MMapBase::Map`, que aborta con «invalid phys» si no está alineado). El shim reparte phys desde `0xa0000000` (4 KiB, en orden).
2. **Backup `op 30` = `Backup_nread(id, buf, tamaño)`**: copia `min(len, tamaño)` a `buf` y devuelve los bytes copiados; `SystemImpl::initialize_setting` (`SystemImpl.cpp:156`) exige `== sizeof(setting)` (id `0x1700000`, 4 B). Códigos de `libbackup.so`: get_datasize 1, get_datasize_multi 2, get_attribute 3, read 4, read_4Byte 5, read_multi 6 (los números del shim anterior estaban desplazados para `op 0/3/4`, que sí funcionan en la práctica porque `m[0]` ya es el índice interno).
3. **`/dev/dmpgles2`** (GPU de DMP, módulo `grm_gles.ko`): `libObj+0x6c53e0` llama `ioctl(0xc0048211)` en bucle mientras la salida (`[arg]`) ≠ 0; el shim devuelve 0 → la espera termina (antes: 390 000 líneas de registro y un hilo a 100 %). También se ven `0x80048206`, `0xc0048202`, `0x80048263` (init, devuelven 0 sin efecto) y `mmap(/dev/dmpgles2, 0x20000)` anónimo.
4. **dmm códigos 1 y 9** (`snd_sync_msg` a `0x14c0424`, `libObj+0x6b9158`): `1` = crear área `{1, 0x258, "\0ws_image_space", …}` (el resultado va en `+0x1c`; si ahí queda el tamaño `MAMessage::send` lo lee como error: «returned error 67108864»), `9` = reservar `{9, 0, tamaño, alineación}`. Con ambos respondidos `GraphicsHAL hal_create` **supera** su aserción (`di_hal.cpp:174`).

Estado tras el avance 19: `im.elf` ya no aborta dentro del GL/`hal_create` y carga `libWlanResource`, pero acaba en un SIGSEGV **no determinista** (a veces `libObj+0x7b0359` con `memset` sobre un puntero devuelto por el asignador de `MemorySpace`, a veces un mutex nulo en `libpthread`), precedido de `MemorySpaceImpl.cpp:437 partially duplicated element found`. Hipótesis (INFERENCIA): las áreas que el shim devuelve para dmm 1/9 solapan o repiten elementos que `MemorySpaceImpl` ya conoce (el tamaño y la alineación de las reservas y el orden código 9 → 1 no coinciden con lo que haría `dmm.ko`), y el segundo SEGV es una carrera por un objeto aún no inicializado.

Siguiente (F2, continuación):
- ~~**dmm**: formato de las respuestas de los códigos 1 y 9~~ (resuelto en §5.3: el servicio es `grm_ma.ko`).
- ~~Determinismo~~: resuelto (§5.3), 3/3 ejecuciones idénticas.
- Servicios aún sin respuesta: `0x80003b` (5 envíos), `0x7a0020` (input.ko), `0x5700f9`, `0x5a0048`, `0x16f4010`; backup `op 1`/`op 5`.

### 5.3 Avance 20 (09-11-2026): servicio de memoria `grm_ma.ko`, GPU y arranque completo hasta el Window System

El servicio `0x14c0424` **no es `dmm.ko` sino `grm_ma.ko`** (`MAMessage`); su despachador `ma_user_sync_cb` (desensamblado ARM, tabla de saltos) fija el formato real. Código = u16 de `m[0]`; entrada en `m+4`, salida según el código:

| Código | Operación | Entrada → salida |
|---|---|---|
| 1 | `dmm_open` | `in[0]`=tipo (0x258), nombre en `m+9` → `m[7]` estado, `m[8]` phys, `m[9]` tamaño, `m[10]` handle del mspace |
| 2 | `dmm_close` | `m[1]`=handle → `m[2]` (libera todas las reservas del handle: `open → malloc(todo) → close → open → malloc…`) |
| 3 | `create_msp` | `{base, tamaño, flag, nombre@m+9}` → `m[8]` estado, `m[9]` handle |
| 5 / 6 | cache flush / invalidate | `m[1]` |
| 7 | `findbyname` | nombre en `m+4` → `m[5]` estado (−9 si no existe), `m[6]` phys, `m[7]` tamaño, `m[8]` handle |
| 9 | `malloc` | `{handle, tamaño, alineación}` → `m[4]` estado, `m[5]` puntero (phys) |
| 10 | `free` | `{handle, ptr}` → `m[4]` |
| 4 | inválido | — |

El shim (`ma_service`) lleva una tabla de mspaces (64 MiB anónimos por área, asignador de rampa; el código 7 devolvía antes un área **nueva** en cada consulta del mismo nombre: de ahí `MemorySpaceImpl.cpp:437 partially duplicated element`). Resto de lo emulado en esta tanda:

- **GPU de DMP** (`/dev/dmpgles2`): `0x80048206` → tamaño de la ventana de registros (`0x20000`; con 0 se mapeaba una página y `rm_reg_init` escribía en `+0x1804`, SIGSEGV); `0xc0048211` (espera de fin) → salida 0; `0xc004820d` (espera de interrupción, bucle de `libObj+0x6c5320`) → **IRQ simulada cada 20 ms** (`GPUIRQ_MS`; con 0 la GPU duerme y la init GL no termina; sin espera el hilo hacía 78 millones de ioctl/70 s).
- ioctl con argumento entero (p. ej. `UI_SET_EVBIT` de `/dev/uinput`) ya no se desreferencian en el registro (SIGSEGV del propio shim).
- `STACKQ=qid` (pila del emisor en el 3.er envío síncrono a esa cola).

**Estado de referencia (3 de 3 ejecuciones)**: `alive=<pid> threads=73 modulos=60–61`, sin aborto, sin SIGSEGV. `libgrm.so` termina su carga (`grm_init` retorna), `hal_create` pasa, arranca el Window System (`[WindowServer] init … w = 640 h = 480 buffer num = 2`, hilo `UX_WINDOW_SYSTEM`) y se cargan `libuxengine`, `libInfraTp/Indctr/Hotshoe/Sircs/Dial/Lanc`, `libInputServant`, `libScalarDaemon`, `libHapiLib`, `libInfraSelector`. El hilo `HotshoeResource` sondea `0x720018` (≈ 5 envíos/s: comportamiento normal). Nota: **`appFw.so` no existe como biblioteca** en este firmware; las suposiciones de los avances 7–8 sobre «etapa 4» eran erróneas.

Siguiente: F3 (pantalla) y F4 (entrada). Pistas: el Window System usa 2 búferes de 640×480 y un hilo propio; `GRM_fbrm*YUV` son stubs de 8 bytes en `libObj` (`0x614924…0x61496c`, tablas de salto); la presentación real sale por servicios del «kernel» aún sin respuesta (`0x80003b`, `0x5700f9`, `0x5a0048`, `0x16f4010`, `0x7a0020`).

### 5.4 Avance 21 (09-11-2026): carga completa y reposo del sistema; por qué aún no hay imagen

- **El cargador de etapas termina**: 66 inicios de módulo (el último, `063_libInfraSelector.so`; `libmprctrl` figura sin «E» solo por un solape de registros). Con 170 s de espera no se carga nada más: `im.elf` queda **en reposo** (hilos de etapa terminados, `HotshoeResource` sondeando `0x720018`). La interfaz de usuario no se lanza desde `im.elf` solo; en la cámara la ponen en marcha mensajes de `av-cam` (BIONZ) que aquí nadie envía (INFERENCIA: modo de encendido, objetivo, teclas).
- **Sin píxeles todavía**: `MEMSCAN=1` (con `DUMPAT=n`; vuelca por área de dispositivo cuántas páginas no son cero) muestra que ninguna área ha sido escrita: `gl_common` 2 páginas, `ws_image_space` 1 y los **4 búferes de `InternalCmd` (`0xe1700` B = 640×480×3 + 0x700)** a cero salvo su página 0. Esos 4 búferes son los destinos de render del Window System (`buffer num = 2` + 2 de apoyo): los rellena la GPU de DMP por listas de comandos, así que **capturar la pantalla exige emular esa GPU** (no hay ruta de dibujo por software que pase por `/dev/fb0`) o, como mínimo, la ruta 2D (`DMP2D_*`/`GRM_gpermRectblit`), que sería el primer candidato por ser un blitter simple.
- Plan F3 revisado: (1) conseguir que arranque la UI (mensajes de `av-cam`: ver `docs/capture` de los paquetes `pkt` BIONZ↔Linux y las colas `0x5700f9`, `0x5a0048`, `0x16f4010`, `0x80003b`); (2) decodificar los comandos que `libObj` escribe en la ventana de registros (`0x20000`, offsets `+0x1800…`, `rm_reg_*`) para ver si el 2D es emulable; (3) volcar los 4 búferes con `MEMSCAN`/`DUMPAT` a PNG en el anfitrión.

### 5.5 Avance 22 (09-11-2026): cómo lanza la cámara `im.elf` y por qué `appFw.so` no llega

- **`bootin.elf` lanza ocho procesos**, no uno: `im.elf s &`, `g &`, `r &`, `u &`, `l &`, `i &`, `a &` y `im.elf` sin argumentos (cadenas de `bootin.elf`; antes el arnés pasaba todas las letras a un solo proceso). El parser de `im.elf` (`0xa628`) convierte cada letra en un indicador: `s`→`0x10000`, `u`→`0x80000`, `l`→`0x100000`, `i`→`0x200000`, `a`→`0x400000`; `g`, `d`, `r` no activan nada; `bootall` activa `0x7f0000`; `global`/`lazy-*` fijan otra opción. `main` ejecuta 5 fases (`0xb6e4(entrada, fase, indicador)`) y una entrada solo se carga si el indicador de su fase es distinto de 0.
- **Tabla de etapas (`imdb_raw` de `libIMDB.so`)**: registros de 11 palabras `{tipo, máscara, máscara de destino, id, nombre, init, exit, sus, res, inact, act}`; destinos `default, qemu, sim, nfs, set, usbj, resub`. `appFw.so` (`Application_System_Init`, símbolo de `libObj` en `0x7ed9f4`: crea el hilo de la UI con `osal_create_thread`) es un registro de tipo `0x20000004` que sigue a `libSyncAndroid`; seguido de `subapp.so`, `libJetControl.so`, los servidores USB/MTP… Nunca se carga en el arnés.
- **Mensajes de `im.elf`**: registra las colas síncronas `0x94016a`/`0x920169`/`0x940270` con el despachador `0x95b0`: `0x9400e1` (sondeo; responde `0x12345678`), `0x940021` (cargar la entrada cuyo **id** va en el `u16` de `+4`: ids como `0x9d`, `0xcc`, `0xeb`, `0xea`, `0xce`, módulos USB/kernel), `0x940022` (descargarla) y reenvío de `0x920143…0x92015c` a `0x94016a`. No es el mecanismo que arranca la UI.
- **Experimentos (negativos)**: (a) `INJECT=seg:qid:w0,w1,…` (nuevo en el shim; hexadecimal) entrega un mensaje por la cola síncrona registrada: `0x940021` con id `1` no carga nada (el id no existe en la tabla); (b) `IMSPLIT=1` (nuevo en `im.sh`: un proceso por letra) deja cada proceso con 0–11 módulos y `i` termina en SIGSEGV: el `uipc` del shim es **por proceso**, así que las colas entre procesos hermanos (`0x94016a`, `0x924127`…) no existen y no es viable sin un `uipc` compartido; (c) `IMARGS=bootall` en un solo proceso: igual que antes (61 módulos, sin `appFw`). Conclusión: los indicadores no son el límite; la fase de `appFw` no se ejecuta aunque se pidan todas.
- **CORREGIDO en §5.6**: la causa era un semáforo sin señalar (`0x83037a`), no los indicadores ni el destino. (Texto original:) averiguar qué condición salta el registro `appFw` en `b640` (comparar el tipo del registro con la fase, terminadores `0x7`/`0x28` y `IMDB_find_target_bit`, que no se ha comprobado qué devuelve bajo QEMU) y, solo después, la GPU de DMP. Recomendado: `TRACEFN`-equivalente para `im.elf` (hoy solo existe para `libObj`).

### 5.6 Avance 23 (09-11-2026): la UI arranca (`appFw.so` + `viewUnified2.so`); lo que falta es la GPU

- **Causa del bloqueo de `appFw`**: el `main` de `im.elf` espera **sin límite** el semáforo `0x83037a` (`osal_wai_sem_tmo(−1)`, `0x9c48`) antes de crear el hilo de aplicación (`0x9475`, argumento/máscara `0xf`), que ejecuta la fase 8 de la tabla de etapas (registros entre los terminadores `7` y `8`: `appFw.so` id `0x83` y `subapp.so`). En la cámara lo señala otro procesador; aquí nadie. El shim lo deja señalado al arrancar (`SEMSIG`, por defecto `83037a`; lista hex; vacío = ninguno).
- **Estructura de la tabla de etapas** (verificada contra `IMDB_find_entry`/`IMDB_get_entries`, instrumentadas con `IMDB_TRACE=1`): registros de 11 palabras `{tipo, máscara, máscara de destino, id}`+nombres; `IMDB_find_target_bit` devuelve `1` (`default`) bajo QEMU; los registros de tipo pequeño (`2…8`, `0x28`) son terminadores de fase; `main` ejecuta las fases 1–5, los hilos `THREAD_INFRA0/1/2` (máscaras 1/2/4) las 5 y 7 y el hilo de aplicación las 7 y 8 (esta con el indicador de la letra `a`).
- **Resultado** (`WAIT=80`): 66–67 módulos; `083_appFw.so` carga; arranca `FbModeResolver` (640×480, RGBA4444, `FB_PARAM_640_480_RGBA4444`), `FbPool` crea el *bitmap* de pantalla en el área `/dev/stream` (`MA malloc 0x96000` → fase `0xb4000000`), `WindowImpl`, `UpdateStatusMonitor`; se cargan `libObj.so` y **`viewUnified2.so`** (las vistas); `vdf_if_port_send_update` manda dos mensajes a la cola de kernel `0x80003b` (descartados); aparece el hilo `Appframework`, que queda en bucles `dmpgles2` `0xc0048211/12`; `InputEven`/`msgq` de entrada creados (cola `0xaf40c2`).
- **Pantalla**: `MEMSCAN` confirma que el *bitmap* de pantalla (`/dev/stream off=0xb4000000`, `0x96000` B = 640×480×2) sigue **a cero**: el dibujo es de la GPU de DMP (`libObj+0x6c4xxx`, ventana de registros de `0x20000` B, listas de comandos en `gl_common`). `PIXDUMP=1|off` (nuevo) vuelca ese área a `/tmp/fb.bin` y `run.py` la extrae a `DIR/fb.bin` (marcas `=====GUESTFILE-*`); queda lista para cuando haya algo que volcar.
- **Avance posterior (10-11-2026)**: el hilo `Appframework` espera el mismo semáforo `0x83037a` una segunda vez (`BLOQUEO sem 0x83037a`); con 4 señales (nuevo valor por defecto de `SEMSIG`) no hay bloqueos y la UI sigue: carga `CautionConfig/ModelCautionConfig/CautionRsrcConfig.so`, `viewUnified8.so`, abre `global.xdb`, `lang_cmn.uxc`, `image_cmn_169.uxc`, `image_EVF.uxc`, `image_DSLR_Only_169.uxc`, `string_spanish.uxc`, `lang.uxb`, `style_cmn.uxc` y abre `/dev/ldec` 62 veces (`ioctl 0x1`; decodificador de imágenes por hardware, sin emular: devuelve 0). Servicios sin atender vistos: `0x7a0029` (`stat_msgq`), `0xaf40c2`, `0x87017b` («Illegal Size [4100]» de IMCfg, 9 veces), red `WRPPR_NET_SVC` (`osal_snd_sync_msg error -1020`). `MEMSCAN`: `/dev/stream off=0xbc000000` (montón de la UI, 169 páginas = 0xa8000 B) tiene datos con aspecto de textura en bloques (no es una imagen lineal 512/640/1024 de ancho en RGBA4444: parece *swizzle*/mosaico); los 3 búferes de pantalla (`0xb0000000/0xb4000000/0xb8000000`) y los 4 `InternalCmd` siguen a cero. `PIXDUMP=<off hex>` permite elegir el área; `run.py` extrae `fb.bin` (corregido el orden de marcas).
- **Diagnóstico de la GPU y de los hilos (10-11-2026, nuevos `AREADUMP=dev@off[,…]` y `DUMPTHR=subcadena`)**: (1) la ventana de registros de `/dev/dmpgles2` (`0x20000` B) solo tiene escrito `+0x100…0x13c` (punteros de usuario y `0x8000de80`/`0x800a3e80` = *bitmaps* de `gl_common`); la ventana de `/dev/mem off=1` tiene `+0xc08/0xc0c = 0x01e00280` (480|640 → tamaño de pantalla), `+0xc10 = 0x4401`, `+0x1800 = 4` y **`+0x1804 = 0x800a3fc0` = dirección de la lista de comandos**. (2) La lista (en `gl_common`, `/dev/stream off=0x80000000`, 7 páginas no nulas) son solo palabras de sincronización: `{0x0116f000, 0x08000068, 0x0117f000, 0x00000001, 0x0044f000, 0, 0x0010f000, 0x12345678}` repetidas (pares dato/cabecera estilo PICA con marca `0x12345678`); **todavía no hay órdenes de dibujo**: la UI no ha llegado al primer *render*. (3) Hilos de la pila gráfica vivos: `grm_gpe` (motor 2D, espera una condición), `grm_result` (`mq_receive` de librt), `grm_dn_vdf_if`, `uxengine_res1/2`, `THREAD_INFRA0` (espera de condición en `libObj+0x6a8401`, capa GL) y **`Appframework` bloqueado en un `pthread_mutex_lock` (`libObj+0x6a83a9`) dentro de la capa GL**: otro hilo retiene ese cerrojo (no identificado). Las direcciones de pila por debajo de `0xe2b70` (p. ej. `0xd559xx`) caen en `.dynstr`: son restos del escaneo de pila, no código. (4) Las colas `0x9a015a`/`0x9c015b` son del bucle HDMI (silenciado). Siguiente paso concreto: identificar el dueño del cerrojo de `libObj+0x6a83a9` y qué evento (¿fin de GPU, *vsync* de `0x80003b`?) espera, antes de emular órdenes de dibujo.
### 5.7 Avance 24 (10-11-2026): la UI deja de bloquearse (GPU mínima y protocolo `vdf`); falta el renderizado

Causa del bloqueo de `Appframework` (§5.6) y arreglos en el shim (todos por defecto; `GPUEMU=0` y `NOVDF=1` los desactivan):

- **El hilo GL retiene el cerrojo desde que envía un trabajo hasta que termina** (`MUTEXWATCH=s` nuevo: informa del dueño `__owner` de un `pthread_mutex_lock` que espera > s y de las esperas de condición; `MUTEXTRACE=sufijo_hex` y `MUTEXSTACK=hilo` trazan bloqueos). Dos esperas distintas lo mantenían:
  1. **GPU**: tras `rm_reg_init`, la ventana de `/dev/dmpgles2` (`0x20000` B) tiene `+4` = índice del trabajo terminado (`0xffffffff` = ninguno), `+0x10` = resultados pendientes / nivel de la FIFO, `+0x14` = estado (el bucle de `libObj+0x6c35a0/0x6c66c4` gira hasta que vale `2`) y una **tabla de trabajos de 0x320 entradas de 0x8c B en `+0xe8`** (`[+0x14]` = id; `libObj+0x6c5510` la recorre). Punteros a esos registros: variables globales `libObj+0x10ac0cc/0fc/0d4/108` (`GLOBDUMP`). `__g_rm_thread_exit` (`0x10ac08c`) mantiene vivo el hilo de interrupciones. **`GPUEMU`** (nuevo): el shim sustituye la instrucción `str r1,[r3,r0]` de `rm_reg_write` (`libObj+0x6c4c46`, `0x5019` → UDF; comprobada antes de parchear) para ver cada escritura; la de `+0x1804` (dirección de la lista de órdenes) es el «timbre»: la GPU pasa a ocupada 3 ms y vuelve a `2`, y, una vez cargadas las vistas, avisa del fin (`+4` = índice de la entrada con id, `+0x10` = 1) hasta que el controlador lo reconoce con `ioctl 0xc0048212 arg 1`. Con la ventana inicializada a `+4 = 0xffffffff`, `+0x14 = 2`. (`GPUEMU_MS`, `GPUEMU_JOB`, `GPUTRACE`, `RINGWATCH`, `REGTRAP`, `GPUDUMP`, `GPUEMU_DUMP` son diagnósticos.)
  2. **Pantalla (`vdf`)**: los mensajes a la cola de kernel `0x80003b` son `{cmd, puntero}`: los comandos pares 2, 4, 6, 8 registran *callbacks* de usuario (`vdf_if_port_exec_cb`=2, `break_cb`=4, `update_cb`=6, `mute_cb`=8; el 9 es `notify_output_cb`, no solicitado) y los impares 1, 3, 5, 7 son peticiones (exec, break, update, mute) que el módulo de kernel contesta llamando al callback `cmd+1`. El shim lo hace con un hilo proxy 3 ms después (`vdf: petición N terminada → callback del cmd N+1`); `VDFUPD=99` los llama uno a uno (diagnóstico).
- **Resultado**: 70 módulos, sin bloqueos de cerrojo, la UI recorre cientos de ciclos `UpdateStatusMonitor` (turnos 97+ en 5 min) y envía ~190 actualizaciones de pantalla; `3 passed` en la prueba de arranque (94 s).
- **Lo que NO funciona**: los búferes de pantalla (`/dev/stream` `0xb0000000/0xb4000000/0xb8000000`) siguen a cero. Solo una lista de órdenes llega por el timbre (`{0x116:0x08000068, 0x117:1, 0x44:0, 0x10:0x12345678}`, pares `(registro<<16 | 0xf000, valor)` con marca de fin `0x12345678`); el dibujo real son **trabajos en la tabla de la ventana** (`libObj+0x6c58c0` encola; descriptores de 0x80 B con tipo 6/8, id, punteros a listas en memoria de usuario/`gl_common`, destino `0x8000de80` 640×480 formato `0x4401`, 640×480 ×3) y listas de órdenes en `gl_common` (`+0xb0680…`, pares `0x0459f000/0x0461f000, valor`, registros `0x4xx–0x5xx`). Hay que decodificar el formato de las listas y de los descriptores (GL ES 2 de DMP: `GL_DMP_program_binary`, `GL_OES_compressed_ETC1_RGB8_texture`, texturas en mosaico) y escribir un rasterizador; no existe documentación y `libObj` no trae nombres de registro. Sin eso, F3 (imagen), F4 (teclas, no verificable sin imagen) y F5 siguen abiertas.
- **Inestabilidad conocida**: con tiempos distintos (p. ej. `REGTRAP`) el aviso de fin puede entregarse sobre una entrada sin *callback* y `libObj+0x6c519e` llama a un puntero no ejecutable (SIGSEGV).
- **Entrada y eventos de arranque (avance 24b)**: el registro de la cámara real (`mem-20261020-log`) muestra que la vista de disparo nace con un evento de tecla (`[INPUTSERVICE] toActive … key_code=0x2 event_code=0x15010010` → `ViewRootPowerSw::getCurrentLayout_POWER_ON`). El hilo `I-InputMain` de `libObj` lee mensajes de 6 palabras de la cola `0x7a0020` (`libObj+0x806f88`): `w0` = identificador de tecla registrado por `InputService` (con `w0=1` → «unknown key», con `w0=2` se acepta; el segundo idéntico → «same event»), `w4` = índice de tecla (≥ 0), `w5` = indicadores (bit 0 = repetición). Nuevo en el shim: `KEYQ=7a0020` (da buzón a esa cola de kernel), `INJECT="seg:qid:w0,w1,…/seg:qid:…"` (hex; `/` separa mensajes) entrega por buzón o callback, y el registro de `reg_*msg_queue_cb` ahora indica `(biblioteca+desplazamiento)` del callback (colas de la UI: `0x83014b` sync `libObj+0xfffe8` (analizador de parámetros TLV), `0x830450` `libObj+0x10b114`, `0x15b043e` `libObj+0x11499c`, `0x1494412` `viewUnified8+0x15820`). **Resultado**: la tecla se acepta pero no se observa `[INPUTSERVICE]` ni apertura de vista; faltan los valores correctos de `w1…w5` y quizá otros eventos de `av-cam`. Sin renderizador (§ anterior) el efecto de cualquier tecla no sería visible de todos modos.
- **Estado F3–F5**: F3 (imagen) **bloqueada solo por la GPU**: hay que decodificar y emular las órdenes que `libObj` escribe en la ventana de registros (formato de las listas, sin documentación) — trabajo de fondo sin garantía. F4 (teclas) viable en principio desde ahora (hay cola de entrada `0xaf40c2` e `InputService`), pero sin imagen no se puede comprobar el efecto; F5 depende de F3. La prueba de arranque (`A6000_HARNESS_RUN=1`) ahora exige `appFw.so` y `viewUnified2.so`: 3 passed en 94 s.

### 5.8 Avance 25 (10-11-2026): el bucle de `Appframework` y por qué no se abre ninguna vista

- **Hilos** (nuevo `[shim] HILO tid nombre` en `DUMPAT`; `DUMPTHR` admite lista separada por comas): la UI son `Appframework`, `ScalarSTM`, `CameraBackgroun`, `uxengine_res1/2`, `grm_gpe/result/dn_vdf_if` e `I-Input*`. Ninguno está bloqueado en un cerrojo: `Appframework` está dormido en `poll()` dentro de `AppSystem::Main` (`libObj+0x7eeee8`; espera `Event::wait` en `0x7eec00`) y despierta por temporizador o por un evento en su cola (`0x7ef940` extrae, `0x7eed0c` despacha por clase: `VM` ViewManager, `MM` ModelManager, `VS`, `UM`). En 75 s solo se despacha **un** evento (`TRACEFN=7eed0c,7ef940`).
- **Apertura de vistas**: `viewManagerIf::openView` (`libObj+0x1251fc`) no abre nada por sí misma: construye un `ParamList` y publica el evento `0x11012001` (parámetros `6` y `0x1a`, ambos cadenas) con `0x7f25e0`. El `ViewManager` lo atiende (aparece `[VMNG] viewId: -1 don't exist in table`: la tabla `viewId → biblioteca/símbolo` de `0x7f05d2`/`0x7f05a2`, `std::map<int,…>`, devuelve −1 para `ViewRoot` y `ViewRootPowerSw`). Cargar la vista = `dlopen(lib)` + `dlsym("<Nombre>ToInstance")` (`0x7f3c18`; las vistas de `viewUnified2.so` son `ViewRoot`, `ViewRootPowerSw`, `ViewRootSelector`, `ViewSnapShotBoot`). Nuevo `OPENVIEW="Vista,…"` + `OPENVIEWAT=s` en el shim llama a esa función desde un hilo propio; el evento llega y se procesa, pero la tabla no tiene esos nombres como `viewId`, así que no hay vista. Falta saber qué clave espera el primer parámetro (¿id numérico en cadena?) y cuándo se rellena la tabla (`AppConfig`: `initializeViewConfig/getViewConfig/initializeModelTree` de `viewUnified2.so`, `libObj+0x106c7c`; nunca aparece ningún `[AppCfg]` en el registro).
- **`InputService::activate(bool)`** (`libObj+0x113d2c`) es lo que registra las teclas (`toActive … insert key_code=… event_code=…`); solo lo llaman tres sitios de `viewUnified2.so` (`+0x16c6b8`, `+0x16c6dc`, `+0x2d6f00`), es decir, las vistas al activarse. Sin vista raíz nadie activa la entrada, por eso el mensaje de tecla de `INJECT` se acepta pero no produce `[INPUTSERVICE]`.
- **Corrección a la lectura del registro real** (`mem-20261020-log`): `Stm received 63!!!` es la orden de terminar el hilo de `libStm` (`libStm+0x3dbe`: `cmp r1,#0x3f` → salir), y todo el registro es un ciclo **suspensión/reanudación** (GPS en `SysSuspend` a los 127 s, `toActive` a los 129 s), no el arranque en frío. No sirve como guion de arranque.
- **Hallazgo negativo**: no hay fichero `AppConfig.so` en el firmware; `"AppConfig.so"` es solo el nombre por defecto del argumento de `Application_System_Init` y del hilo.
- **Siguiente paso para F3/F4**: averiguar quién publica en la cámara el primer evento de `VM` (probable: el modelo de arranque `ModelBoot`/`POWER_CTRL` al recibir un cambio de estado de `ScalarSTM`/`av-cam`) y reproducirlo con `INJECT`/`OPENVIEW` con la clave correcta; después hace falta el renderizador de la GPU (§5.7).

### 5.9 Avance 26 (10-11-2026): la UI sí abre una vista (`ViewScalarboot`); el motor 2D no se usa; F3 sigue bloqueada por la GPU

- **Corrección a §5.8**: `initializeViewConfig/ModelTree/ModelConfig/CautionConfig…` **sí se llaman** (nuevo `DLSYMLOG=1` registra cada `dlsym`: `initializeViewConfig` → `viewUnified2.so`, `initializeModelTree`, etc.). La vista de arranque real es **`ViewScalarboot`** (`viewUnified8.so`, `dlsym(ViewScalarbootToInstance)` ≠ 0, capas `Layer`/`Layout`), no `ViewRoot`: el `OPENVIEW` de §5.8 apuntaba a la clave equivocada. Tras abrirla, `FbPool` crea el *bitmap* y `UpdateStatusMonitor` avanza sin bloqueo.
- **Motor 2D**: `TRACEFN` sobre `GRM_gpermFillrect/Rectblit` y `GRM_fbrm*YUV` (`libObj+0x615248/0x6153a4/0x6149xx`) **no dispara nunca**: la composición de la UI no pasa por el motor 2D (`grm_gpe`) ni por la presentación YUV; solo queda la GPU de DMP.
- **Tabla de nombres GL** (`libObj` file `0x10370e0`, 196 nombres `gl*`/`egl*`, paso `0x30`): son cadenas en línea; la tabla de punteros asociada no está identificada (el candidato `0xfca780` da direcciones sin disparo con `TRACEFN`: glDrawElements `0x597014`, glClear `0x462cec`, glBindTexture `0x45fd7c`, etc. → **no verificado**). Las únicas parejas {nombre, función} halladas son 11 `egl*` en `0x1037024`.
- **Estado**: F3 no cerrada. Falta (a) saber si la vista de arranque dibuja algo (puede ser negra), (b) alcanzar `ViewRoot*` (publicador del primer evento `VM`) y (c) decodificar y rasterizar las listas de la GPU de DMP. F4/F5 siguen dependiendo de F3.

### 5.10 Avance 27 (10-11-2026): `ViewRoot` abierta y `InputService` recibe teclas

- **La clave de `openView` es `view/ROOT`** (nombres `view/…` de `viewUnified2/8.so`: `view/ROOT`, `view/SCALAR`, `view/SNAP_SHOT_BOOT`, `view/ROOT_SELECTOR`…), no `ViewRoot`. `SHIMENV='OPENVIEW=view/ROOT OPENVIEWAT=40'` carga `ViewRootToInstance`, `ViewRootSelector`, `ViewRootPowerSw` (`[ViewRootPowerSw] getCurrentLayout_POWER_ON`, `Root Draw`) y `ModelRoot`, `ModelAirplane`, `ModelJet`…; `InputService::activate` ya registra la tecla (`toActive … key_code=0x2 event_code=0x15010010`).
- La vista de arranque espontánea es `ViewScalarboot` (= `view/SNAP_SHOT_BOOT`, arranque desde instantánea); la transición a `ViewRoot` no ocurre sola porque falta el evento de av-cam. Pendiente: `ViewRootPowerSw` queda en `USBAndClockReady Non-Display` (`getTimeSettled … TIME get error`: falta la hora/reloj).
- **F4 (entrada)**: con `KEYQ=7a0020` e `INJECT` el mensaje llega a `I-InputMain` → `InputService` (`callback_convert_not_user_operation … INH event_code=0x15010010`; las repeticiones dan «same event»). Corregido en el shim el separador de `INJECT` (solo el primer mensaje se separaba por `/`; los tiempos son **hexadecimales**). No se ha encontrado aún la combinación `w1…w5` que dispare una acción de vista; y sin imagen no se puede comprobar el efecto.
- **F3**: el *bitmap* de pantalla (`/dev/stream off=0xb4000000`) sigue a cero con `ViewRoot` activa (`MEMSCAN`). Sigue bloqueada por la GPU de DMP.
- `DLSYMSTACK=subcadena` (nuevo): pila del que pide ese símbolo.

## 6. Auditoría del 09-11-2026 (esta sesión)

Verificado: `build.sh` reproduce byte a byte el `sonyshim.so` que se estaba usando (md5 `5307f8ae…` antes de las correcciones);
`bk.tbl` en uso procede exactamente de `20261105-volcado-total-nvram/backup_flash.bin` (88 volcados probados, 1 coincidencia);
los artefactos de Debian siguen disponibles con los mismos tamaños; el arranque desde el directorio reconstruido llega al mismo punto
que el avance 17 (§3). Correcciones aplicadas:

| Hallazgo | Corrección |
|---|---|
| El directorio de trabajo (kernel, initramfs, sysroot, overlay) vivía en el *scratchpad* de una sesión y no había procedimiento para rehacerlo | `setup.sh` (descargas con reutilización, extracción con `bsdtar`, base, shim, `bk.tbl`); destino `analysis/gui/g22/harness/` ignorado por git |
| El guion del guest se reescribía a mano en cada prueba (`t0…t96.sh`) y las variables del shim no se podían pasar desde el anfitrión | `im.sh` canónico + `SHIMENV` en `run.py` (`/cam/harness.env`) |
| `mbx_take` ignoraba un *timeout* positivo (esperaba para siempre) y devolvía `−1` en vez de `E_TMOUT` con `tmo=0` | espera con `pthread_cond_timedwait`; devuelve `E_TMOUT` |
| El buzón solo servía al grupo `0xaf` (constante): otra cola dinámica habría dormido para siempre | tabla `dynq[]` de colas creadas por `dynamic_id 0x2a` |
| Buzón lleno descartaba la respuesta en silencio | registro `mbx lleno` y liberación |
| `on_trace` usaba `fprintf` dentro del manejador `SIGILL` (riesgo de bloqueo con el cerrojo de `stderr`, el mismo fallo corregido en el avance 8 para `DUMPAT`) | `efp` (`write(2)`) |
| Pila duplicada (`sym(pc); sym(lr)` dos veces), `_GNU_SOURCE` redefinido, `kind[fd]` sin comprobar `fd < MAXFD`, `bk.tbl` vacío → `malloc(−1)` | corregidos |
| Sin pruebas ni documento; `G22-B` no figuraba en la tabla de PENDIENTES; 10 *cores* de 12–14 MB sueltos en la raíz y en `analysis/gui/g22` | `tests/test_gui_harness.py` (2 pruebas), este documento, fila G22-B, `*.core` ignorado y borrados; `ruff` limpio en `scripts/gui/harness` |

No corregido a propósito: `free` de uipc no libera (fuga sin efecto en 2 min), `sem_slot` lineal sobre 16 384 entradas (coste
despreciable), `direct_service` responde 0 a todo.

## 7. Plan para completar el arnés

| Fase | Trabajo | Criterio de cierre |
|---|---|---|
| F0 (hecha 09-11-2026) | Reproducibilidad, correcciones del shim, pruebas, documentación | `setup.sh` + `run.py` llegan al punto de referencia de §3 |
| F1 Cobertura de uipc (**ioctl hechos 09-11-2026; faltan servicios**) | `idx 3/8/9/13` y callbacks modelados (§2.1); quedan servicios de kernel sin respuesta (`0x7a0020`, `0x5700f9`, `0x5a0048`, `0x16f4010`, `0x61003c`), backup `op 1`/`op 5` (ids que son punteros) y `snd_sync_direct 0x910042` | Arranque sin ninguna línea «descartado»/«sin modelar» |
| F2 Desbloquear `grm_init` | (a) con `TIDLOG` seguir al trabajador B tras la respuesta `0xd9016e` hasta su siguiente espera; (b) identificar el servicio de la segunda petición (`0xaf404a`) y responderla como `0xd9016e`; (c) si el bloqueo es el asignador, imitar `65f420` (pools) en lugar de `malloc`; (d) si son los *callbacks* GL, sustituir la ruta GL entera (`0x717830` con `SKIPFN`) y satisfacer `grm_ma` con un asignador falso que no aborte en la limpieza | `grm_init` retorna, `THREAD_INFRA0/1` avanzan y **`appFw.so` se carga** (etapa 4) |
| F3 Pantalla (**bloqueada solo por la GPU, §5.6**) | No hay `/dev/fb0`: enganchar la presentación de [G03](g03-compositor.md) (`GRM_fbrmUpdateYUV` / `0x12e6d0`) para volcar la superficie YUV a `/tmp` y convertirla a PNG en el anfitrión | Imagen reconocible del menú o de la pantalla de disparo |
| F4 Entrada (**parcial: ViewRoot abierta y teclas llegan a InputService, §5.10; sin efecto verificable**) | Modelar `input`/`sircs` (teclas, rueda) por `uipc` o `/dev/input` para navegar | Cambio de pantalla al inyectar una tecla |
| F5 Uso (**no iniciada: depende de F3**) | Arrancar con los `nflasha15` modificados (3.5x, G10/G12/G15–G27) montando el `/usr` del paquete en `/cam/usr` | Menú modificado visible en emulación antes de instalar en cámara |

Riesgos: la semántica de los servicios de kernel de Sony se infiere del cliente (no hay fuente de los `.ko`); el GPU de DMP no es
emulable y la ruta GL tendrá que sustituirse; F3 depende de F2. F1–F2 son estáticas + emulación, sin cámara.

## 8. Límites de evidencia

Todo lo anterior es emulación de un firmware 3.21 con un kernel ajeno: lo que la UI haga aquí no demuestra comportamiento en
cámara (ver [G11](g11-auditoria-307-nflasha15.md) para lo que sí falló en hardware). Las direcciones de `libObj` son del 3.21
(`eb12512e…`). Ninguna afirmación de §5 sobre `grm_gles.ko`/`dmp_allocator` está verificada contra los módulos, que no están en el
firmware extraído.
