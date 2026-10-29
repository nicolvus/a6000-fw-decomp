"""E25-25 — referencias estáticas en una imagen plana (BIONZ / Darwin), offline.

Barrido rápido y conservador: cualquier media palabra que codifique `bl`/`b.w`
se decodifica y, si cae en el rango pedido, se registra.  También se buscan
punteros literales alineados a 4 B.  Un barrido sin referencias **no demuestra**
ausencia de uso indirecto (una base + índice calculados en ejecución no deja
literal); por eso el resultado se clasifica, no se usa como prueba de libertad.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs


def _sign_extend(value: int, bits: int) -> int:
    if value & (1 << (bits - 1)):
        return value - (1 << bits)
    return value


def decode_branch(addr: int, hw1: int, hw2: int) -> int | None:
    """Decodifica `bl` (hw2 & 0xD000 == 0xD000) o `b.w` (== 0x9000)."""
    if not 0xF000 <= hw1 <= 0xF7FF:
        return None
    kind = hw2 & 0xD000
    if kind not in (0xD000, 0x9000):
        return None
    s = (hw1 >> 10) & 1
    imm10 = hw1 & 0x3FF
    j1 = (hw2 >> 13) & 1
    j2 = (hw2 >> 11) & 1
    imm11 = hw2 & 0x7FF
    i1 = 1 - (j1 ^ s)
    i2 = 1 - (j2 ^ s)
    offset = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        offset -= 1 << 25
    return (addr + 4 + offset) & 0xFFFFFFFF


@dataclass(frozen=True)
class Reference:
    source: int
    target: int
    kind: str

    def as_dict(self) -> dict[str, str]:
        return {"source": hex(self.source), "target": hex(self.target), "kind": self.kind}


_BRANCHES: dict[tuple[str, int], list[tuple[int, int, str]]] = {}


def _all_branches(data: bytes, base: int) -> list[tuple[int, int, str]]:
    """Ramas reales de un barrido lineal (Capstone), cacheadas por SHA-256.

    Un barrido por medias palabras en cualquier offset produce falsos positivos al
    leer la segunda mitad de una instrucción de 32 bits; el barrido lineal evita ese
    caso.  Aun así, una tabla de datos puede decodificar como rama: se conserva el
    resultado como cota superior, no como prueba de uso.
    """
    key = (hashlib.sha256(data).hexdigest(), base)
    if key not in _BRANCHES:
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        md.skipdata = True
        found: list[tuple[int, int, str]] = []
        for ins in md.disasm(data, base):
            if ins.id == 0:
                continue
            if ins.mnemonic in ("bl", "b.w", "blx") and ins.op_str.startswith("#"):
                try:
                    found.append((ins.address, int(ins.op_str[1:], 16), ins.mnemonic))
                except ValueError:
                    pass
        _BRANCHES[key] = found
    return _BRANCHES[key]


def branch_references(data: bytes, base: int, lo: int, hi: int) -> list[Reference]:
    """Ramas `bl`/`b.w` cuyo destino cae en [lo, hi), según barrido lineal."""
    return [Reference(src, target, kind) for src, target, kind in _all_branches(data, base) if lo <= target < hi]


def literal_references(data: bytes, base: int, lo: int, hi: int) -> list[Reference]:
    """Palabras alineadas a 4 B cuyo valor cae en [lo, hi) (punteros, GOT, tablas)."""
    out: list[Reference] = []
    for off in range(0, len(data) - 3, 4):
        value = struct.unpack_from("<I", data, off)[0]
        if lo <= value < hi:
            out.append(Reference(base + off, value, "literal"))
        elif lo <= (value & ~1) < hi and value & 1:
            out.append(Reference(base + off, value, "thumb-pointer"))
    return out


def region_report(data: bytes, base: int, lo: int, hi: int) -> dict:
    """Estado de una región candidata a cueva."""
    region = data[lo - base:hi - base]
    return {
        "range": [hex(lo), hex(hi)],
        "length": hi - lo,
        "all_zero": all(b == 0 for b in region),
        "nonzero_bytes": sum(1 for b in region if b),
        "literal_references": [r.as_dict() for r in literal_references(data, base, lo, hi)],
        "branch_references": [r.as_dict() for r in branch_references(data, base, lo, hi)],
        "before": data[max(0, lo - base - 16):lo - base].hex(),
        "after": data[hi - base:hi - base + 16].hex(),
    }


VECTOR_BASE = 0x4200
VECTOR_COUNT = 128


def darwin_vectors(data: bytes) -> list[dict]:
    """Tabla de vectores de Darwin (base 0x4200; el archivo empieza en esa dirección)."""
    out = []
    for index in range(VECTOR_COUNT):
        addr = VECTOR_BASE + index * 4
        value = struct.unpack_from("<I", data, index * 4)[0]
        out.append({"index": index, "address": hex(addr), "value": hex(value), "zero": value == 0})
    return out


def cave_overlaps(report: dict, start: int, length: int, base: int) -> dict:
    """Comprueba que una cueva cabe y que la región no tiene referencias."""
    lo = int(report["range"][0], 16)
    hi = int(report["range"][1], 16)
    return {
        "fits": lo <= start and start + length <= hi,
        "start": hex(start),
        "end": hex(start + length),
        "literal_conflicts": [r for r in report["literal_references"] if start <= int(r["target"], 16) < start + length],
        "branch_conflicts": [r for r in report["branch_references"] if start <= int(r["target"], 16) < start + length],
    }
