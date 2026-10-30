"""E26-R14 — Offline: RAMCFG (Backup 0xfa0080), BOS sector 0 and FAT geometry against the real images.

Static, file-only.  Nothing is written; the camera is never touched.
"""

import hashlib
import json
import sys
import tarfile
from pathlib import Path

import r14_backup as B

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "analysis/camera-dumps"
NAND = D / "nand-20261020"
sys.path.insert(0, str(ROOT))
from scripts.e25_27.tpzl import TpzlImage

N3 = {
    "historico_camara_3.21": NAND / "dev_nflasha3.bin",  # read from the camera, fw 3.21
    "oficial_3.21": ROOT
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3",
    "integrada_3.25": ROOT
    / "analysis/e25-27/artifacts/nflasha3.integrated.bin",  # modified build, not official
}
PKG_BACKUP = {
    "oficial_3.21": ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0110_backup",
    "integrada_3.25": ROOT / "analysis/e25-27/artifacts/firmware.integrated.tar",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def backup_copies() -> dict[str, bytes]:
    """Every BK4 file in the repo's camera dumps (852647 B) plus the two copies on nflasha2."""
    out = {
        str(p.relative_to(D)): p.read_bytes()
        for p in sorted(D.rglob("*.bin"))
        if p.stat().st_size == 852647
    }
    p2 = B.FatVol((NAND / "dev_nflasha2.bin").read_bytes())
    for n in ("\\Backup.bin", "\\Backup.bak"):
        out[f"nflasha2:{n}"] = p2.read(n) or b""
    return out


def package_backups() -> dict[str, bytes]:
    out = {}
    for p in sorted(PKG_BACKUP["oficial_3.21"].rglob("*.bin")):
        out[f"oficial_3.21/{p.name}"] = p.read_bytes()
    with tarfile.open(PKG_BACKUP["integrada_3.25"]) as t:
        for m in t.getmembers():
            if m.name.startswith("0110_backup") and m.name.endswith(".bin"):
                out[f"integrada_3.25/{Path(m.name).name}"] = t.extractfile(m).read()  # type: ignore[union-attr]
    return out


def ramcfg_hashes(copies: dict[str, bytes]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for k, v in copies.items():
        blob = B.BK4(v).read(0xFA0080) or b""
        groups.setdefault(sha(blob), []).append(k)
    return groups


def volumes() -> dict[str, dict[int, B.FatVol]]:
    p2 = B.FatVol((NAND / "dev_nflasha2.bin").read_bytes())
    return {
        k: {2: p2, 3: B.FatVol(TpzlImage.parse(p.read_bytes()).decompressed())}
        for k, p in N3.items()
    }


def bos() -> tuple[bool, list[B.BosRow]]:
    return B.bos_parse((NAND / "dev_nflasha.bin").read_bytes()[:0x200])


if __name__ == "__main__":
    cfg = B.ramcfg(B.BK4.load(D / "20261020-first/backup_flash.bin"))
    print(json.dumps({"ramcfg": [e.__dict__ for e in cfg]}, indent=1))
    g = ramcfg_hashes({**backup_copies(), **package_backups()})
    print({h[:12]: len(v) for h, v in g.items()})
    ok, rows = bos()
    print("BOS sig", ok, [(r.n, hex(r.start), hex(r.size), r.kind) for r in rows[:9]])
    for label, vols in volumes().items():
        print(
            label,
            {
                p: B.fat_checks(v.v[:0x10000])["loader3_accepts"]
                for p, v in vols.items()
            },
        )
        for e in cfg:
            v = B.entry_verdict(e, vols)
            print("  ", e.n, e.part, e.path, v.code, v.reason)
