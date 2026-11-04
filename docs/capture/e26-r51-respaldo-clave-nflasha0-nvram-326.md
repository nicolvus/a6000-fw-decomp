# E26-R51 — Respaldo de la clave de `nflasha0`, NVRAM en 3.26 y paquete 3.28 de reserva (antes de instalar el 3.27)

Fecha: 03-11-2026. Petición del usuario: respaldar lo que faltaba para la recuperación y después instalar el 3.27 ([R50](e26-r50-paquete-327.md)). Continúa [R49](e26-r49-cierre-recuperacion-326.md); misma sonda SWD (RP2040, `debugprobe-zero`) aún soldada.

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Qué faltaba

| Respaldo pendiente | Origen | Estado tras R51 |
|---|---|---|
| Clave de la vía serie del BootROM (`nflasha0`, bloque 0, sector `0xc00`, 8 B) | `E26-R33-BLOQUE0`, `E26-FISICO-BOOT` (2), `E26-R20-KEYTABLE` | **Leída (copia en SRAM)** |
| NVRAM posterior al 3.22 | E24-03 (A = NO) | **Volcada en 3.26** |
| Paquete de vuelta atrás mayor que el 3.27 | R50 §3 | **3.28 construido** |
| Arranque propio de Darwin (`0x0–0x41ff`), escritura de NAND, copia externa | E24-02a, E26-R5, R1 | Siguen abiertos (no hay medio sin `CN4906` ni disco externo) |

## 2. Clave de `nflasha0` (MEDIDO, solo lectura)

Lectura por **AP0 (AHB-AP)** con un target `mem_ap` de OpenOCD, **con la cámara en marcha y sin halt**: no se para la CPU ni se escribe nada. El BootROM carga en cada arranque los tres sectores de `0x600` B del bloque 0 en `0xc0000600` (R33 §1) y la SRAM conserva esa copia con la cámara en 3.26.

| Dato | Valor |
|---|---|
| `0xc0000600` | magia `EXBL` (`0x4c425845`), entradas `Loader2.bin` (`0xc01f0000`) y `DiagUni.bin` (`0xc0038000`) |
| `0xc0001200` palabra 0 (clave) | **`0x5bc022a5`** |
| `0xc0001200` palabra 1 | **`0xa8840468` = `~crc32(clave)`**; CRC-32 de los 8 B = `0xffffffff` → cumple el formato válido de R33 §4 |
| Resto del sector | `0x6`, `0x1`, `0x10100201`, luego `0xffffffff` |
| Repetibilidad | Dos lecturas de los `0x1800` B idénticas; coinciden con el mismo tramo de un volcado de 64 KiB de `0xc0000000` |

**Cierra la duda de R33:** el sector no solo «no está borrado»; contiene una **clave con formato válido**. La vía serie del BootROM (Multi pin 9, R32) queda abierta conociendo la clave. Límite: es la copia en SRAM que hizo el BootROM, no la NAND leída directamente (INFERENCIA fuerte de que son iguales: la cámara arranca por la rama `find_key = 0`).

Archivos (no versionados, en `analysis/camera-dumps/20261103-swd-nflasha0-clave/` y en `~/a6000-r1-backup/`):

| Archivo | SHA-256 |
|---|---|
| `nflasha0_blk0_sectores_0x600-0x1e00_sram.bin` (6144 B) | `54e6ee72f89a6a4473e79946715d01e181ac4ccc6a67290ef37be66faf8ce018` |
| `sram_c0000000_64k.bin` | `d909b0216c2277111ec61b81ce192f1145564ea7204422991fb7bd617bd2a99f` |

## 3. NVRAM en 3.26 (MEDIDO, solo lectura)

`scripts/senser_backup_dump.py analysis/camera-dumps/20261103-nvram-326` (service mode, sin escrituras): ILCE-6000, región `CX77500_E38`, firmware 3.26; `backup_flash.bin` y `backup_mem.bin` de 852 647 B, `bootrom.bin`, `SHA256SUMS`. `senser_backup_compare.py` lo parsea como BK4 válido frente a la referencia del 20-10. Copiado a `~/a6000-r1-backup/`.

