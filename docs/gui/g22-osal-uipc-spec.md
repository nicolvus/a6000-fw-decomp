# G22-E: especificación de `osal_uipc` y `/dev/uipc` compartido entre procesos (T5b/T6)

Fecha: 12-11-2026. Análisis estático de `firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/kmod/osal_uipc.ko` (37 264 B, `vermagic 3.0.27_nl-rt106`, «OSAL Version 3.0», compilado el 24-01-2019) con `llvm-objdump -d -r` y `llvm-readelf -r`. Se cruzó con el modelo en proceso de `scripts/gui/harness/shim/sonyshim.c` (solo lectura). No se usó REA, ninguna VM ni la cámara. Las direcciones son desplazamientos en `.text` del `.ko`.

## 1. Interfaz `ioctl` (`__k_uipc_cdev_ioctl`, 0x5a0)

- `cmd & 0x7fffffff` = índice 0–16; un índice mayor de 16 da `-EINVAL`. `arg` apunta a 8 B de usuario `{w0, w1}` (`copy_from_user` de 8). El manejador es `tabla[idx](w0, w1, ctx)`, con la tabla en `.rodata+0x28` según `.rel.rodata`.
- Si no es `connect` (16) y `ctx+0x14` (base de usuario del `mmap`) vale 0: `-EINVAL`. Primero hay que llamar a `connect` y hacer el `mmap`.
- Si `ctx+0x10` no coincide con el campo `+0xcc` de la tarea actual: `printk("called from different process")` y `-EINVAL`. Un descriptor no se comparte entre procesos: cada proceso abre el suyo.

| idx | Manejador | Entrada (`w0`, `*w1`) | Salida |
|---|---|---|---|
| 0 | `__k_4u_stat_sem` | id | 12 B |
| 1 | `__k_4u_wai_sem_tmo` | id, tmo (ms; 0 = sondeo, −1 = infinito, según el shim) | ret |
| 2 | `__k_4u_sig_sem` | id | ret |
| 3 | `__k_4u_stat_msgq` | qid | 16 B |
| 4 | `__k_4u_snd_msg` | qid, puntero de usuario al cuerpo | ret |
| 5 | `__k_4u_snd_sync_msg` | qid, `&{msg, cb, arg}` (12 B, de ida y vuelta) | 12 B |
| 6 | `__k_4u_snd_sync_direct` | qid, 16 B; copia el mensaje a un bloque del kernel y lo envía síncrono | 16 B |
| 7 | `__k_4u_rcv_msg_tmo` | qid, `&{out, tmo}` (8 B) | 4 B: puntero de usuario |
| 8 | `__k_4u_reg_msg_queue_cb` | qid, `&{arg, cb, prio, sync}` (16 B) | 4 B |
| 9 | `__k_4u_unreg_msg_queue_cb` | qid | ret |
| 0xa | `__k_4u_valloc_msg_wait` | qid, `&{out, size, tmo}` (12 B) | 4 B: puntero de usuario |
| 0xb | `__k_4u_free_msg` | qid, puntero | ret |
| 0xc | `__k_4u_dynamic_id` | 0, `&{tipo, grupo, &id}` (12 B) | 4 B |
| 0xd | `__k_4u_wait_cb` | 0, `&out[4]` (16 B) | `{cb, arg, msg, 0}` (16 B) |
| 0xe | `__k_4u_set_msgq_broadcast_mode` | qid, modo | ret |
| 0xf | `__k_4u_set_msgq_log_mode` | qid, modo | ret |
| 0x10 | `__k_4u_connect` | `w0`, `w1` = `&out[4]` | `{0x80000, 0x20000, 0x8000, qid_dinámica}` |

Los índices coinciden con la tabla del shim (`sonyshim.c:459`). **Diferencia hallada:** `connect` devuelve en `out[3]` una cola dinámica creada con `osal_dynamic_id(0x2a, 0x3f, &out[3])` (0x4c8–0x4d4) y la guarda en `ctx+0x2c`. Tanto el shim como `uipc_stub.c` devuelven 0.

## 2. Memoria compartida (`__k_uipc_cdev_mmap`, 0x2a8)

