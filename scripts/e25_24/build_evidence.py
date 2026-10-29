"""E25-24 — genera la evidencia offline (JSON) de los parches y de la emulación.

No escribe binarios parcheados: solo hashes, diferencias, bytes de los caves y la
matriz de emulación.  Uso:

    python -m e25_24.build_evidence [--out analysis/e25-24]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import emu
from .patch_bionz import BionzImage
from .patch_bionz import apply_bytes as bionz_apply
from .patch_bionz import build_manifest as bionz_manifest
from .patch_darwin import DarwinImage
from .patch_darwin import apply_bytes as darwin_apply
from .patch_darwin import build_manifest as darwin_manifest
from .selector import Mode, Selector, packet_flag

ROOT = Path(__file__).resolve().parents[2]
AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"


def _selector_matrix() -> list[dict[str, object]]:
    rows = []
    for mode in (Mode.EFCS, Mode.ELECTRONIC):
        sel = Selector(mode=mode)
        t = sel.begin_capture()
        rows.append({
            "mode": mode.value,
            "field": 0 if mode is Mode.EFCS else 1,
            "packet_flag": packet_flag(mode),
            "route": t.route,
            "state_during": sel.state.value,
        })
        sel.end_capture()
    return rows


def build(out: Path) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    result: dict[str, object] = {"phase": "E25-24", "selector": _selector_matrix()}

    if AV_CAM.is_file():
        bimg = BionzImage.load(AV_CAM)
        patched, diff = bionz_apply(bimg.data)
        result["bionz"] = bionz_manifest(bimg, patched, diff)
        rows = []
        for r1 in (0, 1):
            for field in (0, 1):
                run = emu.run_bionz_selector(patched, r1, field)
                rows.append({
                    "sp_44": r1,
                    "field_0x41c": field,
                    "pkt_0x0e": run.packet[0x0E],
                    "pkt_0": run.packet[0],
                    "stopped_at": hex(run.stopped_at),
                    "r0": run.r0,
                })
        result["bionz_emulation"] = rows
    else:
        result["bionz"] = {"skipped": f"falta {AV_CAM}"}

    if DARWIN.is_file():
        dimg = DarwinImage.load(DARWIN)
        patched, diff = darwin_apply(dimg.data)
        result["darwin"] = darwin_manifest(dimg, patched, diff)
        rows = []
        for name, code in (("original", dimg.data), ("patched", patched)):
            for flag in (0, 1):
                rows.append({
                    "image": name,
                    "pkt_0x0e": flag,
                    "coil_0x20c74": emu.run_darwin(code, 0x20C74, flag),
                    "motor_0x1fe66": emu.run_darwin(code, 0x1FE66, flag),
                })
        result["darwin_emulation"] = rows
    else:
        result["darwin"] = {"skipped": f"falta {DARWIN}"}

    (out / "evidence.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "analysis/e25-24")
    args = ap.parse_args()
    print(json.dumps(build(args.out), indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
