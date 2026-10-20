"""Búsqueda dirigida y contraste Capstone sobre av-cam A6000, sin modificarlo."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/s58"))
from tdis import data, dis, ins_list


def scan():
    """Candidatos, no xrefs probadas: el barrido lineal puede atravesar datos."""
    instructions = ins_list("A6000")
    targets = {"#0x43ae84c0", "#0x437876dc"}
    hits = []
    for k, (address, mnemonic, operands) in enumerate(instructions):
        if (mnemonic in ("bl", "b.w") and operands in targets) or (
            "#0xdd0" in operands and mnemonic.startswith(("add", "str", "ldr"))
        ):
            hits.append({"address": hex(address), "context": [
                f"{a:08x} {m} {o}" for a, m, o in instructions[max(0, k - 5):k + 9]
            ]})
    return hits


if __name__ == "__main__":
    if len(sys.argv) == 3:
        dis("A6000", int(sys.argv[1], 0), int(sys.argv[2], 0))
    else:
        import hashlib
        print(json.dumps({"sha256": hashlib.sha256(data("A6000")).hexdigest(),
                          "candidate_hits": scan()}, indent=2))
