"""Comandos que libObj envía por la cola 0x40193 y su tabla de despacho en LIRO (av-cam).

Los ocho wrappers de libObj (`osal_snd_msg` a 0x40193) construyen un mensaje de 16 bytes: comando u16 en +2/+3,
código de modo en +8. LIRO consume en el bucle 0x4381d16c con 35 filas {comando, manejador, ajuste} en 0x44000174.
"""

import json
import re
import struct
import subprocess
from pathlib import Path

import fw
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
TABLE, ROWS = 0x44000174, 35
WRAPPERS = [0xAF9264, 0xAF92D8, 0xAF934C, 0xAF93BC, 0xAF9C88, 0xAF9CE8, 0xAF9D48, 0xAF9DA8]
OUT = Path(__file__).with_name("queue_40193_commands.json")


def wrapper_commands(lib: fw.Lib) -> dict:
    rows = {}
    for start in WRAPPERS:
        by_arg = {}
        for arg in (0, 1, 2):
            ok, buf, _ = fw.run_wrapper(lib, start, arg)
            assert ok and buf[2] is not None and buf[3] is not None
            by_arg[arg] = {"command": hex(buf[2] | buf[3] << 8), "mode_byte8": hex(buf[8]), "payload_byte0": hex(buf[0])
                           if 0 in buf else None}
        rows[hex(start)] = by_arg
    return rows


def liro_table() -> list:
    image = AVCAM.read_bytes()
    return [dict(zip(("command", "handler", "adjust"), map(hex, struct.unpack_from("<III", image, TABLE - BASE + 12 * i))))
            for i in range(ROWS)]


def callers(lib: fw.Lib) -> dict:
    """BL/B.W a cada wrapper (barrido lineal de .text) y clase propietaria de los métodos que los contienen."""
    text = lib.e.sections[".text"]
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    decoder.skipdata = True
    targets = {f"#{hex(w)}": w for w in WRAPPERS}
    sites: dict[str, list[int]] = {hex(w): [] for w in WRAPPERS}
    for address, _, mnemonic, ops in decoder.disasm_lite(lib.e.read(text[3], text[5]), text[3]):
        if mnemonic in ("bl", "blx", "b.w") and ops in targets:
            sites[hex(targets[ops])].append(address)
    functions = sorted({lib.fstart(a) for v in sites.values() for a in v})
    classes: dict[str, list[str | None]] = {}
    for function in functions:
        for slot in lib.e.word_hits(function | 1):
            classes.setdefault(hex(function), []).append(vtable_class(lib, slot))
    return {"sites": {k: [hex(a) for a in v] for k, v in sites.items()},
            "functions": [hex(f) for f in functions], "vtable_owner": classes}


def vtable_class(lib: fw.Lib, slot: int) -> str | None:
    """Clase de la vtable que contiene el slot: palabra 0 (offset_to_top) seguida de typeinfo con nombre mangled."""
    for back in range(4000):
        address = slot - 4 * back
        try:
            first, second = lib.e.u32(address), lib.e.u32(address + 4)
            name = lib.cstr(lib.e.u32(second + 4))
        except (ValueError, struct.error):
            continue
        if first == 0 and name and re.fullmatch(r"\d+[A-Za-z_][\w:]*|N[\w]+E", name):
            return subprocess.run(["c++filt", "_ZTS" + name], capture_output=True, text=True, check=False).stdout.strip()[len("typeinfo name for "):]
    return None


def reply_queue_classes() -> dict:
    """0x4379d2ec clasifica la cola de respuesta del solicitante; 0x4379d328 lleva contadores de serie por clase."""
    image = AVCAM.read_bytes()
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    literals = {0x4379D2EC: 0x1502C7, 0x4379D2FA: 0x40193, 0x4379D302: 0xFFD9FE7B}
    checked = {}
    for address, expected in literals.items():
        ins = next(decoder.disasm(image[address - BASE:address - BASE + 4], address, count=1))
        pool = ((address + 4) & ~3) + int(ins.op_str.split("#")[1].rstrip("]"), 0)
        checked[hex(address)] = struct.unpack_from("<I", image, pool - BASE)[0] == expected
    return {"literals_ok": checked, "classes": {"0x1502c7": 1, "0x40193": 1, "0x20002": 2, "0x260185/0x260186": 3, "otras": 4},
            "serial_counters": {"class_1": "this+0xc80", "class_3": "this+0xc84"},
            "handlers": {"0x4042": "0x4379e47c clase 3, flags 1/0", "0x4043": "0x4379e3fc clase 4",
                         "0x4044": "0x43aeaa4a clase 1, traza 0x3003 por 0x43901a8c", "0x4045": "0x43aea9f0 clase 2, traza 0x3004 por 0x43901a8c"}}


def build() -> dict:
    lib = fw.Lib("A6000")
    table = liro_table()
    commands = wrapper_commands(lib)
    sent = sorted({row["command"] for rows in commands.values() for row in rows.values()})
    return {"wrappers": commands, "commands_sent": sent,
            "liro_rows_for_sent_commands": [r for r in table if r["command"] in sent], "liro_table_rows": len(table),
            "callers": callers(lib), "reply_queue_classification": reply_queue_classes(),
            "limits": ("Contenido semántico de cada código de modo (+8) y condición de uso NO_VERIFICADO; la "
                       "recepción en ejecución no se observó. Ver tareas de RelMgr (0x4379d2ec)."), }


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(data["commands_sent"], len(data["callers"]["functions"]), {c for v in data["callers"]["vtable_owner"].values() for c in v})