- Solo acepta `vm_end − vm_start == 0x80000`; con otro tamaño da `-EINVAL`.
- Hace `remap_pfn_range` del **mismo búfer global** (puntero en `.bss+0x28`) en cada proceso. Todos los procesos ven la misma memoria y cada uno la tiene en su propia dirección. Guarda `vm_start` en `ctx+0x14`.
- Traducción de usuario a kernel (rutina 0x1ae0, usada por `snd`/`free`/`rcv`/`valloc`): `o = ptr − ctx.base`; si `o ≥ 0x80000`, error; si no, `kbase + o`. **Los mensajes viven en esta memoria compartida** y los punteros solo son válidos tras restar la base del proceso.

## 3. Mensajes, colas y semáforos

- `qid` = `grupo << 16 | índice`. `osal_valloc_msg_wait` rechaza índices `≥ 0x800` y trata aparte el bit `0x8000`. Para los grupos 0x3e y 0x8f se llama a `uipc_oom` en caso de falta de memoria.
- **Cabecera del mensaje (verificada)**: es de 12 B y el cuerpo empieza en `bloque + 12`. La escribe el asignador de 0x2cf4–0x2e1c y la lee `osal_msg_size` (0x475c):
  - `+0`: enlace de cola.
  - `+4` (`cuerpo[-8]`): nº de bloques de 32 B, igual a `(tamaño + 43) & ~31` dividido entre 32. Vale 0 en un `fblock` de 32 B para cuerpos ≤ 20 B.
  - `+5` (`[-7]`): banderas. Bits 0–5 = 1; bit 6 = cabecera extendida, que resta 24 al tamaño útil; bit 7 = 0.
  - `+6` (`[-6]`): u16 = 1.
  - `+8` (`[-4]`): `0xa5a5a5a5`, el literal en `.text+0x2e68`.

  El tamaño útil es `bloques·32 − 12`, o 20 si `bloques = 0`. Como el nº de bloques es un byte, el **máximo es 8148 B**. **Corrige al shim**: `[-4]` no es la cola origen al asignar, sino `0xa5a5a5a5`. NO_VERIFICADO si el envío la sobrescribe.
- Entrega con callback: `reg_msg_queue_cb` instala `__k_user_msg_cb` en el kernel. Cada envío a esa cola se encola para el proceso dueño, y sus hilos proxy (`[0x10]` de la memoria compartida = 8 hilos) lo recogen con `wait_cb` (idx 13). Después llaman `cb(msg, arg)` en espacio de usuario. Los síncronos (`sync = 1`, `__k_is_user_sync_cb`) se cierran con una segunda llamada `snd_sync_msg` (el shim lo trata con `t5[1] != 0`).
- Semáforos: `get_bsem`, `osal_wai_sem_tmo`/`osal_sig_sem`. Ids dinámicos de tipo 0x32 y colas de tipo 0x2a (`osal_dynamic_id`).
- NO_VERIFICADO: la numeración exacta de `osal_dynamic_id`, el formato de `stat_*`, la semántica de `broadcast`/`log`/`rt mode` y la prioridad de mensajes (`osal_set_msg_pri`).

## 4. Por qué no basta el shim

El shim emula `/dev/uipc` **dentro de un proceso**: abre `/tmp/uipc.shm` y resuelve en el mismo espacio de direcciones las colas, los callbacks y los servicios de kernel (Backup `0x3e014d`, `ma_service`, acuses). Un segundo proceso, como el `WS_SubProcess.elf` de T5b o el zygote, `system_server` y Tweak de T6, no comparte ese estado. Además, los binarios bionic de Android no cargan el shim, que es glibc. Hace falta un dispositivo de caracteres real con `ioctl` y `mmap`. Con CUSE no se puede, porque no permite `mmap`, así que **la vía es un módulo de kernel**. Un demonio con socket solo serviría a procesos glibc que carguen el shim.

## 5. Diseño propuesto

