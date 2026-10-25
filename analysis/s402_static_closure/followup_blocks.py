"""Seguimiento S402: bloque de ajustes G (A7S `S[0]`≡G, A6000 `+0x238`) y emisor del mensaje (0x3a49, 0x3026).

Solo bytes originales y Capstone; no se ejecuta firmware. Resultado en followup_blocks.json.
"""

import json
import re
import struct
from collections import defaultdict
from pathlib import Path

import fw
import queue_commands
import rawfw
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

OUT = Path(__file__).with_name("followup_blocks.json")
G = {"A6000": 0x43EDF684, "A7S": 0x43EA1D84}
PCREL = re.compile(r"\[pc, #(-?)(0x[0-9a-f]+|\d+)\]")


def disasm(model: str):
    lib = rawfw.RawLib(model)
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    return lib, list(cs.disasm_lite(lib.e.data, rawfw.BASE))


def anchors(lib, ins, target: int):
    """Índices (ldr literal, add pc) cuyo destino PIC es `target` (± 0x700) y desplazamiento al destino."""
    base = rawfw.BASE
    for i, (a, _, m, o) in enumerate(ins):
        mm = PCREL.search(o)
        if not (m.startswith("ldr") and mm):
            continue
        pool = ((a + 4) & ~3) + int(mm[2], 0) * (-1 if mm[1] else 1)
        if not base <= pool < base + len(lib.e.data) - 3:
            continue
        value, reg = struct.unpack_from("<I", lib.e.data, pool - base)[0], o.split(",")[0]
        for k in range(i + 1, min(i + 6, len(ins))):
            if ins[k][2] == "add" and ins[k][3] == f"{reg}, pc":
                resolved = (value + ins[k][0] + 4) & 0xFFFFFFFF
                if 0 <= target - resolved < 0x700:
                    yield k, reg, target - resolved
                break


def writers_and_readers(model: str, offsets: list[int]) -> dict:
    """Escritores directos (ancla PIC de G) y lectores `ldr rY,[rX]; ldr.w rZ,[rY,#off]` por doble indirección."""
    lib, ins = disasm(model)
    res: dict = {hex(o): {"anchor_stores": [], "double_indirect_reads": []} for o in offsets}
    for off in offsets:
        for k, reg, delta in anchors(lib, ins, G[model] + off):
            for x in ins[k + 1:k + 30]:
                if re.search(rf"\[{reg}, #{hex(delta)}\]", x[3]) and x[2].startswith("str"):
                    res[hex(off)]["anchor_stores"].append(hex(x[0]))
        for i, (a, _, m, o) in enumerate(ins):
            mm = re.fullmatch(r"(\w+), \[(\w+), #(0x[0-9a-f]+)\]", o)
            if mm and m.startswith("ldr") and int(mm[3], 16) == off and any(
                p[2].startswith("ldr") and re.fullmatch(rf"{mm[2]}, \[\w+\]", p[3]) for p in ins[max(0, i - 3):i]
            ):
                res[hex(off)]["double_indirect_reads"].append(hex(a))
    for v in res.values():
        v["anchor_stores"] = sorted(set(v["anchor_stores"]))
    return res


def emitter_3026() -> dict:
    """Constructores `ObjMsg::SetCateIdMsgId(cat, 0x3026)` en libObj A6000 (barrido de .text, movw r2 + llamada)."""
    lib = fw.Lib("A6000")
    text = lib.e.sections[".text"]
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    ins = list(cs.disasm_lite(lib.e.read(text[3], text[5]), text[3]))
    hits: dict = defaultdict(list)
    for i, (a, _, m, o) in enumerate(ins):
        if m != "movw" or o != "r2, #0x3026":
            continue
        call = next((x for x in ins[i + 1:i + 3] if x[2] in ("bl", "blx") and x[3].startswith("#")), None)
        if call and lib.name(int(call[3][1:], 16)) == "_ZN3MWF6ObjMsg14SetCateIdMsgIdEjj":
            cat = next((x[3] for x in ins[max(0, i - 3):i] if x[2] == "movw" and x[3].startswith("r1,")), "?")
            hits[hex(lib.fstart(a))].append({"site": hex(a), "cat": cat.split("#")[-1]})
    callers = [hex(a) for a, _, m, o in ins if m in ("bl", "blx") and o in {f"#{k}" for k in hits}]
    return {"constructores": dict(hits), "llamadores": callers}


