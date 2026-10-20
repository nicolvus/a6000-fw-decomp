#!/usr/bin/env python3
"""Escribe una palabra en RAM (service mode) y sondea esa dirección para medir cuánto dura.

Uso: senser_write_poll.py 0xDIRFISICA 0xVALOR SEGUNDOS   (dirección alineada a 4)
Escritura única vía dd en /dev/mem; al final restaura el valor original si sigue distinto.
"""
import os, socket, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

addr, val, secs = int(sys.argv[1], 16), int(sys.argv[2], 16), float(sys.argv[3])
assert addr % 4 == 0

def word_cmd(v):
    esc = ''.join('\\0%03o' % ((v >> (8 * i)) & 255) for i in range(4))
    return "echo -ne '%s' | dd of=/dev/mem bs=4 seek=%d count=1\n" % (esc, addr // 4)

def shell_write(be, v):
    a, b = socket.socketpair(); out = []; tw = []
    def feed():
        b.settimeout(0.5)
        def drain(t):
            end = time.time() + t
            while time.time() < end:
                try:
                    d = b.recv(65536)
                    if not d: return
                    out.append(d)
                except socket.timeout: pass
        drain(2)
        c = word_cmd(v)
        for k in range(0, len(c), 32): b.sendall(c[k:k+32].encode()); time.sleep(0.2)
        t0 = time.time()
        while time.time() - t0 < 15 and b'records out' not in b''.join(out):
            drain(0.3)
        tw.append(time.time()); b.shutdown(socket.SHUT_WR); b.close()
    t = threading.Thread(target=feed); t.start(); be.interactiveShell(a); t.join()
    return tw[0] if tw else None

def run(cam):
    be = SenserPlatformBackend(cam); be.start()
    rd = lambda: int.from_bytes(b''.join(p for p in [read(cam)]), 'little')
    def read(c):
        import io; f = io.BytesIO(); be.readMemory(addr, 4, f); return f.getvalue()
    orig = rd(); print('original: %#x' % orig, flush=True)
    t_w = shell_write(be, val); print('escrito %#x' % val, flush=True)
    last = None; t0 = time.time(); n = 0
    while time.time() - t0 < secs:
        v = rd(); n += 1
        if v != last:
            print('t=%+.2fs tras escritura: %#x' % (time.time() - (t_w or t0), v), flush=True); last = v
    print('lecturas:', n, 'en', round(time.time() - t0, 1), 's')
    if rd() != orig:
        shell_write(be, orig); print('restaurado; ahora %#x' % rd())

senserShellCommand(complete=run)
