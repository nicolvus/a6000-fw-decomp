#!/usr/bin/env python3
"""Restaura un volcado de backup (NVRAM) en la cámara por service mode (PMCA). ESCRIBE en la cámara.
Uso: senser_backup_restore.py ARCHIVO.bin SHA256
Comprueba el hash, la región (`CX77500_E38` en status) y el tamaño; escribe con setBackupPresetData (igual que el flujo `tweak` de PMCA),
verifica por relectura y sincroniza a flash (saveBackup). Antes: haz un volcado con senser_backup_dump.py."""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

path, sha = sys.argv[1], sys.argv[2]
data = open(path, 'rb').read()
assert hashlib.sha256(data).hexdigest() == sha, 'hash distinto'

def restore(cam):
    be = SenserPlatformBackend(cam); be.start()
    st = be.getBackupStatus()
    assert b'CX77500_E38' in st, 'región distinta: %r' % st
    cur = be.getBackupData()
    assert len(cur) == len(data), 'tamaño distinto'
    print('cabecera igual:', cur[:0x100] == data[:0x100])
    be.setBackupData(data)
    new = be.getBackupData()
    ok = new[0x100:] == data[0x100:]
    print('verificación en memoria:', ok)
    if not ok: raise SystemExit('NO coincide: no se sincroniza')
    be.syncBackup()
    print('sincronizado a flash')

senserShellCommand(complete=restore)
