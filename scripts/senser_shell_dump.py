#!/usr/bin/env python3
"""Shell del service mode (firmware en ejecución), SOLO LECTURA: ejecuta comandos de consulta y guarda la salida.

Uso: .venv/bin/python -W ignore scripts/senser_shell_dump.py [OUTDIR]
"""
import os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out = sys.argv[1] if len(sys.argv) > 1 else time.strftime('analysis/camera-dumps/senser-shell-%Y%m%d-%H%M%S')
os.makedirs(out, exist_ok=False)
PROC = ['version', 'cmdline', 'cpuinfo', 'meminfo', 'partitions', 'mounts', 'iomem', 'ioports', 'interrupts', 'devices', 'modules', 'kallsyms']
CMDS = ['uname -a', 'pwd'] + ['cat /proc/' + p for p in PROC] + ['ps', 'mount', 'df', 'ls -la / /proc', 'ls -la /dev', 'ls -la /bin /sbin /etc',
        'ls -laR /setting', 'dmesg']

if os.environ.get('SENSER_CMDS'):  # un comando por línea
    CMDS = [l.strip() for l in open(os.environ['SENSER_CMDS']) if l.strip()]

def dump(cam):
    be = SenserPlatformBackend(cam); be.start()
    a, b = socket.socketpair(); got = []
    def feed():
        b.settimeout(0.5)
        def drain(quiet, maxt):  # lee hasta `quiet` s sin datos o `maxt` s en total
            t0 = last = time.time()
            while time.time() - last < quiet and time.time() - t0 < maxt:
                try:
                    d = b.recv(65536)
                    if not d: return
                    got.append(d); last = time.time()
                except socket.timeout: pass
        drain(2, 5)
        for c in CMDS:
            for k in range(0, len(c), 32):  # trozos pequeños: el terminal lee de 0x40 en 0x40
                b.sendall(c[k:k+32].encode()); time.sleep(0.2)
            b.sendall(b'\n'); drain(3, 120)
        b.shutdown(socket.SHUT_WR); b.close()
    t = threading.Thread(target=feed); t.start()
    try: be.interactiveShell(a)
    except Exception as e: print('FALLO shell', e)
    t.join()
    open(os.path.join(out, 'shell.txt'), 'wb').write(b''.join(got))
    print('Guardado', out, sum(map(len, got)), 'bytes')

senserShellCommand(complete=dump)
