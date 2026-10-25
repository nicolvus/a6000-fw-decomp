"""Herramientas estáticas Thumb para libObj.so (A6000/A7S): flujo normalizado, cierre por parejas y evaluador mínimo."""

import bisect
import difflib
import re
import struct
import sys
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s380_libobj_map"))
from followup_audit import plt_names, section_bytes, symbols
from recordimage_audit import LIBRARIES, Elf32

NORET = {"__cxa_end_cleanup", "__cxa_throw", "abort", "__assert_fail", "exit", "_Unwind_Resume", "__cxa_rethrow"}
COND = r"b(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)(\.w|\.n)?"


class Lib:
    """Vista ligera de una libObj: inicios por .ARM.exidx, PLT y GOT; sin índices pesados."""

    def __init__(self, model: str):
        self.model = model
        self.e = Elf32(LIBRARIES[model])
        self.plt = plt_names(self.e)
        self.syms = {v & ~1: n for n, v, _, _ in symbols(self.e, ".dynsym", ".dynstr") if n and v}
        section = self.e.sections[".ARM.exidx"]
        starts = []
        for delta in range(0, section[5], 8):
            place = section[3] + delta
            relative = self.e.u32(place) & 0x7FFFFFFF
            if relative & 0x40000000:
                relative -= 0x80000000
            starts.append((place + relative) & ~1)
        self.starts = sorted(set(starts))
        rels = {}
        sym = symbols(self.e, ".dynsym", ".dynstr")
        for offset, info in struct.iter_unpack("<II", section_bytes(self.e, ".rel.dyn")):
            if info & 255 in (2, 21, 22):
                rels[offset] = sym[info >> 8][0]
        self.gotmap = rels
        self.gotbase = self.e.sections[".got"][3]

    def fstart(self, va: int) -> int:
        return self.starts[bisect.bisect_right(self.starts, va) - 1]

    def fend(self, va: int) -> int:
        return self.starts[bisect.bisect_right(self.starts, va)]

    def name(self, va: int) -> str:
        va &= ~1
        return self.plt.get(va) or self.syms.get(va) or ""

    def cstr(self, va: int):
        try:
            offset = self.e.offset(va)
            raw = self.e.data[offset:self.e.data.index(b"\0", offset)]
        except ValueError:
            return None
        return raw.decode() if 2 <= len(raw) < 200 and all(32 <= c < 127 or c in (9, 10) for c in raw) else None

    def section_of(self, va: int):
        return next((n for n, s in self.e.sections.items()
                     if s[3] <= va < s[3] + s[5] and n in (".bss", ".data", ".data.rel.ro", ".rodata", ".text")), None)


def reachable(lib: Lib, start: int, end: int) -> dict:
    """Descenso recursivo desde start: solo instrucciones alcanzables; descarta pools, tablas de salto y datos."""
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True
    seen, work = {}, [start]
    while work:
        pc, it = work.pop(), 0
        cmp_limit: int | None = None
        while start <= pc < end and pc not in seen:
            ins = next(decoder.disasm(lib.e.read(pc, 4), pc, count=1), None)
            if ins is None:
                break
            seen[pc] = ins
            mnemonic, ops, nxt = ins.mnemonic, ins.op_str, pc + ins.size
            conditional, it = it > 0, max(it - 1, 0)
            if re.fullmatch(r"it[te]{0,3}", mnemonic):
                it, pc = len(mnemonic), nxt
                continue
            if mnemonic == "cmp" and "#" in ops:
                cmp_limit = int(ops.split("#")[1], 0)
            if mnemonic in ("b", "b.w") and ops.startswith("#"):
                work.append(int(ops[1:], 16))
                if not conditional:
                    break
            elif re.fullmatch(COND, mnemonic) and ops.startswith("#"):
                work.append(int(ops[1:], 16))
            elif mnemonic in ("cbz", "cbnz"):
                work.append(int(ops.rsplit("#", 1)[1], 16))
            elif mnemonic in ("tbb", "tbh"):
                step = 1 if mnemonic == "tbb" else 2
                for k in range((cmp_limit or 0) + 1):
                    raw = lib.e.read(nxt + k * step, step)
                    work.append(nxt + 2 * (raw[0] if step == 1 else struct.unpack("<H", raw)[0]))
                break
            elif mnemonic in ("bl", "blx") and ops.startswith("#"):
                if lib.name(int(ops[1:], 16)) in NORET:
                    break
            elif ((mnemonic.startswith("pop") and "pc" in ops) or (mnemonic == "bx" and ops == "lr")
                  or (mnemonic.startswith("ldr") and ops.startswith("pc,"))) and not conditional:
                break
            pc = nxt
    return seen


