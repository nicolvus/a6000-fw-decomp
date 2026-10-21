"""S62: tabla de modos SHD (sombreado dependiente de la lente) extraída del `tbb` de GetShdMode.

GetShdMode (0x438ef40e) recibe el `drive_mode` (0..0x44) y devuelve el ShdMode mediante una
tabla de saltos `tbb [pc, r3]`. Este script:
  1. lee la tabla de bytes (0x45 entradas, base = direccion de la instruccion tbb + 4);
  2. sigue cada entrada (destino = base + 2*offset) y lee el valor inmediato que se devuelve;
  3. devuelve el mapa drive_mode -> ShdMode con la dirección del destino de cada entrada.

Uso: shd_modes.py [A6000|A7S]
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

TBB = 0x438EF414           # instruccion `tbb [pc, r3]`
N = 0x45                   # drive_mode 0..0x44


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    d = data(model)
    base = TBB + 4
    table = d[base - B:base - B + N]
    print(f"# {model}: tabla tbb en {base:#x} ({N} entradas)")
    print("drive_mode | shd_mode | target")
    rows = []
    for mode in range(N):
        off = table[mode]
        tgt = base + 2 * off
        ins = list(MD.disasm(d[tgt - B:tgt - B + 8], tgt))
        val = None
        for i in ins:
            if i.mnemonic in ("movs", "mov") and re.match(r"^r0, #(0x[0-9a-f]+|\d+)$", i.op_str):
                val = int(i.op_str.split("#")[1], 0)
                break
        rows.append((mode, val, tgt))
        print(f"{mode:10d} | {('0x%02x' % val) if val is not None else '   ?':7} | {tgt:#x}")
    vals = sorted({v for _, v, _ in rows if v is not None})
    print(f"\n# ShdMode distintos: {[hex(v) for v in vals]}")
    counts = {}
    for _, v, _ in rows:
        counts[v] = counts.get(v, 0) + 1
    print("# reparto:", {hex(k): v for k, v in sorted(counts.items(), key=lambda kv: (kv[0] is None, kv[0]))})


if __name__ == "__main__":
    main()
