"""Alcanzabilidad diferencial de las primitivas del motor según la compuerta `0x1fe66` (E24-05, solo lectura).

Intérprete abstracto mínimo sobre los bytes de `darwin_core.bin`: registros con constantes (literales, `movs`, `add/sub`
inmediatos), banderas tras `cmp/tst`, ramas condicionales resueltas cuando hay constantes y exploradas por ambos lados
si no. Los resultados de `0x1fe66`/`0x1f5a2` (compuerta) y `0x20c74` (tipo de bobina) los fija el escenario. Las
máquinas de estados (`0x1e150` fija la lista de ids; los motores `0x20184`/`0x1fca2` los ejecutan) se expanden con
las tablas reales (id→manejador). No ejecuta ni emula el firmware: es un cierre de alcanzabilidad con poda.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from capstone import arm
from dwn import BASE, Core

GATE_FUNCS = (0x1FE66, 0x1F5A2)
COIL_FUNC = 0x20C74
PRIMS = {0x1FE50: "motor=1", 0x1FE86: "motor=2", 0x1FEB6: "motor=3 (freno)", 0x1FE32: "motor=0 (apagar)"}
ERR = 0x16558
SELECT, RUN_OUTER, RUN_INNER, RUN_GENERIC = 0x1E150, 0x20184, 0x1FCA2, 0x1E33E
# máquinas: descriptor → (tablas id→manejador, id máximo/terminal)
OUTER, INNER = 0x29CF0, 0x297C0
INNER_TABLES = (0x29868, 0x29940, 0x29A18, 0x29AF0, 0x29BC8)
# utilidades sin relación con el motor (registro, memcpy/memset, sección crítica, temporizadores, log)
SKIP = {0x25290, 0x255A6, 0x25642, 0x25632, 0x5C9E, 0x5C88, 0x16ADC, 0x2020A, 0x93E6, 0x8E7E, 0x941E, 0x51C0, 0x51C6,
        0x51CC, 0x1E512, 0x1E50E, 0x25738, 0x6C0C, 0xA4AC, 0xA4C4}
REG = re.compile(r"^(r\d+|sb|sl|fp|ip|sp|lr)$")
NAMES = {"sb": "r9", "sl": "r10", "fp": "r11", "ip": "r12"}


def rn(x: str) -> str:
    return NAMES.get(x, x)


@dataclass
class Scenario:
    gate: int            # valor que devuelve 0x1fe66
    coil: int = 0        # valor que devuelve 0x20c74 (0 = parche tipo 0)
    name: str = ""


@dataclass
class Result:
    funcs: set = field(default_factory=set)            # entradas de función exploradas
    calls: list = field(default_factory=list)         # (llamante_func, sitio, destino, r0 const)
    lists: list = field(default_factory=list)         # (descriptor, puntero de lista)
    states: set = field(default_factory=set)          # (descriptor, id) ejecutables
    open_indirect: set = field(default_factory=set)   # sitios blx/bx reg no resueltos


class Reach:
    def __init__(self, core: Core | None = None):
        self.c = core or Core()

    # ---- lectura de tablas de máquinas -------------------------------------------------------
    def list_ids(self, ptr: int, terminal: int) -> list[int]:
        out = []
        for k in range(0x40):
            v = self.c.u8(ptr + k)
            out.append(v)
            if v >= terminal:
                break
        return out

    def handlers(self, table: int, ids: list[int], n: int) -> dict[int, int]:
        res = {}
        for k in range(n + 1):
            i, h = self.c.u32(table + 8 * k), self.c.u32(table + 8 * k + 4)
            if i in ids:
                res[i] = h & ~1
        return res

    # ---- exploración --------------------------------------------------------------------------
    def run(self, entry: int, sc: Scenario, r0: int | None = None, res: Result | None = None) -> Result:
        res = res or Result()
        self._func(entry, sc, res, (r0, None, None, None), set())
        return res

    def _expand(self, desc: int, ptr: int, sc, res, seen):
        if desc == OUTER:
            ids = self.list_ids(ptr, 0xA)
            tabs = [(0x29D0C, 0xA)]
        else:
            ids = self.list_ids(ptr, 0x1A)
            tabs = [(t, 0x1A) for t in INNER_TABLES]
        for t, n in tabs:
            for sid, h in self.handlers(t, ids, n).items():
                res.states.add((desc, sid))
                self._func(h, sc, res, (None,) * 4, seen)

    def _func(self, entry, sc: Scenario, res: Result, args, seen):
        key = (entry, args)
        if key in seen:
            return
        seen.add(key)
        res.funcs.add(entry)
        c = self.c
        regs0: dict[str, int | None] = {f"r{i}": None for i in range(13)}
        for i, v in enumerate(args):
            regs0[f"r{i}"] = v
        work = [(entry, tuple(sorted(regs0.items())), None)]
        done = set()
        n_it = 0
        while work:
            a, regs_t, flags = work.pop()
            if (a, regs_t, flags) in done or not (BASE <= a < c.end - 4):
                continue
            n_it += 1
            if n_it > 4000:
                res.open_indirect.add(("limite", entry))
                break
            done.add((a, regs_t, flags))
            regs: dict[str, int | None] = dict(regs_t)
            while True:
                ins = next(c.md.disasm(c.data[a - BASE:a - BASE + 4], a, 1), None)
                if ins is None:
                    break
                mn, ops, nxt = ins.mnemonic, ins.op_str, a + ins.size
                o = ins.operands
                lit = c.lit_of(ins)
                if mn in ("pop", "pop.w") and "pc" in ops or (mn == "bx" and ops == "lr"):
                    break
                if mn in ("bl", "blx") and o and o[0].type == arm.ARM_OP_IMM:
                    self._call(ins, o[0].imm, regs, sc, res, seen, entry)
                    regs = {k: (None if k in ("r0", "r1", "r2", "r3", "r12") else v) for k, v in regs.items()}
                    tgt = o[0].imm
                    if tgt in GATE_FUNCS:
                        regs["r0"] = sc.gate
                    elif tgt == COIL_FUNC:
                        regs["r0"] = sc.coil
                    a = nxt
                    flags = None
                    continue
                if mn in ("bl", "blx") or (mn == "bx" and ops != "lr"):
                    res.open_indirect.add(a)
                    regs = {k: (None if k in ("r0", "r1", "r2", "r3", "r12") else v) for k, v in regs.items()}
                    if mn == "bx":
                        break
                    a = nxt
                    continue
                if mn.startswith(("tbb", "tbh")):
                    n = None
                    for p in reversed(c.dis(a - 16, 16)):
                        if p.mnemonic == "cmp" and p.operands[1].type == arm.ARM_OP_IMM:
                            n = p.operands[1].imm + 1
                            break
                    if n is None:
                        res.open_indirect.add(a)
                    else:
                        for k in range(n):
                            off = c.u8(a + 4 + k) if mn.startswith("tbb") else c.u16(a + 4 + 2 * k)
                            work.append((a + 4 + 2 * off, tuple(sorted(regs.items())), None))
                    break
                if mn in ("cbz", "cbnz"):
                    r = rn(ops.split(",")[0])
                    v = regs.get(r)
                    tgt = o[-1].imm
                    take = None if v is None else ((v == 0) == (mn == "cbz"))
                    if take is None or take:
                        work.append((tgt, tuple(sorted(regs.items())), flags))
                    if take is None or not take:
                        a = nxt
                        continue
                    break
                m = re.match(r"^b(eq|ne|hs|lo|cs|cc|mi|pl|hi|ls|ge|lt|gt|le)(\.w)?$", mn)
                if m:
                    tgt = o[0].imm
                    take = self._cond(m.group(1), flags)
                    if take is None or take:
                        work.append((tgt, tuple(sorted(regs.items())), flags))
                    if take is None or not take:
                        a = nxt
                        continue
                    break
                if mn in ("b", "b.w") and o:
                    tgt = o[0].imm
                    if entry <= tgt < entry + 0x600 and tgt != entry and tgt not in (RUN_OUTER, RUN_INNER, RUN_GENERIC, SELECT):
                        a = tgt
                        continue
                    self._call(ins, tgt, regs, sc, res, seen, entry, tail=True)
                    break
                regs, flags = self._step(ins, regs, flags, lit)
                a = nxt

    def _call(self, ins, tgt, regs, sc, res, seen, caller, tail=False):
        res.calls.append((caller, ins.address, tgt, regs.get("r0")))
        if tgt in GATE_FUNCS or tgt == COIL_FUNC or tgt in PRIMS or tgt == ERR:
            return
        if tgt == SELECT and regs.get("r0") in (OUTER, INNER) and regs.get("r1") is not None:
            res.lists.append((regs["r0"], regs["r1"]))
        if tgt == RUN_OUTER:
            for d, p in [x for x in res.lists if x[0] == OUTER][-1:]:
                self._expand(d, p, sc, res, seen)
        if tgt == RUN_INNER or (tgt == RUN_GENERIC and regs.get("r0") == INNER):
            for d, p in [x for x in res.lists if x[0] == INNER][-1:]:
                self._expand(d, p, sc, res, seen)
        if tgt in SKIP or len(res.funcs) > 900:
            return
        args = (regs.get("r0"), None, None, None)
        self._func(tgt, sc, res, args, seen)

    # ---- semántica mínima ---------------------------------------------------------------------
    @staticmethod
    def _cond(cc, f):
        if f is None:
            return None
        n, z, cf, v = f
        return {"eq": z, "ne": not z, "hs": cf, "cs": cf, "lo": not cf, "cc": not cf, "mi": n, "pl": not n,
                "hi": cf and not z, "ls": (not cf) or z, "ge": n == v, "lt": n != v,
                "gt": (not z) and n == v, "le": z or n != v}[cc]

    def _step(self, ins, regs, flags, lit):
        mn, ops = ins.mnemonic, ins.op_str
        o = ins.operands
        regs = dict(regs)
        base = mn.rstrip("s") if mn.endswith("s") and mn not in ("movs",) else mn
        if lit is not None:
            regs[rn(ops.split(",")[0])] = lit
            return regs, flags
        if mn in ("cmp", "cmp.w", "cmn", "tst", "tst.w"):
            a = regs.get(rn(ops.split(",")[0]))
            b = o[1].imm & 0xFFFFFFFF if o[1].type == arm.ARM_OP_IMM else regs.get(rn(o[1].reg and ops.split(",")[1].strip()))
            if a is None or b is None:
                return regs, None
            if mn.startswith("tst"):
                r = a & b
                return regs, (bool(r & 0x80000000), r == 0, flags[2] if flags else False, False)
            r = (a - b) & 0xFFFFFFFF
            sa, sb = a - (1 << 32 if a >> 31 else 0), b - (1 << 32 if b >> 31 else 0)
            return regs, (bool(r >> 31), r == 0, a >= b, not (-(1 << 31) <= sa - sb < (1 << 31)))
        parts = [p.strip() for p in ops.split(",")]
        d = rn(parts[0]) if parts and REG.match(parts[0]) else None
        if mn.startswith(("str", "push", "stm", "it", "dmb", "dsb", "isb", "nop", "cpsi", "msr")):
            return regs, (None if mn.startswith("it") else flags)
        if d is None:
            return regs, None
        imm = o[-1].imm if o and o[-1].type == arm.ARM_OP_IMM else None
        if mn in ("movs", "mov", "mov.w", "movs.w", "movw") and imm is not None:
            regs[d] = imm & 0xFFFFFFFF
            return regs, ((bool(regs[d] >> 31), regs[d] == 0, False, False) if mn.startswith("movs") else flags)
        if mn in ("mov", "movs", "mov.w") and len(parts) == 2 and REG.match(parts[1]):
            regs[d] = regs.get(rn(parts[1]))
            return regs, flags if mn == "mov" else None
        if mn == "movt" and regs.get(d) is not None:
            regs[d] = (regs[d] & 0xFFFF) | (imm << 16)
            return regs, flags
        if (base in ("add", "sub", "addw", "subw", "add.w", "sub.w") or mn in ("adds", "subs", "adds.w", "subs.w")) and imm is not None:
            src = rn(parts[1]) if len(parts) == 3 else d
            sv = regs.get(src)
            if sv is not None and REG.match(src):
                sign = 1 if mn.startswith("add") else -1
                regs[d] = (sv + sign * imm) & 0xFFFFFFFF
                return regs, (None if mn.endswith("s") else flags)
        regs[d] = None
        return regs, None if (mn.endswith("s") or mn in ("ands", "orrs", "bics", "lsls", "lsrs", "asrs", "muls")) else flags


def summarize(res: Result, targets: dict[int, str]) -> dict:
    """Primitivas/errores alcanzados: {destino: [(llamante, sitio, r0)]}."""
    out: dict[int, list] = {}
    for caller, site, tgt, r0 in res.calls:
        if tgt in targets:
            out.setdefault(tgt, []).append((caller, site, r0))
    return out
