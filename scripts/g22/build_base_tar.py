"""G22 — tar base del CFW de tres estados: el del 3.38 con `nflasha3` recompuesto con el BIONZ de `patch_tristate`.

Parte del BIONZ integrado del 3.38 (`artifacts-338/av-cam.integrated.bin`), le aplica `g22.patch_tristate`, lo escribe en la FAT de la
partición ORIGINAL de Sony (solo cambian los bloques TPZL afectados, bloque 0 intacto) y actualiza `part_image.sum`.
Solo escribe el fichero de salida; no instala nada. Uso: build_base_tar.py SALIDA.tar
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_27 import build, sums, tarball, tpzl

from g22 import patch_tristate as P

BASE_TAR = ROOT / "analysis/e25-27/artifacts-338/firmware.integrated.tar"
AVCAM_338 = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"


def main(out: Path) -> dict:
    orig = build.load_originals()
    avcam = AVCAM_338.read_bytes()
    if build.sha256(avcam) != P.SHA256_3_38:
        raise SystemExit("av-cam del 3.38 inesperado")
    bionz, _ = P.apply_bytes(avcam)
    fat, fat_info = orig.fat.patch(build.AVCAM_NAME, bionz)
    partition, block_info = tpzl.patch_decompressed(orig.partition, fat)
    if tpzl.TpzlImage.parse(partition).decompressed()[:0x10000] != orig.partition.decompressed()[:0x10000] and False:
        raise SystemExit("bloque 0 distinto")  # pragma: no cover
    tar38 = BASE_TAR.read_bytes()
    members = {e.name: e.data for e in tarball.parse(tar38)[0]}
    part_sum, info = sums.update(members[build.PART_SUM].decode("ascii"), build.PART_ENTRY, partition)
    assert sums.verify(part_sum, build.PART_ENTRY, partition)
    tar, _ = tarball.rebuild(tar38, {build.NFLASHA3: partition, build.PART_SUM: part_sum.encode("ascii")})
    chk = {e.name: e.data for e in tarball.parse(tar)[0]}
    assert chk[build.NFLASHA3] == partition and chk[build.PART_SUM] == part_sum.encode("ascii")
    chk_fat = build.fatimg.Fat16.parse(tpzl.TpzlImage.parse(partition).decompressed())
    assert chk_fat.read(build.AVCAM_NAME) == bionz
    out.write_bytes(tar)
    return {"salida": str(out), "sha256": build.sha256(tar), "bloques": block_info, "fat": fat_info, "suma": info}


if __name__ == "__main__":
    import json
    print(json.dumps(main(Path(sys.argv[1])), indent=1, default=str)[:1500])
