# Runbook: la instalación falla con `0x1043` por `/setting` llena (verificado 27-11-2026)

**Síntoma.** `pmca-console firmware … --flash` escribe ~170 MB y falla con `Response error 0x1043`; la cámara se queda en el actualizador (`lsusb`: `054c:03e2`). `0x1043` = LED `0x43` (`FsysWrapper` Open/Write/Mkdir). Falla siempre al crear `0800_appli/setting/init_bk.bak`.

**Causa.** `/setting` (`nflasha2`, vfat de 13,6 MB, 830 clústeres de 16 KB) está llena. Un `make_init_bk.sh` cortado (`echo warm`, apagados abortados) deja `/setting/init_bk.bak` de ~6,8 MB (de fábrica 1,35 MB). El actualizador en modo app (`uc_mkfs -m app`) no formatea `nflasha2` ni pasa `dosfsck`.

**Arreglo (solo RAM del actualizador, no flashea nada).**
1. Cámara en el actualizador (`lsusb | grep 054c:03e2`). Si no, lanzar una instalación que falle o `updatershell` la pone ahí.
2. venv con `axmlparserpy pycryptodomex pyusb pyyaml tlslite-ng`; la shell es `scripts/cam/ushell.py` (usa `references/pmca`, `be.start()` y `model='ILCE-6000'`, imprescindibles; sin ellos da `Sense 0x5 0x20`).
3. Diagnóstico: `python -u scripts/cam/ushell.py "$PWD" "ls -l /setting; cat /proc/mounts | grep setting"` (no hay `df`, `du`, `tr`, `stat`; `/tmp` es de solo lectura, usar `/tmp_updater`).
4. Arreglo: `python -u scripts/cam/ushell.py "$PWD" "rm /setting/init_bk.bak; ls -l /setting"` (debe salir sin error).
5. Reinstalar el `.dat` (`--flash --confirm --reflash`). Con el `.dat` 4.05 dio `Done`.
6. Volcado opcional antes de borrar: `dd if=/dev/nflasha2 of=/tmp_updater/x` + `PULL` (ver `analysis/camera-dumps/20261127-updater-setting/`).

**No hacer.** `timeout`/`kill` sobre pmca con la cámara en el actualizador: desincroniza el USB y obliga a apagar y encender la cámara. Lanzar en segundo plano con `python -u` y esperar. Un reinicio USB por libusb no recupera el actualizador; solo apagar/encender.

**Prevención.** No repetir `echo warm` (cada intento reescribe `/setting/init_bk.bak`).
