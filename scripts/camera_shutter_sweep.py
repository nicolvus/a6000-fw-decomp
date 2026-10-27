#!/usr/bin/env python3
"""Barrido de velocidades con RemoteShutter (/nr, /ss, /shoot, /last): guarda cada JPEG y mide luminancia y bandas.
Uso: camera_shutter_sweep.py OUTDIR [n/d ...]   (por defecto 1/4000 … 1/15). App abierta en la cámara, escena fija."""
import io, os, sys, time, urllib.request
from PIL import Image, ImageStat

HOST = 'http://192.168.1.29:8080'
get = lambda p, t=60: urllib.request.urlopen(HOST + p, timeout=t).read()
out = sys.argv[1]
speeds = sys.argv[2:] or ['1/4000', '1/2000', '1/1000', '1/500', '1/250', '1/125', '1/60', '1/30', '1/15']
os.makedirs(out, exist_ok=False)
log = open(f'{out}/log.txt', 'w')
def say(*a):
    print(*a, flush=True); print(*a, file=log, flush=True)

say('nr', get('/nr?v=0').decode().strip())
for sp in speeds:
    n, d = sp.split('/')
    r = get(f'/ss?n={n}&d={d}').decode().strip()
    t0 = time.time(); get('/shoot')
    while time.time() - t0 < 40:
        st = get('/status').decode().strip()
        if st.startswith(('done', 'shoot-error')): break
        time.sleep(0.3)
    jpg = get('/last')
    open(f'{out}/{n}_{d}.jpg', 'wb').write(jpg)
    im = Image.open(io.BytesIO(jpg)); im.draft('L', (1500, 1000)); g = im.convert('L')
    rows = [sum(g.crop((0, y, g.width, y + 1)).getdata()) / g.width for y in range(g.height)]
    # bandas: desviación típica de la diferencia entre filas suavizadas (detecta parpadeo LED con exposición por filas)
    sm = [sum(rows[max(0, y - 3):y + 4]) / len(rows[max(0, y - 3):y + 4]) for y in range(len(rows))]
    band = (sum((a - b) ** 2 for a, b in zip(sm[8:], sm[:-8])) / (len(sm) - 8)) ** 0.5
    say(f'{sp:>7} {r:28} {st:16} L={ImageStat.Stat(g).mean[0]:6.1f} bandas={band:5.2f} {len(jpg)} B')
