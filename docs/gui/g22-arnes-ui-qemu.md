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
| 4 | snd_msg | `0x8f0139/a` trazas (texto) · `0xd9016e` responde al solicitante (cabecera `0x61003c`, estado 0) · `0x9a015a/0x9c015b` (HDMI/WLAN) silenciadas · resto: descartado y registrado |
| 5 | snd_sync_msg | `0x8f013a` trazas · `0x3e014d` **backup** (op 0 tamaño, 3 lectura, 4 lectura de 4 B, 8 escritura descartada; datos de `bk.tbl`) · `0x14c0424` **dmm** (código 7: área por nombre → phys desde `0x80000000`, 64 MiB por área) |
| 6 | snd_sync_direct | responde 0 (`0x910042`… sin modelar) |
| 7 | rcv_msg | colas dinámicas (`dynamic_id` tipo `0x2a`) leen su buzón con el *timeout* pedido; las demás «duermen» y devuelven `E_TMOUT` |
| 10 / 11 | valloc / free | reserva `tamaño+0x240` con cabecera de 0x20; `free` no libera (fuga aceptada) |
| 12 | dynamic_id | tipo `0x32` semáforo y `0x2a` cola: id `(grupo<<16)|n` |
| 13 | wait_cb | bloquea para siempre (proxy) |
| **3, 8** | — | **sin modelar** (vistos en el arranque: `idx=8` tras crear la cola `0x3c4049`, `idx=3 args 0x7a0029`) |

Otros ganchos: cualquier otro `/dev/*` → fd inerte sobre `/dev/null` con `mmap` anónimo (`/dev/mem`, `/dev/stream*`, `/dev/nflasha4`…);
`/proc/modules` simulado con `grm_ma`/`grm_gles`; `dlopen`/`system`/`fopen`/`munmap` registrados; `abort()` vuelca `r4–r8/lr`;
`SIGSEGV/BUS/ILL/ABRT` imprimen la pila (direcciones resueltas por `/proc/self/maps`) y dejan el *core*.

### 2.2 Variables del shim (se pasan con `SHIMENV` de `run.py`)

| Variable | Efecto |
|---|---|
| `WAIT` / `TAILN` | `im.sh`: segundos de espera (50) y líneas finales mostradas (40) |
| `VERB=1` | muestra valloc/free/direct, `MSGHEX` de envíos a colas de kernel y `LOGRAW` |
| `TIDLOG=1` | antepone el tid a cada línea |
| `BKV=1` | registra cada petición al backup (por defecto solo los ids ausentes) |
| `CVWAIT=s` | tope en el `pthread_cond_wait` de `grm_init` (`libObj+0x719ee1`); `0` = sin tope |
| `POKE=dir` | escribe la dirección de `malloc` en `libObj+dir` (asignador del GPU: `fef348`) |
| `SKIPFN=dir[=v],…` | sustituye funciones Thumb de `libObj` por `movs r0,#v; bx lr` |
| `TRACEFN=dir,…` / `TRACEPEEK=dir,…` | traza única de entrada (`r0–r3`, `lr`) mediante UDF + `SIGILL`; `TRACEPEEK` lee palabras de `libObj` en cada traza |
| `WATCH=dir` | hilo que sondea cada ms `libObj+dir` y registra cambios |
| `DUMPAT=n` | a los n s manda `SIGUSR1` a cada hilo: pila con nombre |
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
`snd_msg 0xd9016e -> respuesta a 0xaf403b`, última espera `rcv_msg qid=0xaf404a tmo=-1`, sin `ABORT`/`EXIT`.

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
| F1 Cobertura de uipc | Modelar `ioctl idx 3` y `8` (ver §2.1), backup `op 1`/`op 5` (ids que son punteros), `snd_sync_direct 0x910042` según su estructura real; contar «ignorada / sin modelar» por arranque | Arranque sin ninguna línea «ignorada»/«sin modelar» |
| F2 Desbloquear `grm_init` | (a) con `TIDLOG` seguir al trabajador B tras la respuesta `0xd9016e` hasta su siguiente espera; (b) identificar el servicio de la segunda petición (`0xaf404a`) y responderla como `0xd9016e`; (c) si el bloqueo es el asignador, imitar `65f420` (pools) en lugar de `malloc`; (d) si son los *callbacks* GL, sustituir la ruta GL entera (`0x717830` con `SKIPFN`) y satisfacer `grm_ma` con un asignador falso que no aborte en la limpieza | `grm_init` retorna, `THREAD_INFRA0/1` avanzan y **`appFw.so` se carga** (etapa 4) |
| F3 Pantalla | No hay `/dev/fb0`: enganchar la presentación de [G03](g03-compositor.md) (`GRM_fbrmUpdateYUV` / `0x12e6d0`) para volcar la superficie YUV a `/tmp` y convertirla a PNG en el anfitrión | Imagen reconocible del menú o de la pantalla de disparo |
| F4 Entrada | Modelar `input`/`sircs` (teclas, rueda) por `uipc` o `/dev/input` para navegar | Cambio de pantalla al inyectar una tecla |
| F5 Uso | Arrancar con los `nflasha15` modificados (3.5x, G10/G12/G15–G27) montando el `/usr` del paquete en `/cam/usr` | Menú modificado visible en emulación antes de instalar en cámara |

Riesgos: la semántica de los servicios de kernel de Sony se infiere del cliente (no hay fuente de los `.ko`); el GPU de DMP no es
emulable y la ruta GL tendrá que sustituirse; F3 depende de F2. F1–F2 son estáticas + emulación, sin cámara.

## 8. Límites de evidencia

Todo lo anterior es emulación de un firmware 3.21 con un kernel ajeno: lo que la UI haga aquí no demuestra comportamiento en
cámara (ver [G11](g11-auditoria-307-nflasha15.md) para lo que sí falló en hardware). Las direcciones de `libObj` son del 3.21
(`eb12512e…`). Ninguna afirmación de §5 sobre `grm_gles.ko`/`dmp_allocator` está verificada contra los módulos, que no están en el
firmware extraído.
