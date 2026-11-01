# 3. NVRAM backup (mandatory)

The NVRAM stores settings and calibration **specific to your camera**. If something corrupts it, this copy is the only thing that restores it.
Every camera is different: do not use someone else's.

```sh
source .venv/bin/activate
python scripts/senser_backup_dump.py ~/a6000-backup-$(date +%Y%m%d)   # READ ONLY
```

Keep `backup_mem.bin`, `backup_flash.bin`, `bootrom.bin`, `status.bin`, `info.txt` and `SHA256SUMS`. The script does not perform
writes (`writeBackup`/`saveBackup`). It needs the camera connected over USB in `pmca` service mode
(procedure and restore details, in Spanish: `docs/capture/custom-fw-recovery-and-install.md`).

**Keep the backup outside the repository** (it contains data specific to your camera, such as the serial number) and make a second external copy.
Restore (only if the NVRAM got corrupted): `scripts/senser_backup_restore.py FILE SHA256`, tested by the author on hardware on 2026-10-20.
