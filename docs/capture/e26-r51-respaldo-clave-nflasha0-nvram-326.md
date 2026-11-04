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
