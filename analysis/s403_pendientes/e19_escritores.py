"""E19: escritores del campo +0x6a4 (id DFE que lee `[LGA]` 0x4389b320 vía r8+0x6a4) en av-cam A6000.
Barre los `str/strh/strb.w rX,[rY,#0x6a4]`, busca hacia atrás la última definición lineal del registro fuente y clasifica por campos vecinos.
Salida: e19_escritores.json. shortcut: búsqueda lineal sin ramas, así que un valor tomado de una rama anterior puede no ser el del camino real;
la identidad de la estructura con la del lector es probable por el campo compartido +0x6a8, no demostrada por tipos: los siete escritores son manejadores de estado (punteros en tablas de la imagen) y el lector recibe `r4+0x20` de una rutina `0x438cc66c`."""
import json
import re
import sys
from pathlib import Path

import capstone
import numpy as np
import pic

HERE = Path(__file__).parent
OFF = 0x6A4
BACK, FWD = 0x260, 0x40
# Rama que la búsqueda lineal no ve: el `bne 0x43550292` salta el `ldr r1,[sp,#0x190]` de 0x43550288 y r1=1 viene de 0x43550186 (sin `bl` entre medias).
MANUAL = {0x43550298: {"inmediato": 1, "en": "0x43550186", "nota": "verificado a mano: la rama bne 0x43550292 salta 0x43550288"}}


def disasm(md, blob, lo, hi):
    return list(md.disasm(blob[lo - pic.BASE : hi - pic.BASE], lo))


def store_sites(blob, md):
    hw = np.frombuffer(blob[: len(blob) // 2 * 2], dtype="<u2")
    for i in np.nonzero(((hw[1:] & 0xFFF) == OFF) & ((hw[:-1] & 0xFE00) == 0xF800))[0]:
        a = pic.BASE + 2 * int(i)
        for ins in md.disasm(blob[a - pic.BASE : a - pic.BASE + 4], a):
            m = re.match(rf"(r\w+), \[(r\w+), #{hex(OFF)}\]$", ins.op_str)
            if m and ins.mnemonic in ("str", "str.w"):  # 32 bits: el lector hace `ldr`
                yield ins, m.group(1)


def last_def(md, blob, addr, reg, delta=0):
    """Última definición lineal de `reg` antes de `addr`; pliega `movs #imm` seguido de `adds/subs #imm`. Ventana corta primero para no desincronizar el desensamblado."""
    for back in (0x40, 0x100, BACK):
        for ins in reversed(disasm(md, blob, addr - back, addr)):
            if not ins.op_str.startswith(reg + ",") or ins.mnemonic.startswith(("str", "cmp", "tst", "push", "b")):
                continue
            imm = re.fullmatch(rf"{reg}, #(0x[0-9a-f]+|\d+)", ins.op_str)
            if ins.mnemonic in ("movs", "mov", "mov.w", "movw") and imm:
                return {"inmediato": int(imm.group(1), 0) + delta, "en": hex(ins.address)}
            step = re.fullmatch(rf"{reg}, #(0x[0-9a-f]+|\d+)", ins.op_str)
            if ins.mnemonic in ("adds", "subs", "add", "sub") and step:
                sign = 1 if ins.mnemonic.startswith("add") else -1
                return last_def(md, blob, ins.address, reg, delta + sign * int(step.group(1), 0))
            return {"origen": f"{ins.mnemonic} {ins.op_str}", "en": hex(ins.address)}
    return {"origen": "sin definición en la ventana"}


def neighbours(md, blob, addr):
    near = {int(m.group(1), 16) for ins in disasm(md, blob, addr - FWD, addr + FWD)
            if (m := re.search(r"\[r\w+, #(0x[0-9a-f]+)\]", ins.op_str)) and ins.mnemonic.startswith("str")}
    return near


def classify(near):
    if 0x6A8 in near or 0x738 in near:
        return "bloque de modo (escribe también +0x6a8 o +0x738; el lector 0x438eff48 lee +0x6a8)"
    if {0x630, 0x718} & near:
        return "otra estructura: matriz de paso 0x74 (0x630/0x6a4/0x718)"
    return "reinicio masivo u otra estructura"


def main() -> None:
    blob = pic.load("a6000")
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    rows = []
    for ins, reg in store_sites(blob, md):
        near = neighbours(md, blob, ins.address)
        rows.append({"direccion": hex(ins.address), "instruccion": f"{ins.mnemonic} {ins.op_str}", "fuente": MANUAL.get(ins.address) or last_def(md, blob, ins.address, reg),
                     "clase": classify(near)})
    modo = [r for r in rows if r["clase"].startswith("bloque")]
    out = {"campo": hex(OFF), "lector": "0x4389b384 (ldr r0,[r8,#0x6a4] → id de 0x43ae92ee)", "escritores": rows,
           "valores_bloque_de_modo": sorted({r["fuente"].get("inmediato", -1) for r in modo})}
    (HERE / "e19_escritores.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(rows), "escritores;", len(modo), "en el bloque de modo", file=sys.stderr)


if __name__ == "__main__":
    main()
