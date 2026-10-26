"""E17: listas de createTopology/destroyTopology que e10_topologias.py no resolvió (151 de 300 sitios) de libObj.so (A6000).
Evaluador simbólico lineal por función: registros = ('c',v) | ('sp',off) | ('ret',callee,descriptor) | ('mem',base,off) | None.
Fila dinámica: `0x420688`→`0x415e8c` busca la primera fila de la tabla de 210 (0x20 bytes) cuyo descriptor coincide en [0],[1],[2..4],[5..7].
Miembros: r2 cargado de `[this,#off]` → la lista se guardó antes en otro método de la clase (se rastrea la tienda).
shortcut: lineal sin seguir saltos (una asignación bajo condicional cuenta como la última lineal); descriptores con campos dinámicos dan un conjunto de filas candidatas, no una fila. Salida: e17_listas.json."""
import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
sys.path.insert(0, str(Path(__file__).parent))
from e10_topologias import class_index, owner
from fw import Lib

SHOOTING = ("ModelStillRec", "ModelBootEE", "ModelBootEE3D", "ModelMovieRec", "ModelCamera", "ModelScalarCameraPatch",
            "ModelScalarStillRecPatch", "ModelStillIntervalRec")
YC_ROWS = ("0x2a", "0xb4")
RESOLVED = ("pila", "heap", "miembro_proyectado", "estatica", "nula")
FIND, FIND_IMPL, ROW_TABLE, ROWS = 0x420688, 0x415E8C, 0xCC4210, 210
Sym = tuple | None
MAX_CAND = 16
END = (0, 0xFFFFFFFF)  # fin de lista: 0, o -1 en las listas estáticas de ModelHighlightSave


# Motivo por el que una lista sin resolver no se sigue. shortcut: la relevancia se decide por la clase propietaria (vtable/llamadores/cercanía), no por alcanzabilidad desde el disparo.
DESCARTE = {
    "heap_incompleta": "lista armada en bucle desde el vector de registros de this+0x9c, rellenado fuera de la función; sin valor estático",
    "heap_dinamica": "lista armada en bucle desde datos de ejecución; sin valor estático",
    "sin_valor": "r2 depende de una rama que el evaluador lineal no sigue",
    "miembro": "puntero a lista guardado en un miembro sin tienda estática en la clase",
    "otro": "lista de un std::vector del objeto (this+0x84), rellenado en ejecución",
}


def parse_imm(text: str) -> int | None:
    m = re.fullmatch(r"#(-?(?:0x)?[0-9a-f]+)", text.strip())
    return int(m[1], 0) if m else None


class Frame:
    """Estado simbólico: registros y memoria de pila (clave = desplazamiento sobre el SP de entrada del marco)."""

    def __init__(self) -> None:
        self.reg: dict[str, Sym] = {f"r{i}": ("arg", i) for i in range(4)}
        self.reg["sp"] = ("sp", 0)
        self.mem: dict[tuple, Sym] = {}
        self.pend: dict[str, int] = {}
        self.heap = 0

    def val(self, token: str) -> Sym:
        imm = parse_imm(token)
        return ("c", imm) if imm is not None else self.reg.get(token.strip())

    @staticmethod
    def key(base: Sym, off: int) -> tuple | None:
        if base and base[0] == "sp":
            return ("s", base[1] + off)
        return ("h", base[1], base[2] + off) if base and base[0] == "heap" else None

    def store(self, base: Sym, off: int, value: Sym) -> None:
        if (k := self.key(base, off)) is not None:
            self.mem[k] = value

    def load(self, base: Sym, off: int) -> Sym:
        if (k := self.key(base, off)) is not None:
            return self.mem.get(k)
        return ("mem", base, off) if base else None

    def descriptor(self, base: Sym) -> list[Sym] | None:
        if base and base[0] == "sp":
            return [self.mem.get(("s", base[1] + 4 * k), ("c", 0)) for k in range(8)]  # memset previo a cero: lo no escrito es 0
        return None


