# FILM-PB-1 — apagado `warm` (WBI) emulado en el arnés (27-11-2026)

Sin cámara. Script: `scripts/gui/harness/wbi_apagado.sh DIR_TRABAJO SALIDA [factor_hex]`. `im.elf` real bajo `sonyshim.so`; el shim hace de `upm.ko`.

## Qué reproduce (MEDIDO en el arnés)
- Cadena inyectada en la cola `0x94016a` (`INJECT`, separador `@`, tiempos en hex): `0x920143` (factor `0x27` → tipo 8) → `inact_all`; `0x92014B` → `sus_all_i` con `SyncAndroid_sus`; `0x92014D` → `sus_all_u`; `0x92014F` → `open("/sys/power/state")` (capturado en `/cam/tmp/power_state`; una ejecución sin `0x92014B` escribió `warm`).
- `ANDROIDFS=real`: `/android/data` y `data/{data,system}` son tmpfs reales; `mount(/dev/ramN)` → tmpfs; `umount` real.
- `SyncAndroid_sus` tipo 8: `osal_wait_thread_exit` → `system(make_init_bk.sh 8)` → 0 → `umount(/android/data)` → **0**. `/setting/init_bk.bak` = 1 314 816 B (cámara: 1 346 048 B), `iniok` presente.

## Conclusión para la cámara
Con montajes anidados, `libSyncAndroid` y `make_init_bk.sh` como únicos actores, el `umount` **no** da EBUSY. En cámara sí (errno 16 ×11). El culpable es un proceso real con `cwd`/`fd`/`mmap` bajo el vfat `/dev/nflasha17` que el arnés no tiene (candidatos: servicios Android —`init.rc` crea `dalvik-cache`, `app`, `misc` ahí— o `adbd`). Medida pendiente en cámara durante el `make` de 26 s: `ls -l /proc/*/cwd /proc/*/fd | grep android/data`.

## Resultado de la pasada completa (MEDIDO, 28-11-2026)
`wbi_apagado.sh` con factor `0x27`: `inact_all` → `sus_all_i` (incluye `SyncAndroid_sus` tipo 8, `umount(/android/data)`=0) → `sus_all_u` → `0x92014F` → **`POWERSTATE escrito: [warm] (4 B)`** (modo 2 nativo, como en cámara).

## Cadena por eventos y reproducción de la ruta B (MEDIDO, 28-11-2026)
`WBICHAIN=27` encadena `0x920143 → 0x92014B → 0x92014D → 0x92014F` esperando al `E In 094_inact_all / sus_all_i / sus_all_u` del registro de `im.elf` (sin tiempos fijos). Salida normal: `umount`=0 y `POWERSTATE escrito: [warm]`.
`BUSY=1` (`ANDROIDBUSY`): `umount("/android/data")` devuelve `-1/EBUSY`, dato medido en cámara. Resultado idéntico al registro de cámara (`boottime-cuelgue-syncandroid-sus.txt:259-270`): 1 intento + 10 reintentos con errno 16, `umount AD: retry failed.`, `abort()` con `lr=libSyncAndroid+0x209f` (llamada en `0x209a`), `EXIT=134`; no se llega al `write` ⇒ no hay imagen. Es decir, **con solo ese dato la ruta B del arnés reproduce el fallo de la cámara**; lo que sigue desconocido es qué proceso retiene el vfat, no sus consecuencias.

## Atajos del arnés (no son datos de la cámara)
- `SKIPSUS`: `CEC_sus`, `HDMI_sus` y `UsbControl_Suspend` se neutralizan (esperan hilos de `/dev/cec`, `/dev/hdmi` y `/dev/usb/event`, no modelados).
- `DEVREADWAKE`: en fase de suspensión, toda lectura bloqueada de dispositivo no modelado (salvo `/dev/usb/event`, donde EINTR hace caer a `libusb` con SIGSEGV) expira cada 200 ms.
- Aviso de método: tres pasadas intermedias usaron un `.so` viejo porque `build.sh` fallaba en silencio; comprobar siempre la hora del `.so`.

## Límites (no idéntico al 100 %)
- Kernel Debian: no fabrica la imagen (`warm.c`, `liro`) ni reanuda; el `umount` da 0 en el arnés y EBUSY en cámara (falta el proceso que retiene `/android/data`; medir `/proc/*/cwd,fd` en cámara).
- `0x92014E` (`dmm_pre_suspend`) lo consume `upm.ko`, no `im.elf`: no se inyecta. El EBUSY de `BUSY=1` se impone, no se deduce.