def normalize(lib: Lib, start: int, end: int, targets: list | None = None) -> list[tuple[Any, ...]]:
    """Flujo comparable entre modelos: llamadas por nombre, cadenas PIC por texto, punteros GOT por símbolo/sección."""
    out: list[tuple[Any, ...]] = []
    pending: dict[str, tuple[int, int]] = {}
    for ins in (v for _, v in sorted(reachable(lib, start, end).items())):
        mnemonic, ops = ins.mnemonic, ins.op_str
        if mnemonic in ("bl", "blx") and ops.startswith("#"):
            target = int(ops[1:], 16)
            out.append(("call", lib.name(target) or "LOCAL"))
            if targets is not None and not lib.name(target):
                targets.append(target)
        elif mnemonic.startswith("ldr") and "[pc," in ops:
            pool = ((ins.address + 4) & ~3) + ins.operands[1].mem.disp
            value = lib.e.u32(pool)
            reg = ops.split(",")[0]
            slot = (lib.gotbase + value) & 0xFFFFFFFF
            symbol = lib.gotmap.get(slot)
            kind = None
            if not symbol and lib.e.sections[".got"][3] <= slot < lib.e.sections[".got"][3] + lib.e.sections[".got"][5]:
                kind = lib.section_of(lib.e.u32(slot))
                if kind == ".text" and targets is not None:
                    targets.append(lib.e.u32(slot) & ~1)
            pending[reg] = (value, len(out))
            out.append(("ldrlit", reg, ("GOT", symbol) if symbol else ("GOTLOCAL", kind) if kind
                        else value if value < 0x100000 or value >= 0x10000000 else "ADDR"))
        elif mnemonic == "add" and ops.endswith(", pc") and ops.split(",")[0] in pending:
            reg = ops.split(",")[0]
            value, index = pending[reg]
            out[index] = ("ldrlit", reg, "PCREL")
            text = lib.cstr((value + ins.address + 4) & 0xFFFFFFFF)
            out.append(("picref", reg, text or "PTR"))
        elif re.fullmatch(rf"((b|bl|blx)(\.w|\.n)?|{COND}|cbz|cbnz)", mnemonic) and re.search(r"#0x[0-9a-f]+$", ops):
            target = int(ops.rsplit("#", 1)[1], 16)
            name = lib.name(target) if mnemonic in ("b", "b.w") else ""
            tail = mnemonic in ("b", "b.w") and not name and not (start <= target < end)
            out.append((mnemonic, ops.rsplit("#", 1)[0], name or ("TAIL_LOCAL" if tail else ("rel", target - start))))
            if tail and targets is not None:
                targets.append(target)
        else:
            out.append((mnemonic, ops))
    return out


def is_line_only(a, b) -> bool:
    """movw rN,#línea: el número de línea de __LINE__ cambia entre compilaciones sin cambiar la lógica."""
    return (len(a) == len(b) and all(x[0] in ("movw", "mov.w") and y[0] in ("movw", "mov.w")
                                    and x[1].split(",")[0] == y[1].split(",")[0] for x, y in zip(a, b)))


def residue(na: list, nb: list) -> list:
    matcher = difflib.SequenceMatcher(None, na, nb, autojunk=False)
    return [(i1, j1, na[i1:i2][:3], nb[j1:j2][:3]) for tag, i1, i2, j1, j2 in matcher.get_opcodes()
            if tag != "equal" and not is_line_only(na[i1:i2], nb[j1:j2])]


