# RAM física del sistema en marcha (service mode, 2026-10-20)

ILCE-6000, fw 3.21, arranque normal tras restaurar la NVRAM. Leída con `scripts/senser_ram_dump.py` (RMEM por senser, solo lectura): 1024 MiB desde 0x80000000 en tramos de 16 MiB, sin fallos. `ram_0x80000000.bin` no se versiona (1 GiB); sha256 `f96c6152f697a8680f6d342cfdc0133bc28b8ab85a6baf48c19358546ff2fdbf` en `SHA256SUMS`.

- Distinto del volcado de `full-20261020-nand/ram_0x80000000.bin`, que es la RAM del modo actualizador, no del sistema principal.
- Mapa: virtual `0x43xxxxxx` = físico `0x83xxxxxx` (offset en el archivo = físico − 0x80000000).
- Espejo de ajustes `0x83edf684` (offset `0x3edf684`): `+0x238` (Silent) = 0; `+0x210` = 1. Sin interpretar: no se sabe si 1 es el valor por defecto tras arrancar o consecuencia de la restauración de NVRAM.
- 36 de 64 tramos son distintos entre sí (el resto repite contenido, p. ej. ceros); 61 tienen datos en la muestra.
