#!/usr/bin/env python3
"""S123 — extrae la constante de **estado** que cada etapa del control de captura
escribe en el objeto (`strb rX, [r?, #0xb]`).

Las 20 funciones que emiten las trazas `[CAMERA_MAIN_CC]: <M>()` delegan en una
función de etapa distinta; cada una de esas etapas fija un byte de estado en el
objeto (offset 0xb) antes de ejecutar su parte.

Uso:  stage_states.py
"""
import json
import os
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# método CC -> función de etapa (extraído del grafo de llamadas)
STAGES = {
    "ExtractCaptureData()": 0x43aeb2ae,
    "CaptureInit()": 0x43aeb2ec,
    "SetReadImageParam()": 0x43aeb324,
    "SetNRParam()": 0x43aeb358,
    "SetOPDParam()": 0x43aeb3a6,
    "AfterOPDAfterNR()": 0x43aeb3f8,
    "SetDevelopParam()": 0x437a1314,
    "SetDevDetectDevelopParam()": 0x43aeb472,
    "DetectYC()": 0x43aeb4ca,
    "SetDualRecParam()": 0x43aeb50e,
    "SetDAEParam()": 0x43aeb564,
    "SetSACCParam()": 0x43aeb568,
    "WriteExifMakernote()": 0x43aeb5a6,
    "SetPlayRawDevDetectDevelop": 0x43aeb5ca,
    "SetPlayRawDevelopParam()": 0x43aeb5e8,
    "SetReviewDevelopParam()": 0x43aeb606,
    "WriteSACCMakerNote()": 0x437a16a4,
}


def main():
    dest = os.path.join(HERE, "stage_states.json")
    data = open(BIN, "rb").read()
    out = []
    for name, addr in STAGES.items():
        fh = open(BIN, "rb")
        fh.seek(addr - BASE)
        code = fh.read(0x400)
        fh.close()
        state = None
        last_movs = None
        ctx = []
        for ins in md.disasm(code, addr):
            if ins.mnemonic == "movs" and ins.op_str.startswith("r2, #"):
                last_movs = ins.op_str
            if ins.mnemonic == "strb" and "#0xb]" in ins.op_str:
                state = {"insn": f"{ins.address:#x} {ins.mnemonic} {ins.op_str}",
                         "r2_inmediato": last_movs,
                         "ctx": ctx[-4:]}
                break
            ctx.append(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}")
            if ins.mnemonic == "pop" and "pc" in ins.op_str:
                break
        out.append({"method": name, "stage_func": f"0x{addr:x}", "state": state})
        print(f"{name:32s} stage=0x{addr:x}  r2={state and state['r2_inmediato']}  "
              f"{state and state['insn']}")
    json.dump({"module": "CAMERA_MAIN_CC", "stages": out},
              open(dest, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
