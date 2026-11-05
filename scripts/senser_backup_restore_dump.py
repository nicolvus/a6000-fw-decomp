#!/usr/bin/env python3
"""Restaura un BK4 y vuelca la NVRAM en la MISMA sesión de servicio, sin reiniciar la cámara. ESCRIBE en la cámara.
Uso: senser_backup_restore_dump.py ARCHIVO.bin SHA256 OUTDIR   (OUTDIR: backup_mem.bin y backup_flash.bin tras sincronizar)"""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

path, sha, out = sys.argv[1:4]
data = open(path, 'rb').read()
assert hashlib.sha256(data).hexdigest() == sha, 'hash distinto'
os.makedirs(out, exist_ok=False)

def run(cam):
    be = SenserPlatformBackend(cam); be.start()
    assert b'CX77500_E38' in be.getBackupStatus(), 'región distinta'
    assert len(be.getBackupData()) == len(data), 'tamaño distinto'
    be.setBackupData(data)
    assert be.getBackupData()[0x100:] == data[0x100:], 'no coincide: no se sincroniza'
    be.syncBackup(); print('restaurado y sincronizado a flash')
    for n, ram in (('backup_mem.bin', True), ('backup_flash.bin', False)):
        d = cam.getBackupPresetData(ram); open(os.path.join(out, n), 'wb').write(d)
        print(n, len(d), hashlib.sha256(d).hexdigest())

senserShellCommand(complete=run)
