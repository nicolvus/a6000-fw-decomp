# FILM-PB-1 · Escalera SSBI y WBI propio del CFW 4.05: dónde falla `warm`

Coordinación de 10 subagentes (DeepSeek V4.1 Flash, `thinking=max`), 26-11-2026. Todo **estático** más los
registros ya capturados; sin cámara, sin SWD, sin escrituras.
Entregables: `reports/evidence/film-pb-1-ssbi-20261126/A1.md … A10.md`.

---

## 1. Respuesta en una página

**El tipo de apagado es el interruptor de todo.** `im.elf` no elige nada: reduce el factor de `0x920143` a un
tipo (`8` si factor `0x27`, `4` si `msg[8]==0x1b`, si no `1`) y lo pasa como `r0` a los 34 manejadores
`Is *_sus` (`im.elf@0xac52-0xac56`). De esos 34, **solo `SyncAndroid_sus` ramifica con el tipo**
(`libSyncAndroid.so@0x232c: cmp r4,#8`). El modo que se escribe en `/sys/power/state` es otra cosa: `0x27`→2,
`0x154d0`==1→1, resto→0; **modos 2 y 1 escriben `"warm"`, solo el modo 0 escribe `"mem"`** (`im.elf@0xa012`,
`@0xa030`, literales `0xa060`/`0xa068`).

| Ruta | Primera operación que falla (VERIFICADO) | Consecuencia |
|---|---|---|
| **B** · factor `0x27`, tipo 8, modo 2 nativo | `umount("/android/data")` devuelve `-1` con **errno 16 (EBUSY)**, 1 intento + 10 reintentos de 1 s, `retry failed.` → **`abort()` en `libSyncAndroid.so@0x209a`** | el proceso `im.elf` muere; el despachador nunca imprime `E Is 155_SyncAndroid_sus` ni pide el suspend al kernel ⇒ **no hay imagen** (`nflasha5` igual). Registro: `boottime-cuelgue-syncandroid-sus.txt:243-270` |
| **A** · factor `0x7`, tipo 1, `"mem"`→`"warm"` por SWD | en la **reanudación** `mount_fs()` (`0x19f8`) devuelve `-1` en `res_load_backup` (`0x1dc2` → `cbz` → **`abort@0x1dc8`**) | `raise(SIGABRT)` → `em_reboot(0)` → `RSTREQ_STAT=0` → `BUG at wdt.c:182` → frío. Registro: `klog-reanudacion-abort-imelf.txt` (`raise ← …`, pila `0x1dcd`) |

**Lo que unía las dos rutas y ahora está cerrado:** `mount_fs` **no** monta `/android/data`; monta
`/dev/ram8`→`data/data` y `/dev/ram9`→`data/system` (`ext2`, `flags=0x90`, cwd `/android`) — `libSyncAndroid.so@0x19f8`.
Antes, `SyncAndroid_res` imprime **`mount_ad: skipping`** (`boottime-mode12-reset.txt:197`, 6365 ms): **da por
montado** `/android/data` (pestillo `.data+0xc928`) y no lo monta. Si no lo está, `data/data` y `data/system`
no existen y `mount_fs` falla. **Es exactamente lo que pasó en la ruta A**, cuyo apagado fue tipo 1: sin el
bloque de tipo 8, nadie desmontó `/android/data` antes de la instantánea, y la reanudación lo dio por bueno.

