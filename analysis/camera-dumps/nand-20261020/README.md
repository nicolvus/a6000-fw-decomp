# Volcado completo de la NAND (solo lectura, 2026-10-20)

ILCE-6000, fw 3.21. Leído en modo actualizador con `scripts/updater_nand_dump.py` (`PULL` de `/dev/nflasha*`; sin escrituras). Los `.bin` NO se versionan (916 MB, binarios Sony, `nflasha2` lleva ajustes de usuario): solo `SHA256SUMS`, `shell.txt` y este README. Los archivos están en el disco local.

- `dev_nflasha.bin` (473 MiB) es la NAND entera; `dev_nflashaN.bin` son las particiones de `docs/capture/custom-fw-recovery-and-install.md` (`partinf.conf`). Las particiones 2, 3, 5 y 7 coinciden byte a byte con su ventana dentro de `dev_nflasha.bin`; `1` también.
- `nflasha3`, `5`, `7`, `15` y `16` empiezan con la imagen exacta del paquete oficial 3.21 (`firmware.tar_unpacked/0700_part_image/dev/`); el resto de 3, 5 y 7 es 0xFF (relleno). `15` y `16` tienen datos tras la imagen, sin analizar.
- Sin tamaño (nodos inexistentes): `nflasha0`, `8`, `9`, `12`–`14`, `19`–`22`, `24`–`31`.
- Para restaurar una partición haría falta un camino de escritura que el shell de pmca no ofrece (`PUSH` escribe archivos, no dispositivos): este volcado es un respaldo, no una restauración probada.

SHA-256 de cada archivo en `SHA256SUMS`.
