# G22-E T6: viabilidad de apps PMCA en el emulador interactivo

Fecha: 12-11-2026. Solo emulador y análisis estático; sin cámara, sin flasheo y sin arrancar la VM del arnés. En esta sesión no se arrancó ninguna VM: las mediciones de arranque son de ejecuciones `run.py` anteriores en `analysis/gui/g22/harness/t6/` (ignorado), hechas con `scripts/gui/harness/android/`.

## Veredicto

**No es viable a coste bajo.** La capa de kernel es barata y en buena parte está hecha: el binder de 32 bits se midió y ashmem ya compila. El bloqueo real es **`osal_uipc` entre procesos**, el mismo de T5b. Casi todo el lado Sony de Android (system_server, gralloc, sensores, servicios scalar) y la propia OpenMemories Tweak hablan por colas `osal_uipc` con el proceso principal de la cámara. El shim del arnés solo modela esas colas dentro del proceso principal. Ejecutar Tweak con funciones reales exige emular `osal_uipc.ko` (kernel 3.0.27) entre procesos y tener servidores de Backup y DI en el lado principal. Coste alto: ingeniería inversa de `osal_uipc.ko` (89 funciones) y del protocolo de mensajes de Backup.

## Evidencia

| Capa | Estado | Evidencia |
|---|---|---|
| Kernel de la cámara | 3.0.27 (`vermagic 3.0.27_nl-rt106`) | `nflasha15_unpacked_unpacked/kmod/osal_uipc.ko` |
| binder | **MEDIDO OK** en 6.12.113: el binder moderno (u64) da `EINVAL` con el `BINDER_WRITE_READ 0xc0186201` de 2.3; recompilado con `BINDER_IPC_32BIT`, `servicemanager` queda vivo | `build_binder32.sh`; `zyg1.out`/`zyg2.out` |
| ashmem | Retirado del kernel (5.18). **Compila** como módulo para 6.12.113 (port mínimo, sin shrinker); **sin probar en el invitado** | `build_ashmem.sh` → `t6/ash/ashmem.ko`, `vermagic 6.12.113+deb13-armmp` |
| Necesidad de ashmem | `libdvm.so`: `dalvik-heap`, `ashmem LinearAlloc failed`, caché JIT; `libcutils.so` abre `/dev/ashmem` | `strings` |
| `/dev/uipc` | **MEDIDO**: sin él, zygote muere (`open /dev/uipc error`). Con un `uipc_stub.ko` anterior muere en `ioctl :: Not a typewriter`; la cadena `ioctl :` es de `libosal_uipc.so`. No hay medición con el stub actual (`zyg3.out` vacío, interrumpido) | `zyg1.out`, `zyg2.out` |
| Dependencia de uipc | 19 bibliotecas de `/system/lib` enlazan `libosal_uipc.so`, entre ellas `libandroid_servers.so` (system_server), `libhardware_legacy.so`, `gralloc.diadem.so` (vía `libdihal.so`), `sensors.diadem.so`, `libscalar_*`, `libusbappdl.so`, `libma.so` y `libavindex.so` | `readelf -d` |
| Pantalla | `egl.cfg` = `dmp` (`/dev/dmpgles2`, GPU DMP); gralloc `diadem` por DI HAL/uipc. `gralloc.default.so` (fb0) es la única salida sin Sony | `lib/egl`, `lib/hw` |
| Tweak (APK del volcado `live/data`) | `libtweak.so` necesita `libosal_uipc.so` (`osal_snd_sync_msg`, `osal_valloc_msg_wait`) y llama `Backup_read/write/get_attribute`, `backup_senser_cmd_preset_data_read` y `/dev/mem`. `libprotectiontweak.so` está enlazada contra glibc (`libc.so.6`, `libbackup.so`, `libusbcmd.so`): es para el lado Linux, no para Dalvik | `readelf`, `strings` |
| PMCA por USB | Lo atienden `ScalarAUsbDlApp`/`libusbappdl.so` (también por uipc). En el emulador no hace falta: basta copiar el APK | `/system/app`, `readelf` |

## Qué haría falta, en orden

1. **Kernel (barato, casi hecho):** `binder32.ko` (medido), `ashmem.ko` (compilado) y una prueba de carga en el invitado. También `/dev/alarm` (`libutils`, `libandroid_servers`), retirado en 3.20: hay que portarlo o tolerar su fallo (NO_VERIFICADO). Logger: `android.sh` ya usa ficheros normales.
2. **`osal_uipc` entre procesos (caro, bloqueo común con T5b):** colas, semáforos y memoria compartida reales en un módulo, o un servidor en el anfitrión. Hoy `uipc_stub.c` solo responde a `0x80000010` y al `mmap` de 0x80000 B; las demás órdenes devuelven 0 sin efecto, así que cualquier `osal_snd_sync_msg` queda sin respuesta.
3. **Servicios Sony del lado principal:** servidor de Backup (para Tweak; el shim ya tiene los datos de `bk.tbl` en proceso), DI HAL o display para gralloc, árbitro de sensores, `androidsystemstateservice` y los 13 `com.sony.scalar.*.jar` del `BOOTCLASSPATH` (`init.rc` de `nflasha15` ramdisk, línea 20). Sin ellos, `system_server` no llega a lanzar el launcher Sony.
4. **Pantalla:** sustituir gralloc/EGL `dmp` por `gralloc.default` + `libGLES_android` (render por software) en un framebuffer virtual. Es el camino estándar de Android 2.3, pero la composición con la UI Sony no sería la de la cámara.
5. **Instalación sin USB:** copiar el APK a `/data/app/<pkg>-1.apk` y las `.so` a `/data/lib/<pkg>/lib/` (como en el volcado `live/data`). PackageManager de 2.3 escanea `/data/app` al arrancar y genera `dalvik-cache`. El lanzador `ScalarALauncher`/`ScalarAAppManager` puede exigir además su propio registro (NO_VERIFICADO).

