"""Productor de 0x10000005 (MSGID_RECORD_IMAGE_CALL): lo crea ObjStillRecorder al recibir un PlayData 0x1003.

Cadena estática verificada contra bytes de libObj.so A6000 fw3.21 (VA del ELF, sin sesgo REA +0x10000).
"""

import json
import struct
from pathlib import Path

import s402_fw as fw
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

OUT = Path(__file__).with_name("producer_10000005.json")
MSG = 0x10000005


def constructor_sites(lib: fw.Lib) -> list:
    """Cargas literales de MSG seguidas de MWF::ObjMsg::ObjMsg(buf, categoría, id): la categoría sale de r1."""
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.detail = True
    decoder.skipdata = True
    rows = []
    for pool in lib.e.word_hits(MSG):
        code = lib.e.read(pool - 0x1000, 0x1000)
        for ins in decoder.disasm(code, pool - 0x1000):
            if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str and ((ins.address + 4) & ~3) + ins.operands[1].mem.disp == pool:
                around = list(decoder.disasm(lib.e.read(ins.address - 12, 24), ins.address - 12))
                calls = [lib.name(int(i.op_str[1:], 16)) for i in around if i.mnemonic in ("bl", "blx") and i.op_str.startswith("#")]
                category = next((int(i.op_str.split("#")[1], 0) for i in reversed(around)
                                 if i.address < ins.address and i.mnemonic in ("mov.w", "movw", "movs") and i.op_str.startswith("r1,")), None)
                rows.append({"load": hex(ins.address), "function": hex(lib.fstart(ins.address)), "register": ins.op_str.split(",")[0],
                             "category_r1": hex(category) if category is not None else None, "calls_nearby": calls})
    return rows


def state_row(lib: fw.Lib) -> dict:
    row = 0x101F11C
    return dict(zip(("state", "message", "check", "call", "next_state_function", "next_state"),
                    map(hex, struct.unpack_from("<6I", lib.e.read(row, 24)))))


def handler_branch(lib: fw.Lib) -> list:
    """0x919ca0: GetMessageId == 0x1003 -> ObjMsg(0x3500, 0x10000005) con AddParam(0x10000006, mensaje recibido)."""
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [f"{i.address:#x} {i.mnemonic} {i.op_str}" for i in decoder.disasm(lib.e.read(0x919F1C, 0x40), 0x919F1C)]


def pbcap_chain(lib: fw.Lib) -> dict:
    """ModelPbCap: Action(idx 6) -> 0x6137b0 -> ObjMsg(0x3500,0x3001){0x1005=0} -> IssueCommandAsync."""
    table = 0x614158
    index6 = struct.unpack("<H", lib.e.read(table + 12, 2))[0]
    target = table + 2 * index6
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    stub = next(decoder.disasm(lib.e.read(target, 8), target, count=2))
    body = [f"{i.address:#x} {i.mnemonic} {i.op_str}" for i in decoder.disasm(lib.e.read(0x6137B0, 0x40), 0x6137B0)]
    vtable_slot = 0x101242C
    return {"action_dispatcher": hex(0x61414C), "vtable_slot_word": hex(lib.e.u32(vtable_slot)), "tbh_entry_6_target": hex(target),
            "stub": f"{stub.mnemonic} {stub.op_str}", "body_head": body[:20]}


def build() -> dict:
    lib = fw.Lib("A6000")
    sites = constructor_sites(lib)
    ctor = [s for s in sites if "_ZN3MWF6ObjMsgC1Ejj" in s["calls_nearby"] and s["category_r1"] == "0x3500"]
    return {"state_row": state_row(lib), "sites_loading_message": sites, "constructors_in_category_0x3500": ctor,
            "handler_0x919ca0_branch_0x1003": handler_branch(lib), "pbcap": pbcap_chain(lib),
            "limits": ("Se verifica la creación local y la cadena de interfaz PbCap->RecordImage; el evento de UI que "
                       "dispara la transición de ModelPbCap con la acción 6 y el productor del PlayData siguen "
                       "documentados en S13/S14 (ObjEffect pin YC 1) sin observación física.")}


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(data["state_row"], [s["load"] for s in data["constructors_in_category_0x3500"]], data["pbcap"]["tbh_entry_6_target"], data["pbcap"]["stub"])
