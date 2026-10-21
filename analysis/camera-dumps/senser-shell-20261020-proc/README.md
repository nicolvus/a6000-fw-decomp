# Consultas extra del shell de service mode (2026-10-20)

`shell.txt` (salida de `scripts/senser_shell_dump.py` con `SENSER_CMDS`): `/proc/vmallocinfo`, `slabinfo`, `zoneinfo`, `clock(s)`, `/etc/fstab`, `/etc/inittab`, listados de `/lens` y `/android`. `/proc/config.gz` **no existe** en el kernel de la cámara (`ls: No such file or directory`); `/proc/kallsyms` y `/proc/iomem` del sistema en marcha ya están en `senser-shell-20261020-180946`.