def _word(lib, va: int) -> int:
    return struct.unpack("<I", lib.e.read(va, 4))[0]


def _literal(lib, pc: int, offset: int) -> int:
    """Valor del literal de `ldr rX, [pc, #offset]` situado en `pc`."""
    return _word(lib, ((pc + 4) & ~3) + offset)


def sequence_class_3026() -> dict:
    """Clase que la factoría `0x3a9a80` asocia al id 0x3026: creador `0x3a7978` → constructor → typeinfo."""
    lib = fw.Lib("A6000")
    creator = _word(lib, (_literal(lib, 0x3A9684, 0x10) + 0x3A968C + 4 + _literal(lib, 0x3A9688, 0x10)) & 0xFFFFFFFF) & ~1
    got = (_literal(lib, 0x3D3134, 0x38) + 0x3D313E + 4 + _literal(lib, 0x3D313C, 0x34)) & 0xFFFFFFFF
    typeinfo = _word(lib, _word(lib, got) + 4)
    offset = lib.e.offset(_word(lib, typeinfo + 4))
    name = lib.e.data[offset:lib.e.data.index(b"\0", offset)].decode()
    return {"creador": hex(creator), "constructor": "0x3d3130", "typeinfo": name}


def pb_action_events() -> dict:
    """Eventos del estado 4 de `ModelScalarPb` que llevan a la acción 13 y estado/acción 6 de `ModelPbCap`."""
    lib = fw.Lib("A6000")
    pool = {a: _literal(lib, a, o) for a, o in [
        (0x65BA78, 0x88), (0x65BA84, 0x80), (0x65BA8C, 0x7C), (0x65BA90, 0x7C), (0x65BA96, 0x7C), (0x65BA9E, 0x78),
        (0x65BAA4, 0x74), (0x65BAAA, 0x74)]}
    entry = lib.e.read(0x613182, 6)
    return {
        "ModelScalarPb_estado4_accion13": {
            "locales": ["0x4", "0x109"],
            "mensajes": [hex(pool[a]) for a in (0x65BA84, 0x65BA90, 0x65BA9E)],
            "accion13": "0x65bd0a -> 0x65bc38 -> 0x65b0bc (emisor 0x659cb0)",
        },
        "ModelPbCap_accion6": {
            "estado_de_entrada": [i for i, b in enumerate(entry) if 0x613182 + 2 * b == 0x6131B2],
            "transicion": "estado 2, evento local 2, guardia 0x61320c -> estado 5 (0x61343a)",
        },
    }


IMM = re.compile(r"r\d+, #(0x[0-9a-f]+|\d+)$")
MOVES = ("movs", "mov.w", "movw", "mov")
# Constructor de id (0x120168) y envoltorios que lo llaman; valor = registro con el evento local.
POSTERS = {0x120168: "r2", 0x420630: "r1", 0x420656: "r1", 0x132230: "r1", 0x131eb0: "r1", 0x131f28: "r2", 0x131f76: "r2"}
MESSAGE_CATEGORY = {0x1004: 0x3500, 0x3002: 0x3500, 0x4026: 0x3A49}


def _imm(operands: str, reg: str = "") -> int | None:
    """Inmediato de `rN, #imm` (si se indica `reg`, solo para ese registro)."""
    match = IMM.match(operands)
    return int(match[1], 0) if match and operands.startswith(f"{reg}") else None


def _code(lib) -> list:
    """Instrucciones de .text de libObj; shortcut: se descarta lo posterior a 0x700000 (datos), válido solo para A6000 fw3.21."""
    text = lib.e.sections[".text"]
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.skipdata = True
    return [i for i in decoder.disasm_lite(lib.e.read(text[3], text[5]), text[3]) if i[0] < 0x700000]


