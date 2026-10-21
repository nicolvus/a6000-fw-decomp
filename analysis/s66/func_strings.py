"""S62: secuencias de cadenas y llamadas dentro de una función (av-cam.bin, Thumb).

Uso: func_strings.py MODEL 0xSTART 0xEND [--calls]
Imprime, en orden, las cadenas referenciadas por la instrucción y los destinos de llamada.
La referencia de cadena se resuelve con el patrón PIC de Thumb:
    ldr rX, [pc, #imm]   (literal = valor en la tabla de literales)
    add rX, pc           (destino = literal + (addr_add + 4))
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB  # noqa: E402

# skipdata: el barrido lineal debe sobrevivir a los pools de literales y a los
# huecos de datos (si no, Capstone se detiene en el primer byte inválido y se
# pierde el resto de la función).
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = False
md.skipdata = True

LIT_RE = re.compile(r"^(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$")


def u32(model, a):
    return struct.unpack_from("<I", data(model)[a - B:a - B + 4])[0]


def read_cstr(model, addr, limit=200):
    d = data(model)
    off = addr - B
    if off < 0 or off >= len(d):
        return None
    end = d.find(b"\x00", off, off + limit)
    if end < 0:
        return None
    s = d[off:end]
    if not s or any(b < 0x20 or b > 0x7e for b in s):
        return None
    return s.decode("ascii")


def main():
    model = sys.argv[1]
    start, end = int(sys.argv[2], 0), int(sys.argv[3], 0)
    show_calls = "--calls" in sys.argv
    d = data(model)
    pending = {}   # registro -> (instr, literal address)
    for i in md.disasm(d[start - B:end - B], start):
        m = LIT_RE.match(i.op_str)
        if i.mnemonic.startswith("ldr") and m:
            la = ((i.address + 4) & ~3) + int(m.group(2), 0)
            pending[m.group(1)] = (i.address, la)
            continue
        if i.mnemonic == "add" and i.op_str.endswith(", pc") and i.op_str.startswith("r"):
            reg = i.op_str.split(",")[0]
            if reg in pending:
                ia, la = pending.pop(reg)
                lit = u32(model, la)
                tgt = (lit + (i.address + 4)) & 0xffffffff
                s = read_cstr(model, tgt)
                if s is not None:
                    print(f"{i.address:#x}  STR  {tgt:#x}  {s!r}")
                else:
                    print(f"{i.address:#x}  PTR  {tgt:#x}")
                continue
        if show_calls and i.mnemonic in ("bl", "blx") and i.op_str.startswith("#"):
            print(f"{i.address:#x}  CALL {int(i.op_str[1:], 16):#x}")


if __name__ == "__main__":
    main()
