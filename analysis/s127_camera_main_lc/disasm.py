#!/usr/bin/env python3
"""S127 — utilidades de desensamblado Thumb con capstone sobre av-cam.bin.

  disasm.py range LO HI [N]     desensambla el rango (vaddr)
  disasm.py func  ADDR [N]      desensambla N instrucciones desde ADDR
  disasm.py bounds ADDR...      comprueba si ADDR es frontera de función
  disasm.py calls LO HI         lista los `bl` del rango con su destino

Convención: vaddr = 0x43541000 + file_offset.
"""
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True
MD.skipdata = True


def load():
    return open(BIN, "rb").read()


def dis(data, lo, n=40):
    off = lo - BASE
    for ins in MD.disasm(data[off:off + n * 4], lo):
        print(f"0x{ins.address:x}\t{ins.bytes.hex():10s}\t{ins.mnemonic}\t{ins.op_str}")


def is_boundary(data, addr):
    """Heurística: el hueco anterior es relleno, un `b`/`bx lr` o un `pop {..pc}`."""
    prev = [ins for ins in MD.disasm(data[addr - BASE - 8:addr - BASE + 2], addr - 8)]
    tail = prev[-1] if prev else None
    ok = False
    if tail is not None and tail.address + tail.size == addr:
        m = tail.mnemonic
        ok = (m == "b" or (m == "bx" and tail.op_str == "lr")
              or (m == "pop" and "pc" in tail.op_str)
              or (m in ("nop",) and False))
    return ok, (f"0x{tail.address:x} {tail.mnemonic} {tail.op_str}" if tail else "?")


def main():
    data = load()
    cmd = sys.argv[1]
    if cmd == "range":
        lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
        dis(data, lo, (hi - lo) // 2)
    elif cmd == "func":
        lo = int(sys.argv[2], 16)
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        dis(data, lo, n)
    elif cmd == "bounds":
        for a in sys.argv[2:]:
            ok, prev = is_boundary(data, int(a, 16))
            print(f"0x{int(a,16):x}\t{'OK' if ok else 'NO'}\tprev={prev}")
    elif cmd == "calls":
        lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
        for ins in MD.disasm(data[lo - BASE:hi - BASE], lo):
            if ins.mnemonic in ("bl", "blx"):
                print(f"0x{ins.address:x}\t{ins.mnemonic} {ins.op_str}")


if __name__ == "__main__":
    main()
