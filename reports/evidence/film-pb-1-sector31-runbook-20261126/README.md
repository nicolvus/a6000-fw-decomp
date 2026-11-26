# Evidencia — `scripts/film_pb1_sector31.py` verificado EN SECO en el invitado del arnés

Nada de esto toca la cámara: todo es QEMU sobre una copia del volcado. Perfil del arnés
`analysis/gui/g22/harness/live/nf4` (`NFLASH4=1` → `/dev/nflasha4` = copia real de
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin`, 10 485 760 B) **sin** precargar
`nf4inject.so` (la inyección de consola ya no hace falta: las dos líneas entran desde fuera con
`ptrace`; y ejecutaría `InitB` por su cuenta, contaminando el «antes»), más **telnet del invitado**
(`busybox telnetd` del firmware, `hostfwd 127.0.0.1:2323 → 23`).

| fichero | qué es |
|---|---|
| `verifica_arnes.py` | arranca la VM, espera a `im.elf` y ejecuta los tres modos del script; códigos esperados: seco=1, escribe=0, verifica=0 |
| `arranca_vm.py` | igual, pero deja la VM viva para probar a mano por telnet (`127.0.0.1:2323`) |
| `1-aplica-seco.out` | `--aplica` sin `--escribe`: comprueba todo y **no escribe**; imprime el plan (rc=1) |
| `2-aplica-escribe.out` | **la pasada buena** (repetida dos veces, mismo resultado): `dd` del volcado de 10 MiB (`10240+0 records out`, `md5 b4142827…`), subida de `ptcall` (10 092 B, `md5 6e20b3a6…`), `FBM EWBDFD 4 3 0` (A 0→17), `FBM InitB 6 3` (A 17→31), idx 10 `0x31 h3 v1 om6` → **VEREDICTO OK** |
| `3-verifica.out` | `--verifica` (sólo lectura) con el sector ya creado: `EXISTE`, 2/30 con handle |
| `consola.log` | consola del invitado: arranque y `NET telnetd: puerto 23` (confirma que el telnet es el del propio firmware, no un apaño) |

Repetición (desde la raíz del repo):

```sh
VM_MEM=1024 QEMU_SMP=4 python3 reports/evidence/film-pb-1-sector31-runbook-20261126/verifica_arnes.py 420
```

Notas del invitado (no son límites del script, sí de su busybox de 92 applets): no hay `awk`, `df`,
`id`, `tr` ni `head`, así que la prueba usó `--origen-volcado /nflasha4.img` (el nodo `/dev/nflasha4`
lo intercepta el shim dentro de `im.elf`, no existe en el sistema de ficheros) y `--destino /tmp`
(con el aviso de que no puede leer el espacio libre). En la cámara real el busybox del Tweak sí trae
`awk`/`df`/`id`, y `/dev/nflasha4` y `/mnt/sdcard` son los de verdad.
