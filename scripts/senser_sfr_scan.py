#!/usr/bin/env python3
"""Barrido SOLO LECTURA por páginas de 4 KiB de un rango físico (RMEM por service mode), tolerante a fallos y reanudable.

Uso (un intento):  python -W ignore scripts/senser_sfr_scan.py OUTDIR [INICIO=0xf0000000] [FIN=0xf4000000]
Bucle automático:  scripts/senser_sfr_scan.sh OUTDIR [INICIO] [FIN]
Estado en OUTDIR/state.json (páginas ok/malas/tramos saltados tras fallos seguidos). Una página que provoque excepción o cuelgue (>25 s) se marca mala ANTES de reintentar, y el proceso termina
(código 3 fallo, 4 cuelgue, 5 cámara no disponible, 0 fin) para que el bucle espere a que la cámara reinicie. Datos en OUTDIR/scan_<inicio>.bin (ceros = no leída)."""
import json, os, sys, threading, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand
from pmca.platform.backend.senser import SenserPlatformBackend

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
start = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0xf0000000
end = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0xf4000000
PAGE = 0x1000
sp = os.path.join(out, 'state.json'); dp = os.path.join(out, 'scan_%#x.bin' % start)
st = json.load(open(sp)) if os.path.exists(sp) else {'ok': [], 'bad': []}
ok, bad = set(st['ok']), set(st['bad'])
skipped = st.get('skipped', []); consec = [st.get('consec', 0)]
save = lambda: json.dump({'ok': sorted(ok), 'bad': sorted(bad), 'skipped': skipped, 'consec': consec[0]}, open(sp, 'w'))
if not os.path.exists(dp):
    with open(dp, 'wb') as f: f.truncate(end - start)
ran = [False]; cur = [None]; beat = [time.time()]


def watchdog():
    while True:
        time.sleep(2)
        if cur[0] is not None and time.time() - beat[0] > 25:
            bad.add(cur[0]); consec[0] += 1; save(); print('CUELGUE en %#x' % cur[0], flush=True); os._exit(4)
threading.Thread(target=watchdog, daemon=True).start()


def dump(cam):
    ran[0] = True
    be = SenserPlatformBackend(cam); be.start(); n = 0
    with open(dp, 'r+b') as f:
        for addr in range(start, end, PAGE):
            if addr in ok or addr in bad or any(a <= addr < b for a, b in skipped): continue
            cur[0] = addr; beat[0] = time.time(); buf = bytearray()
            class W:
                def write(self, d): buf.extend(d); return len(d)
            try:
                be.readMemory(addr, PAGE, W())
            except Exception as e:
                bad.add(addr); consec[0] += 1
                # fallos seguidos: se salta un tramo que se duplica (64 KiB .. 4 MiB) para no reiniciar la cámara por cada página; límite: puede perder islas mapeadas dentro
                skip = min(0x10000 << (consec[0] - 1), 0x400000); a, b = addr + PAGE, min(((addr // skip) + 1) * skip, end)
                if b > a: skipped.append([a, b])
                save(); print('FALLO %#x: %s (salto hasta %#x)' % (addr, e or type(e).__name__, b), flush=True); os._exit(3)
            f.seek(addr - start); f.write(bytes(buf)); ok.add(addr); cur[0] = None; consec[0] = 0
            n += 1
            if n % 512 == 0: save(); f.flush(); print('%#x ok=%d bad=%d' % (addr, len(ok), len(bad)), flush=True)
    save(); open(os.path.join(out, '.fin'), 'w').close(); print('FIN ok=%d bad=%d' % (len(ok), len(bad)), flush=True)

senserShellCommand(complete=dump)
sys.exit(0 if ran[0] else 5)