## 4. Paquete 3.28 de reserva (contenido oficial)

`build_326.py` acepta ahora la versión menor (`build_326.py 0x28`; sin argumento sigue dando el 3.26). Mismo 3.24 verificado de E25-05 con solo `versionMinor` y sus sumas cambiados; todas las comprobaciones OK.

| Archivo (no versionado) | SHA-256 |
|---|---|
| `analysis/darwin-patch/fdat/recuperacion-328/firmware_packed.dat` | `e0d676d44bc95ce875e3f0ec8bfd044d710b639fb51665435c8f57266800a7ae` |
| `…/firmware_packed.fdat` | `7a625b26c627e6ff9895ce8e97efc16097e5feefa6b37640ed6caf6087e3e88c` |

Si el 3.27 bloquea la cámara: repetir R49 (SWD → actualizador) e instalar el 3.28.

## 5. Instalación del 3.27 (MEDIDO)

Autorizada por el usuario en esta petición. `pmca-console firmware -f analysis/e25-27/artifacts-327/package-3.27/firmware_packed.dat` (`0a5145a7…`): «Updating from version 3.26 to version 3.27», 5 %…100 %, `Done`, código 0, sin `0x1063`. Desconexión USB a las 22:56:36 y reconexión sola en Mass Storage (`054c:07c4`) a las 22:56:49. `pmca-console info`: **ILCE-6000, firmware 3.27**, objetivo `0x12a08019` (2.00).

**Primera prueba física de que el `nflasha3` con la forma de Sony (R45) arranca:** Loader3 carga `\sabin\idt_cam.bin` donde el 3.25 daba −302. Confirma en hardware la causa de R36 y la corrección del constructor.

**NO VERIFICADO:** el código nuevo (selector EFCS/Electronic, C3-B, compuertas Darwin) no se ha ejercitado todavía; sigue siendo `E25-27` (validación física con su protocolo). Si falla al usarlo: 3.28 de §4.

## 6. Crash al activar adb en 3.27 (03-11-2026, MEDIDO por SWD y telnet, solo lectura)

Dos medios: SWD (AP0, búfer de log del kernel en `0x83400000`, sobrevive a reinicios) y telnet `192.168.1.29:23` (`/proc`, sin escrituras).

| # | Evidencia | Lectura |
|---|---|---|
| 1 | Primer crash: Wi-Fi arriba a los 252 s; a los 304,6 s `[LDEC ERR] mumin_devif_wait_trans : -10003` → `LDEC request error (retry)` → `mumin_pbm_s_read_pages_in_pblkgroup` (pblk `0x02c3`, página 22) → `muminblk_request: request=write, sector=662525` → `end_request: I/O error, dev nflasha0` → `NULL pointer dereference at 0x6`, `Oops: 817 [#1] PREEMPT SMP` → `WARMBOOT` | Una escritura necesita leer antes la página (`read_modify_write_ltu`); la lectura falla y el kernel cae |
| 2 | Sector 662525 × 512 = `0x1437fa00` → dentro de `nflasha0p17` = `/dev/nflasha17`, montada en `/android/data` (vfat, `batch_sync`), calculado con `/proc/partitions` | Es la partición de datos de Android, donde adb guardaría su estado |
| 3 | Arranque posterior, sin intervención: el mismo `LDEC ERR -10003 (retry)` a los 77,7 / 128,7 / 179,7 s (cada ~51 s) y luego silencio; no existe `/android/data/misc/adb` | La página `0x02c3` da lecturas fallidas intermitentes aunque no se escriba |
| 4 | Segundo intento (adb activado otra vez): **no hay oops ni reinicio**. El log no cambia, uptime sigue (≥ 380 s), telnet responde, pero `loadavg` sube a 73 (1/5/15 min: 73/55/26). Hilo `bdev_dnflasha` (pid 69) parado en `mumin_devif_wait_trans`; `nmemories.tweak` (pid 850) y los `busybox` que tocan flash en `sleep_on_buffer` | La cámara se **cuelga** en vez de caerse: el controlador de la flash espera una transferencia que nunca termina y todo proceso que toque `/android/data` o `/setting` queda en estado D. No es la CPU (SWD y telnet viven) |

