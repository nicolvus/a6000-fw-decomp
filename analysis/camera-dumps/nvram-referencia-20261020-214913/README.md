# BK4 de referencia con la cámara funcionando (21:49)

Backup BK4 (NVRAM, 852 647 B, región CX77500_E38) leído por service mode con `scripts/senser_backup_dump.py`: `backup_mem.bin` (RAM) y `backup_flash.bin` (flash), más `bootrom.bin`, `status.bin`, `info.txt`. Tomado tras confirmar el usuario que enciende y apaga correctamente: es la copia buena para cualquier recuperación futura (`scripts/senser_backup_restore.py FILE SHA256`).

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_backup_dump.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 394 | `ba5cb056e4fda72e2e0a6e77f2e209b649661f035cf7afedc44ff2bac1a318fd` |
| `backup_flash.bin` | 852647 | `bdf4e8a6d9721f26b466ce86c726623d8c7806d57140c4943a9a829efa5eef32` |
| `backup_mem.bin` | 852647 | `617869105315634c6c54274572e52d60aeed9a9600417b08a038b4ba23420143` |
| `bootrom.bin` | 24576 | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `info.txt` | 143 | `d50824204e78697e70081d720fcadd068a3e8e48a9f5087cd23b7cd735c41d07` |
| `status.bin` | 52 | `5c7b079603769df879c368ad72bbd976a0a95ab9c2140baa685a048c961ce672` |
