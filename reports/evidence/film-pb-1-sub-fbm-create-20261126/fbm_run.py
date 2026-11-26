#!/usr/bin/env python3
"""Arranque del arnés para medir la tabla de sectores FBM 0xA3699C antes/después del parche.

Construye el initrd como run.py/live.py: overlay del arnés + overlay PROPIO con
  cam/usr/lib/sonyshim.so   (shim instrumentado, hilo FBMTAB)
  cam/usr/lib/libmpr.so     (sólo si se pasa la biblioteca parcheada: sustituye a la de Sony)
más la cabeza FAT32 de la SD (~/A6000-SD) y la imagen de /dev/nflasha4. Arranca qemu con
-serial file:consola.log y corta cuando el invitado ya lleva >=PARA s de muestras FBMTAB
(o al agotar SEGUNDOS). Deja consola.log en SALIDA e imprime las líneas FBMTAB.

uso: fbm_run.py SEGUNDOS SALIDA [LIBMPR_PARCHEADA] [PARA]
"""
import base64
import gzip
import hashlib
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
H = REPO / "scripts/gui/harness"
sys.path.insert(0, str(H))
import run          # noqa: E402
import sd_emu       # noqa: E402
import sd_image     # noqa: E402

NFLASH4 = Path(os.environ.get("FBMNFLASH4") or REPO / "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin")


def main() -> None:
    secs = int(sys.argv[1])
    salida = Path(sys.argv[2]).resolve()
    parcheada = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 and sys.argv[3] else None
    para = int(sys.argv[4]) if len(sys.argv) > 4 else 90
    fin_marca = os.environ.get("FBMFIN", "")
    salida.mkdir(parents=True, exist_ok=True)
    overlay = salida / "overlay"
    shutil.rmtree(overlay, ignore_errors=True)
    (overlay / "cam/usr/lib").mkdir(parents=True)
    shutil.copy2(HERE / "sonyshim.so", overlay / "cam/usr/lib/sonyshim.so")
    if parcheada:
        shutil.copy2(parcheada, overlay / "cam/usr/lib/libmpr.so")
    work = REPO / "analysis/gui/g22/harness"
    cadena = ("CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,view/STLREC OPENVIEWAT=40 OPENVIEWGAP=14 CALMA=4 CALMA0=10 "
              "STARTEV=11004002:100,11004012,11004013 POSTROOTEV=11004002:e3 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 "
              "ACKQ0=58003f KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177,7025:3:27 KEYINITON= "
              "KEYINITAFTER=not_user_operation OPENVIEWARG=3 NO4015E=1 BKMULTIPTR=1 FRONTRM=3 FRONTARG2=1 FRONTRMDELAY=3 "
              "INSHORT=1 SDIMG=1 SDSECT=8388608 NULLMWF=1 SYNCWAIT=37807c:300")   # CADENA de scripts/gui/harness/estable.sh
    # NFLASH4=<sha256[:12]>: el shim (sonyshim.c:111 nf_name) sólo emula /dev/nflasha4 con esa variable
    # puesta; sin ella el FBS no tiene dispositivo y CreateSector32 devuelve 0x7 (FBS_INVALID_PROCESS).
    nf4 = f" NFLASH4={hashlib.sha256(NFLASH4.read_bytes()).hexdigest()[:12]}" if NFLASH4.is_file() else ""
    shimenv = os.environ.get("FBMSHIMENV", f"{cadena} WAIT=120 FBMTAB=1") + nf4 + " " + os.environ.get("FBMEXTRA", "")
    consola = salida / "consola.log"
    consola.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cabeza = t / "sd.head"
        nsec = sd_image.construye(sd_emu.raiz_sd(""), cabeza, 4.0)
        print(f"[fbm_run] SD {sd_emu.raiz_sd('')} -> {cabeza} ({nsec} sectores)", flush=True)
        print(f"[fbm_run] overlay {overlay} · nflasha4 {NFLASH4.name} · SHIMENV {shimenv}", flush=True)
        initrd = run.build_initrd(work, HERE / "im_fbm.sh", t, shimenv, str(overlay), None, cabeza, NFLASH4)
        cmd = run.qemu_cmd(work, initrd, [], ["-serial", f"file:{consola}", "-display", "none"])
        print("[fbm_run] " + " ".join(cmd)[:300], flush=True)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        fin = None
        while time.time() - t0 < secs and p.poll() is None:
            time.sleep(3)
            if not consola.exists():
                continue
            txt = consola.read_text(errors="replace")
            ts = [int(m.group(1)) for m in re.finditer(r"FBMTAB t=(\d+)s", txt)]
            llenas = [int(m.group(1)) for m in re.finditer(r"llena=(\d+) nh=", txt)]
            # corta cuando la tabla lleva llena (=FBM::Init corrió) y estable >= para s
            if fin_marca and fin_marca in txt:     # FBMFIN: espera a que el guion del invitado llegue al final
                print(f"[fbm_run] marcador final {fin_marca!r} a los {time.time() - t0:.0f} s de pared", flush=True)
                time.sleep(5)                      # margen para que qemu vuelque lo último de la serial
                break
            if not fin_marca and ts and llenas and max(llenas) == 30 and max(ts) >= para and txt.count("sin cambios") >= 2:
                fin = max(ts)
                print(f"[fbm_run] tabla llena y estable hasta t={fin}s a los {time.time() - t0:.0f} s de pared", flush=True)
                break
            if not fin_marca and "alive=" in txt and "FBMTAB" in txt:
                print(f"[fbm_run] el guion del invitado terminó a los {time.time() - t0:.0f} s", flush=True)
                break
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        print(f"[fbm_run] qemu terminó a los {time.time() - t0:.0f} s (rc={p.returncode})", flush=True)
    texto = consola.read_text(errors="replace") if consola.exists() else ""
    while "=====GUESTFILE-BEGIN" in texto and "=====GUESTFILE-END" in texto:   # ficheros del invitado (NF4DUMP/NFLIMG)
        pre, rest = texto.split("=====GUESTFILE-BEGIN", 1)
        head, blob = rest.split("=====GUESTFILE-END", 1)[0].split("\n", 1)
        destino = salida / head.strip()
        try:
            datos = gzip.decompress(base64.b64decode("".join(blob.split())))
            destino.write_bytes(datos)
            print(f"[fbm_run] GUESTFILE {head.strip()} -> {destino} ({len(datos)} B)", flush=True)
        except Exception as ex:                      # noqa: BLE001
            print(f"[fbm_run] GUESTFILE {head.strip()}: no se pudo decodificar ({ex})", flush=True)
        texto = pre + f"[{head.strip()} extraido]" + rest.split("=====GUESTFILE-END", 1)[1]
    print(f"[fbm_run] consola.log: {len(texto)} B en {consola}", flush=True)
    for ln in texto.splitlines():
        if any(m in ln for m in ("FBMTAB", "IMEXIT", "alive=", "FlashLib", "FBS_", "CreateSector", "WriteBaseData",
                                 "PROBE", "NF4DIFF", "NF4IMG", "NFLASH4")):
            print(ln[:230], flush=True)


if __name__ == "__main__":
    main()