1. **`uipc_core.c` (hecho):** núcleo sin bloqueos ni dependencias que implementa las secciones 1–3 sobre un búfer de 0x80000 B. Incluye traducción por base de proceso, colas FIFO, callbacks por proceso dueño, semáforos e ids dinámicos. **Asigna bloques de 32 B contiguos** con mapa de bits (primer hueco), escribe la cabecera del `.ko` y admite hasta 8148 B. `connect` crea la cola dinámica del grupo 0x3f. Diferencia con el `.ko`: no usa `fblock` (bloques = 0) para cuerpos ≤ 20 B; da el mismo tamaño útil.
2. **Módulo `uipc_shared.ko` (hecho, `uipc_shared.c` + `build_uipc.sh`; compila sin avisos contra 6.12.113 con `clang` sin `-w`; sin probar en el invitado):** sustituye a `uipc_stub.c`.
   - Dispositivo `misc` `/dev/uipc` (0666) con `vmalloc_user(0x80000)` y `remap_vmalloc_range` en cada `mmap`, que fija la base del proceso.
   - Cada `open` es un proceso de `uipc_core` y comprueba el `tgid` como el `.ko`. `release` desconecta y libera sus colas.
   - Los 17 ioctls se atienden bajo un mutex. Las esperas usan `wait_event_interruptible_timeout` sobre un contador de generación (tmo en ms: < 0 infinito, 0 sondeo). `rcv`/`valloc`/`wai_sem`/`wait_cb` esperan de verdad.
   - `snd_sync_msg` a otro proceso encola al dueño y espera su cierre (segunda llamada con `cb ≠ 0`). Si el dueño es el mismo proceso, devuelve `{cb, arg}` como el shim. `snd_sync_direct` copia sus 16 B a un bloque compartido, hace la entrega síncrona y los devuelve.
   - NO_VERIFICADO:
     - tiempo agotado: el módulo devuelve −1022 como valor del `ioctl`, que a través de libc llega como `-1/errno 1022`. El shim devuelve −1022 directamente. Comprobar qué espera `libosal_uipc.so`;
     - formatos de `stat_*` (se devuelven ceros);
     - modos 0xe/0xf (sin efecto).
3. **Servicios de kernel (Backup, etc.) — especificación para el agente de la VM (dueño de `sonyshim.c`):** se quedan en el shim del proceso principal. En modo compartido (variable nueva, p. ej. `UIPC_SHARED=1`), el shim reenvía al `/dev/uipc` real los `ioctl` de colas que no resuelve. Además se registra con `reg_sync_msg_queue_cb` como dueño de las colas de servicio (`0x3e014d`, `0x14c0424`…). Así una petición de Tweak llega por `wait_cb` a un proxy del shim y la atiende el `backup_service` actual, que escribe la misma NVRAM emulada. Al trasladar el estado de colas del shim al módulo, sus punteros deben pasar a la ventana compartida: `valloc` debe asignar en el `mmap` y no con `calloc` (`sonyshim.c:470`). Pasos concretos en el shim:
   - a) no redirigir `open("/dev/uipc")` a `/tmp/uipc.shm` si existe el dispositivo real;
   - b) en el `ioctl`, llamar al `ioctl` real para los índices 0–2, 4 (salvo los servicios que el shim intercepta), 7–0xd y 0x10;
   - c) arrancar un hilo que haga `reg_sync_msg_queue_cb` de las colas de servicio y atienda `wait_cb` llamando a `backup_service`/`ma_service`/`direct_service`, y cerrar cada entrega con `snd_sync_msg {msg, cb≠0}`;
   - d) la cabecera `[-4]` es `0xa5a5a5a5` (sección 3).
4. **Orden de prueba:** cargar `binder32` + `ashmem` + `uipc_shared`. Luego el `MODE=zyg` de `android.sh` y, para T5b, `WS_SubProcess.elf`. El criterio sale de PENDIENTES: zygote pasa de `libosal_uipc` y «Conf. punto acceso» muestra la lista de redes.

## 6. Prueba

`tests/test_uipc_core.py` compila `uipc_core.c` y `uipc_core_test.c` con `cc` y comprueba lo siguiente con dos procesos de bases distintas:
- envío y recepción con traducción de punteros, y rechazo de punteros fuera de la ventana;
- entrega por callback, tanto de lo encolado antes del registro como después;
- `unreg`, semáforos, ids dinámicos y límites de tamaño.

