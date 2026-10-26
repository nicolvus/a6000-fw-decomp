"""E10: censo de las llamadas a createTopology/destroyTopology de libObj.so (A6000): lista de filas por sitio y modelo propietario.
Responde con bytes originales quién crea las filas que llevan YC o STILL_DATA al ObjStillRecorder (0x2a, 0xb4, 0x8, 0xb0, 0xb1).
Evaluador lineal desde el inicio de función hasta el sitio (sin seguir saltos): una lista no resuelta se anota como tal, no como vacía.
shortcut: listas en heap o construidas en otro marco quedan `None`; el propietario por cercanía (vtable previa) es heurístico. Salida: e10_topologias.json."""
import bisect
import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
from fw import Lib

CREATE, DESTROY = 0x420630, 0x420656
INTERES = {0x2A: "YC Effect→StillRecorder", 0xB4: "YC obj53→StillRecorder", 0x08: "STILL_DATA Camera→StillRecorder",
           0xB0: "STILL_DATA Camera→obj53", 0xB1: "STILL_DATA obj53→StillRecorder"}
OWNERS = json.loads((ROOT / "analysis/session20/evidence/libobj-rtti-vtables.json").read_text())


def class_index() -> tuple[list[int], dict[int, str]]:
    table: dict[int, str] = {}
    for info in OWNERS["classes"].values():
        for vt in info["vtables"]:
            for m in vt["methods"]:
                if m.get("entry"):
                    table.setdefault(int(m["entry"], 16) & ~1, info["name"])
    return sorted(table), table


def owner(starts: list[int], table: dict[int, str], func: int) -> tuple[str | None, str]:
    if func in table:
        return table[func], "vtable"
    i = bisect.bisect_right(starts, func) - 1
    return (table[starts[i]], "cercania") if i >= 0 and func - starts[i] < 0x1000 else (None, "ninguno")


def evaluate(lib: Lib, cs: Cs, func: int, site: int) -> list[int] | None:
    regs: dict[str, object] = {}
    stack: dict[int, int | None] = {}
    pend: dict[str, int] = {}
    cs.detail = True
    for i in cs.disasm(lib.e.read(func, site - func), func):
        m, o = i.mnemonic, i.op_str
        parts = [p.strip() for p in o.split(",")]
        if m in ("movs", "mov", "mov.w", "movw") and len(parts) == 2:
            imm = re.fullmatch(r"#(-?(?:0x)?[0-9a-f]+)", parts[1])
            regs[parts[0]] = int(imm[1], 0) if imm else regs.get(parts[1])
        elif m.startswith("ldr") and "[pc" in o:
            pend[parts[0]] = lib.e.u32(((i.address + 4) & ~3) + i.operands[1].mem.disp)
            regs[parts[0]] = None
        elif m == "add" and parts[-1] == "pc" and parts[0] in pend:
            regs[parts[0]] = (pend[parts[0]] + i.address + 4) & 0xFFFFFFFF
        elif m in ("add", "add.w") and len(parts) == 3 and parts[1] == "sp":
            regs[parts[0]] = ("SP", int(parts[2][1:], 0))
        elif m.startswith("str") and "[sp" in o:
            off = re.search(r"#(0x[0-9a-f]+|\d+)\]", o)
            val = regs.get(parts[0])
            stack[int(off[1], 0) if off else 0] = val if isinstance(val, int) else None
        elif m.startswith(("bl", "blx")):
            for r in ("r0", "r1", "r2", "r3"):
                regs[r] = None
        elif parts and parts[0] in regs and not m.startswith(("cmp", "tst", "str", "b")):
            regs[parts[0]] = None
    r2 = regs.get("r2")
    if isinstance(r2, tuple):
        out: list[int] = []
        for k in range(16):
            slot = stack.get(r2[1] + 4 * k)
            if slot is None:
                return None
            out.append(slot)
            if slot == 0:
                return out
        return None
    if isinstance(r2, int) and r2 > 0x1000:
        words: list[int] = []
        for k in range(32):
            word = lib.e.u32(r2 + 4 * k)
            words.append(word)
            if word == 0:
                return words
    return None