**Conclusión (INFERENCIA fuerte):** el fallo está en la capa de flash (`mumin`/LDEC) sobre una página física concreta de la partición de datos de Android, no en el parche del 3.27 (BIONZ/Darwin). No hay línea base con 3.21/3.26 para descartar al 100 % que el 3.27 influya. **NO VERIFICADO:** que la página esté dañada físicamente y qué escribe exactamente adb.

**Consecuencias:** no activar adb en esta cámara; la validación de `E25-27` debe hacerse sin tocar `/android/data` (RemoteShutter/telnet leyendo RAM no escriben flash). Telnet por sí solo funciona (lecturas de `/proc` y `/dev/mem`).

Evidencia: `analysis/camera-dumps/20261103-swd-nflasha0-clave/kernel-log-ram-*` (copiada a `~/a6000-r1-backup/`).

### 6.1 Origen del sector defectuoso (04-11-2026, MEDIDO por telnet en solo lectura, y SWD)

`/dev/nflasha17` (`/android/data`, FAT16: 512 B/sector, 4 sectores/clúster, 1 reservado, 2 FAT de 200 sectores, 512 entradas raíz; datos desde el sector 433) empieza en el sector 659 456 de `nflasha0`. El sector 662 525 de R51 §6 es el sector 3069 de la partición = **clúster 661**, que es entero el directorio **`/MISC/WIFI/SOCKETS`** (`FAT[661] = 0xffff`, cadena de un clúster), donde `wpa_supplicant` crea su socket de control. Con Wi-Fi apagado y **adb activado** (usuario, SWD sobre el log del kernel de este arranque), vuelve el `LDEC ERR -10003 (retry)` a los 764 y 815 s y la cámara queda colgada: adb también toca la página dañada (la página física puede compartir LTU con clústeres vecinos; **NO VERIFICADO** qué lee adb).

### 6.2 Reubicación fuera de la zona dañada (04-11-2026, MEDIDO por telnet)

Dueños de los clústeres vecinos del 661 (FAT de `/android/data`): 640–651 `/BACKUP/BK1.BAK`, 652 `/DONTPANIC/`, 653 `/MISC/`, 654–664 subdirectorios de `/MISC` (bluetooth, vpn, systemkeys, wifi, wapi, **sockets = 661**, wpa_supplicant, hostapd, dhcp), 665 en adelante `/LOCAL`, `/APP`, `/LIB/…`. Si la unidad de escritura (LTU) es de 32 KB, el sector 662 525 la comparte con los clústeres 645–661: crear `/data/misc/adb` (adb) o el socket de `wpa_supplicant` (Wi-Fi) reescribe esa LTU y obliga a leer la página dañada (INFERENCIA coherente con R51 §6 y §6.1).

Con la flash sin colgar (escritura de prueba con `sync` correcta, sin `LDEC ERR` en el arranque), en este orden: `mv misc misc_bad` y árbol `misc/…` nuevo con `wpa_supplicant*.conf` y el `dhcpcd` copiados (clústeres nuevos 1657–1671); `BK1.BAK` copiado a uno nuevo (verificado con `busybox cmp`) y el original renombrado `BK1.OLD`; `dontpanic` → `dontpanic_bad` y uno nuevo. **No borrar** `misc_bad`, `BK1.OLD` ni `dontpanic_bad`: mantienen ocupados los clústeres de la zona dañada. Pendiente: probar adb y un arranque con Wi-Fi.

