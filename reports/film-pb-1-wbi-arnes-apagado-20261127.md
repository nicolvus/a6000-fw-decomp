# FILM-PB-1 — apagado `warm` (WBI) emulado en el arnés (27-11-2026)

Sin cámara. Script: `scripts/gui/harness/wbi_apagado.sh DIR_TRABAJO SALIDA [factor_hex]`. `im.elf` real bajo `sonyshim.so`; el shim hace de `upm.ko`.

## Qué reproduce (MEDIDO en el arnés)
- Cadena inyectada en la cola `0x94016a` (`INJECT`, separador `@`, tiempos en hex): `0x920143` (factor `0x27` → tipo 8) → `inact_all`; `0x92014B` → `sus_all_i` con `SyncAndroid_sus`; `0x92014D` → `sus_all_u`; `0x92014F` → `open("/sys/power/state")` (capturado en `/cam/tmp/power_state`; una ejecución sin `0x92014B` escribió `warm`).
- `ANDROIDFS=real`: `/android/data` y `data/{data,system}` son tmpfs reales; `mount(/dev/ramN)` → tmpfs; `umount` real.
- `SyncAndroid_sus` tipo 8: `osal_wait_thread_exit` → `system(make_init_bk.sh 8)` → 0 → `umount(/android/data)` → **0**. `/setting/init_bk.bak` = 1 314 816 B (cámara: 1 346 048 B), `iniok` presente.

## Conclusión para la cámara
Con montajes anidados, `libSyncAndroid` y `make_init_bk.sh` como únicos actores, el `umount` **no** da EBUSY. En cámara sí (errno 16 ×11). El culpable es un proceso real con `cwd`/`fd`/`mmap` bajo el vfat `/dev/nflasha17` que el arnés no tiene (candidatos: servicios Android —`init.rc` crea `dalvik-cache`, `app`, `misc` ahí— o `adbd`). Medida pendiente en cámara durante el `make` de 26 s: `ls -l /proc/*/cwd /proc/*/fd | grep android/data`.

## Límites (no idéntico aún)
- `sus_all_i` no termina: `09c_CEC_sus`/`09a_HDMI_sus` esperan a hilos que leen `/dev/cec`/`/dev/hdmi` (no modelados). `DEVREADWAKE` los despierta con EINTR pero el resultado cambia entre pasadas (carrera). El `write` final no está verificado con la cadena completa.
- Kernel Debian: no fabrica la imagen (`warm.c`, `liro`) ni reanuda.
- Tiempos de inyección fijos; `0x92014E` (`dmm_pre_suspend`) no se inyecta.
