# Volcado completo de la NAND (solo lectura, 05-11-2026, ~20:30)

ILCE-6000, fw 3.37, `scripts/updater_nand_dump.py` (modo actualizador, `PULL` de `/dev/nflasha*`). Los `.bin` no se versionan: solo `SHA256SUMS`, `shell.txt` y este README.

Comparación byte a byte con `nand-20261020` (3.21, original):

| Archivo | Tamaño | Bytes distintos |
|---|---|---|
| `dev_nflasha5/6/7/11/15/16` | — | **0** (idénticos) |
| `dev_nflasha1` | 6 MiB | 8 (contadores) |
| `dev_nflasha18` | 20 MiB | 72 (contadores) |
| `dev_nflasha23` | 1 MiB | 7 (contador) |
| `dev_nflasha3` | 30 MiB | 79 579 (relleno periódico tras la imagen, `0xaf4f10-0xb0940f`) |
| `dev_nflasha2` | 13 MiB | 1 305 304 (Setting: `Backup.bin`, `.etools`, `.hasp`, `dat4`, `comp`) |
| `dev_nflasha4` | 10 MiB | 265 301 (MPR) |
| `dev_nflasha10` | 5 MiB | 1 308 863 (logs de arranque) |
| `dev_nflasha17` | 100 MiB | 21 964 129 (Android /data: apps, restos de pruebas) |
| `dev_nflasha.bin` (lógico completo) | 473 MiB | 24 923 263 |

Frente al volcado de las 00:11 del mismo día: `1`, `3`, `18`, `23` idénticos; `2` 26 447 B, `4` 244 718 B, `10` 2 096 B, `17` 28 406 B distintos.
`Backup.bin` de `nflasha2` frente al `backup_flash.bin` de la NVRAM volcada hoy: 183 B distintos.
