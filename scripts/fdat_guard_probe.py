#!/usr/bin/env python3
"""Sondea SOLO el chequeo de guardia (CMD_CHK_GUARD, sin escribir) del updater de la cámara con FDAT mínimos de distintas versiones.

Uso: fdat_guard_probe.py [VERSION ...]   (por defecto 3.20 3.21 3.22 9.99). Cámara en modo MTP o almacenamiento masivo.
No llama a switchMode ni writeFirmware: no cambia nada en la cámara."""
import io, os, shutil, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT + '/references/fwtool'); sys.path.insert(0, ROOT + '/references/pmca')
from fwtool.sony import fdat
from pmca.commands.usb import getFdat, importDriver, getDevice
from pmca.usb.sony import SonyUpdaterCamera, SonyExtCmdDevice, SonyExtCmdCamera

base = getFdat('ILCE-6000')
_, dec = fdat.decryptFdat(io.BytesIO(base)); tmp = io.BytesIO(); shutil.copyfileobj(dec, tmp); tmp.seek(0)
f = fdat.readFdat(tmp)
print('FDAT base: modelo %#x región %#x versión %s' % (f.model, f.region, f.version))

with importDriver(None) as driver:
    device = getDevice(driver)
    assert isinstance(device, SonyExtCmdDevice), 'cámara no está en MTP/almacenamiento masivo'
    print('Cámara:', SonyExtCmdCamera(device).getCameraInfo().modelName)
    dev = SonyUpdaterCamera(device)
    for v in sys.argv[1:] or ['3.20', '3.21', '3.22', '9.99']:
        out = io.BytesIO(); fdat.writeFdat(f._replace(version=v), out); out.seek(0)
        data = fdat.encryptFdat(out, 'CXD90014').read()
        try:
            dev.init(); dev.checkGuard(io.BytesIO(data), len(data))
            print(v, '-> ACEPTADA', dev.getFirmwareVersion())
        except Exception as e:
            print(v, '-> RECHAZADA:', e)
