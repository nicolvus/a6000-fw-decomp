#!/usr/bin/env python3
"""Lanzador del arnés G22 con /dev/nflasha4 REAL emulado (NFLASH4=1) y la sonda `nf4clip.so`.

Copia de reports/evidence/fbm-initb-6-3-nflasha4-20261126/pb_run_nf4.py con dos cambios:
  · precarga /usr/lib/nf4clip.so en vez de /usr/lib/nf4inject.so,
  · reenvía al invitado TODAS las variables de entorno `NF4*` del anfitrión (NF4MODE, NF4INJECT…),
    no sólo NF4MODE.

uso: python3 pb_run_clip.py SEGUNDOS SALIDA IMAGEN_NFLASHA4 [NF4INJECT]

Perfil: analysis/gui/g22/harness/live/nf4/ (overlay con nf4clip.so).
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
H = REPO / "scripts/gui/harness"
sys.path.insert(0, str(H))

IMG = Path(sys.argv[3]).resolve()
os.environ["LIVE_NFLASH4"] = str(IMG)          # el shim recibe NFLASH4=<huella> en SHIMENV
import run       # noqa: E402
import sd_emu    # noqa: E402
import sd_image  # noqa: E402
import live      # noqa: E402


def main() -> None:
    secs = int(sys.argv[1])
    salida = Path(sys.argv[2]).resolve()
    inyecta = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("NF4INJECT", "20")
    salida.mkdir(parents=True, exist_ok=True)
    work = REPO / "analysis/gui/g22/harness"
    overlay2 = REPO / "analysis/gui/g22/harness/live/nf4/overlay"
    shimenv = live.SHIMENV.replace(" LIVE=auto", "").replace("WAIT=999999", "WAIT=1200")
    shimenv += f" NF4INJECT={inyecta}"
    for k, v in os.environ.items():
        if k.startswith("NF4") and k != "NF4INJECT" and v and " " not in v:
            shimenv += f" {k}={v}"
    consola = salida / "consola.log"
    consola.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        guion = (H / "im.sh").read_text()
        assert "LD_PRELOAD=/usr/lib/sonyshim.so" in guion
        guion = guion.replace("LD_PRELOAD=/usr/lib/sonyshim.so",
                              'LD_PRELOAD="/usr/lib/sonyshim.so /usr/lib/nf4clip.so"')
        (t / "im_nf4clip.sh").write_text(guion)
        cabeza = t / "sd.head"
        nsec = sd_image.construye(sd_emu.raiz_sd(""), cabeza, 4.0)
        print(f"[pb_run] SD {sd_emu.raiz_sd('')} -> {cabeza} ({nsec} sectores)", flush=True)
        print(f"[pb_run] nflasha4: {IMG} ({IMG.stat().st_size} B)", flush=True)
        print(f"[pb_run] SHIMENV NF4: {[x for x in shimenv.split() if x.startswith('NF4')]}", flush=True)
        initrd = run.build_initrd(work, t / "im_nf4clip.sh", t, shimenv, str(overlay2), None, cabeza, IMG)
        cmd = run.qemu_cmd(work, initrd, [], ["-serial", f"file:{consola}", "-display", "none"])
        print("[pb_run] " + " ".join(cmd)[:300], flush=True)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < secs and p.poll() is None:
            time.sleep(2)
            if consola.exists() and "[FBMC] FIN" in consola.read_text(errors="replace"):
                print(f"[pb_run] [FBMC] FIN a los {time.time() - t0:.0f} s", flush=True)
                break
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        print(f"[pb_run] qemu terminó a los {time.time() - t0:.0f} s (rc={p.returncode})", flush=True)
    texto = consola.read_text(errors="replace") if consola.exists() else ""
    print(f"[pb_run] consola.log: {len(texto)} B en {consola}", flush=True)
    for ln in texto.splitlines():
        if any(m in ln for m in ("[NF4]", "[FBMC]", "NFLASH4", "alive=", "EXIT=", "IMEXIT")):
            print(ln[:240], flush=True)


if __name__ == "__main__":
    main()
