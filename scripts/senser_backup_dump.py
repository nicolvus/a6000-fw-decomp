#!/usr/bin/env python3
"""Volcado SOLO LECTURA del backup (NVRAM) de la cámara vía service mode (PMCA).

Uso: .venv/bin/python scripts/senser_backup_dump.py [OUTDIR]
Guarda backup_mem.bin (RAM), backup_flash.bin (flash), bootrom.bin, status.bin, info.txt y SHA256SUMS.
No ejecuta ninguna escritura (sin writeBackup/setBackupPresetData/saveBackup).
"""
import hashlib, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform import PropertyInterface
from pmca.platform.backend.senser import SenserPlatformBackend

out = sys.argv[1] if len(sys.argv) > 1 else time.strftime('analysis/camera-dumps/%Y%m%d-%H%M%S')
os.makedirs(out, exist_ok=False)

def dump(cam):
    be = SenserPlatformBackend(cam)
    be.start()
    files = {'status.bin': be.getBackupStatus(),
             'backup_mem.bin': cam.getBackupPresetData(True),
             'backup_flash.bin': cam.getBackupPresetData(False)}
    import io; b = io.BytesIO(); be.readMemory(0xffff0000, 0x6000, b); files['bootrom.bin'] = b.getvalue()
    info = ''.join('%s: %s\n' % (d, v) for _, d, v in PropertyInterface(be).getProps())
    files['info.txt'] = info.encode()
    for n, d in files.items():
        open(os.path.join(out, n), 'wb').write(d)
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for n, d in files.items():
            f.write('%s  %s\n' % (hashlib.sha256(d).hexdigest(), n))
    print(info); print('Volcado en', out, {n: len(d) for n, d in files.items()})

senserShellCommand(complete=dump)
