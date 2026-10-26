"""E4: `0x4379d378` es `IsNeedForceS1ON(trig)` (por su cadena de error); clasificación de trig 0–10 y origen del argumento en sus dos llamadores.
Salida: e4_trig.json. Solo bytes originales (Capstone + índice PIC)."""
import json
from pathlib import Path

import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
FN, TABLE_FN = 0x4379D378, 0x4379D364
FORCE_MASK, KEEP_MASK, COND_BIT = 0x708, 0xF3, 4  # de `ands r1,r3,#0x708`, `ands r5,r3,#0xf3`, `tst.w r3,#4`


def text(blob: bytes, addr: int) -> str:
    o = addr - pic.BASE
    return blob[o:o + 120].split(b"\0")[0].decode()


def before(blob: bytes, addr: int) -> str:
    ins = list(CS.disasm(blob[addr - 4 - pic.BASE:addr - pic.BASE], addr - 4))
    return f"{ins[-1].mnemonic} {ins[-1].op_str}"


def main() -> None:
    blob = pic.load("a6000")
    err = next(r for r in pic.pic_refs(blob) if FN <= r["ldr"] < FN + 0x80 and text(blob, r["target"]).startswith("[IMAGING_REL]"))
    classes = {t: "forzar_S1" if (1 << t) & FORCE_MASK else "no_forzar" if (1 << t) & KEEP_MASK else "condicional" if (1 << t) & COND_BIT else "?"
               for t in range(11)}
    out = {
        "cadena_de_error": {"ldr": hex(err["ldr"]), "texto": text(blob, err["target"])},
        "limite_trig": CS.disasm(blob[FN - pic.BASE:FN - pic.BASE + 2], FN).__next__().op_str,
        "clasificacion": classes,
        "llamadores": {hex(s): before(blob, s) for s in pic.branch_sites(blob, FN)},
        "tabla_43ca530e": {"bytes_0_10": list(blob[0x43CA530E - pic.BASE:0x43CA530E - pic.BASE + 11]),
                           "llamadores": {hex(s): before(blob, s) for s in pic.branch_sites(blob, TABLE_FN)}},
    }
    (Path(__file__).with_name("e4_trig.json")).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
