"""S74: mapa ID -> nombre de los comandos ADJ_CMD del manejador de panel/EVF (0x4363524c).

El manejador es una cadena larga if/else: cada rama compara el ID (u16 en [r6+0x18]) con un
inmediato y, si coincide, carga el literal con el nombre del comando (ldr rX,[pc,#imm]; add rX,pc)
y lo pasa al logger. Este script empareja cada literal de nombre con el `cmp` inmediatamente
anterior en el flujo (el último `cmp` con inmediato antes de la carga del literal).

Uso: adj_cmd_map.py [A6000|A7S]
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

START = 0x4363524C
LIT_RE = re.compile(r"^(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$")
CMP_RE = re.compile(r"^(r\d+), #(0x[0-9a-f]+|\d+)$")


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


def function_end(model, start, limit=0x4000):
    d = data(model)
    for i in MD.disasm(d[start - B:start - B + limit], start):
        if i.mnemonic != ".byte" and i.mnemonic.startswith("push") and "lr" in i.op_str and i.address > start:
            return i.address
    return start + limit


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    end = function_end(model, START)
    print(f"# {model}: manejador {START:#x}-{end:#x}")
    d = data(model)
    ins = [i for i in MD.disasm(d[START - B:end - B], START) if i.mnemonic != ".byte"]
    pending = {}
    last_cmp = None
    rows = []
    for i in ins:
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
                rows.append((i.address, tgt, s, last_cmp))
            continue
        m2 = CMP_RE.match(i.op_str)
        if i.mnemonic.startswith("cmp") and m2:
            last_cmp = (i.address, int(m2.group(2), 0), i.op_str.split(",")[0])
    print(f"{'nombre':52} {'cmp@':>10} {'ID':>8}")
    for addr, tgt, s, cmp_info in rows:
        c = f"{cmp_info[0]:#x}" if cmp_info else "-"
        v = f"{cmp_info[1]:#x}" if cmp_info else "?"
        print(f"{s:52} {c:>10} {v:>8}")


if __name__ == "__main__":
    main()
