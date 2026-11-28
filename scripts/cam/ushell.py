import sys, socket, threading, time
ROOT = sys.argv[1]
CMDS = sys.argv[2]
sys.path.insert(0, ROOT + '/references/pmca')
from pmca.commands import usb as U
from pmca.platform.backend.usb import UsbPlatformBackend
def complete(device):
    be = UsbPlatformBackend(device)
    for _ in range(6):
        try: be.start(); break
        except Exception as e: print('[start]',repr(e)); time.sleep(3)
    a, b = socket.socketpair()
    t = threading.Thread(target=be.interactiveShell, args=(a,), daemon=True); t.start()
    time.sleep(2)
    b.sendall((CMDS + "; echo __FIN__\n").encode())
    b.settimeout(90); buf = b''
    try:
        while buf.count(b'__FIN__') < 2:
            d = b.recv(65536)
            if not d: break
            buf += d
    except socket.timeout: print('[timeout leyendo]')
    sys.stdout.write(buf.decode('latin1')); sys.stdout.flush()
    b.sendall(b"exit\n"); time.sleep(2); b.close(); t.join(10)
    try: be._req(b'EXIT')
    except Exception as e: print('[EXIT]', repr(e))
U.updaterShellCommand(model='ILCE-6000', complete=complete)