Resultado: 1 passed. ruff y mypy sin avisos. Desde esta revisión la prueba cubre también mensajes de 8148 B, la cabecera del `.ko`, el doble `free`, el agotamiento y la recuperación del espacio.

**Prueba en el invitado (lista, sin ejecutar):** `build_uipc.sh` compila también `uipc_guest_test.c`, un binario ARM estático sin libc con syscalls directas. `prueba_uipc.sh` carga el módulo y lanza esa prueba. Dos procesos, cada uno con su `open`/`mmap`, se sincronizan con un semáforo y entregan un mensaje de 5000 B por callback (`wait_cb`). La prueba comprueba el contenido y la cabecera, el `free` y un `rcv` con tiempo agotado de 100 ms; imprime `UIPC OK` o `FALLO n`. Bajo `qemu-arm` en el anfitrión, sin `/dev/uipc`, termina con `FALLO 01` en ambos procesos, como se espera: confirma el binario y las syscalls. Se ejecuta en un `DIR_TRABAJO` propio con `run.py`, nunca en la VM interactiva.

## 7. Medición en el invitado (12-11-2026)

Se usó `run.py` con un `DIR_TRABAJO` propio (`analysis/gui/g22/harness/t6`, ignorado), sin red ni puerto, y una sola VM a la vez que se apagó sola al terminar. Los logs están en `t6/uipc_prueba.log` y `t6/zyg_diag3.log`.

- **`prueba_uipc.sh`: PASA.** `insmod uipc_shared.ko` crea `/dev/uipc` (`crw-rw-rw- 10,258`). `uipc_guest_test` imprime `UIPC OK` (salida 0), lo que confirma:
  - semáforo entre procesos con espera real de hasta 5 s;
  - `valloc` de 5000 B y entrega por callback a otro proceso (`wait_cb` devuelve `{cb, arg}`, el contenido y la cabecera `[-8]` = 157 bloques);
  - `free`;
  - `rcv` con tiempo agotado: −1022 tras 100 ms.

  En el invitado no hay `timeout` de busybox; se sustituyó por un vigilante con `sleep` y `killall`.
- **Convenio del tiempo agotado, resuelto por evidencia estática** (`libosal_uipc.so` de `nflasha16`): tras cada `ioctl` hace `r = ioctl(...); if (r == -1) r = -errno;` y compara `r` con −1021 para reintentar (`u_uipc_exit` 0x57f0–0x5824, `u_osal_reg_msg_queue_cb` 0x58ec–0x5914). Por tanto, un −1022 devuelto por el kernel (que libc entrega como `-1/errno 1022`) y el −1022 directo del shim **llegan iguales** al llamador. Ante una señal, el módulo devuelve ahora −1021 (no `-ERESTARTSYS`), para que la biblioteca reintente como con el `.ko` real.
- **Zygote con `binder32` + `ashmem` + `uipc_shared`:** primero salía con código 0 y sin traza. Con `diag.sh`, la salida estándar mostró que **Dalvik arranca** (`dalvikvm -version` = 1.4.0) y que `ZygoteInit.main` se ejecuta, pero falla en `ANDROID_SOCKET_zygote unset`, porque sin el init de Android no hay socket. `zygote_launch.c` (nuevo, ARM sin libc) crea `/dev/socket/zygote` y exporta la variable. Con él, el log `main` muestra `Zygote: Preloading classes...`, `setreuid() failed. errno: 2` y después **`dalvikvm-gc: Could not mmap 1748992-byte ashmem region 'dalvik-mark-stack'` → `VM aborting`**. `libosal_uipc` ya no es el bloqueo: el zygote pasa la carga de clases con el `/dev/uipc` real.
- **Frontera siguiente (sin resolver):** el `mmap` de una región ashmem en el GC. Probablemente el camino `MAP_PRIVATE` del port a 6.12 de `build_ashmem.sh` (`vma_set_anonymous` + `vma_set_file`); NO_VERIFICADO, falta el errno. Después vendrán el `setreuid` (errno 2) y las propiedades sin init (system_server).