### 6.3 Prueba tras la reubicación (04-11-2026, MEDIDO): sigue colgándose

Al activar adb tras la reubicación: `LDEC ERR -10003 (retry)` a los 465,75 s (`dmesg` por telnet, que sigue respondiendo); `flush-252:0` en `sleep_on_page`, un `busybox` en `sleep_on_buffer`, `bdev_nflasha`/`bdev_dnflasha` en D. `misc/adb` no llegó a crearse. El `loadavg ≈ 73` es la línea base: unos 70 hilos `liro-kliro_*` en D desde el arranque, no el cuelgue. Los directorios nuevos se habían creado con 755; corregido a 777 como los originales. **No se sabe qué sector toca adb ahora**: el `dmesg` no lo dice (en R51 §6 solo salió con el oops). Siguiente: `/proc/sys/vm/block_dump` (existe) para registrar cada E/S con sector y proceso antes del error.

Nota: el log del kernel leído por AP0 (SWD) se queda en el segundo 28 de este arranque: el anillo de `printk` no llega a la DRAM mientras está en la caché; para el log actual hay que usar `dmesg` por telnet.

### 6.4 Causa real del cuelgue con adb (04-11-2026, MEDIDO): `/android/system/framework/core.odex`

La reubicación de §6.2 dejó `misc` en 755 en la flash (el `chmod` hecho durante el cuelgue no llegó a escribirse) y el Wi-Fi dejó de conectar; corregido desde `pmca-console updatershell` (montaje con `posix_attr`, `chmod 777`, `umount` limpio). Con Wi-Fi funcionando y `/proc/sys/vm/block_dump` = 1, al activar adb:

* Procesos en D: `bdev_dnflasha` (pid 69) en `mumin_devif_wait_trans`, dos hilos en `muminlzp_request` (descompresor LZP), `nmemories.tweak` en `sleep_on_page` tras `READ block 118892 on dnflasha144 (248 sectors)`, un `busybox` en `sleep_on_buffer`. **Nada en `/android/data`.**
* `dnflasha144` = menor 144 = `dnflasha16` = **`/android/system`** (ext2 sobre TPZL, solo lectura). Con `debugfs` sobre `nflasha16_unpacked` del 3.21: sector 118892 → bloques ext2 59446–59570 → inodo 15670 = **`/framework/core.odex`**; bloque TPZL 928 de `nflasha16`.

Conclusión (INFERENCIA fuerte): el cuelgue lo causa la lectura de un bloque comprimido de `nflasha16` que el LDEC no descomprime (`-10003`); cualquier proceso Dalvik que necesite esa zona de `core.odex` lo dispara (Tweak al activar adb; probablemente también el arranque del Wi-Fi en R51). `nflasha16` es el original de Sony (no lo cambia ningún paquete propio), así que apunta a la NAND física o a que el actualizador no la reescribe. La reubicación de §6.2 no era necesaria para adb (la deja, inocua). **NO VERIFICADO:** que el actualizador reescriba `nflasha16` en cada instalación.

### 6.5 Lectura cruda del bloque TPZL 928 de `nflasha16` (04-11-2026, MEDIDO)

Bloque 928 en la imagen oficial: offset `0x1dc0600`, 44 544 B (87 sectores desde el 60 931), 0 violaciones del modelo LDEC. Leído en la cámara recién arrancada por la vía cruda (`dd if=/dev/nflasha16 bs=512 skip=60931 count=87`, sin descompresor): **SHA-1 `9492728e…` idéntico** a la imagen. Los datos grabados están bien y la vía normal de lectura los devuelve; falla solo la lectura por el LDEC (`dnflasha16`). Hipótesis (INFERENCIA): errores de bit corregibles por la vía normal pero no por la del LDEC (desgaste o retención de esa página). Arreglo posible: reescribir esos 87 sectores con los mismos bytes para que la FTL los grabe de nuevo (refresco). **NO VERIFICADO.**