def closure(a: Lib, b: Lib, pa: int, pb: int, max_depth: int = 12, seen=None, result=None) -> dict:
    """Compara A6000/A7S desde (pa,pb) y recursivamente los destinos locales emparejados por posición."""
    seen = set() if seen is None else seen
    result = {} if result is None else result
    if (pa, pb) in seen or max_depth < 0:
        return result
    seen.add((pa, pb))
    ta: list[int] = []
    tb: list[int] = []
    na, nb = normalize(a, pa, a.fend(pa), ta), normalize(b, pb, b.fend(pb), tb)
    result[(pa, pb)] = {"len": (len(na), len(nb)), "identical": na == nb, "residue": residue(na, nb),
                        "calls": (len(ta), len(tb))}
    if len(ta) == len(tb):
        for x, y in zip(ta, tb):
            closure(a, b, x, y, max_depth - 1, seen, result)
    return result


def run_wrapper(lib: Lib, start: int, arg: int, limit: int = 120):
    """Evalúa un wrapper corto (new/memset + stores de constantes al búfer). No es emulación del firmware."""
    regs: dict[str, Any] = {f"r{i}": None for i in range(13)}
    regs["r2"] = arg
    buf: dict[int, Any] = {}
    calls: list[str] = []
    flags: tuple[Any, Any] | None = None
    pc = start
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True

    def val(x):
        x = x.strip()
        return int(x[1:], 0) if x.startswith("#") else regs.get(x)

    for _ in range(limit):
        ins = next(decoder.disasm(lib.e.read(pc, 4), pc, count=1), None)
        if ins is None:
            break
        m, o, nxt = ins.mnemonic, ins.op_str, pc + ins.size
        if m in ("movs", "mov", "mov.w", "movw") and "," in o:
            a, b = (t.strip() for t in o.split(",", 1))
            regs[a] = val(b) if a in regs else None
        elif m in ("adds", "add", "add.w", "subs", "sub", "sub.w"):
            p = [t.strip() for t in o.split(",")]
            p = [p[0], p[0], p[1]] if len(p) == 2 else p
            x, y = val(p[1]), val(p[2])
            sign = 1 if m.startswith("add") else -1
            regs[p[0]] = (x + sign * y) & 0xFFFFFFFF if isinstance(x, int) and isinstance(y, int) else None
        elif m == "cmp":
            a, b = (t.strip() for t in o.split(","))
            flags = (val(a), val(b))
        elif m.startswith("str"):
            mm = re.match(r"(\w+), \[(\w+)(?:, #(0x[0-9a-f]+|\d+))?\]", o)
            if mm and regs.get(mm.group(2)) == ("BUF",):
                buf[int(mm.group(3) or "0", 0)] = regs.get(mm.group(1))
        elif m.startswith("ldr") and "[pc," in o:
            regs[o.split(",")[0]] = lib.e.u32(((ins.address + 4) & ~3) + ins.operands[1].mem.disp)
        elif m in ("bl", "blx") and o.startswith("#"):
            name = lib.name(int(o[1:], 16))
            calls.append(name or hex(int(o[1:], 16)))
            for k in ("r0", "r1", "r2", "r3"):
                if not (name == "memset" and k == "r0"):
                    regs[k] = None
            if name == "_Znwj":
                regs["r0"] = ("BUF",)
            if name not in ("_Znwj", "memset"):
                break
        elif m in ("beq", "bne", "bcs", "bhi", "bls", "blt", "bge", "ble", "bgt", "bcc", "blo", "bhs"):
            if not flags or not all(isinstance(v, int) for v in flags):
                return None, buf, calls
            x, y = flags
            if {"beq": x == y, "bne": x != y, "bcs": x >= y, "bhs": x >= y, "bcc": x < y, "blo": x < y,
                "bhi": x > y, "bls": x <= y, "blt": x < y, "bge": x >= y, "ble": x <= y, "bgt": x > y}[m]:
                nxt = int(o[1:], 16)
        elif m in ("b", "b.w") and o.startswith("#"):
            nxt = int(o[1:], 16)
        elif m.startswith("pop") or m == "bx":
            break
        pc = nxt
    return True, buf, calls