def step(fr: Frame, lib: Lib, i) -> None:
    m, o = i.mnemonic, i.op_str
    p = [x.strip() for x in re.split(r",(?![^\[]*\])", o)]
    sp = fr.reg["sp"]
    imm_sp = parse_imm(p[-1])
    if sp is None and (m.startswith(("push", "pop")) or p[0] == "sp"):
        return  # el SP se perdió (p. ej. `mov sp, rX` con rX desconocido): sin seguimiento de pila hasta el final del marco
    if sp is None:
        pass
    elif m.startswith("push"):
        fr.reg["sp"] = ("sp", sp[1] - 4 * (o.count(",") + 1))
    elif m.startswith("pop"):
        fr.reg["sp"] = ("sp", sp[1] + 4 * (o.count(",") + 1))
    elif p[0] == "sp" and m in ("sub", "sub.w", "subs", "add", "add.w", "adds") and imm_sp is not None:
        fr.reg["sp"] = ("sp", sp[1] + (1 if m.startswith("add") else -1) * imm_sp)
    elif m.startswith("ldr") and "[pc" in o:
        fr.pend[p[0]] = lib.e.u32(((i.address + 4) & ~3) + i.operands[1].mem.disp)
        fr.reg[p[0]] = None
    elif m == "add" and p[-1] == "pc" and p[0] in fr.pend:
        fr.reg[p[0]] = ("c", (fr.pend[p[0]] + i.address + 4) & 0xFFFFFFFF)
    elif m in ("movs", "mov", "mov.w", "movw") and len(p) == 2:
        fr.reg[p[0]] = fr.val(p[1])
    elif m in ("add", "add.w", "adds") and len(p) in (2, 3):
        src, imm = (fr.val(p[1]), parse_imm(p[2])) if len(p) == 3 else (fr.val(p[0]), parse_imm(p[1]))
        base = src if src else None
        if base and imm is not None and base[0] in ("sp", "c"):
            fr.reg[p[0]] = (base[0], base[1] + imm)
        elif base and imm is not None and base[0] == "heap":
            fr.reg[p[0]] = ("heap", base[1], base[2] + imm)
        else:
            fr.reg[p[0]] = None
    elif m in ("subs", "sub", "sub.w") and len(p) in (2, 3) and p[0] != "sp":
        src, imm = (fr.val(p[1]), parse_imm(p[2])) if len(p) == 3 else (fr.val(p[0]), parse_imm(p[1]))
        fr.reg[p[0]] = ("c", src[1] - imm) if src and src[0] == "c" and imm is not None else None
    elif m.startswith("stm"):
        regs = re.search(r"\{(.*)\}", o)
        base = fr.reg.get(p[0].rstrip("!"))
        if regs:
            for k, r in enumerate(x.strip() for x in regs[1].split(",")):
                fr.store(base, 4 * k, fr.reg.get(r))
    elif m.startswith("str") and "[" in o:
        mem = re.search(r"\[(\w+)(?:, #(-?(?:0x)?[0-9a-f]+))?\]", o)
        if mem and m in ("str", "str.w", "strd"):
            fr.store(fr.reg.get(mem[1]), int(mem[2], 0) if mem[2] else 0, fr.reg.get(p[0]))
        elif mem:
            fr.store(fr.reg.get(mem[1]), int(mem[2], 0) if mem[2] else 0, None)
    elif m.startswith("ldr") and "[" in o:
        mem = re.search(r"\[(\w+)(?:, #(-?(?:0x)?[0-9a-f]+))?\]", o)
        fr.reg[p[0]] = fr.load(fr.reg.get(mem[1]), int(mem[2], 0) if mem and mem[2] else 0) if mem and m in ("ldr", "ldr.w") else None
    elif m.startswith(("bl", "blx")):
        target = int(o[1:], 16) & ~1 if o.startswith("#") else None
        desc = fr.descriptor(fr.reg.get("r0")) if target in (FIND, FIND_IMPL) else None
        if desc:
            ret: Sym = ("find", tuple(desc))
        elif target and lib.name(target) in ("_Znaj", "_Znwj"):
            fr.heap += 1
            ret = ("heap", fr.heap, 0)
        else:
            ret = ("ret", target)
        for r in ("r1", "r2", "r3"):
            fr.reg[r] = None
        fr.reg["r0"] = ret
    elif p and p[0] in fr.reg and not m.startswith(("cmp", "tst", "b", "cb", "push", "it")):
        fr.reg[p[0]] = None


def run(lib: Lib, cs: Cs, func: int, site: int) -> Frame:
    fr = Frame()
    cs.detail = True
    for i in cs.disasm(lib.e.read(func, site - func), func):
        step(fr, lib, i)
    return fr


