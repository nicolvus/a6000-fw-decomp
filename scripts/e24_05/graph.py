"""Grafo de llamadas por descenso recursivo sobre `darwin_core.bin` (E24-05, solo lectura).

Aristas: BL/B.W directos (llamada o cola), punteros Thumb cargados por `ldr pc-relativo` (dirección tomada) y
palabras impares en el código/datos (tablas de callbacks). Las llamadas indirectas (`blx rN`, `bx rN`, `ldr pc`) se
reportan aparte como dependencias abiertas.
"""
from __future__ import annotations

from collections import defaultdict
from typing import ClassVar

from capstone import arm
from dwn import BASE, Core

CODE_END = 0x2A744  # tabla de scatter-load: a partir de aquí hay datos comprimidos


class Graph:
    def __init__(self, core: Core | None = None):
        self.c = core or Core()
        self.ptr_words = self._pointer_words()
        self.bodies: dict[int, set[int]] = {}
        self.calls: dict[int, set[int]] = defaultdict(set)
        self.tails: dict[int, set[int]] = defaultdict(set)
        self.taken: dict[int, set[int]] = defaultdict(set)
        self.indirect: dict[int, list[int]] = defaultdict(list)
        self.tbb: dict[int, list[int]] = {}
        self.owner: dict[int, int] = {}
        self.rev: dict[int, set[int]] = defaultdict(set)

    def _pointer_words(self) -> dict[int, int]:
        """{dirección de palabra: destino} para palabras impares dentro del código (candidatas a punteros Thumb)."""
        out = {}
        for a in range(BASE, CODE_END - 3, 4):
            v = self.c.u32(a)
            if v & 1 and BASE <= v - 1 < CODE_END:
                out[a] = v - 1
        return out

    def describe(self, entry: int) -> dict:
        """Recorre el cuerpo de la función en `entry` (descenso recursivo)."""
        if entry in self.bodies:
            return {"body": self.bodies[entry]}
        c, body, work = self.c, set(), [entry]
        while work:
            a = work.pop()
            while BASE <= a < CODE_END and a not in body:
                got = next(c.md.disasm(c.data[a - BASE:a - BASE + 4], a, 1), None)
                if got is None:
                    break
                body.add(a)
                mn, ops = got.mnemonic, got.operands
                nxt = a + got.size
                lit = c.lit_of(got)
                if lit is not None and lit & 1 and BASE <= lit - 1 < CODE_END:
                    self.taken[entry].add(lit - 1)
                if mn in ("bl", "blx") and ops and ops[0].type == arm.ARM_OP_IMM:
                    self.calls[entry].add(ops[0].imm)
                elif mn in ("bl", "blx") or (mn in ("bx",) and got.op_str != "lr") or \
                        (mn.startswith("ldr") and got.op_str.startswith("pc,")) or (mn == "mov" and got.op_str.startswith("pc,")):
                    self.indirect[entry].append(a)
                if mn.startswith(("tbb", "tbh")):
                    tgts = self._jump_table(a, got)
                    self.tbb[a] = tgts
                    work.extend(tgts)
                    break
                is_ret = (mn == "pop" or mn == "pop.w") and "pc" in got.op_str or mn == "bx" and got.op_str == "lr"
                if is_ret:
                    break
                if mn.startswith("b") and ops and ops[0].type == arm.ARM_OP_IMM and mn not in ("bl", "blx", "bic", "bics", "bfi", "bfc"):
                    tgt = ops[0].imm
                    if mn in ("b", "b.w"):
                        if tgt != entry and (tgt < entry or tgt > max(body | {a}) + 0x200 or tgt in self.funcs_hint and tgt not in body):
                            self.tails[entry].add(tgt)
                        else:
                            work.append(tgt)
                        break
                    work.append(tgt)
                if mn in ("cbz", "cbnz") and ops:
                    work.append(ops[-1].imm)
                a = nxt
        self.bodies[entry] = body
        return {"body": body}

    funcs_hint: ClassVar[set[int]] = set()

    def _jump_table(self, a, ins) -> list[int]:
        c = self.c
        k = [i for i in c.dis(a - 16, 16)]
        n = None
        for p in reversed(k):
            if p.mnemonic == "cmp" and p.operands[1].type == arm.ARM_OP_IMM:
                n = p.operands[1].imm + 1
                break
        if n is None:
            return []
        tab, pc = a + 4, a + 4
        out = []
        for i in range(n):
            if ins.mnemonic.startswith("tbb"):
                out.append(pc + 2 * c.u8(tab + i))
            else:
                out.append(pc + 2 * c.u16(tab + 2 * i))
        return out


def build(roots: list[int], g: Graph | None = None, follow_taken: bool = True):
    """Clausura directa (+ punteros cargados por literal) desde `roots`. Devuelve (grafo, funciones alcanzadas)."""
    g = g or Graph()
    if not Graph.funcs_hint:
        Graph.funcs_hint = {i.operands[0].imm for i in g.c.all_insns
                            if i.mnemonic in ("bl",) and i.operands and i.operands[0].type == arm.ARM_OP_IMM} | set(g.ptr_words.values())
    seen, work = set(), list(roots)
    while work:
        f = work.pop()
        if f in seen or not (BASE <= f < CODE_END):
            continue
        seen.add(f)
        g.describe(f)
        work.extend(g.calls[f] | g.tails[f] | (g.taken[f] if follow_taken else set()))
    return g, seen


def build_all(g: Graph | None = None) -> Graph:
    """Describe todas las funciones candidatas (destinos de BL y punteros Thumb) y arma el índice dirección→función."""
    g = g or Graph()
    build([], g)
    for f in sorted(Graph.funcs_hint):
        if BASE <= f < CODE_END:
            g.describe(f)
    for f in sorted(g.bodies, reverse=True):  # la entrada más baja gana si los cuerpos se solapan
        for a in g.bodies[f]:
            g.owner[a] = f
    for f in g.bodies:
        for t in g.calls[f] | g.tails[f]:
            g.rev[t].add(f)
    return g


def chains(g: Graph, target: int, depth: int = 6, stop=lambda f: False):
    """Cadenas de llamantes directos hacia `target` (lista de listas, de la raíz hacia el destino)."""
    out = []

    def walk(f, path):
        if len(path) > depth:
            return
        ups = sorted(g.rev.get(f, ()))
        if not ups or stop(f):
            out.append(path[::-1])
            return
        for u in ups:
            if u in path:
                continue
            walk(u, path + [u])
    walk(target, [target])
    return out
