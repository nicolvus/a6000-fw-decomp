"""E10: quién carga la dirección de cada vtable de libObj.so (A6000), es decir, qué funciones construyen objetos de cada clase.
Evaluador lineal por función (e17_listas.step) con `ldr rX,[rA,rB]` sobre constantes (GOT) leído del ELF; una vtable se detecta
cuando algún registro vale su base (la GOT guarda la base y el constructor suma 8; posición del typeinfo − 4). Salida: e10_vtable_refs.json {clase: [funciones]}.
shortcut: lineal, sin seguir saltos ni punteros guardados; una clase creada por una fábrica en datos no aparece."""
import json
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
sys.path.insert(0, str(Path(__file__).parent))
from e10_topologias import OWNERS, class_index
from e17_listas import Frame, call_owners, step
from fw import Lib


def vtable_points(lib: Lib) -> dict[int, str]:
    """{base de la vtable: clase}, a partir de la palabra typeinfo en .data.rel.ro (vtable+4)."""
    sec = lib.e.sections[".data.rel.ro"]
    blob = lib.e.read(sec[3], sec[5])
    words = struct.unpack(f"<{len(blob) // 4}I", blob[: len(blob) // 4 * 4])
    ti = {int(k, 16): v["name"] for k, v in OWNERS["classes"].items()}
    return {sec[3] + 4 * k - 4: ti[w] for k, w in enumerate(words) if w in ti and k and words[k - 1] < 0x100}


def scan(lib: Lib, cs: Cs, points: dict[int, str]) -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = {}
    cs.detail = True
    for func in lib.starts[:-1]:
        fr = Frame()
        seen = set()
        for i in cs.disasm(lib.e.read(func, lib.fend(func) - func), func):
            m = re.fullmatch(r"(r\w+), \[(r\w+), (r\w+)\]", i.op_str) if i.mnemonic in ("ldr", "ldr.w") else None
            if m:
                a, b = fr.reg.get(m[2]), fr.reg.get(m[3])
                if a and b and a[0] == b[0] == "c":
                    addr = (a[1] + b[1]) & 0xFFFFFFFF
                    try:
                        fr.reg[m[1]] = ("c", lib.e.u32(addr))
                    except (ValueError, KeyError, IndexError, struct.error):
                        fr.reg[m[1]] = None
                else:
                    fr.reg[m[1]] = None
            else:
                step(fr, lib, i)
                if i.mnemonic.startswith("ldr") and "[pc" in i.op_str:  # literal sin `add pc` posterior = desplazamiento de la GOT
                    dest = i.op_str.split(",")[0].strip()
                    if dest in fr.pend:
                        fr.reg[dest] = ("c", fr.pend[dest])
            for r in fr.reg.values():
                if r and r[0] == "c" and r[1] in points and (r[1], i.address) not in seen:
                    seen.add((r[1], i.address))
                    found.setdefault(points[r[1]], []).append({"funcion": hex(func), "sitio": hex(i.address)})
    return found


def main() -> None:
    lib = Lib("A6000")
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    points = vtable_points(lib)
    found = scan(lib, cs, points)
    starts, table = class_index()
    owners = call_owners(lib, cs, starts, table)
    for refs in found.values():
        for r in refs:
            r["propietario"] = owners[int(r["funcion"], 16)][0]
    (Path(__file__).with_name("e10_vtable_refs.json")).write_text(json.dumps({"vtables": len(points), "clases_con_constructor": len(found), "refs": found}, indent=1) + "\n")
    print(len(points), "vtables;", len(found), "clases con referencia", file=sys.stderr)


if __name__ == "__main__":
    main()
