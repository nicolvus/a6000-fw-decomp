"""E25-26 — evidencia de C3-B: bytes, emulación end-to-end y tabla de velocidades."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for p in ("scripts", "scripts/e25_18", "scripts/e25_16", "scripts/e25_17"):
    sys.path.insert(0, str(ROOT / p))

from e25_24 import patch_bionz as PB

from e25_26 import emu
from e25_26 import patch_c3b as PC

AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
RAPIDAS = {"1/8000": 1 / 8000, "1/4000": 1 / 4000, "1/1000": 1 / 1000,
           "1/250": 1 / 250, "1/125": 1 / 125, "1/60": 1 / 60, "1/30": 1 / 30}


def speed_table() -> dict:
    import silent_plan as P
    out: dict[str, Any] = {}
    for name, t in RAPIDAS.items():
        tv = P.tv_code(t)
        row: dict[str, Any] = {"tv": tv, "nominal_us": t * 1e6}
        for pred in (0, 1):
            nat = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, pred)
            shd, svd = nat["shd"], nat["svd"]
            if pred == 1 and svd == 1 and shd > P.VTS_MEDIDO:
                shd, svd = shd - P.VTS_MEDIDO, 0
            exp = (P.VTS_MEDIDO - shd) * P.PERIODO_Q8 / 256
            row[f"pred{pred}"] = {
                "native_shd": nat["shd"], "native_svd": nat["svd"], "native_shutmode": nat["shutmode"],
                "lineas": nat["lineas"], "c3b_shd": shd, "c3b_svd": svd,
                "exposicion_us": round(exp, 1), "error_pct": round((exp / row["nominal_us"] - 1) * 100, 2),
            }
        out[name] = row
    out["_nota"] = ("VTS 4219 y período 3891 Q8 son la referencia de T046/T047; el diseño lee VTS de "
                    "cap+0x5e0 y no lo fija. 1/8000 y 1/30 son solo emulación.")
    return out


def main() -> None:
    image = PB.BionzImage.load(AV_CAM)
    selector, dsel = PB.apply_bytes(image.data)
    combined, dc3b = PC.apply_bytes(selector)
    restored = PC.restore_bytes(combined)
    restored = PB.restore_bytes(restored)
    matrix = emu.matrix(combined)

    out = {
        "phase": "E25-26",
        "status": "offline",
        "installable": False,
        "source_sha256": image.sha256(),
        "selector_sha256": PB.sha256(selector),
        "combined_sha256": PC.sha256(combined),
        "selector_diff_count": len(dsel),
        "c3b_diff_count": len(dc3b),
        "restore_ok": restored == image.data and PC.sha256(restored) == PC.SHA256_ORIGINAL,
        "hook": {"address": hex(PC.HOOK), "original": PC.HOOK_OLD.hex(), "patched": PC.hook_bytes().hex(),
                 "target": hex(PC.HOOK_TARGET)},
        "cave": {"address": hex(PC.CAVE), "length": PC.CAVE_LEN, "bytes": PC.cave_bytes().hex()},
        "conditions": ["cap+0x41c == 1", "paso 0", "svd nativo <= 1", "VTS != 0", "shd > VTS"],
        "writes": [hex(PC.CAP_SHD), hex(PC.CAP_SVD), hex(PC.CAP_SHUTMODE)],
        "emulation": matrix,
        "speeds": speed_table(),
        "limits": [
            "No se modela el IMX210 ni el cierre físico de la exposición.",
            "SetExposure/SetRead/SSB/Execute son stubs que registran argumentos.",
            "cap+0x650 se restaura a r7 en 0x438c8334: el host sigue viendo el plan nativo.",
            "cap+0x73b se calcula en 0x43b1e520 antes del enganche: queda con el ShutMode nativo (3).",
            "No se cubren largas (svd > 1); la cueva se inhibe.",
            "No se ejecutó en cámara ni se instaló nada.",
        ],
    }
    dst = ROOT / "analysis/e25-26/evidence.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("restore_ok", out["restore_ok"], "diff", len(dsel), len(dc3b))
    print("efcs_identical", matrix["efcs_identical"], "errors_identical", matrix["errors_identical"],
          "electronic_normalized", matrix["electronic_normalized"])
    print("written", dst)


if __name__ == "__main__":
    main()
