#!/usr/bin/env python3
"""Diff del `/usr` del 3.93 (`pp`, instalado) contra el del 4.05: debe salir SOLO `lib/libmpr.so`.

Vuelca los dos ext2 con `debugfs rdump` (solo lectura) y compara con `diff -rq`.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tpzl  # noqa: E402


def main() -> dict:
    a = tpzl.TpzlImage.parse((ROOT / "build/cfw_func393/pp/nflasha15-393.bin").read_bytes()).decompressed()
    b = tpzl.TpzlImage.parse((ROOT / "build/cfw_bypass_guardas/nflasha15-405.bin").read_bytes()).decompressed()
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        dirs = {}
        for n, data in (("pp393", a), ("b405", b)):
            img = t / f"{n}.img"
            img.write_bytes(data)
            (t / n).mkdir()
            subprocess.run(["debugfs", "-R", f"rdump / {t / n}", str(img)], capture_output=True, check=True)
            dirs[n] = t / n
        out = subprocess.run(["diff", "-rq", "--no-dereference", str(dirs["pp393"]), str(dirs["b405"])],
                             capture_output=True, text=True, check=False).stdout
    lineas = [ln.replace(str(dirs["b405"]), "b405").replace(str(dirs["pp393"]), "pp393") for ln in out.splitlines()]
    solo_libmpr = len(lineas) == 1 and lineas[0].endswith("lib/libmpr.so differ")
    assert solo_libmpr, lineas
    return {"diff_pp393_vs_405": lineas, "solo_lib_libmpr_so": solo_libmpr,
            "iguales_en_tamano_ext2": len(a) == len(b)}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
