# E26-R89 — ADJUST, dmode y smode en la A6000 fw3.21 (arranque sin app)

Fecha: 11-11-2026. Origen: hilo [pmca-re-reloaded#13](https://github.com/masterflai/pmca-re-reloaded/discussions/13) (A6100 con `/usr/lib/CautionConfig.so` truncado y bucle de arranque). Pregunta: ¿hay alguna ruta en el bootloader o en `init` para arrancar sin la app? **Solo análisis estático** de `rootfs/sbin/init` (idéntico a `main/initrd.img_unpacked/sbin/init`), `usr/bin/bootin.elf`, `im.elf`, `upm.ko` y de `nflasha15` descomprimido (`analysis/camera-dumps/nand-20261020/dev_nflasha15.bin`, TPZL → ext2 con `scripts/e25_27/tpzl.py`). Sin cámara.

## 1. Resultado

| Pregunta | Respuesta | Etiqueta |
|---|---|---|
| ¿Existe un «service mode» en Loader3? | No. Loader3 solo tiene el modo 3 (UPDATER) que evita `nflasha3` ([R37](e26-r37-cierre-estatico-recuperacion.md) §2). El service mode lo decide `init` (Linux) | BINARIO |
| ¿Qué hace ADJUST (modo 5 de Loader3)? | El kernel lo publica en `/proc/udm/upm_bootmode` como `ADJUST`; `init` solo **omite `/usr/bin/s_start_android.sh`**, que arranca **Android** (`chroot /android`, `dnflasha16`/`nflasha17`, `usbg_adb.ko`), **no la app de cámara**. La app sigue arrancando por `bootin.elf` → `im.elf`. ADJUST **no evita** el fallo de una app que se cuelga | BINARIO + SCRIPT |
| ¿Quién pasa `amode=adj` a `bootin`? | No se encontró: ni `init` ni ningún script/binario de `/usr` lo hace (`s_start_android.sh`, `change_mode.sh`, `network.sh`, `up.sh`, `sen.elf`, `adjstctl.elf` no lo contienen) | LEÍDO |
| `net_cmdd.elf` | `init` lo lanza, pero **no existe en `/usr` del 3.21** (`debugfs: File not found`): no hace nada | LEÍDO |

## 2. Ficheros de control (todos en `/setting` = `nflasha2`, la FAT que Loader3 monta como dispositivo 2)

| Fichero | Lo lee | Efecto |
|---|---|---|
| `/setting/mode/dmode` | `bootin.elf` (`file=`, por defecto) | 1.er carácter `0`–`3`: `0` solo kernel, `1` + infra global, `2` + LIRO, `3` + appFw (por defecto). Sufijos: `n` driver no unificado, `L` LeakTracer, `w` Wfree, `k` KMC ICE, `g` gdb, `s` gdbserver, `d` DUMA, `e` EFence. Lo escribe `/usr/bin/change_mode.sh` |
| `/setting/sen/smode` | `init` (`check_forced_senser`) e `im.elf` | Si empieza por `UU` y `upm_bootmode` no es `BIS` → `init` lanza `/usr/bin/sen.elf` (service/senser) |
| `\updater\mode` | Loader3 `chk updater` | Modo 3 (updater de fábrica de `nflasha1`) |
| `\mode\cmode` | Loader3 `chk adjust` | Modo 5 (ADJUST) |

`usbg_sen.ko` y `usb_extcmd.ko` los carga `init` en **todos** los arranques (klog `20261110-swd-371`), antes de la app; lo que falta para el service mode es `sen.elf`.
Toda la userland (`bootin`, `sen.elf`, `im.elf`, `change_mode.sh`) está en `/usr` = `nflasha15`: un `/usr` roto impide también `bootin`/`sen.elf`.

## 3. Aplicación al hilo (A6100, CXD90045)

- El mismo mecanismo `smode`/`dmode` de la ZV-E10 (qn06142/zv-e10-re) existe en la A6000 con `change_mode.sh` incluido: confirmación independiente, no extensible sin más a la A6100.
- Para evitar la app basta una entrada de directorio FAT en `nflasha2` (`dmode`=`0`/`2` o `smode`=`UU`), mucho menos que reparar 12 MB, pero exige escribir NAND igualmente.
- **Método offline reutilizable:** en la A6000 `nflasha15` es TPZL (Sony) de un ext2. `scripts/gui/build_nflasha15.py` descomprime, sustituye ficheros con `debugfs`, exige `e2fsck -fn` limpio y respeta el bloque 0 de Sony. Si la `nflasha15` de la A6100 fuera un ext2 plano, bastaría `debugfs`/montaje loop del PC en vez de parchear bytes.

## 4. Límites

- No se probó nada en cámara. ADJUST nunca se forzó por SWD; la lectura es de A6000 fw3.21.
- La corrección de R89: la conclusión provisional anterior de esta sesión («ADJUST omite la app») era errónea; omite Android.
- No se decodificó quién pasa `amode=adj`; `im.elf` solo lee `upm_bootmode` en la comprobación `BIS` de forced-senser.
- La A6100 puede diferir (SoC, `init`, formato de `/usr`).
