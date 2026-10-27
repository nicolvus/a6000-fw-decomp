"""Recorrido de flujo de control con poda por tipo de bobina y detección de ciclos (SCC) en el grafo alcanzable.

Reutiliza E24-05h-3 (`adcb_p29`). Un `bl 0x20c74` seguido de `cbz/cbnz r0` o de `cmp r0,#k` + `beq/bne` fija r0:
tipo 0 ⇒ r0 = 0; tipo ≠ 0 ⇒ r0 ∈ {1,2,3}. La rama imposible se elimina; el resto se explora por ambos lados.
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "e24_05h3")]

import adcb_p29 as P

TYPE_FN = 0x20C74
PINMUX = 0x1B30A
CMP_R0 = re.compile(r"r0, #(0x[0-9a-f]+|\d+)")
BARE_B = {"bl", "blx", "bic", "bics", "bfi", "bfc", "bx"}


class Flow:
    def __init__(self, c: P.Core, g: P.E.G, stop: set[int] | None = None):
        self.c, self.g, self.stop = c, g, stop or set()
        self.ins = {i.address: i for i in c.all_insns}
        order = sorted(self.ins)
        self.nxt = dict(itertools.pairwise(order))

    def prev(self, a: int) -> int:
        for d in (2, 4):
            p = self.ins.get(a - d)
            if p is not None and p.address + p.size == a:
                return p.address
        return -1

    def after_type(self, a: int) -> bool:
        """`a` sigue inmediatamente a `bl 0x20c74` (o a un `cmp r0,#k` que lo sigue)."""
        p = self.ins.get(self.prev(a))
        if p is None:
            return False
        if p.mnemonic == "bl" and p.operands[0].imm == TYPE_FN:
            return True
        return p.mnemonic.startswith("cmp") and CMP_R0.fullmatch(p.op_str) is not None and self.after_type(p.address)

    def tbb_targets(self, a: int) -> list[int]:
        """Destinos de `tbb [pc, rN]` acotados por el `cmp rN, #k` previo (k casos); [] si no se encuentra."""
        reg = self.ins[a].op_str.split(", ")[1].rstrip("]")
        p = a
        for _ in range(4):
            p = self.prev(p)
            if p < 0:
                return []
            m = re.fullmatch(rf"{reg}, #(0x[0-9a-f]+|\d+)", self.ins[p].op_str)
            if self.ins[p].mnemonic.startswith("cmp") and m:
                base = a + 4
                return [base + 2 * self.c.u8(base + j) for j in range(int(m.group(1), 0))]
        return []

    def pinmux_target(self, a: int) -> int | None:
        """Destino real de `bl/b.w 0x1b30a(r0, r1)` cuando r0/r1 son constantes (réplica de 0x1b30a–0x1b336: r1&0xf0, r1&0xf, r0 = 0x2c/0x1a)."""
        r = P.regs_before(self.c, {i.address: k for k, i in enumerate(self.c.all_insns)}[a], 8)
        if r[0] is None or r[1] is None:
            return None
        hi, lo = r[1] & 0xF0, r[1] & 0xF
        if r[0] == 0x2C:
            return 0x1B586 if lo == 4 else 0x1B56E
        if hi == 0x10:
            return 0x5D70 if lo == 4 else 0x5D00
        if r[0] == 0x1A:
            return 0x1B586 if lo != 1 else 0x1B56E
        return 0

    def succ(self, a: int, tipo: int) -> tuple[list[int], list[int], list[str]]:
        """(sucesores de flujo, destinos de llamada, indirectos no resueltos) de la instrucción `a`. `tipo`: 0 o 1 (≠0)."""
        i, n = self.ins[a], self.nxt.get(a)
        m, op = i.mnemonic, i.op_str
        imm = i.operands[0].imm if i.operands and i.operands[0].type == 2 else None
        fall = [n] if n else []
        if imm == PINMUX and m in ("bl", "b.w") and (pm := self.pinmux_target(a)) is not None:
            return (fall if m == "bl" else []), [pm] if pm else [], []
        if m in ("b", "b.w") and imm in self.stop:
            return [], [imm], []
        if m == "bl":
            return fall, [imm] if imm is not None else [], []
        if m == "blx":
            return fall, [], [f"{a:#x} blx {op}"]
        if m == "tbb":
            tb = self.tbb_targets(a)
            return tb, [], [] if tb else [f"{a:#x} tbb {op}"]
        if m == "bx" or (m in ("pop", "pop.w") and "pc" in op) or (m.startswith("ldr") and op.startswith("pc")):
            return [], [], [f"{a:#x} {m} {op}"] if m == "bx" and not op.startswith("lr") else []
        if m in ("cbz", "cbnz"):
            tgt = i.operands[1].imm
            if op.startswith("r0") and self.after_type(a):
                return [x for x in (tgt if (tipo == 0) == (m == "cbz") else n,) if x], [], []
            return [x for x in (tgt, n) if x], [], []
        if m in ("b", "b.w") and imm is not None:
            return [imm], [], []
        if m.startswith("b") and m not in BARE_B and imm is not None:
            p = self.ins.get(self.prev(a))
            cond = m[1:].replace(".w", "")
            if p is not None and cond in ("eq", "ne") and p.mnemonic.startswith("cmp") and self.after_type(p.address):
                mk = CMP_R0.fullmatch(p.op_str)
                if mk:
                    k = int(mk.group(1), 0)
                    z = (tipo == 0) if k == 0 else (False if tipo == 0 else None)
                    if z is not None:
                        return [x for x in (imm if z == (cond == "eq") else n,) if x], [], []
            return [x for x in (imm, n) if x], [], []
        return fall, [], []

    def walk(self, entry: int, tipo: int) -> dict:
        seen: set[int] = set()
        calls: set[int] = set()
        ind: list[str] = []
        edges: dict[int, list[int]] = {}
        todo = [entry]
        while todo:
            a = todo.pop()
            if a in seen or a not in self.ins:
                continue
            seen.add(a)
            s, cl, ib = self.succ(a, tipo)
            edges[a] = s
            calls |= set(cl)
            ind += ib
            todo += s
        return {"nodos": seen, "llamadas": calls, "indirectos": ind, "aristas": edges}

    def periph_literals(self, nodes: set[int]) -> list[int]:
        out = set()
        for a in nodes:
            i = self.ins[a]
            if i.mnemonic.startswith("ldr") and "pc" in i.op_str:
                v = self.c.lit_of(i)
                if v is not None and (0x40000000 <= v < 0x60000000 or v >= 0xE0000000):
                    out.add(v)
        return sorted(out)


def scc_cycles(edges: dict[int, list[int]]) -> list[list[int]]:
    """Componentes fuertemente conexas con ciclo (|SCC|>1 o autolazo), Tarjan iterativo."""
    index: dict[int, int] = {}
    low: dict[int, int] = {}
    on: set[int] = set()
    stack: list[int] = []
    out: list[list[int]] = []
    ctr = 0
    for root in edges:
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            v, k = work.pop()
            if k == 0:
                index[v] = low[v] = ctr
                ctr += 1
                stack.append(v)
                on.add(v)
            ch = [w for w in edges.get(v, []) if w in edges]
            if k < len(ch):
                work.append((v, k + 1))
                w = ch[k]
                if w not in index:
                    work.append((w, 0))
                elif w in on:
                    low[v] = min(low[v], index[w])
                continue
            low[v] = min([low[v]] + [low[w] for w in ch if w in on])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1 or v in edges.get(v, []):
                    out.append(sorted(comp))
    return out


def deep(fl: Flow, entry: int, tipo: int, stop: set[int]) -> dict[int, dict]:
    """Cierre transitivo podado: ciclos, llamadas, indirectos y literales de periférico por función explorada."""
    funcs: dict[int, dict] = {}
    todo = [entry]
    while todo:
        f = todo.pop()
        if f in funcs or f in stop:
            continue
        w = fl.walk(f, tipo)
        funcs[f] = {"ciclos": scc_cycles(w["aristas"]), "llamadas": sorted(w["llamadas"]), "indirectos": w["indirectos"], "n": len(w["nodos"]),
                    "periferico": fl.periph_literals(w["nodos"])}
        todo += [t for t in w["llamadas"] if t not in stop]
    return funcs
