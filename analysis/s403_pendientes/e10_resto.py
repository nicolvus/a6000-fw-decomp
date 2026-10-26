"""E10 (resto): alcanzabilidad de los dos escritores de EffectInternalMode=1, StsId de las filas YC y liberación en StillConverter, sobre libObj.so (A6000).
Lee e10_vtable_refs.json / e10_topologias.json / e17_listas.json y recorre las llamadas directas (bl/b.w) del .text.
shortcut: llamadas directas solamente; una clase creada por puntero a función o por fábrica en datos no aparece como llamador. Salida: e10_resto.json."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
sys.path.insert(0, str(Path(__file__).parent))
from e10_topologias import class_index
from e17_listas import SHOOTING, call_owners, table_rows
from fw import Lib

HERE = Path(__file__).parent
WRITERS = {"0x154990": "OBJEFFECT::ExecCmdAppFaderEfctEndEvt", "0x1e069c": "OBJEFFECT::SequencePinDeliverBase"}
CONVERTER = (0x91E000, 0x920400)  # StillConverter / MprAcsr (cadena `[StillConverter] Receive CBID_ENCODE_STILL` en 0x91eb60)
YC_ROWS = (0x2A, 0xB4)


def direct_calls(lib: Lib, cs: Cs) -> dict[int, list[int]]:
    sec = lib.e.sections[".text"]
    calls: dict[int, list[int]] = defaultdict(list)
    for i in cs.disasm(lib.e.read(sec[3], sec[5]), sec[3]):
        if i.mnemonic in ("bl", "b.w", "blx") and i.op_str.startswith("#"):
            calls[int(i.op_str[1:], 16) & ~1].append(i.address)
    return calls


def writer_reach(lib: Lib, calls: dict, owners: dict, refs: dict) -> dict:
    out = {}
    for writer, cls in WRITERS.items():
        users = sorted({int(r["funcion"], 16) for r in refs[cls]})  # funciones que cargan la vtable (constructor, destructor, creador)
        callers = {hex(u): sorted({str(owners[lib.fstart(a)][0]) for a in calls.get(u, [])}) for u in users}
        out[writer] = {"clase": cls, "funciones_con_vtable": [hex(u) for u in users], "clases_llamadoras": callers}
    return out


def sts_usage(lib: Lib, owners: dict) -> dict:
    rows = table_rows(lib)
    e10, e17 = (json.loads((HERE / n).read_text()) for n in ("e10_topologias.json", "e17_listas.json"))

    def ids(lst: list) -> set[int]:
        flat = [y for x in lst for y in (x if isinstance(x, list) else [x]) if y != "?"]
        return {int(y, 16) if isinstance(y, str) else y for y in flat} - {0, 0xFFFFFFFF}

    use: dict[str, set[int]] = defaultdict(set)
    for r in e10["filas"]:
        cls = owners[int(r["funcion"], 16)][0]
        if r["lista"] is not None and r["tipo"] == "create" and cls in SHOOTING:
            use[cls] |= ids(r["lista"])
    for e in e17["sitios"]:
        lists = [e["lista"]] if "lista" in e else [o["lista"] for o in e.get("origenes", []) if isinstance(o["lista"], list)]
        if e["tipo"] == "create" and e["clase"] in SHOOTING:
            for lst in lists:
                use[e["clase"]] |= ids(lst)
    return {"filas_con_StsId_6": [hex(k) for k, r in enumerate(rows) if r[1] == 6], "yc": {hex(y): rows[y][1] for y in YC_ROWS},
            "StsId_por_modelo_de_disparo": {c: sorted({rows[x][1] for x in v if x < len(rows)}) for c, v in sorted(use.items())}}


def converter_frees(lib: Lib, cs: Cs) -> dict:
    found = {}
    for f in (s for s in lib.starts if CONVERTER[0] <= s < CONVERTER[1]):
        hits = [lib.name(int(i.op_str[1:], 16)) for i in cs.disasm(lib.e.read(f, lib.fend(f) - f), f)
                if i.mnemonic in ("bl", "blx", "b.w") and i.op_str.startswith("#")]
        frees = [n for n in hits if re.search(r"DmmFree|DmmCloseAndFree|BufFree", n)]
        if frees:
            found[hex(f)] = sorted(set(frees))
    return found


def main() -> None:
    lib = Lib("A6000")
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    starts, table = class_index()
    owners = call_owners(lib, cs, starts, table)
    refs = json.loads((HERE / "e10_vtable_refs.json").read_text())["refs"]
    out = {"escritores": writer_reach(lib, direct_calls(lib, cs), owners, refs), "StsId": sts_usage(lib, owners),
           "StillConverter_libera": converter_frees(lib, cs)}
    (HERE / "e10_resto.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["StsId"]), file=sys.stderr)


if __name__ == "__main__":
    main()