def static_lists(lib: Lib, cs: Cs, text: tuple[int, int]) -> list[dict]:
    """Listas `u32…0` (ids de fila 1..210) a las que apunta una pareja `ldr rX,[pc]`+`add rX,pc` y que contienen un id de interés."""
    cs.detail = False
    spans = [(s[3], s[3] + s[5]) for n, s in lib.e.sections.items() if n in (".rodata", ".data.rel.ro", ".data")]
    pend: dict[str, int] = {}
    found: dict[tuple[int, int], dict] = {}
    for i in cs.disasm(lib.e.read(*text), text[0]):
        m, o = i.mnemonic, i.op_str
        if m.startswith("ldr") and "[pc, #" in o:
            r = o.split(",")[0]
            disp = re.search(r"#(-?(?:0x)?[0-9a-f]+)\]", o)
            assert disp
            pend[r] = lib.e.u32(((i.address + 4) & ~3) + int(disp[1], 0))
        elif m == "add" and o.endswith(", pc") and o.split(",")[0] in pend:
            a = (pend.pop(o.split(",")[0]) + i.address + 4) & 0xFFFFFFFF
            if any(lo <= a < hi for lo, hi in spans) and a % 4 == 0:
                vals = []
                for k in range(24):
                    v = lib.e.u32(a + 4 * k)
                    vals.append(v)
                    if v == 0 or v > 210:
                        break
                if vals[-1] == 0 and len(vals) >= 2 and INTERES.keys() & set(vals):
                    found.setdefault((a, lib.fstart(i.address)), {"lista": [hex(v) for v in vals], "direccion": hex(a),
                                                                  "funcion": hex(lib.fstart(i.address)), "sitio": hex(i.address)})
    return sorted(found.values(), key=lambda x: x["sitio"])


def main() -> None:
    lib = Lib("A6000")
    sec = lib.e.sections[".text"]
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    starts, table = class_index()
    sites = []
    for i in cs.disasm(lib.e.read(sec[3], sec[5]), sec[3]):
        if i.mnemonic in ("bl", "b.w") and i.op_str.startswith("#") and (int(i.op_str[1:], 16) & ~1) in (CREATE, DESTROY):
            sites.append((i.address, int(i.op_str[1:], 16) & ~1))
    rows = []
    for site, target in sites:
        func = lib.fstart(site)
        cls, how = owner(starts, table, func)
        lst = evaluate(lib, cs, func, site)
        rows.append({"sitio": hex(site), "funcion": hex(func), "tipo": "create" if target == CREATE else "destroy",
                     "clase": cls, "clase_por": how, "lista": None if lst is None else [hex(v) for v in lst]})
    resumen: dict[str, dict] = {hex(k): {"sentido": v, "sitios": [{"sitio": r["sitio"], "clase": r["clase"], "tipo": r["tipo"]}
                                                    for r in rows if r["lista"] and hex(k) in r["lista"]]}
               for k, v in INTERES.items()}
    estaticas = static_lists(lib, cs, (sec[3], sec[5]))
    for e in estaticas:
        e["clase"], e["clase_por"] = owner(starts, table, int(e["funcion"], 16))
    out = {"listas_estaticas_con_ids_de_interes": estaticas, "sitios": len(rows), "con_lista": sum(r["lista"] is not None for r in rows), "interes": resumen, "filas": rows}
    (Path(__file__).with_name("e10_topologias.json")).write_text(json.dumps(out, indent=1) + "\n")
    for e in estaticas:
        print(e["sitio"], e["clase"], e["clase_por"], e["lista"])
    print(out["sitios"], "sitios;", out["con_lista"], "con lista resuelta")
    for k, v in resumen.items():
        print(k, v["sentido"], [(s["sitio"], s["clase"], s["tipo"]) for s in v["sitios"]])


if __name__ == "__main__":
    main()
