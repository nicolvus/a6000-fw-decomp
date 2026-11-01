# 3. Backup de NVRAM (obligatorio)

La NVRAM guarda ajustes y calibración **propios de tu cámara**. Si algo la corrompe, esta copia es lo único que la restaura.
Cada cámara es distinta: no uses la de otra persona.

```sh
source .venv/bin/activate
python scripts/senser_backup_dump.py ~/a6000-backup-$(date +%Y%m%d)   # SOLO LECTURA
```

Guarda `backup_mem.bin`, `backup_flash.bin`, `bootrom.bin`, `status.bin`, `info.txt` y `SHA256SUMS`. El script no ejecuta
escrituras (`writeBackup`/`saveBackup`). Requiere la cámara conectada por USB en el modo de servicio de `pmca`
(detalle del procedimiento y de la restauración: `docs/capture/custom-fw-recovery-and-install.md`).

**Guarda la copia fuera del repositorio** (contiene datos propios de tu cámara, como el número de serie) y haz una segunda copia externa.
Restaurar (solo si la NVRAM quedó corrupta): `scripts/senser_backup_restore.py FILE SHA256`, probado por el autor en hardware el 20-10-2026.
