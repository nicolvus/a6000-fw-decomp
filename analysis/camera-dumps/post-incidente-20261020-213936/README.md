# BK4 en estado fallado (21:39)

Backup BK4 (NVRAM, 852 647 B, región CX77500_E38) leído por service mode con `scripts/senser_backup_dump.py`: `backup_mem.bin` (RAM) y `backup_flash.bin` (flash), más `bootrom.bin`, `status.bin`, `info.txt`. Estado tras el fallo de obturador/objetivo (ajustes ≈ preset de fábrica). Ver `docs/capture/s65-nvram-incident-diff.md`. NO restaurar.

- Cámara: ILCE-6000, fw 3.21, 2026-10-20. Generado con: senser_backup_dump.py.
- Solo lectura sobre la cámara salvo donde el doc de la fase indique escritura en RAM.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `SHA256SUMS` | 394 | `88b69506cdec0a7040ef6324b50afa2fd6a609e9064d945e2c2ff7a9b86c1dee` |
| `backup_flash.bin` | 852647 | `06c0c650d4d737050287e8b458908cc42e4bd86ca169a9a2f5551e27c8d1e025` |
| `backup_mem.bin` | 852647 | `f5c69441e798a5d1711411d46598ad773431a14692099513e0b7b4527d653755` |
| `bootrom.bin` | 24576 | `81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026` |
| `info.txt` | 143 | `d50824204e78697e70081d720fcadd068a3e8e48a9f5087cd23b7cd735c41d07` |
| `status.bin` | 52 | `5c7b079603769df879c368ad72bbd976a0a95ab9c2140baa685a048c961ce672` |