**La receta de fábrica es la ruta B (INFERENCIA fuerte, no verificada en la imagen).** A8 sostuvo que el
`nflasha5` de Sony lleva dentro el log del apagado que lo creó (`count_sections_p2:1164, 42236`, física
`0x80396554`; 63 `cannot open file: ///android/data/backup/bk1.bak`; `/setting` con `iniok` e `init_bk.bak` de
1 346 048 B, sin `first_ssboot`). **No he podido reproducirlo**: el `nflasha5` del paquete
(`firmware/extracted/fw321/…/dev/nflasha5`, md5 `b49d6a7f…`, 42 293 120 B) contiene **0** apariciones de
`count_sections_p2`, `android/data/backup`, `iniok` y `first_ssboot`, y las direcciones físicas citadas
contienen **código Thumb** en el volcado `full-20261020-nand/ram_0x80000000.bin` (probado: `0x80396554`,
`0x8039774B`, `0x80395796`). El fichero empaquetado es 4× menor que su `oDataSize` (172 998 656 B), lo que
apunta a secciones comprimidas y explicaría la ausencia de texto.
Lo que **sí** está verificado es lo que hace falta: el ritual tipo 8 es el único que escribe `"warm"` y el único
que hace `unlink bk2.bak` + `make_init_bk.sh` + `umount_ad`; el tipo 1 no hace nada de eso. La imagen de fábrica
queda como **corroboración pendiente** (medida propuesta: descomprimir una sección del WBI y buscar el log).

**Conclusión operativa:** la ruta B es la correcta y está a **una sola cosa** de funcionar: que
`umount("/android/data")` deje de devolver EBUSY. No es un problema del CFW, ni de `im.elf`, ni del kernel:
es que **algo mantiene ocupado el vfat** en nuestra cámara cuando se apaga. Eso es lo único que queda por medir.

---

## 2. Hechos del bloque común que resultaron FALSOS (corregidos contra bytes y registro)

