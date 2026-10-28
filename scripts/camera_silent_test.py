#!/usr/bin/env python3
"""E25-11: prueba del modo silencioso con el parche aplicado desde el PC (scripts/camera_silent.py) y guardián en la cámara.

Uso: camera_silent_test.py OUTDIR   (RemoteShutter abierta, adb 5555, telnet 23, escena fija y sin tocar)
0) prueba del guardián: parchea y NO revierte; a los ~25 s la cámara debe volver sola a los bytes originales;
1) referencias normales (1/60, 1/30, 1/15) en RAW; 2) disparos silenciosos a 1/4000…1/30 ×2 y 1/15 (cae a normal);
3) ráfaga de 4 con un solo parche; cada disparo vigilado: si la app no responde o pasan 45 s, se revierte y se aborta.
Deja ISO automático y JPEG; verifica los bytes originales al final."""
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
import camera_silent as S

HOST, NB = S.HOST, 32
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=False)


def get(p, t=20):
    return urllib.request.urlopen(f"http://{HOST}:8080{p}", timeout=t).read().decode().strip()


def count() -> int:
    return int(get("/info").split("count=")[1].split()[0])


adb = AdbDeviceTcp(HOST, 5555, default_transport_timeout_s=60)
adb.connect(rsa_keys=None, auth_timeout_s=10)


def card_files():
    folder = max((x for x in adb.shell("ls /mnt/sdcard/DCIM").split() if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {f"{folder}/{f}" for f in adb.shell(f"ls /mnt/sdcard/DCIM/{folder}").split() if f.startswith("DSC")}


def wait_shots(c0, n, token):
    """Vigilante de la app: sin respuesta o más de 45 s ⇒ revierte y aborta."""
    t0, last_ok = time.time(), time.time()
    while True:
        try:
            if count() >= c0 + n and not get("/status").startswith(("shooting", "queued")):
                return
            last_ok = time.time()
        except Exception:  # noqa: BLE001 (timeout o conexión: la app puede estar colgada)
            if time.time() - last_ok > 12:
                S.revert(token)
                raise RuntimeError("la app no responde: parche revertido") from None
        if time.time() - t0 > 45:
            S.revert(token)
            raise TimeoutError("el disparo no termina en 45 s: parche revertido")
        time.sleep(0.4)


def bands_of(card_path, tag):
    dst = OUT / f"{tag}.ARW"
    adb.pull(f"/mnt/sdcard/DCIM/{card_path}", str(dst))
    r = rawpy.imread(str(dst))
    x = r.raw_image_visible.astype(np.float32) - np.mean(r.black_level_per_channel)
    k = x.shape[0] // NB
    return [round(float(x[i * k:(i + 1) * k].mean()), 2) for i in range(NB)]


def shot(tag, silent):
    """Un disparo RAW; si silent y la velocidad cabe en el cuadro, con parche aplicado solo durante el disparo."""
    before, c0 = card_files(), count()
    sec = float(get("/info").split("speed=")[1].split()[0])
    r5 = S.r5_for(sec) if silent else -1
    token = f"{tag}"
    if r5 > 0:
        S.apply(r5, token)
    try:
        get("/shoot")
        wait_shots(c0, 1, token)
    finally:
        if r5 > 0:
            ok = S.revert(token)
            print("  reversión", "OK" if ok else "¡FALLO!", flush=True)
            if not ok:
                raise RuntimeError("no se pudo verificar la reversión")
    time.sleep(1.5)
    arw = sorted(f for f in card_files() - before if f.endswith(".ARW"))
    if not arw:
        raise RuntimeError(f"{tag}: sin ARW ({get('/status')})")
    return bands_of(arw[0], tag), r5, get("/status")


assert S.is_original(), "los sitios de BIONZ no están originales antes de empezar"
print("antes:", get("/info"), flush=True)
res, refs = [], []
try:
    # 0) guardián
    S.apply(3956, "guardia")
    print("guardián: parche aplicado sin revertir; esperando", S.GUARD_S + 3, "s…", S.state(), flush=True)
    time.sleep(S.GUARD_S + 3)
    g_ok = S.is_original()
    print("guardián:", "revirtió solo: OK" if g_ok else "¡NO REVIRTIÓ!", flush=True)
    if not g_ok:
        S.revert("guardia")
        raise RuntimeError("el guardián no funciona; abortado")
    print("fmt", get("/fmt?v=rawjpeg"), "iso", get("/iso?v=100"), flush=True)
    for sp in ("1/60", "1/30", "1/15"):
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        refs.append((int(n) / int(d), shot(f"ref_{n}_{d}", False)[0]))
        print("ref", sp, flush=True)
    for sp, rep in [(s, r) for s in ("1/4000", "1/1000", "1/250", "1/60", "1/30", "1/15") for r in (0, 1)]:
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        bands, r5, st = shot(f"sil_{n}_{d}_r{rep}", True)
        res.append({"speed": sp, "rep": rep, "status": st, "r5": r5, "bandas": bands})
        print(sp, rep, st, "r5", r5, flush=True)
    # ráfaga con un solo parche
    get("/ss?n=1&d=250")
    c0 = count()
    S.apply(S.r5_for(1 / 250), "rafaga")
    try:
        get("/burst?n=4&gap=0")
        wait_shots(c0, 4, "rafaga")
    finally:
        ok = S.revert("rafaga")
    res.append({"speed": "rafaga 4×1/250", "disparos": count() - c0, "revertido": ok, "status": get("/status")})
    print("ráfaga", res[-1], flush=True)
finally:
    if not S.is_original():
        S.revert("final")
    print("restaurar", get("/iso?v=0"), get("/fmt?v=jpeg"), flush=True)
    print("bytes finales", S.state(), "OK" if S.is_original() else "¡FALLO!", flush=True)

T = np.array([t for t, _ in refs])
L = np.array([b for _, b in refs])
s = np.array([np.polyfit(T, L[:, b], 1)[0] for b in range(NB)])
report = {"guardian_ok": g_ok, "tanda": []}
print("\nvelocidad rep  objetivo_ms  medido_ms  error  octavos_ms")
for r in res:
    if "bandas" in r:
        e = 1000 * np.array(r.pop("bandas")) / s
        octs = [round(float(e[i * NB // 8:(i + 1) * NB // 8].mean()), 2) for i in range(8)]
        n, d = r["speed"].split("/")
        tgt = 1000 * int(n) / int(d)
        r.update({"objetivo_ms": tgt, "medido_ms": float(e.mean()), "octavos_ms": octs})
        print(f"{r['speed']:>7} {r['rep']}  {tgt:9.2f}  {e.mean():9.2f}  {100 * (e.mean() / tgt - 1):+6.1f}%  {octs}  r5={r['r5']}")
    report["tanda"].append(r)
(OUT / "report.json").write_text(json.dumps(report, indent=1))