def table_rows(lib: Lib) -> list[tuple[int, ...]]:
    import struct
    return [struct.unpack("<8I", lib.e.read(ROW_TABLE + 0x20 * k, 0x20)) for k in range(ROWS)]


def candidates(rows: list[tuple[int, ...]], desc: tuple) -> list[int]:
    """Filas cuya descripción coincide en los campos del descriptor que son constantes (los dinámicos son comodín)."""
    def ok(a: Sym, b: int) -> bool:
        return a is None or a[0] != "c" or a[1] == b
    return [k for k, row in enumerate(rows) if all(ok(desc[j], row[j]) for j in range(8))]


def fmt(lst: list) -> list:
    return [hex(x) if isinstance(x, int) else [hex(y) for y in x] if isinstance(x, list) else x for x in lst]


def read_list(lib: Lib, fr: Frame, rows: list[tuple[int, ...]], r2: Sym) -> tuple[list | None, str]:
    """(elementos, motivo). Elemento = id (int) o lista de filas candidatas (fila dinámica)."""
    if r2 is None:
        return None, "sin_valor"
    if r2[0] == "mem":
        return None, "miembro"
    if r2 == ("c", 0):
        return [], "nula"
    if r2[0] == "c" and r2[1] > 0x1000:
        out: list = []
        for k in range(32):
            w = lib.e.u32(r2[1] + 4 * k)
            out.append(w)
            if w in END:
                return out, "estatica"
        return None, "estatica_sin_fin"
    if r2[0] in ("sp", "heap"):
        out = []
        for k in range(16):
            slot = fr.mem.get(Frame.key(r2, 4 * k) or ())
            if slot is None:
                return None, f"{r2[0]}_incompleta"
            if slot[0] == "c":
                out.append(slot[1])
                if slot[1] in END:
                    return out, "pila" if r2[0] == "sp" else "heap"
            elif slot[0] == "find":
                cand = candidates(rows, slot[1])
                out.append(cand if len(cand) <= MAX_CAND else "?")  # descriptor casi comodín: no se informa
            else:
                return None, f"{r2[0]}_dinamica"
        return None, f"{r2[0]}_sin_fin"
    return None, "otro"


def call_owners(lib: Lib, cs: Cs, starts: list[int], table: dict[int, str]) -> dict[int, tuple[str | None, str]]:
    """Propietario por función: vtable > llamadores (todos los llamadores etiquetados dan la misma clase; 8 pasadas) > cercanía."""
    sec = lib.e.sections[".text"]
    callers: dict[int, set[int]] = {}
    for i in cs.disasm(lib.e.read(sec[3], sec[5]), sec[3]):
        if i.mnemonic in ("bl", "b.w") and i.op_str.startswith("#"):
            callers.setdefault(int(i.op_str[1:], 16) & ~1, set()).add(lib.fstart(i.address))
    label = {f: (c, "vtable") for f, c in table.items()}
    for _ in range(8):
        for f in lib.starts[:-1]:
            if f in label:
                continue
            cls = {label[c][0] for c in callers.get(f, ()) if c in label}
            if len(cls) == 1 and all(c in label for c in callers[f]):
                label[f] = (cls.pop(), "llamadores")
    return {f: label.get(f) or owner(starts, table, f) for f in lib.starts[:-1]}


def member_stores(lib: Lib, cs: Cs, rows: list, owners: dict, wanted: dict[str | None, set[int]]) -> dict:
    """{(clase, desplazamiento): [(función, sitio de la tienda, lista|motivo)]}: tiendas `str X,[this,#off]` en métodos de la clase.
    La lista se lee con el marco al final de la función: el puntero se guarda antes de rellenar el vector."""
    found: dict[tuple, list] = {}
    for func in lib.starts[:-1]:
        cls = owners[func][0]
        if cls is None or cls not in wanted:
            continue
        fr, pending = Frame(), []
        cs.detail = True
        for i in cs.disasm(lib.e.read(func, lib.fend(func) - func), func):
            if i.mnemonic in ("str", "str.w"):
                mem = re.search(r"\[(\w+)(?:, #(-?(?:0x)?[0-9a-f]+))?\]", i.op_str)
                off = int(mem[2], 0) if mem and mem[2] else 0
                val = fr.reg.get(i.op_str.split(",")[0].strip())
                if mem and fr.reg.get(mem[1]) == ("arg", 0) and off in wanted[cls] and val and val[0] in ("c", "sp", "heap") \
                        and (val[0] != "c" or val[1] > 0x1000):
                    pending.append((off, i.address, val))
            step(fr, lib, i)
        for off, addr, val in pending:
            lst, why = read_list(lib, fr, rows, val)
            found.setdefault((cls, off), []).append((hex(func), hex(addr), lst if lst is not None else why))
    return found


