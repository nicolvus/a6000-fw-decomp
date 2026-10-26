"""E14: clasificación de los 14 escritores anchos de `+0x654` (palabra que contiene `params[+9]` = byte `+0x655`) por origen del valor
y por clase de objeto (layout de vecinos). Entrada: e3_params9.json. Salida: e14_writers.json. Solo bytes originales (Capstone)."""
import json
import re
from pathlib import Path

import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = Path(__file__).parent
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
DEFS = ("movs", "mov", "movw", "ldr", "ldrb", "ldrh", "adds", "add", "ldrsh", "uxtb", "orr", "orrs", "sub", "subs")


# Orígenes que el barrido lineal no ve: el valor es 0 por la rama que lleva al `str` (cbz/beq con registro nulo).
NOTAS = {"0x4364c27e": "cero: ruta de `cbz r0` con r0 == 0", "0x43b0b8ac": "cero: ruta de `subs r3,#1; beq` con r3 == 0"}


def kind(insn: str) -> str:
    mnem = insn.split()[0].split(".")[0]
    if mnem in ("movs", "mov", "movw") and "#" in insn:
        return "constante"
    if mnem.startswith("ldr") and "[sp" in insn:
        return "pila"
    if mnem.startswith("ldr") and "#0x654]" in insn:
        return "copia_de_otro_bloque"
    return "carga" if mnem.startswith("ldr") else "calculo"


def classify(blob: bytes, addr: int, insn: str) -> dict:
    m0 = re.match(r"str[h]?\.w (r\d+), \[(r\d+), #0x654\]", insn)
    assert m0, insn
    src, base = m0.groups()
    before = list(CS.disasm(blob[addr - 0x60 - pic.BASE:addr - pic.BASE], addr - 0x60))
    d = next((i for i in reversed(before) if re.match(rf"{src},", i.op_str) and i.mnemonic.split(".")[0] in DEFS), None)
    around = CS.disasm(blob[addr - 0x30 - pic.BASE:addr + 0x30 - pic.BASE], addr - 0x30)
    near = sorted({m.group(1) for i in around for m in [re.search(rf"\[{base}, #(0x[0-9a-f]+)\]", i.op_str)] if m})
    cls = "estado_fsm" if set(near) <= {"0x650", "0x654", "0x3b4"} else "bloque_de_parametros"
    if hex(addr) in NOTAS:
        return {"addr": hex(addr), "insn": insn, "clase": cls, "vecinos": near, "origen": "constante_0", "definicion": NOTAS[hex(addr)]}
    return {"addr": hex(addr), "insn": insn, "clase": cls, "vecinos": near,
            "origen": kind(f"{d.mnemonic} {d.op_str}") if d else "fuera_de_ventana",
            "definicion": f"{d.address:#x} {d.mnemonic} {d.op_str}" if d else None}


def main() -> None:
    blob = pic.load("a6000")
    ws = json.loads((HERE / "e3_params9.json").read_text())["escritores_anchos_en_0x654"]
    rows = [classify(blob, int(w["addr"], 16), w["insn"]) for w in ws]
    (HERE / "e14_writers.json").write_text(json.dumps(rows, indent=1) + "\n")
    for r in rows:
        print(r["addr"], r["clase"], r["origen"])


if __name__ == "__main__":
    main()
