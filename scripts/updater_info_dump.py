#!/usr/bin/env python3
"""Información SOLO LECTURA vía updatershell de PMCA (la cámara reinicia en modo updater).

Uso: .venv/bin/python -W ignore scripts/updater_info_dump.py [OUTDIR]
Guarda info.txt, backup.bin, bootrom.bin, boot*.bin, shell.txt (salida de comandos de lectura) y SHA256SUMS.
Sin PUSH/BKWR/BKDA-write/BKSY/BKPR/AUMT: no escribe en la cámara.
"""
import hashlib, io, os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import updaterShellCommand
from pmca.platform import PropertyInterface
from pmca.platform.backend.usb import UsbPlatformBackend

out = sys.argv[1] if len(sys.argv) > 1 else time.strftime('analysis/camera-dumps/updater-%Y%m%d-%H%M%S')
os.makedirs(out, exist_ok=False)
CMDS = ['uname -a', 'id', 'cat /proc/version /proc/cmdline /proc/cpuinfo /proc/mtd /proc/partitions /proc/mounts /proc/meminfo',
        'ls -la / /dev /bin /sbin /etc /proc/device-tree', 'ps', 'mount', 'df', 'dmesg | head -300', 'ls -laR /tmp /sys/class | head -300']

def dump(device):
    be = UsbPlatformBackend(device)
    be.start()
    files = {}
    def save(n, d):
        files[n] = d; open(os.path.join(out, n), 'wb').write(d)
    for step, fn in (('info.txt', lambda: ''.join('%s: %s\n' % (d, v) for _, d, v in PropertyInterface(be).getProps()).encode()),
                     ('backup.bin', be.getBackupData),
                     ('bootrom.bin', lambda: (lambda b: (be.readMemory(0xffff0000, 0x6000, b), b.getvalue())[1])(io.BytesIO())),
                     ('bootloader.bin', lambda: b''.join(be.readBootloader()))):
        try: save(step, fn())
        except Exception as e: print('FALLO', step, e)
    a, b = socket.socketpair(); got = []
    def feed():
        time.sleep(2)
        for c in CMDS: b.sendall((c + '\n').encode()); time.sleep(1.5)
        b.sendall(b'exit\n'); time.sleep(2); b.shutdown(socket.SHUT_WR)
        b.settimeout(3)
        try:
            while True:
                d = b.recv(4096)
                if not d: break
                got.append(d)
        except OSError: pass
        b.close()
    t = threading.Thread(target=feed); t.start()
    try: be.interactiveShell(a)
    except Exception as e: print('FALLO shell', e)
    t.join(); save('shell.txt', b''.join(got))
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for n, d in files.items(): f.write('%s  %s\n' % (hashlib.sha256(d).hexdigest(), n))
    try: be.stop()
    except Exception as e: print('stop:', e)
    print(files.get('info.txt', b'').decode()); print('Volcado en', out, {n: len(d) for n, d in files.items()})

updaterShellCommand(model='ILCE-6000', complete=dump)