def main() -> None:
    lib = Lib("A6000")
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    starts, table = class_index()
    rows = table_rows(lib)
    prev = json.loads((Path(__file__).parent / "e10_topologias.json").read_text())["filas"]
    owners = call_owners(lib, cs, starts, table)
    out: list[dict] = []
    wanted: dict[str | None, set[int]] = {}
    for row in sorted((r for r in prev if r["lista"] is None), key=lambda r: int(r["sitio"], 16)):
        func, addr = int(row["funcion"], 16), int(row["sitio"], 16)
        row["clase"], row["clase_por"] = owners[func]
        fr = run(lib, cs, func, addr)
        r2 = fr.reg.get("r2")
        lst, motivo = read_list(lib, fr, rows, r2)
        entry = {"sitio": row["sitio"], "funcion": row["funcion"], "tipo": row["tipo"], "clase": row["clase"], "clase_por": row["clase_por"], "motivo": motivo}
        if motivo == "miembro" and r2 and r2[1] == ("arg", 0):
            entry["miembro"] = r2[2]
            wanted.setdefault(row["clase"], set()).add(r2[2])
        if lst is not None:
            entry["lista"] = fmt(lst)
        out.append(entry)
    stores = member_stores(lib, cs, rows, owners, wanted)
    for e in out:
        if "miembro" in e:
            src = stores.get((e["clase"], e["miembro"]), [])
            e["miembro"] = hex(e["miembro"])
            e["origenes"] = [{"funcion": a, "tienda": b, "lista": fmt(c) if isinstance(c, list) else c}
                             for a, b, c in src]
            e["motivo"] = "miembro_proyectado" if any(isinstance(c, list) for _, _, c in src) else "miembro_sin_origen"
    disparo: dict[str, dict] = {}
    for r in prev:
        if r["lista"] is None:
            continue
        cls = owners[int(r["funcion"], 16)][0]
        if cls in SHOOTING:
            d = disparo.setdefault(cls, {"sitios": 0, "resueltos": 0, "filas_yc": 0})
            d["sitios"] += 1
            d["resueltos"] += 1
            d["filas_yc"] += bool(set(YC_ROWS) & set(r["lista"]))
    for e in out:
        if e["clase"] in SHOOTING:
            d = disparo.setdefault(e["clase"], {"sitios": 0, "resueltos": 0, "filas_yc": 0})
            d["sitios"] += 1
            res = e["motivo"] in RESOLVED
            d["resueltos"] += res
            lists = [e["lista"]] if "lista" in e else [o["lista"] for o in e.get("origenes", []) if isinstance(o["lista"], list)]
            d["filas_yc"] += any(set(YC_ROWS) & set(x if isinstance(x, list) else [x]) for lst in lists for x in lst)
    for e in out:
        if e["motivo"] in RESOLVED + ("miembro_proyectado",):
            continue
        causa = e["origenes"][0]["lista"] if e.get("origenes") else e["motivo"]
        e["descarte"] = DESCARTE.get(causa, "miembro sin ninguna tienda estática en los métodos atribuidos a la clase")
        e["de_disparo"] = e["clase"] in SHOOTING
    resumen: dict[str, int] = {}
    for e in out:
        resumen[e["motivo"]] = resumen.get(e["motivo"], 0) + 1
    (Path(__file__).with_name("e17_listas.json")).write_text(json.dumps({"no_resueltos_e10": len(out), "motivos": resumen, "sin_resolver": sum("descarte" in e for e in out),
                                                                     "sin_resolver_de_disparo": sum(e.get("de_disparo", False) for e in out), "modelos_de_disparo": disparo, "sitios": out}, indent=1) + "\n")
    print(resumen, file=sys.stderr)


if __name__ == "__main__":
    main()
