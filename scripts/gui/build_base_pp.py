#!/usr/bin/env python3
"""G31 — pasa el parche PP del núcleo (curvas, tablas, datos y ganchos de `pp_curves_patch`) de la RAM a la imagen: `av-cam.pp.bin` dentro de `nflasha3`. NO instala nada.

Parte de un firmware.tar cuyo BIONZ es el del CFW (3.38 + tres estados), sustituye `AV-CAM.BIN` en la FAT de `nflasha3`, recompone solo los bloques TPZL
tocados y actualiza `part_image.sum`. El resultado es el mismo núcleo que dejaba `pp_ram.sh` en RAM, sin script de arranque ni vigilante.
Uso: build_base_pp.py BASE.tar SALIDA.tar [--sin-color]
"""
import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
import pp_curves_patch
from e25_27 import build, fatimg, sums, tarball, tpzl
from g22 import patch_silent_r5


def bionz_cfw(bionz: bytes, color: bool = True, tone: bool = True, silent_r5: bool = True) -> bytes:
    """BIONZ del CFW (3.38 + tres estados) → + parche PP del núcleo y, opcional, Silent calibrado (también lo usa la auditoría G22)."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "av-cam.base.bin"
        src.write_bytes(bionz)
        pp_curves_patch.main(src, Path(tmp) / "pp", None, color=color, tone=tone)
        nuevo = (Path(tmp) / "pp/av-cam.pp.bin").read_bytes()
    if silent_r5:   # E26-R86: Silent con ShutMode 0 + r5 desde la velocidad (calibración R56), solo en foto
        nuevo = patch_silent_r5.apply_bytes(nuevo)
    return nuevo


def main(base_tar: Path, out_tar: Path, color: bool = True, tone: bool = True, silent_r5: bool = True) -> dict:
    tar = base_tar.read_bytes()
    entries, _ = tarball.parse(tar)
    members = {e.name: e.data for e in entries}
    part = tpzl.TpzlImage.parse(members[build.NFLASHA3])
    fat = fatimg.Fat16.parse(part.decompressed())
    bionz = fat.read(build.AVCAM_NAME)
    nuevo = bionz_cfw(bionz, color, tone, silent_r5)
    assert len(nuevo) == len(bionz) and nuevo != bionz
    fat2, _ = fat.patch(build.AVCAM_NAME, nuevo)
    part2, info = tpzl.patch_decompressed(part, fat2)
    assert fatimg.Fat16.parse(tpzl.TpzlImage.parse(part2).decompressed()).read(build.AVCAM_NAME) == nuevo
    part_sum, _ = sums.update(members[build.PART_SUM].decode("ascii"), build.PART_ENTRY, part2)
    assert sums.verify(part_sum, build.PART_ENTRY, part2)
    out, _ = tarball.rebuild(tar, {build.NFLASHA3: part2, build.PART_SUM: part_sum.encode("ascii")})
    out_tar.write_bytes(out)
    return {"bloques_tpzl": len(info), "partition_igual_tamano": len(part2) == len(members[build.NFLASHA3]), "bytes_cambiados": sum(a != b for a, b in zip(bionz, nuevo))}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--sin-color", action="store_true")
    ap.add_argument("--sin-tono", action="store_true")
    ap.add_argument("--sin-silent-r5", action="store_true")
    a = ap.parse_args()
    print(main(a.base, a.salida, not a.sin_color, not a.sin_tono, not a.sin_silent_r5))