| Hecho del prompt | Estado real | Evidencia |
|---|---|---|
| «La ruta B termina en `Is 155_SyncAndroid_sus` (106,588 s) y nunca marca su `E`; no aparece `155 B make`» | **Falso.** El registro sigue: `E osal_wait_thread_exit` 109 398 ms, `B make` 109 549 → `E make` 135 698 ms, `umount AD` EBUSY×11 → `retry failed.` 145 804 ms y `L: BOOT`. La marca `make` sale **sin ruta** por una errata del script (`$des_init_bk` vs `des_ini_bk`) | `boottime-cuelgue-syncandroid-sus.txt:243-270`; `bin/make_init_bk.sh` |
| «La espera `osal_wait_thread_exit` es el cuelgue» | **Falso.** Es `pthread_join` sin plazo, sí, pero **volvió** en 2,81 s | `boottime-…:244` y `:256` (buffers 3 y 1, misma línea de tiempo) |
| «El abort de la ruta A se debe a que `/android/data` quedó montado» | **Refutado como causa, y como estado es lo contrario:** `mount_fs` no toca `/android/data`; falla porque la reanudación **no** lo montó (`mount_ad: skipping`) y faltaban los directorios | `libSyncAndroid.so@0x19f8`, `@0x1dc0-0x1dc8`; `boottime-mode12-reset.txt:197` |
| «`res_load_backup@0x1dc8`: `mount_fs` ≠0 → `abort`» | **Verificado** (`cbz r0`/`blx abort`) | `libSyncAndroid.so@0x1dc2-0x1dc8` |
| «`SyncAndroid_sus`: solo tipo 8 llega a `0x1fb8`» | **Verificado** (`0x232c cmp r4,#8` / `0x232e bne 0x2366`), y las tres cosas exclusivas del tipo 8: `unlink bk2.bak` (`0x2334`), `system(make_init_bk.sh)` (`0x235e`), `umount_ad` (`0x2362`) | bytes citados en A1/A9/A10 |
| «`im.elf@0x9F44` compara un contador» (CURRENT.md) | **Falso en el paquete**: `im.elf` del CFW tiene 4 B (`01 20 70 47` = `movs r0,#1; bx lr`) y es el **único** diff contra fábrica (`a8fe0d32…` → `00aa05ea…`) | A4, A5, A10 |
| «Parchear `cmp r3,#0x27` en `0xa130` equivale al `0x27` de Sony» | **Falso como parche de fichero**: `0xa132 str r3,[0x153e0]` guarda el factor real (`0x7`) y el modo se queda en 0 → `"mem"`. La conversión de SWD sí es equivalente porque cambia `r3` **antes** del `str` | A4; `swd-resumen.log` («CONVERTED off_factor 0x7 -> 0x27 (tipo 8, modo 2 nativo)`) |
| «`wdt_intr` con `STAT=0` viene de un watchdog» | **Falso**: `STAT=0` descarta ambos watchdogs; es `em_reboot(0)` desde el `abort` del proceso | A10 |

---

## 3. La cadena medida, extremo a extremo

### 3.1 Quién decide el factor (A5)

`0x920143` es `UPM_CMD_OFF` de `upm.ko` (`upm.ko@.rodata+0x148`), no algo que decida `im.elf`. El factor viaja
en `msg[4]` desde el **registro ganador** de `g_off_factor` (`upm.ko@.data+0x608`), que se llena con
`UPM_CMD_OFF_FACTOR` (`0x920141`) y se resuelve con el **máximo** (`get_max_off_factor`). El interruptor entra
por `libObj.so@0x8035f8` con especificador `0x00000000` ⇒ factor **7**, motivo `0x1c`. **Nadie emite `0x27` en
4.05**: los factores medidos son 7/`0x1a` (app), `0x0d` (updater), `0x24` (NFC) y `0x24/0x25/0x26`
(`ExtBackupCommunicator::ForcePowerOff`). El `0x27` solo se **consume**: `upm.ko@0xeff0` (`msleep(2000)` +
`ssboot_optimizer_stop_profiling`) y `im.elf@0xa130/0xa266`. La cadena de apagado cálido «de producto» exige
además el flag de Backup **`0x510023`** (`upm.ko@0xe6d4`, la misma clave que `im.elf@0x154d0`), que **ningún
binario de `/usr` escribe**.

### 3.2 Qué hace el tipo 8 y por qué aborta (A1, A2, A9)

`SyncAndroid_sus` (`0x22f0`): `0x2138` (compuerta `Backup_read(0x51000f)==5`) → marca `155 B osal_wait_thread_exit`
→ `0x1f34(0)` (mensaje a `0x8F013A`) → `osal_wait_thread_exit(*(0xC924))` (= `pthread_join` del hilo
`sus_android` creado por `SyncAndroid_inact`) → `0x1f34(1)` → **si `r4==8`**: `unlink("/android/data/backup/bk2.bak")`,
`system("/usr/bin/make_init_bk.sh 8")` (**26,1 s medidos**), `umount_ad()`.

`umount_ad` (`0x1fb8`): `umount("/android/data")` → `-1/16`, `sleep(1)`, ×10 → **`abort()` en `0x209a`**.
De ahí que el despachador `sus_all_i` no continúe, que no haya `E` del manejador y que el kernel nunca reciba
la orden de suspender: **la cámara se reinicia en frío sin imagen**.

### 3.3 Qué hace la reanudación y por qué aborta con tipo 1 (A3, A7)

`SyncAndroid_res` (`0x288c`): `mount_ad` (**`skipping`**: se fía del pestillo `0xc928`) → `select_bk_file`
(bk1/bk2/bk1.old) → `ld_bk_file` (escribe la imagen de 1 310 732 B en `/dev/ram8|9`) → `mount_fs`
(`/dev/ram8`→`data/data`, `/dev/ram9`→`data/system`, `ext2`) → si `-1`, **`abort@0x1dc8`**.

Con tipo 1 el apagado **no** ejecutó el bloque de tipo 8, así que `/android/data` quedó **montado** en la
instantánea; tras reanudar, ese estado no es utilizable, `mount_ad` no lo monta y `mount_fs` no encuentra los
directorios. **La ruta A no puede funcionar por construcción**: el tipo 1 no es la receta.

### 3.4 La escalera SSBI (A7)

Una sola palabra, `cxd90014_ssboot_stat` (`0x400523A0`), que **escribe el vector de reanudación**:
`0 MINSSBI` (frío ⇒ imagen `prof`) → `1 PROFILE` (el apagado siguiente solo **reetiqueta** el vector a
`_optimize`, no rehace imagen) → `2 OPTSSBI` (imagen `WBI0` + `_ssboot_pre` + `em_reboot(1)`) →
`3 SSBOOT_PRE` (el resume reescribe `WBI1` + `_ssboot`, `stat=4`, `SSBI Create Completed!`) → `4 SSBOOT`.
`free_some_memory` solo corre con `stat==0`. `/log/ssbi_prof.bin` **no está en el camino crítico**: su lector
(`ssboot_basic_optimize`) solo se alcanza en el bloque `Rewrite` del peldaño 2, y `ssboot_snapshot/write/finish`
no tienen llamantes. Hoy la cámara está en **peldaño 0 y ha llegado al 1** (`ssboot: basic: start profiling...`);
del 2 en adelante no hay ninguna medida.

---

## 4. Reparto de los diez subagentes

| # | Hallazgo | Estado |
|---|---|---|
| A1 | `SyncAndroid_sus` completo; las tres llamadas exclusivas del tipo 8; `umount_ad` con `abort@0x209a` | VERIFICADO |
| A2 | El hilo esperado es `sus_android` (`SyncAndroid_inact`), la espera es `pthread_join` sin plazo y **volvió** (2,81 s); `29189` = `BR_DEAD_REPLY` | VERIFICADO |
| A3 | `mount_fs` = ram8/ram9 ext2 bajo cwd `/android`; `mount_fs≠0` → `abort@0x1dc8`; refuta «/android/data montado» como causa | VERIFICADO |
| A4 | Factor→tipo, tipo como `r0` de los 34 manejadores, tres modos (`warm`/`mem`), orden inverso de los `Is` | VERIFICADO |
| A5 | `0x920143` = `UPM_CMD_OFF`; el factor es el **máximo** de `g_off_factor`; el interruptor emite 7; nadie emite `0x27`; clave `0x510023` | VERIFICADO (la vía de producto `0x24-0x26`→`0x27` es INFERENCIA) |
| A6 | Solo `SyncAndroid_sus` ramifica con el tipo; candidatos posteriores a bloquear: hotshoe, gps_rsrc, nfc, netservice | VERIFICADO |
| A7 | La escalera es una palabra que escribe el vector; orden 0→4; `ssbi_prof.bin` fuera del camino | VERIFICADO |
| A8 | Sostiene que el WBI de Sony lleva el log del apagado que lo creó (`/android/data` desmontado, `/setting` con `iniok`+`init_bk.bak`, sin `first_ssboot`) | **NO VERIFICADO**: no reproducible en el `nflasha5` del paquete ni en el volcado de RAM (ver §1) |
| A9 | Recetas híbridas con un solo disparo; EBUSY×11 → `abort`; el fallo de la ruta A es el destino inexistente | VERIFICADO + INFERENCIA |
| A10 | Auditoría: 2 eslabones falsos del bloque común, modo de 3 ramas, `tgkill`/`raise`, `wdt.c:182`, `STAT=0` sin watchdog | VERIFICADO |

---

## 5. La prueba física prioritaria (una sola)

**Objetivo:** saber **quién** mantiene `/android/data` ocupado (EBUSY) en el apagado tipo 8. Es lo único que
separa «la ruta B funciona» de «no funciona».

**Pasos (sólo lectura hasta el paso 4; el 5 es opcional y reversible al apagar):**

1. Root por telnet: `cat /proc/mounts > /tmp/m1.txt` y `grep -c . /tmp/m1.txt`.
2. `fuser -vm /android/data 2>&1 || busybox fuser -m /android/data`.
3. `for p in /proc/[0-9]*; do ls -l $p/fd 2>/dev/null | grep -q android/data && echo "$p $(cat $p/cmdline | tr '\0' ' ')"; done`.
4. Disparar el apagado tipo 8 (SWD `0x27` en `im.elf@0xa130`, como en `swd-imelf-offfactor-0x27.cfg`) y capturar
   el registro de arranque (`/proc/snsc_boot_time`).
5. Si el paso 2/3 da un PID: matarlo y repetir el 4 **una vez**.

**Predicciones**

| Observación | Conclusión | Siguiente paso |
|---|---|---|
| `fuser`/`/proc/*/fd` devuelve un proceso (p. ej. `android.process.media`, `ujlog.elf`) | el EBUSY es de **espacio de usuario**; matándolo, `umount AD` debe salir 0 y el apagado seguir | repetir con el proceso parado: si `umount AD` sale 0 y aparece `E Is 155_SyncAndroid_sus` + imagen `prof`, **cerrado** |
| Nadie lo tiene abierto y sigue EBUSY | es **kernel**: vfat sucio/writeback o un segundo montaje del mismo dispositivo | montar en solo-lectura o `sync`+`echo 3 > /proc/sys/vm/drop_caches` antes de apagar (repetir el 4) |
| `mount_ad: skipping` ya no aparece en la reanudación | el pestillo `0xc928` era el problema de la ruta A | cerrar A3 con el BP de `mount(2)` en `libc+0x9BC10` |

**Plan B si el paso 4 no puede instrumentarse:** un único breakpoint one-shot en `libSyncAndroid.so@0x2090`
(`0x09D74090`, último reintento, condición `r4==0xA`), leyendo `r7`/`r5`/`*(base+0xC928)` y el `errno` del
`umount` anterior; y otro en `libc-2.11.2.so+0x9BC10` (`0x04323C10`, condición `r7==0x15 && r0!=0`) para el
`mount(2)` de la reanudación.

---

## 6. Dudas abiertas (declaradas, no inferidas)

- **NO VERIFICADO** quién retiene `/android/data` (EBUSY): es la incógnita central.
- **NO VERIFICADO** qué `r0` (tipo) recibe `_sus` en la ruta B: el registro no lo imprime; se deduce del SWD.
- **NO VERIFICADO** el `errno` real del `mount(2)` de la reanudación (el código no lo lee).
- **NO VERIFICADO** el valor de `Backup 0x510023` en nuestra cámara (gobierna el modo 1) ni quién escribe
  `[obj+0x20c]` en `libObj.so`.
- **NO VERIFICADO** que el loader acepte una cabecera `invl` (peldaño 4) y qué vector elige en cada apagado.
- **NO VERIFICADO** el contenido del WBI de fábrica (A8): el fichero del paquete no contiene el log citado; hay que descomprimir una sección para comprobarlo.
- El orden de los `Is` posteriores al 5.º se tomó de un apagado con tipo ≠ 8 (`mem-20261020-log`).

---

## 7. Evidencia

`reports/evidence/film-pb-1-ssbi-20261126/`: `A1.md` (396 l.), `A2.md` (326), `A3.md` (294), `A4.md` (303),
`A5.md` (314), `A6.md` (205), `A7.md` (220), `A8.md` (339), `A9.md` (206), `A10.md` (227) — y los registros
`boottime-cuelgue-syncandroid-sus.txt`, `boottime-mode12-reset.txt`, `klog-reanudacion-abort-imelf.txt`,
`klog-reanudacion-wdt-bug.txt`, `swd-*.cfg`, `swd-resumen.log`, `resultado-ciclos-1-2.txt`, `armar.sh`.

Binarios: `build/wbi_silent/files/bin/im.elf` (`00aa05ea…`),
`build/cfw_fbm31_pkg397/work/xn397/lib/libSyncAndroid.so` (`768c6299…`, con símbolos),
`firmware/extracted/fw321/…/dev/nflasha5` (WBI de Sony, `b49d6a7f…`),
`firmware/extracted/fw321/…/nflasha3_unpacked_unpacked/vmlinux.bin` (VA `0x40038000`),
`analysis/session18/codex-g/oss-linux/linux/{kernel/exception.c,arch/arm/common/warm.c,arch/arm/mach-cxd90014/*}`.
