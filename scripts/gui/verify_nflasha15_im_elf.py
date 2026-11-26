#!/usr/bin/env python3
"""Comprueba que una `nflasha15` (TPZL) lleva exactamente el `/bin/im.elf` que se espera.

Uso: verify_nflasha15_im_elf.py IMAGEN_NFLASHA15 IM_ELF_ESPERADO [--sony IM_ELF_DE_FABRICA]
Sale con 1 si el contenido no coincide o si la compuerta del WBI (`0x9F44`) no es la parcheada.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tpzl


def main(imagen: Path, esperado: Path, sony: Path | None) -> int:
    img = tpzl.TpzlImage.parse(imagen.read_bytes())
    tmp = Path(tempfile.mkdtemp(prefix="verify-")) / "usr.ext2"
    tmp.write_bytes(img.decompressed())
    dentro = subprocess.run(["debugfs", "-R", "cat /bin/im.elf", str(tmp)],
                            capture_output=True, check=True).stdout
    esp = esperado.read_bytes()
    print("im.elf en la imagen :", len(dentro), hashlib.sha256(dentro).hexdigest())
    print("im.elf esperado     :", len(esp), hashlib.sha256(esp).hexdigest())
    print("IGUAL               :", dentro == esp)
    print("compuerta 0x9F44    :", dentro[0x1F44:0x1F48].hex(), "(esperado 01207047)")
    if sony and sony.exists():
        original = sony.read_bytes()
        print("bytes distintos vs Sony:", sum(a != b for a, b in zip(original, dentro)))
    return 0 if dentro == esp and dentro[0x1F44:0x1F48] == bytes.fromhex("01207047") else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    sony = None
    if "--sony" in args:
        i = args.index("--sony")
        sony = Path(args[i + 1])
        del args[i:i + 2]
    raise SystemExit(main(Path(args[0]), Path(args[1]), sony))
