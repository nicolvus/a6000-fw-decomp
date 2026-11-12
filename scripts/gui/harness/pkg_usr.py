#!/usr/bin/env python3
"""Arnés de la UI, F5 (G22): saca de un `nflasha15` de CFW los ficheros que difieren del `/usr` de Sony y los deja como overlay.

uso: pkg_usr.py NFLASHA15.bin USR_SONY DESTINO
  NFLASHA15.bin = imagen TPZL del paquete (p. ej. analysis/gui/g22/pkg-379w/nflasha15-379.bin); USR_SONY = DIR_TRABAJO/stage/cam/usr.
  DESTINO/cam/usr/… recibe solo los ficheros nuevos o distintos (con su modo del ext2); run.py lo superpone con OVERLAY2=DESTINO.
Se lee la imagen ya construida (TPZL → ext2 → `debugfs rdump`, sin root), no los ficheros de entrada del constructor.
"""
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from e25_27 import tpzl


def main(img: Path, stock: Path, dest: Path) -> list[str]:
    with tempfile.TemporaryDirectory() as t:
        ext2, root = Path(t) / "usr.ext2", Path(t) / "usr"
        ext2.write_bytes(tpzl.TpzlImage.parse(img.read_bytes()).decompressed())
        root.mkdir()
        subprocess.run(["debugfs", "-R", f"rdump / {root}", str(ext2)], capture_output=True, check=True)
        changed = sorted(str(f.relative_to(root)) for f in root.rglob("*") if f.is_file() and not f.is_symlink()
                         and not ((stock / f.relative_to(root)).is_file() and filecmp.cmp(f, stock / f.relative_to(root), shallow=False)))
        assert changed and len(changed) < 500, f"{len(changed)} ficheros distintos: ¿USR_SONY correcto?"
        shutil.rmtree(dest, ignore_errors=True)
        for rel in changed:
            (dest / "cam/usr" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, dest / "cam/usr" / rel)
    return changed


if __name__ == "__main__":
    for f in main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])):
        print(f)
