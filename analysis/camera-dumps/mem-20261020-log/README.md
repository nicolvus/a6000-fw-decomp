# Búfer de log del firmware (RAM 0x83400000, 1,2 MiB)

`log.txt` es el texto extraído del búfer de consola del firmware (`[POWER_CTRL]`, `[ViewRoot]`, ...).

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: dd sobre /dev/mem.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 90 | `38823aff06d8bdca6c7eb2b102c238ca68074556afaffdbba96cbd51d1f10e6d` |
| `log.txt` | 251957 | `25c48019842192b36e226ba3b209411d31f0a61ee93b8a07ba95af1f89decf2c` |
| `mem_83400000_130000.bin` | 1245184 | `7e3089b9bb729377522096051f9a557fd1f47a42a8b5f97c5b10db999cc03ce4` |
