# Primer volcado del updater (2026-10-20): RAM física y shell

Lectura con `scripts/updater_full_dump.py`. `ram_0x80000000.bin` (1 GiB de RAM física desde 0x80000000, no versionado) y `shell.txt` (kallsyms truncado). Los intentos de `PULL` de particiones fallaron (nombres de nodo `nflasha0pN` incorrectos): las particiones están en `nand-20261020`. Hashes en `SHA256SUMS`.
