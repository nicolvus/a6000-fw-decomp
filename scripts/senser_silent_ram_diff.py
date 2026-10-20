#!/usr/bin/env python3
"""Una sesión de service mode: vuelca una región de RAM en varios estados del campo SilentShutter.

Uso: senser_silent_ram_diff.py OUTDIR 0xINICIO 0xTAM [0xDIRFISICA=0x83edf8bc] [CICLOS=3]
Secuencia: off0, y por ciclo: escribe 1, on<i>, restaura, off<i>. Solo escribe esa palabra (restaurada).
"""
import hashlib, io, os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out, start, size = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
addr = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x83edf8bc
cycles = int(sys.argv[5]) if len(sys.argv) > 5 else 3
CH = 0x8000
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
    def rdw():
        f = io.BytesIO(); be.readMemory(addr, 4, f); return int.from_bytes(f.getvalue(), 'little')
    def snap(tag):
        f = io.BytesIO()
        for o in range(0, size, CH): be.readMemory(start + o, min(CH, size - o), f)
        open(os.path.join(out, tag + '.bin'), 'wb').write(f.getvalue())
        print(tag, 'campo=%#x' % rdw(), len(f.getvalue()), flush=True)
    orig = rdw(); print('original: %#x' % orig, flush=True)
    snap('off0')
    for i in range(1, cycles + 1):
        shell_write(be, 1); print('escrito 1; leído %#x' % rdw(), flush=True)
        snap('on%d' % i)
        shell_write(be, orig); print('restaurado; leído %#x' % rdw(), flush=True)
        snap('off%d' % i)
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for n in sorted(os.listdir(out)):
            f.write('%s  %s\n' % (hashlib.sha256(open(os.path.join(out, n), 'rb').read()).hexdigest(), n))

senserShellCommand(complete=run)
