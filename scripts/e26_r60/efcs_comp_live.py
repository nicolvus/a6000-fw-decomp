#!/usr/bin/env python3
"""E26-R60 — Compensación EFCS de prueba: resta N líneas a `sl` (record+0x64) del productor 0x4383fa40, en RAM por SWD.

Productor compartido por el planificador EFCS (0x438417c0) y el normal (0x437b46d0): mientras esté puesto, TAMBIÉN afecta a EFCS
desactivado; no disparar más lento de 1/125 (sl puede desbordar). Reversible: se pierde al apagar, o con --revert.
Uso: efcs_comp_live.py [--lineas 84] [--apply | --revert]   (sin flags: solo lee y muestra el plan). Requiere sonda SWD en el BIONZ.
Escribe en RAM del BIONZ solo con --apply/--revert, solo en 0x8383fac4 (DRAM validada) y solo si los bytes actuales son los esperados."""
import argparse, struct, subprocess, sys, tempfile

VA = 0x4383FAC4                 # `uxth.w sl, sl` en el productor
PA = VA + 0x40000000
OLD = bytes.fromhex("1ffa8afa")  # uxth.w sl, sl
CFG = """adapter driver cmsis-dap
transport select swd
adapter speed 1000
swd newdap chip tap -enable
dap create chip.dap -chain-position chip.tap
init
proc rd {a} { chip.dap apreg 0 0x04 $a; return [string trim [chip.dap apreg 0 0x0c]] }
proc wr {a v} { chip.dap apreg 0 0x04 $a; chip.dap apreg 0 0x0c $v }
%s
shutdown
"""


def sub_w(n: int) -> bytes:
    """sub.w r10, r10, #n  (T3, imm12 modificado: n < 256)."""
    assert 0 < n < 256
    return struct.pack("<HH", 0xF1AA, 0x0A00 | n)


def run(body: str) -> list[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".cfg") as f:
        f.write(CFG % body); f.flush()
        r = subprocess.run(["openocd", "-f", f.name], capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr).splitlines()


def word(b: bytes) -> int:
    return struct.unpack("<I", b)[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lineas", type=int, default=84)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--revert", action="store_true")
    a = ap.parse_args()
    new = sub_w(a.lineas)
    txt = run(f'echo "ACTUAL [rd {PA:#x}]"')
    line = next((l for l in txt if l.startswith("ACTUAL")), None)
    if not line:
        print("sin respuesta del BIONZ:", " | ".join(txt[-3:])); return 2
    cur = int(line.split()[1], 16)
    print(f"{VA:#x} (física {PA:#x}) = {cur:#010x}; original {word(OLD):#010x}; parche {word(new):#010x}")
    if not (a.apply or a.revert):
        print("solo lectura; use --apply o --revert"); return 0
    target = new if a.apply else OLD
    if cur == word(target):
        print("ya está en el estado pedido"); return 0
    if cur != word(OLD if a.apply else new):
        print("bytes inesperados: no se escribe nada"); return 3
    out = run(f'wr {PA:#x} {word(target):#x}\necho "TRAS [rd {PA:#x}]"')
    print(next((l for l in out if l.startswith("TRAS")), "sin lectura de verificación"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
