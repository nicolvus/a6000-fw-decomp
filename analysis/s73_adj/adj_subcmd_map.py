"""S74: mapa sub-comando -> nombre en el manejador ADJ_CMD de panel/EVF (0x4363524c).

Estructura verificada:
  - ID de comando u16 en [r6+0x18] (se compara con 0x302 al inicio del manejador);
  - sub-comando u8 en [r6+0x1a] (rango 0..0x28);
  - dispatch por tabla `tbb [pc, r2]` en 0x436354fc (tabla de bytes justo despues);
  - dentro del caso de WB, un segundo `tbb [pc, r3]` en 0x436357b2 para los canales R/G/B.

Este script lee la tabla tbb, resuelve el destino de cada entrada y devuelve el literal de nombre
que se carga en ese bloque (si lo hay).

Uso: adj_subcmd_map.py [A6000|A7S]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs  # noqa: E402

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

LIT_RE = re.compile(r"^(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$")
TBB = 0x436354FC
START = 0x4363524C
END = 0x436364A8


def u32(model, a):
    import struct
    return struct.unpack_from("<I", data(model)[a - B:a - B + 4])[0]


def cstr(model, addr, limit=200):
    d = data(model)
    off = addr - B
    if off < 0 or off >= len(d):
        return None
    end = d.find(b"\x00", off, off + limit)
    if end < 0:
        return None
    s = d[off:end]
    if not s or any(b < 0x20 and b not in (0x09, 0x0A) or b > 0x7E for b in s):
        return None
    return s.decode("ascii")


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    d = data(model)
    ins = [i for i in MD.disasm(d[START - B:END - B], START) if i.mnemonic != ".byte"]
    by_addr = {i.address: k for k, i in enumerate(ins)}

    # tabla tbb: base = direccion de la instruccion + 4
    base = TBB + 4
    table = d[base - B:base - B + 0x30]
    n = 0
    while n < len(table) and table[n] != 0 and n < 0x2B:
        n += 1
    # VERIFICADO: el valor de dispatch es (sub_cmd - 1) con rango 0..7 -> 8 entradas
    # (subs r2,#1 @ 0x436354f6 ; cmp r2,#7 @ 0x436354f8 ; tbb @ 0x436354fc)
    entries = []
    for k in range(8):
        entries.append(base + 2 * table[k])
    print(f"# {model}: tbb en {TBB:#x}, tabla en {base:#x}, {len(entries)} entradas (sub_cmd 1..8)")
    print("#   tabla:", " ".join(f"{b:02x}" for b in table[:8]))

    def name_in_block(start_addr, stop_addr):
        """Primer literal ADJ_CMD/WB_Sub cargado entre start_addr y stop_addr."""
        pending = {}
        for i in ins:
            if i.address < start_addr:
                continue
            if i.address >= stop_addr:
                break
            m = LIT_RE.match(i.op_str)
            if i.mnemonic.startswith("ldr") and m:
                la = ((i.address + 4) & ~3) + int(m.group(2), 0)
                pending[m.group(1)] = la
                continue
            if i.mnemonic == "add" and i.op_str.endswith(", pc"):
                reg = i.op_str.split(",")[0]
                la = pending.pop(reg, None)
                if la is None:
                    continue
                tgt = (u32(model, la) + (i.address + 4)) & 0xFFFFFFFF
                s = cstr(model, tgt)
                if s and (s.startswith("ADJ_CMD_") or s.startswith("WB_Sub")):
                    return s
        return None

    order = sorted(entries)
    for idx, tgt in enumerate(entries):
        nxt = order[idx + 1] if idx + 1 < len(order) else END
        nm = name_in_block(tgt, nxt)
        print(f"sub {idx:2d} (0x{idx:02x}) -> {tgt:#x}  {nm!r}")


if __name__ == "__main__":
    main()
