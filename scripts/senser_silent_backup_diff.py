#!/usr/bin/env python3
"""Una sesión de service mode: backup base, escribe 1 en el campo SilentShutter (RAM), backup, restaura, backup.

Uso: senser_silent_backup_diff.py OUTDIR [0xDIRFISICA]   (por defecto 0x83edf8bc)
Solo escribe esa palabra de RAM (se restaura al final); los backups son lecturas.
"""
import hashlib, io, os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out = sys.argv[1]; addr = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x83edf8bc
os.makedirs(out, exist_ok=False)

def shell_write(be, v):
    esc = ''.join('\\0%03o' % ((v >> (8 * i)) & 255) for i in range(4))
    cmd = "echo -ne '%s' | dd of=/dev/mem bs=4 seek=%d count=1\n" % (esc, addr // 4)
    a, b = socket.socketpair(); buf = []
    def feed():
        b.settimeout(0.5)
        def drain(t):
            end = time.time() + t
            while time.time() < end:
                try:
                    d = b.recv(65536)
                    if not d: return
                    buf.append(d)
                except socket.timeout: pass
        drain(2)
        for k in range(0, len(cmd), 32): b.sendall(cmd[k:k+32].encode()); time.sleep(0.2)
        t0 = time.time()
        while time.time() - t0 < 15 and b'records out' not in b''.join(buf): drain(0.3)
        b.shutdown(socket.SHUT_WR); b.close()
    t = threading.Thread(target=feed); t.start(); be.interactiveShell(a); t.join()

def run(cam):
    be = SenserPlatformBackend(cam); be.start()
    def rd():
        f = io.BytesIO(); be.readMemory(addr, 4, f); return int.from_bytes(f.getvalue(), 'little')
    def snap(tag):
        for kind, mem in (('mem', True), ('flash', False)):
            open(os.path.join(out, '%s_%s.bin' % (tag, kind)), 'wb').write(cam.getBackupPresetData(mem))
        print(tag, 'campo=%#x' % rd(), flush=True)
    orig = rd(); print('original: %#x' % orig, flush=True)
    snap('1-base')
    shell_write(be, 1); print('escrito 1; leído %#x' % rd(), flush=True)
    snap('2-silent')
    shell_write(be, orig); print('restaurado; leído %#x' % rd(), flush=True)
    snap('3-revertido')
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for n in sorted(os.listdir(out)):
            f.write('%s  %s\n' % (hashlib.sha256(open(os.path.join(out, n), 'rb').read()).hexdigest(), n))

senserShellCommand(complete=run)
