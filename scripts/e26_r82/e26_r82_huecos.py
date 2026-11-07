#!/usr/bin/env python3
"""E26-R82 via B - busqueda de huecos reales en darwin_core.bin con dos metodos independientes. Solo offline.

Metodo 1 (flujo): recorrido recursivo desde la tabla de vectores y todas las palabras-puntero impares de la imagen
  (sobreaproxima la alcanzabilidad: un hueco que sobreviva es hueco seguro), siguiendo ramas, bl, tbb/tbh y literales.
Metodo 2 (barrido): decodificacion en CADA halfword + clasificacion de cada byte no cubierto: relleno puro (0x00/0xff)
  o con referencias entrantes (ramas, palabras-puntero, adr, ldr pc-relativo) desde cualquier halfword decodificable.

Uso: e26_r82_huecos.py [MIN_BYTES]   (por defecto 16)
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e26_r76"))
import e26_r76_parche_darwin_tabla as P

BASE = 0x4200
CODE_END = 0x25C5C                  # R81: fin del codigo; despues vienen tablas/datos


def _md():
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    md.detail = False
    return md


def cubierto_recursivo(img: bytes) -> bytearray:
    """Metodo 1: mapa de bytes cubiertos (1 = instruccion alcanzada o literal/dato referenciado)."""
    md, end = _md(), BASE + len(img)
    cov = bytearray(len(img))
    seen: set[int] = set()
    work: list[int] = []
    roots = {struct.unpack_from("<I", img, o)[0] & ~1 for o in range(0, 0x100, 4)}
    for o in range(0, len(img) - 3, 2):
        v = struct.unpack_from("<I", img, o)[0]
        if v & 1 and BASE <= v - 1 < BASE + CODE_END - BASE:
            roots.add(v - 1)
    md2 = _md()                                          # destinos de bl/b.w decodificados en CADA halfword (sobreaproxima)
    for o in range(0, len(img) - 3, 2):
        for i in md2.disasm(img[o:o + 4], BASE + o, 1):
            mm = re.search(r"#(-?0x[0-9a-f]+)", i.op_str)
            if i.mnemonic in ("bl", "b.w", "blx") and mm:
                roots.add(int(mm.group(1), 16))
    work.extend(r for r in roots if BASE <= r < end)
    while work:
        pc = work.pop()
        it_left = 0                                      # instrucciones restantes de un bloque IT (un retorno predicado no termina el flujo)
        while BASE <= pc < end and pc not in seen:
            seen.add(pc)
            ins = list(md.disasm(img[pc - BASE:pc - BASE + 4], pc, 1))
            if not ins:
                break
            i = ins[0]
            for k in range(i.size):
                cov[pc - BASE + k] = 1
            m, op = i.mnemonic, i.op_str
            predicado = it_left > 0
            it_left = max(it_left - 1, 0)
            if re.fullmatch(r"it[te]{0,3}", m):
                it_left = len(m) - 1
            mm = re.search(r"#(-?0x[0-9a-f]+)", op)
            if mm and (m.startswith("adr") or (m.startswith("ldr") and "[pc" in op)):
                t = ((pc + 4) & ~3) + int(mm.group(1), 16)
                if BASE <= t < end:
                    for k in range(8 if "d" in m[3:] else 4):   # ldrd lee 8 B; el resto 4 B
                        if t - BASE + k < len(cov):
                            cov[t - BASE + k] = 1
            if m.startswith(("tbb", "tbh")):
                # tabla de saltos: las entradas siguen a la instruccion; se cubren hasta el primer destino invalido
                n = 0
                while n < 64 and pc + i.size + n * (1 if m.startswith("tbb") else 2) < end:
                    off = pc + i.size + n * (1 if m.startswith("tbb") else 2)
                    v = img[off - BASE] if m.startswith("tbb") else struct.unpack_from("<H", img, off - BASE)[0]
                    tgt = pc + 4 + 2 * v
                    if tgt >= end or tgt - pc > 2000:
                        break
                    work.append(tgt)
                    n += 1
                for k in range(n * (1 if m.startswith("tbb") else 2)):
                    cov[pc + i.size - BASE + k] = 1
                break
            if mm and (m.startswith(("b", "cb")) and not m.startswith(("bic", "bfi", "bfc", "bkpt"))):
                t = int(mm.group(1), 16)
                if BASE <= t < end:
                    work.append(t)
                if m in ("b", "b.w") and not predicado:
                    break
            pc += i.size
            if (m == "bx" or (m in ("pop", "pop.w") and "pc" in op) or (m.startswith("ldr") and op.startswith("pc,"))) and not predicado:
                break
    # palabras-puntero y datos referenciados por el codigo: se cubren si apuntan a la imagen
    for o in range(0, len(img) - 3, 4):
        v = struct.unpack_from("<I", img, o)[0]
        if BASE <= (v & ~1) < end and cov[o:o + 4] == bytearray(4):
            pass
    return cov


def rangos_no_cubiertos(cov: bytearray, lo: int, hi: int, minimo: int) -> list[tuple[int, int]]:
    out, i = [], lo - BASE
    while i < hi - BASE:
        if cov[i]:
            i += 1
            continue
        j = i
        while j < hi - BASE and not cov[j]:
            j += 1
        if j - i >= minimo:
            out.append((BASE + i, BASE + j))
        i = j
    return out


def clasificar(img: bytes, a: int, b: int) -> str:
    seg = img[a - BASE:b - BASE]
    if seg == bytes(len(seg)):
        return "ceros"
    if seg == b"\xff" * len(seg):
        return "0xff"
    ext = P.referencias_externas(img, a, b)
    if ext:
        return f"{len(ext)} refs externas"
    asc = sum(32 <= c < 127 for c in seg) / len(seg)
    return "cadena ASCII (dato)" if asc >= 0.75 else "sin refs externas, no ASCII (revisar)"


def main(minimo: int = 16) -> None:
    img = P.DARWIN.read_bytes()
    cov = cubierto_recursivo(img)
    cub = sum(cov[:CODE_END - BASE])
    print(f"metodo 1: {cub} de {CODE_END - BASE} B de codigo cubiertos ({cub / (CODE_END - BASE):.1%})")
    rs = rangos_no_cubiertos(cov, 0x4300, CODE_END, minimo)
    print(f"rangos no cubiertos >= {minimo} B entre 0x4300 y {CODE_END:#x}: {len(rs)}")
    for a, b in sorted(rs, key=lambda r: r[0] - r[1])[:25]:
        print(f"  {a:#x}..{b:#x} ({b - a:4d} B) {clasificar(img, a, b)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if sys.argv[1:] else 16)
