"""Origen estático del selector Silent de A7S (root+0x78c) y su único campo de entrada `+0x250`.

av-cam A7S fw3.20, base 0x43541000. Complementa analysis/s401_a7s_caif (que fija el bit 0x20 de payload[0x12])."""

import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"
A6000 = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
OUT = Path(__file__).with_name("a7s_silent_selector.json")
DECODER = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
DECODER.detail = True

EXPECTED = {  # dirección -> texto Capstone
    0x4379EC24: "cmp r0, #1", 0x4379EC2C: "ldr.w r0, [r2, r0, lsl #2]", 0x4379EC38: "ldrb.w r3, [r3, #0x7a]",
    0x4379EC44: "bl #0x438f7114", 0x4379EC48: "movs r0, #2",
    0x43813E90: "ldr.w r0, [r3, #0x250]", 0x43813E94: "bl #0x4379ec04", 0x43813E98: "cmp r0, #2",
    0x43813E9A: "str.w r0, [r4, #0x78c]", 0x43813EA2: "str.w r3, [r4, #0x748]",
    0x437B6F70: "ldr.w r0, [r3, #0x250]", 0x437B6F74: "bl #0x4379ec04", 0x437B6F7E: "str.w r0, [r7, #0x7e8]",
    # manejador LIRO 0x40e3 de A7S: byte +8 del comando -> bloque de ajustes +0x250
    0x437A9CB0: "ldr r3, [pc, #0xc]", 0x437A9CB2: "ldrb r2, [r0, #8]", 0x437A9CB4: "movs r0, #1",
    0x437A9CB6: "add r3, pc", 0x437A9CB8: "str.w r2, [r3, #0x250]",
    # InitSettingsDefaults: pone a cero el campo en el mismo bloque
    0x437AAE4E: "movs r5, #0", 0x437AAFC4: "str.w r5, [r4, #0x250]",
}
LIBOBJ_EXPECTED = {  # libObj.so A7S: CamUser::SequenceSetSilentShutterMode (0x93a078)
    0x93A0AE: "movs r2, #9", 0x93A0B2: "blx #0xe178c", 0x93A0BC: "movw r0, #0x40e3", 0x93A0C0: "bl #0x9334fc",
    0x93A0D2: "bl #0x881c34",
}
TABLE_ROW_A7S = 0x43FF79E4  # {cmd u16, flags u16, handler, pad}
TABLE_ROW_A6000 = 0x43FFFC60
G_BLOCK = 0x43EA1D84


def at(image: bytes, address: int) -> str:
    ins = next(DECODER.disasm(image[address - BASE:address - BASE + 4], address, count=1))
    return f"{ins.mnemonic} {ins.op_str}"


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - BASE)[0]


def pic(image: bytes, load: int, add: int) -> int:
    ins = next(DECODER.disasm(image[load - BASE:load - BASE + 4], load, count=1))
    pool = ((load + 4) & ~3) + ins.operands[1].mem.disp
    return (u32(image, pool) + add + 4) & 0xFFFFFFFF


def libobj_checks() -> dict:
    import s402_fw as fw

    lib = fw.Lib("A7S")
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    bad = {}
    for address, text in LIBOBJ_EXPECTED.items():
        ins = next(decoder.disasm(lib.e.read(address, 4), address, count=1))
        if f"{ins.mnemonic} {ins.op_str}" != text:
            bad[hex(address)] = f"{ins.mnemonic} {ins.op_str}"
    names = [b"N7CamUser28SequenceSetSilentShutterModeE", b"MSGID_SET_SILENT_SHUTTER_MODE_CMD",
             b"VALUEID_SILENT_SHUTTER_ON", b"VALUEID_SILENT_SHUTTER_OFF", b"PARAMID_SILENT_SHUTTER_MODE"]
    return {"instruction_mismatches": bad, "strings_present": {n.decode(): n in lib.e.data for n in names}}


def build() -> dict:
    image, other = A7S.read_bytes(), A6000.read_bytes()
    row = struct.unpack_from("<HHII", image, TABLE_ROW_A7S - BASE)
    row6 = struct.unpack_from("<HHII", other, TABLE_ROW_A6000 - BASE)
    handler_block = pic(image, 0x437A9CB0, 0x437A9CB6)  # ldr r3,[pc]; add r3,pc
    mismatches = {hex(a): (at(image, a), t) for a, t in EXPECTED.items() if at(image, a) != t}
    table = pic(image, 0x4379EC28, 0x4379EC2A)  # ldr r2,[pc]; add r2,pc
    singleton = pic(image, 0x437B38EC, 0x437B38EE)
    text = pic(image, 0x4379EC3E, 0x4379EC42)
    raw = image[text - BASE:image.index(b"\0", text - BASE)].decode()
    return {
        "selector_function": "0x4379ec04",
        "table": {"address": hex(table), "entries": [u32(image, table), u32(image, table + 4)]},
        "debug_force_flag": {"address": "0x43ea3182", "effect": "si distinto de 0: registra el tipo 2 y devuelve 2"},
        "log_string": {"address": hex(text), "text": raw},
        "setting_singleton": hex(singleton),
        "callers": {"0x43813e94": "root+0x78c = F(**S+0x250, ctx); si 2 -> root+0x748 = 1",
                    "0x437b6f74": "ctx2+0x7e8 = F(**S+0x250, ctx)"},
        "input_field": "S[0]+0x250 (u32; 0 o 1 -> 0 o 2)",
        "liro_command": {"a7s_row": {"address": hex(TABLE_ROW_A7S), "cmd": hex(row[0]), "handler": hex(row[2])},
                         "a6000_row": {"address": hex(TABLE_ROW_A6000), "cmd": hex(row6[0]), "handler": hex(row6[2])},
                         "a7s_handler_writes": f"{handler_block + 0x250:#x} = byte comando+8 (bloque G {handler_block:#x})",
                         "settings_block_G": hex(G_BLOCK), "init_defaults": "0x437aae44 pone G+0x250 = 0"},
        "libobj_a7s": libobj_checks(),
        "instruction_mismatches": mismatches,
        "a6000_has_silent_type_string": b"Silent Shutter Type" in other,
        "a7s_has_silent_type_string": b"Silent Shutter Type" in image,
        "limits": ("Falta la escritura S[0] = &G (identidad estricta entre el bloque que escribe 0x40e3 y el que lee "
                   "el contexto raíz): solo hay evidencia estructural (mismas disposiciones +0x250/+0x580 en el "
                   "mismo clúster). El selector admite {0->0, 1->2} y el override de depuración."),
    }


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(data["table"], data["log_string"], data["setting_singleton"], data["instruction_mismatches"], data["a6000_has_silent_type_string"])
