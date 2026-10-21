# BK4 tras restaurar la línea base (21:43)

Backup BK4 (NVRAM, 852 647 B, región CX77500_E38) leído por service mode con `scripts/senser_backup_dump.py`: `backup_mem.bin` (RAM) y `backup_flash.bin` (flash), más `bootrom.bin`, `status.bin`, `info.txt`. Cámara recuperada: enciende y apaga bien.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_backup_dump.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 394 | `2a1c3b5b638bf5833949c5a7f2fa49865ac5d033033007689911a30822951999` |
| `backup_flash.bin` | 852647 | `55cdbb569ea733a8a85e01b539afbb568643255a1b7a180e31d79d19251dead2` |
| `backup_mem.bin` | 852647 | `30135e8debbcc6bb9cad7300ce13da663e86331632a120cda3977f6208a9c343` |
| `bootrom.bin` | 24576 | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `info.txt` | 143 | `d50824204e78697e70081d720fcadd068a3e8e48a9f5087cd23b7cd735c41d07` |
| `status.bin` | 52 | `5c7b079603769df879c368ad72bbd976a0a95ab9c2140baa685a048c961ce672` |
