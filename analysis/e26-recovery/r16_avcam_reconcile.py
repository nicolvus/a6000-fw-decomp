"""R16 §9: concilia las tres imágenes av-cam.bin (original 3.21, integrada E25-27, extraída de nflasha3).

Solo lectura. Salida: r16-avcam-reconcile.json
"""

from __future__ import annotations

import hashlib
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import patch_bionz as PB  # type: ignore[import-not-found]
from e25_24 import patch_darwin as PD  # type: ignore[import-not-found]
from e25_26 import patch_c3b as PC  # type: ignore[import-not-found]

from scripts.e25_27.fatimg import Fat16
from scripts.e25_27.tpzl import TpzlImage

ORIG = (
    ROOT
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
INTEG = ROOT / "analysis/e25-27/artifacts/av-cam.integrated.bin"
NFLASH = ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin"
TAR = ROOT / "analysis/e25-27/artifacts/firmware.integrated.tar"
MEMBER = "0700_part_image/dev/nflasha3"
BASE = PB.BASE


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def avcam_from(nflasha: bytes) -> bytes:
    fat = TpzlImage.parse(nflasha).decompressed()
    return Fat16.parse(fat).read("av-cam.bin")


def intervals(a: bytes, b: bytes) -> list[tuple[int, int]]:
    out, start = [], None
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y and start is None:
            start = i
        elif x == y and start is not None:
            out.append((start, i - start))
            start = None
    if start is not None:
        out.append((start, len(a) - start))
    return out


def main() -> dict:
    orig, integ = ORIG.read_bytes(), INTEG.read_bytes()
    nf = NFLASH.read_bytes()
    with tarfile.open(TAR) as t:
        names = t.getnames()
        member = next(n for n in names if n.endswith(MEMBER))
        fobj = t.extractfile(member)
        assert fobj is not None
        nf_tar = fobj.read()
    ext = avcam_from(nf)
    ext_tar = avcam_from(nf_tar)
    res = {
        "sha256": {
            "orig": sha(orig),
            "integ": sha(integ),
            "extraida_nflasha3": sha(ext),
            "nflasha3_artifact": sha(nf),
            "nflasha3_en_tar": sha(nf_tar),
            "extraida_tar": sha(ext_tar),
        },
        "size": {"orig": len(orig), "integ": len(integ), "extraida": len(ext)},
        "integ_eq_extraida": integ == ext,
        "nflasha3_artifact_eq_tar": nf == nf_tar,
    }
    ivs = intervals(orig, integ)
    res["bytes_distintos_orig_vs_integ"] = sum(n for _, n in ivs)
    res["intervalos_orig_vs_integ"] = len(ivs)
    res["bytes_distintos_orig_vs_extraida"] = sum(n for _, n in intervals(orig, ext))
    rows = []
    # parches selector (direcciones virtuales) + cueva C3-B
    spans = [
        (a - BASE, len(o), r, "selector (patch_bionz)") for a, o, n, r in PB.PATCHES
    ]
    spans.append(
        (PC.HOOK - BASE, len(PC.HOOK_OLD), "bl imager -> bl cueva C3-B", "patch_c3b")
    )
    spans.append((PC.CAVE - BASE, PC.CAVE_LEN, "cueva C3-B", "patch_c3b"))
    c3b_extra = [p for p in dir(PC) if p.isupper()]
    res["c3b_consts"] = c3b_extra
    res["patches_selector"] = [(hex(o), l, r) for o, l, r, _ in spans]
    res["parcheados_total"] = sum(l for _, l, _, _ in spans)
    for off, ln, role, comp in spans:
        diff = sum(1 for i in range(off, off + ln) if orig[i] != integ[i])
        rows.append(
            {
                "offset": hex(off),
                "va": hex(off + BASE),
                "len": ln,
                "distintos": diff,
                "rol": role,
                "comp": comp,
            }
        )
    res["tabla"] = rows
    res["distintos_en_parches"] = sum(r["distintos"] for r in rows)
    covered = {i for off, ln, *_ in spans for i in range(off, off + ln)}
    res["distintos_fuera_de_parches"] = [
        hex(i) for i in range(len(orig)) if orig[i] != integ[i] and i not in covered
    ]
    res["intervalos"] = [(hex(s), n) for s, n in ivs]
    # Los 111 B del manifiesto E25-27 = 28 (selector) + 61 (C3-B) + 22 (Darwin), no solo BIONZ.
    d0 = (
        ROOT
        / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
    ).read_bytes()
    d1 = (ROOT / "analysis/e25-27/artifacts/darwin_core.integrated.bin").read_bytes()
    res["darwin_sha_orig_ok"] = sha(d0) == PD.SHA256
    res["darwin_distintos"] = sum(1 for x, y in zip(d0, d1) if x != y)
    res["bionz_escritos"] = res["parcheados_total"]
    mf = json.loads((ROOT / "analysis/e25-27/manifest.json").read_text())
    res["manifiesto_diff_count"] = {
        k: v["diff_count"] for k, v in mf["components"].items()
    } | {"total": mf["diff_count"]}
    return res


if __name__ == "__main__":
    r = main()
    (Path(__file__).parent / "r16-avcam-reconcile.json").write_text(
        json.dumps(r, indent=1)
    )
    print(json.dumps({k: v for k, v in r.items() if k not in ("tabla",)}, indent=1))
    for row in r["tabla"]:
        print(row)
