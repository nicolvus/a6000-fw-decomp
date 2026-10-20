#!/usr/bin/env python3
"""Volcado máximo SOLO LECTURA vía updatershell: NAND completa, RAM física, /proc, /setting, /dev/mem.

Uso: .venv/bin/python -W ignore scripts/updater_full_dump.py [OUTDIR]
Cada paso falla de forma independiente. Sin escrituras en la cámara (no PUSH/BKWR/BKDW/BKSY/BKPR/AUMT).
"""
import hashlib, os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import updaterShellCommand
from pmca.platform.backend.usb import UsbPlatformBackend

out = sys.argv[1] if len(sys.argv) > 1 else time.strftime('analysis/camera-dumps/full-%Y%m%d-%H%M%S')
os.makedirs(out, exist_ok=False)
PARTS = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 15, 16, 17, 18, 23]
PROC = ['/proc/kallsyms', '/proc/iomem', '/proc/ioports', '/proc/interrupts', '/proc/devices', '/proc/modules', '/proc/cmdline',
        '/proc/cpuinfo', '/proc/meminfo', '/proc/partitions', '/proc/mounts', '/proc/version', '/proc/config.gz',
        '/proc/vmallocinfo', '/proc/slabinfo', '/proc/zoneinfo', '/proc/clock', '/proc/clocks']
FILES = ['/etc/passwd', '/etc/inittab', '/etc/fstab', '/etc/rcS', '/etc/init.d/rcS']
# PULL no sirve con /proc (tamaño 0) ni /proc/kmsg (bloquea): se leen con cat en el shell
SHELL = ['for f in ' + ' '.join(PROC) + '; do echo "=== $f"; cat $f 2>&1; done',
         'dmesg', 'ps', 'ls -laR /dev /bin /sbin /etc /kmod /setting /lib /usr', 'ls -la /sys/class /sys/block /sys/bus /sys/devices',
         'cat /sys/kernel/debug/* 2>&1 | head -50', 'ls -l /tmp_updater /tmp_updater/updater /tmp_updater/updater/bodyfs']
sums = {}

def tee(name):
    f = open(os.path.join(out, name), 'wb')
    class W:
        def write(self, d): f.write(d); return len(d)
        def close(self): f.close()
        def flush(self): f.flush()
    return W()

def step(name, fn):
    t = time.time()
    try:
        fn(); print('OK   %-28s %.0fs' % (name, time.time() - t), flush=True)
    except Exception as e:
        print('FALLO %-27s %s' % (name, e), flush=True)

def pull(be, remote, name):
    w = tee(name)
    try: be.readFile(remote, w)
    finally: w.close()

def dump(device):
    be = UsbPlatformBackend(device); be.start()
    os.makedirs(os.path.join(out, 'nand')); os.makedirs(os.path.join(out, 'proc')); os.makedirs(os.path.join(out, 'etc'))
    step('shell', lambda: run_shell(be))
    for p in FILES: step(p, lambda p=p: pull(be, p, 'etc/' + p.replace('/', '_')))
    for n in PARTS:
        d = '/dev/nflasha0' + ('p%d' % n if n else '')
        step(d, lambda d=d: pull(be, d, 'nand/' + d.split('/')[-1] + '.bin'))
    # RAM física por tramos de 16 MiB hasta 1 GiB (RMEM); se detiene al primer fallo
    def ram():
        w = tee('ram_0x80000000.bin'); n = 0
        try:
            for off in range(0x80000000, 0xC0000000, 0x1000000):
                be.readMemory(off, 0x1000000, w); n += 1
        finally: w.close(); print('  RAM tramos de 16MiB leídos:', n, flush=True)
    step('RAM 0x80000000', ram)
    step('SFR 0xf0000000', lambda: be.readMemory(0xf0000000, 0x1000000, (lambda w: w)(tee('mmio_0xf0000000.bin'))))
    try: be.stop()
    except Exception as e: print('stop:', e)
    with open(os.path.join(out, 'SHA256SUMS'), 'w') as f:
        for r, _, fs in os.walk(out):
            for n in sorted(fs):
                p = os.path.join(r, n)
                if n != 'SHA256SUMS':
                    h = hashlib.sha256()
                    with open(p, 'rb') as g:
                        for c in iter(lambda: g.read(1 << 20), b''): h.update(c)
                    f.write('%s  %s\n' % (h.hexdigest(), os.path.relpath(p, out)))
    print('Terminado:', out, flush=True)

def run_shell(be):
    a, b = socket.socketpair(); got = []
    def feed():
        time.sleep(2)
        for c in SHELL: b.sendall((c + '\n').encode()); time.sleep(2)
        b.sendall(b'exit\n'); time.sleep(2); b.shutdown(socket.SHUT_WR); b.settimeout(3)
        try:
            while True:
                d = b.recv(65536)
                if not d: break
                got.append(d)
        except OSError: pass
        b.close()
    t = threading.Thread(target=feed); t.start()
    be.interactiveShell(a); t.join()
    open(os.path.join(out, 'shell.txt'), 'wb').write(b''.join(got))

updaterShellCommand(model='ILCE-6000', complete=dump)
