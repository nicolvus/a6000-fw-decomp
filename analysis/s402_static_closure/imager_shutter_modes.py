"""Modos de obturador (`params[+9]`, 0..4) de SetExposure: IMX210 (A6000) frente a IMX235 (A7S).

Ambos drivers despachan con `tbb` sobre ese byte. A6000 tiene cuerpo para los cinco valores; A7S manda el valor 2
a la rama «ShutMode:%d is not supported.». Los significados eléctricos de los bits no se infieren."""

import json
from pathlib import Path

import s402_fw as fw
import rawfw
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

OUT = Path(__file__).with_name("imager_shutter_modes.json")
SWITCH = {"A6000": (0x436D70C6, 0x436D70CA), "A7S": (0x436F4242, 0x436F4246)}  # tbb, tabla
PARAM_LOAD = {"A6000": (0x436D6FB6, "ldrb.w sb, [r1, #9]"), "A7S": (0x436F4198, "ldrb.w r6, [sl, #9]")}


def case_targets(lib, tbb: int, table: int) -> list:
    return [table + 2 * lib.e.read(table + i, 1)[0] for i in range(5)]


def head(lib, address: int, count: int = 14) -> list:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [f"{i.mnemonic} {i.op_str}" for i in decoder.disasm(lib.e.read(address, 4 * count), address, count=count)]


def build() -> dict:
    out: dict = {"limits": "Significado eléctrico de los bits (registros sombra +2 / +4) NO_VERIFICADO."}
    for model, (tbb, table) in SWITCH.items():
        lib = rawfw.RawLib(model)
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        load_address, load_text = PARAM_LOAD[model]
        ins = next(decoder.disasm(lib.e.read(load_address, 4), load_address, count=1))
        targets = case_targets(lib, tbb, table)
        out[model] = {"tbb": hex(tbb), "param_load": f"{ins.mnemonic} {ins.op_str}", "param_load_ok": f"{ins.mnemonic} {ins.op_str}" == load_text,
                      "case_targets": [hex(t) for t in targets], "case_heads": {str(i): head(lib, t, 10) for i, t in enumerate(targets)}}
    # A7S: el caso 2 debe ser la rama de error; se comprueba la cadena en el cuerpo de ese destino.
    b = rawfw.RawLib("A7S")
    text = [x[2] for x in fw.normalize(b, int(out["A7S"]["case_targets"][2], 16), int(out["A7S"]["case_targets"][2], 16) + 0x30) if x[0] == "picref"]
    out["A7S"]["case2_strings"] = text
    out["A7S"]["case2_unsupported"] = any("not supported" in t for t in text)
    out["A6000"]["case2_sets_bits"] = [i for i in out["A6000"]["case_heads"]["2"] if i.startswith(("orr", "bfc"))]
    return out


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(data["A6000"]["case_targets"], data["A7S"]["case_targets"], data["A7S"]["case2_unsupported"], data["A6000"]["case2_sets_bits"])
