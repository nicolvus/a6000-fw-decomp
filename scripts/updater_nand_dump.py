#!/usr/bin/env python3
"""Volcado SOLO LECTURA de las particiones NAND vía updatershell (PULL de /dev/nflasha*).

Uso: python -W ignore scripts/updater_nand_dump.py OUTDIR      (cámara en MTP/almacenamiento masivo o ya en modo actualizador)
Primero lista nodos con el shell (/proc/partitions, ls /dev); luego hace PULL de cada nflasha* con tamaño > 0. Sin escrituras."""
import hashlib, os, re, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'pmca'))
from pmca.commands.usb import updaterShellCommand
from pmca.platform.backend.usb import UsbPlatformBackend

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
CMDS = ['cat /proc/partitions', 'ls -l /dev/ | grep -i -E "nflash|mtd|mmc|block"', 'mount', 'cat /proc/mtd']


def shell(be):
    a, b = socket.socketpair(); got = []
    def feed():
        time.sleep(2)
        for c in CMDS: b.sendall((c + '\n').encode()); time.sleep(2)
        b.sendall(b'exit\n'); time.sleep(2); b.shutdown(socket.SHUT_WR); b.settimeout(3)
        try:
            while True:
                d = b.recv(65536)
                if not d: break
                got.append(d)
        except OSError: pass
        b.close()
    t = threading.Thread(target=feed); t.start(); be.interactiveShell(a); t.join()
    txt = b''.join(got).decode('utf-8', 'replace'); open(os.path.join(out, 'shell.txt'), 'w').write(txt); return txt


def pull(be, remote):
    path = os.path.join(out, remote.strip('/').replace('/', '_') + '.bin')
    with open(path, 'wb') as f:
        class W:
            def write(self, d): f.write(d); return len(d)
            def flush(self): pass
            def close(self): pass
        be.readFile(remote, W())
    return path


def dump(device):
    be = UsbPlatformBackend(device); be.start()
    txt = shell(be); print(txt, flush=True)
    nodes = sorted(set(re.findall(r'\b(nflasha\d+)\b', txt)), key=lambda s: int(s[7:]))
    for n in ['nflasha'] + nodes:
        r = '/dev/' + n
        try:
            p = pull(be, r); print('OK   %-16s %d B' % (r, os.path.getsize(p)), flush=True)
        except Exception as e:
            print('FALLO %-15s %s' % (r, e or type(e).__name__), flush=True)
    try: be.stop()
    except Exception as e: print('stop:', e)
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for n in sorted(os.listdir(out)):
            p = os.path.join(out, n)
            if n != 'SHA256SUMS' and os.path.getsize(p):
                h = hashlib.sha256()
                with open(p, 'rb') as g:
                    for c in iter(lambda: g.read(1 << 20), b''): h.update(c)
                f.write('%s  %s\n' % (h.hexdigest(), n))
    print('Terminado:', out)

updaterShellCommand(model='ILCE-6000', complete=dump)
