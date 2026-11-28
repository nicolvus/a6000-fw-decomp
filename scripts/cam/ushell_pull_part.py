"""Vuelca una partición del actualizador en trozos de 8 MiB (RAM del actualizador = 12 MB). Solo lectura.
Uso: python -u ushell_pull_part.py <raiz-repo> <dispositivo> <dir-salida> [nº de trozos]"""
import sys, socket, threading, time, os
ROOT, DEV, OUTD = sys.argv[1:4]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 8
sys.path.insert(0, ROOT + '/references/pmca')
from pmca.commands import usb as U
from pmca.platform.backend.usb import UsbPlatformBackend
CH = 128  # bloques de 64 KiB por trozo
def shell(be, cmd, wait=240):
    a, b = socket.socketpair()
    t = threading.Thread(target=be.interactiveShell, args=(a,), daemon=True); t.start(); time.sleep(2)
    b.sendall((cmd + "; echo __F$((1+1))__\n").encode()); b.settimeout(wait); buf = b''
    while b'__F2__\n' not in buf.replace(b'\r', b''):
        d = b.recv(65536)
        if not d: break
        buf += d
    b.sendall(b"exit\n"); time.sleep(2); b.close(); t.join(15)
    return buf.decode('latin1')
def complete(device):
    be = UsbPlatformBackend(device)
    for _ in range(8):
        try: be.start(); break
        except Exception as e: print('[start]', repr(e)); time.sleep(3)
    os.makedirs(OUTD, exist_ok=True)
    for i in range(N):
        r = shell(be, f"busybox dd if={DEV} of=/tmp_updater/c.bin bs=65536 skip={i*CH} count={CH} 2>&1; ls -l /tmp_updater/c.bin")
        print(f'[trozo {i}]', r.strip().splitlines()[-3:], flush=True)
        p = f'{OUTD}/part{i:02d}.bin'
        with open(p, 'wb') as f: be.readFile('/tmp_updater/c.bin', f, lambda s: None)
        sz = os.path.getsize(p); print(f'[trozo {i}] {sz} B', flush=True)
        shell(be, "busybox rm /tmp_updater/c.bin")
        if sz < CH * 65536: break
    try: be._req(b'EXIT')
    except Exception as e: print('[EXIT]', repr(e))
U.updaterShellCommand(model='ILCE-6000', complete=complete)
