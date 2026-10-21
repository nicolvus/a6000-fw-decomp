# Backup BK4 (17:49)

Backup BK4 (NVRAM, 852 647 B, región CX77500_E38) leído por service mode con `scripts/senser_backup_dump.py`: `backup_mem.bin` (RAM) y `backup_flash.bin` (flash), más `bootrom.bin`, `status.bin`, `info.txt`. Mismo hash de flash que `20261020-first`.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_backup_dump.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 394 | `286a66785d925a77aa1d651804daa6cb9127b5d28600f89992a6babf426f3027` |
| `backup_flash.bin` | 852647 | `60a810eb2f3d0348788851000f8678a1f24d9eced04f233c1802acc7f539a18b` |
| `backup_mem.bin` | 852647 | `713c1afb8710140bc86a9450e3244f4b02f9b775f4f84eeaeeed23d193662dfe` |
| `bootrom.bin` | 24576 | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `info.txt` | 143 | `d50824204e78697e70081d720fcadd068a3e8e48a9f5087cd23b7cd735c41d07` |
| `status.bin` | 52 | `5c7b079603769df879c368ad72bbd976a0a95ab9c2140baa685a048c961ce672` |