## Qué rompe o queda falso

- Sin el paso 2, Tweak abriría a lo sumo su interfaz Java. Sus lecturas y escrituras de Backup quedarían colgadas o fallarían, y no escribiría en la NVRAM emulada. Esto incumple el requisito de «mismo dato verificado».
- `/dev/mem` de Tweak apunta a registros físicos de la cámara que no existen en `virt`.
- Con gralloc/EGL por software, la apariencia y el rendimiento no son los de la cámara.

## Prototipo de esta sesión

`scripts/gui/harness/android/build_ashmem.sh DIR_TRABAJO` descarga `ashmem.c` de Linux 5.15.170, lo adapta a 6.12 (`mm_get_unmapped_area`, `vm_flags_clear`, `mmap` de shmem en vez de `shmem_zero_setup`, que ya no se exporta, sin shrinker) y lo compila con el entorno de `build_binder32.sh`. Se versionan también los scripts previos sin commit de T6 (`android.sh`, `prep.sh`, `build_binder32.sh`, `uipc_stub.c`). Para medirlo falta añadir `insmod ashmem.ko` en `android.sh` y una ejecución `MODE=zyg` cuando la VM esté libre.

## Medición 13-11-2026: zygote → system_server

Solo emulador (`run.py`, `DIR_TRABAJO=analysis/gui/g22/harness/t6`, salidas en `analysis/gui/g22/harness/runs/t6-*`, ignorados). Sin cámara ni flasheo.

| Paso | Resultado | Evidencia |
|---|---|---|
| `chmod 666 /dev/ashmem /dev/binder` (como `ueventd.rc` del firmware) | **MEDIDO**: desaparece `Could not mmap … 'dalvik-mark-stack'`; el zygote (euid 9999 al precargar) termina la precarga y crea system_server (`Entered system_init()`) | `t6/init4.log` |
| `MODE=init`: gralloc `diadem` | **MEDIDO**: `[Connect][121]osal_valloc_msg error err = -9` → SIGSEGV de system_server. `-9` es EBADF: `u_osal_valloc_msg_wait` (0x5a50) devuelve `-errno` del `ioctl`; el hijo del fork reabre `/dev/uipc` en el `pthread_atfork` de `u_uipc_init` (0x6414/0x6438 → `do_init` 0x6180) y cierra el fd si `open`/`mmap` fallan | `t6/init4.log`, desensamblado de `libosal_uipc.so` |
| Causa del EBADF | **MEDIDO**: en el `/dev` de Android, `/dev/uipc` es `c 251,207` (número del `osal_uipc.ko` real; la cadena `/dev/uipc` está en el `/init` de Sony), pero `uipc_shared.ko` es misc `10:260` (sysfs). `android.sh` rehace el nodo con el número de sysfs cada vez que init lo recrea (4–8 veces al arrancar) | `runs/t6-init7.out`, `runs/t6-init9.out` |
| Con el nodo corregido | **MEDIDO**: sin EBADF; gralloc registra `OSAL_MSGQ_GID_HAL` y falla en `[getBufferManager][178]osal error!!` (`osal_snd_sync_msg err = -1022`, tiempo agotado) → `failed to get BufferManager` → SIGSEGV en `system_init()` | `runs/t6-init9.out`, `runs/t6-init10.out` (`couldn't open framebuffer HAL (Invalid argument)`) |
| `MODE=zyg` (sin init ni propiedades) | **MEDIDO**: la parte nativa de system_server termina (`entering thread pool`), Java llega a EntropyService/PowerManager y muere en `ActivityManagerService.getIntProp` (`unable to parse '' as integer`) | `t6/zyg12.log` |

**Bloqueo actual:** `gralloc.diadem.so` necesita un servidor `BufferManager` al otro lado de uipc (en la cámara lo da el sistema Sony fuera de Android); sin él no hay SurfaceFlinger y system_server cae. Opciones siguientes, sin probar: (a) quitar `gralloc.diadem.so` para que libhardware use `gralloc.default.so` (necesita `/dev/graphics/fb0`, no comprobado en `-M virt`); (b) un servidor `BufferManager` mínimo sobre `uipc_shared` (protocolo sin estudiar); (c) registrar `uipc_shared.ko` en `251:207` en vez de rehacer el nodo (shortcut actual en `android.sh`).
