"""D6: rutinas Thumb sin ubicar por REA (7 trazas con homólogo en A7S de d3_equivalence.json). El inicio de la rutina se toma como el
`push {..., lr}` más cercano anterior a cada referencia PIC a la cadena (hasta 0x600 B); se compara con el mismo motor que D3
(`fw.closure`, profundidad 3). Salida: d6_homologos.json. Límite: el inicio por heurística de prólogo puede no ser el de la función."""
import json
import re
import sys
from pathlib import Path

import d3_equivalence as d3
import dual_scan
import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
import rawfw

CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
BACK = 0x600


def prologue_before(blob: bytes, addr: int) -> int | None:
    for a in range(addr, max(addr - BACK, pic.BASE), -2):
        i = next(CS.disasm(blob[a - pic.BASE:a - pic.BASE + 4], a, count=1), None)
        if i and i.mnemonic.startswith("push") and re.search(r"\blr\b", i.op_str):
            return a
    return None


def main() -> None:
    A, C = pic.load("a6000"), pic.load("a7s")
    idx = {"a6000": dual_scan.index(pic.pic_refs(A)), "a7s": dual_scan.index(pic.pic_refs(C))}
    libs = {"a6000": rawfw.RawLib("A6000"), "a7s": rawfw.RawLib("A7S")}
    rows = [r for r in json.loads((d3.OUT).read_text()) if not r["a6000_funciones"] and r["modelos"]["a7s"]["homologos"]]
    out = []
    for r in rows:
        core, vaddr, text = next(t for t in _traces(r["ficha"]) if t[0].startswith(r["nucleo"][:30]))
        sa = d3.refs(idx["a6000"], vaddr, len(text))
        sb = sorted({r2 for off in d3.find_all(C, core) for r2 in d3.refs(idx["a7s"], off, len(core) + 40)})
        fa = sorted({p for s in sa if (p := prologue_before(A, s))})
        fb = sorted({p for s in sb if (p := prologue_before(C, s))})
        best = None
        for pa in fa:
            for pb in fb:
                c = d3.compare(libs["a6000"], libs["a7s"], pa, pb)
                c.update({"a6000": hex(pa), "a7s": hex(pb)})
                if best is None or (c["root_igual_salvo_lineas"], -c["con_diferencias"]) > (best["root_igual_salvo_lineas"], -best["con_diferencias"]):
                    best = c
        out.append({"ficha": r["ficha"], "nucleo": r["nucleo"], "a6000_inicios": list(map(hex, fa)), "a7s_inicios": list(map(hex, fb)), "mejor": best})
    (Path(__file__).with_name("d6_homologos.json")).write_text(json.dumps(out, indent=1) + "\n")
    for o in out:
        print(o["ficha"], o["nucleo"][:30], o["a6000_inicios"][:3], o["a7s_inicios"][:3], o["mejor"] and (o["mejor"]["root_igual_salvo_lineas"], o["mejor"]["len"]))


def _traces(ficha: str) -> list[tuple[str, int, str]]:
    out = []
    for p in sorted((ROOT / "analysis").glob(f"{ficha.lower()}_*/*.json")):
        d = json.loads(p.read_text())
        for t in d.get("trace_strings", []):
            core = (t.get("core_text") or t["text"].removeprefix(d.get("prefix", ""))).strip()
            out.append((core, int(t["vaddr"], 16), t["text"]))
    return out


if __name__ == "__main__":
    main()
