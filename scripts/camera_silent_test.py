#!/usr/bin/env python3
"""E25-11: prueba del modo silencioso de RemoteShutter v8 (ShutMode 0 + r5 desde la velocidad, parche RAM con reversión).

Uso: camera_silent_test.py OUTDIR   (RemoteShutter v8 abierta, adb 5555, telnet 23, escena fija y sin tocar)
1) referencias normales (1/60, 1/30, 1/15) en RAW ⇒ escena por banda; 2) `/silent?v=1` y disparos a 1/4000…1/30 (x2) y 1/15 (debe caer a normal);
3) ráfaga 4×1/250 sin pausa; 4) tras cada disparo comprueba que los dos sitios de BIONZ están originales (lectura por la app y, al final, por telnet).
Deja modo silencioso apagado, jpeg e ISO automático. Informa exposición medida por filas frente al objetivo y la uniformidad."""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import rawpy
from adb_shell.adb_device import AdbDeviceTcp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST, NB = "192.168.1.29", 32
SM_O, R5_O = "91f80990", "28125ffa85fe"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=False)


def get(p, t=120):
    return urllib.request.urlopen(f"http://{HOST}:8080{p}", timeout=t).read().decode().strip()


def rd(addr, n):
    out = run(HOST, [f"dd if=/dev/mem bs=1 skip={addr} count={n} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z"])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(":", " ").split()
        if parts and len(parts[0]) == 8 and all(c in "0123456789abcdef" for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    return data[:n].hex()


def original_by_app() -> bool:
    s = get("/silent")
    return f"sm={SM_O}" in s and f"r5={R5_O}" in s and "patched=false" in s


adb = AdbDeviceTcp(HOST, 5555, default_transport_timeout_s=60)
adb.connect(rsa_keys=None, auth_timeout_s=10)


def card_files():
    folder = max((x for x in adb.shell("ls /mnt/sdcard/DCIM").split() if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {f"{folder}/{f}" for f in adb.shell(f"ls /mnt/sdcard/DCIM/{folder}").split() if f.startswith("DSC")}


def count() -> int:
    return int(get("/info").split("count=")[1].split()[0])


def shoot_raw(tag):
    before, c0 = card_files(), count()
    get("/shoot")
    t0 = time.time()
    # el modo silencioso tarda en poner «shooting» (abre, lee y parchea): se espera a que suba el contador, no al estado
    while count() == c0:
        if get("/status").startswith("shoot-error") or time.time() - t0 > 60:
            raise RuntimeError(f"{tag}: {get('/status')}")
        time.sleep(0.3)
    status = get("/status")
    time.sleep(1.5)
    arw = sorted(f for f in card_files() - before if f.endswith(".ARW"))
    if not arw:
        raise RuntimeError(f"{tag}: sin ARW ({status})")
    return pull_bands(arw[0], tag), status


def pull_bands(card_path, tag):
    dst = OUT / f"{tag}.ARW"
    adb.pull(f"/mnt/sdcard/DCIM/{card_path}", str(dst))
    r = rawpy.imread(str(dst))
    x = r.raw_image_visible.astype(np.float32) - np.mean(r.black_level_per_channel)
    k = x.shape[0] // NB
    return [round(float(x[i * k:(i + 1) * k].mean()), 2) for i in range(NB)]


print("antes:", get("/info"), "|", get("/silent"), flush=True)
assert original_by_app(), "los sitios de BIONZ no están originales antes de empezar"
res, refs, ok_all = [], [], True
try:
    print("fmt", get("/fmt?v=rawjpeg"), "iso", get("/iso?v=100"), "silent", get("/silent?v=0"), flush=True)
    for sp in ("1/60", "1/30", "1/15"):
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        bands, st = shoot_raw(f"ref_{n}_{d}")
        refs.append((int(n) / int(d), bands))
        print("ref", sp, st, flush=True)
    print(get("/silent?v=1"), flush=True)
    for sp, rep in [(s, r) for s in ("1/4000", "1/1000", "1/250", "1/60", "1/30", "1/15") for r in (0, 1)]:
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        bands, st = shoot_raw(f"sil_{n}_{d}_r{rep}")
        log = get("/log").splitlines()[-1].split(",")
        revert = original_by_app()
        ok_all &= revert
        res.append({"speed": sp, "rep": rep, "status": st, "r5_usado": int(log[5]) if len(log) > 5 else None, "revertido": revert, "bandas": bands})
        print(sp, rep, st, "r5", res[-1]["r5_usado"], "revertido" if revert else "¡NO REVERTIDO!", flush=True)
    # ráfaga sin pausa, 1/250
    get("/ss?n=1&d=250")
    c0 = len(card_files())
    get("/log?clear=1")
    get("/burst?n=4&gap=0")
    time.sleep(1)
    t0 = time.time()
    while "bursting=true" in get("/info") and time.time() - t0 < 120:
        time.sleep(1)
    blog = [x.split(",") for x in get("/log").splitlines()]
    res.append({"speed": "rafaga 4×1/250", "disparos": len(blog), "r5_usado": [int(x[5]) for x in blog], "revertido": original_by_app(), "status": get("/status")})
    print("ráfaga", res[-1], flush=True)
    ok_all &= res[-1]["revertido"]
finally:
    print("apagar", get("/silent?v=0"), "|", "iso", get("/iso?v=0"), get("/fmt?v=jpeg"), flush=True)
    fin = (rd(0x836D6FB6, 4), rd(0x836D7000, 6))
    print("telnet:", fin, "OK" if fin == (SM_O, R5_O) else "¡FALLO!", flush=True)

# exposición por banda: escena y τ con las referencias normales
T = np.array([t for t, _ in refs])
L = np.array([b for _, b in refs])
fit = [np.polyfit(T, L[:, b], 1) for b in range(NB)]
s = np.array([f[0] for f in fit])
report = {"ok_reversion_app": ok_all, "telnet_final": list(fin), "tanda": []}
print("\nvelocidad rep  objetivo_ms  medido_ms  error  octavos_ms")
for r in res:
    if "bandas" not in r:
        continue
    e = 1000 * np.array(r["bandas"]) / s
    octs = [round(float(e[i * NB // 8:(i + 1) * NB // 8].mean()), 2) for i in range(8)]
    n, d = r["speed"].split("/")
    tgt = 1000 * int(n) / int(d)
    r.update({"objetivo_ms": tgt, "medido_ms": float(e.mean()), "octavos_ms": octs})
    err = 100 * (e.mean() / tgt - 1)
    print(f"{r['speed']:>7} {r['rep']}  {tgt:9.2f}  {e.mean():9.2f}  {err:+6.1f}%  {octs}")
    r.pop("bandas")
    report["tanda"].append(r)
report["tanda"].append(res[-1])
(OUT / "report.json").write_text(json.dumps(report, indent=1))
