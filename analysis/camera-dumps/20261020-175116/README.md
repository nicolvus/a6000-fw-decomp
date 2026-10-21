# Backup BK4 (17:51)

Backup BK4 (NVRAM, 852 647 B, región CX77500_E38) leído por service mode con `scripts/senser_backup_dump.py`: `backup_mem.bin` (RAM) y `backup_flash.bin` (flash), más `bootrom.bin`, `status.bin`, `info.txt`. El flash difiere de 17:49: cambios de runtime entre ambos arranques.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_backup_dump.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 394 | `23af81006eb7b1db7af66f1f3096be24871a95059d490db93666ada34a53f46f` |
| `backup_flash.bin` | 852647 | `1bf27077baeb667b301a33f1eabeb158ad322f82cf42f1a51fe592d06e228617` |
| `backup_mem.bin` | 852647 | `9d03a279ba2cf11701e599cdd7cb055306bb9d7aba72d9ac7e22a544867c4fbd` |
| `bootrom.bin` | 24576 | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `info.txt` | 143 | `d50824204e78697e70081d720fcadd068a3e8e48a9f5087cd23b7cd735c41d07` |
| `status.bin` | 52 | `5c7b079603769df879c368ad72bbd976a0a95ab9c2140baa685a048c961ce672` |