def local_posts_in(low: int, high: int) -> dict:
    """Funciones de [low, high) que publican un evento local inmediato (id = 0x12000000 + modelo<<12 + local)."""
    lib = fw.Lib("A6000")
    ins = _code(lib)
    found: dict = defaultdict(set)
    for i, (a, _, m, o) in enumerate(ins):
        reg = POSTERS.get(int(o[1:], 16)) if low <= a < high and m in ("bl", "blx", "b.w") and o.startswith("#") else None
        imm = next((_imm(x[3], f"{reg},") for x in reversed(ins[max(0, i - 12):i])
                    if reg and x[2] in MOVES and _imm(x[3], f"{reg},") is not None), None)
        if imm is not None:
            found[hex(imm)].add(hex(lib.fstart(a)))
    return {k: sorted(v) for k, v in sorted(found.items(), key=lambda kv: int(kv[0], 16))}


def message_constructors() -> dict:
    """Funciones que cargan a la vez la categoría y el id de los mensajes 0x35001004, 0x35003002 y 0x3a494026."""
    lib = fw.Lib("A6000")
    ins = _code(lib)
    found: dict = defaultdict(set)
    for i, (a, _, m, o) in enumerate(ins):
        message = _imm(o) if m in MOVES else None
        if message in MESSAGE_CATEGORY and any(
                x[2] in MOVES and _imm(x[3]) == MESSAGE_CATEGORY[message] for x in ins[max(0, i - 8):i + 8]):
            found[hex(message)].add(hex(lib.fstart(a)))
    return {k: sorted(v) for k, v in found.items()}


MODEL_ENTRY = re.compile(rb"@M([0-9A-F]{3})\0model(\w+)\.so\0")
SELF_POSTERS = (0x420630, 0x420656, 0x120168)
MODEL_GETTER = "#0x10cf18"  # devuelve this+0x18, el número de modelo propio
SELF_EMITTERS = {2: [0x4AE6AC, 0x50FB42, 0x5E2F20, 0x699BA4], 4: [0x5A760C, 0x5A7C54, 0x621440, 0x6B2690]}


def model_ids() -> dict:
    """Tabla `@Mnnn` → módulo; `IdGenerator::Get` (0x12d670) decodifica esos tres dígitos como el número de modelo."""
    return {m[2].decode(): int(m[1], 16) for m in MODEL_ENTRY.finditer(fw.Lib("A6000").e.data)}


def explicit_model_posts() -> list:
    """Funciones que publican un evento sin tomar el modelo de `this+0x18` (única vía cruzada posible)."""
    lib = fw.Lib("A6000")
    ins = _code(lib)
    return sorted({hex(lib.fstart(a)) for i, (a, _, m, o) in enumerate(ins)
                   if m in ("bl", "blx", "b.w") and o.startswith("#") and int(o[1:], 16) in SELF_POSTERS
                   and not any(x[2] in ("bl", "blx") and x[3] == MODEL_GETTER for x in ins[max(0, i - 12):i])})


def self_emitter_owners() -> dict:
    """Clase propietaria (vtable) de cada emisor inmediato del local 2 y del 4: publica a su propio modelo."""
    lib = fw.Lib("A6000")
    ins = _code(lib)
    owners: dict = {}
    for local, functions in SELF_EMITTERS.items():
        for function in functions:
            callers = {lib.fstart(a) for a, _, m, o in ins if m in ("bl", "blx", "b.w") and o == f"#{hex(function)}"}
            owners.setdefault(str(local), set()).update(
                queue_commands.vtable_class(lib, slot) for caller in callers for slot in lib.e.word_hits(caller | 1))
    return {k: sorted(v) for k, v in owners.items()}


def main() -> None:
    a7s = writers_and_readers("A7S", [0x250, 0x56C, 0x570])
    a6000 = writers_and_readers("A6000", [0x238])
    emitters = emitter_3026()
    result = {
        "A7S_G_0x43ea1d84": a7s,
        "A6000_G_0x43edf684": a6000,
        "emisor_ObjMsg_cat_0x3026": emitters,
        "secuencia_0x3026": sequence_class_3026(),
        "eventos_Pb": pb_action_events(),
        "eventos_locales_Pb": local_posts_in(0x659000, 0x65F000),
        "eventos_locales_PbCap": local_posts_in(0x613000, 0x615000),
        "constructores_de_mensaje": message_constructors(),
        "ids_de_modelo": {k: hex(v) for k, v in model_ids().items() if k in ("ScalarPb", "PbCap")},
        "publicadores_con_modelo_explicito": explicit_model_posts(),
        "propietarios_emisores_locales_2_4": self_emitter_owners(),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
