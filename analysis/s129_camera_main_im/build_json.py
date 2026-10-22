#!/usr/bin/env python3
"""S129 — construye `camera_main_im.json` a partir de los bytes y del mapa PIC estricto.

Recomputa cadenas, sitios y funciones (prólogo Thumb corregido a mano con la entrada
real: los sitios que caen en funciones con preámbulo PC-relativo antes del `push`).

Uso: .venv/bin/python analysis/s129_camera_main_im/build_json.py
"""
import json
import os
import re
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = "[CAMERA_MAIN_IM]: "

# función -> (prólogo detectado, entrada real, papel verificado)
FUNCS = {
    0x43547362: (0x43547362, 0x43547362, "diferencial térmico movie (dos int16 globales)"),
    0x437b8774: (0x437b8774, 0x437b8774, "comprobación térmica periódica (tablas movie/bulb/still, Abs/Env)"),
    0x437b8e1c: (0x437b8e1c, 0x437b8e1c, "instantánea EcGain/isoAuto/bulb por mensaje"),
    0x437b8ed4: (0x437b8ed6, 0x437b8ed4, "StartImThermal (alloc+set timer)"),
    0x437b8fb0: (0x437b8fb2, 0x437b8fb0, "EndImThermal (free timer + sendCaution(false))"),
    0x437b9064: (0x437b906a, 0x437b9064, "RecStart / ImStartMovThermal"),
    0x437b915c: (0x437b9162, 0x437b915c, "RecEnd / ImEndMovThermal (+ Timer2Callback)"),
    0x437b91e8: (0x437b91ea, 0x437b91e8, "callback de temporizador (TimeA ImgTmp)"),
    0x437b93c0: (0x437b93c0, 0x437b93c0, "consulta ZitZ1cDriver"),
    0x4386bbec: (0x4386bbee, 0x4386bbec, "validación ZitDdcDriver"),
}

DISPATCH_TABLE = 0x43befc32
DISPATCH_FUNC = 0x437b8384


def read_strings(data, prefix=PREFIX):
    out = []
    start = 0
    while True:
        i = data.find(prefix.encode(), start)
        if i < 0:
            break
        e = data.find(b"\0", i)
        out.append((BASE + i, data[i:e].decode("latin1")))
        start = i + 1
    return out


def interior(text):
    return text.split(": ", 1)[1]


def whole_strings(path):
    d = open(path, "rb").read()
    return set(m.group().decode("latin1") for m in re.finditer(rb"[^\x00]+", d))


def main():
    data = open(BIN, "rb").read()
    g = json.load(open(GLOBAL))
    strings = read_strings(data)

    rows, by_func = [], {}
    for vaddr, text in strings:
        sites = [int(x) for x in g.get(f"0x{vaddr:x}", [])]
        for s in sites:
            cand = [f for f in FUNCS if f <= s]
            f = max(cand) if cand else None
            rows.append({"vaddr": f"0x{vaddr:x}", "text": text,
                         "interior": interior(text), "site": f"0x{s:x}",
                         "func_entry": f"0x{f:x}" if f else None})
            by_func.setdefault(f, []).append(s)

    funcs = []
    for f, (pro, real, role) in sorted(FUNCS.items()):
        sites = sorted(by_func.get(f, []))
        texts = [r["text"] for r in rows if r["func_entry"] == f"0x{f:x}"]
        funcs.append({"entry": f"0x{real:x}", "prologue": f"0x{pro:x}",
                      "role": role, "n_sites": len(sites),
                      "sites": [f"0x{s:x}" for s in sites],
                      "strings": texts})

    # tabla del despachador: 24 pares u16 {id, código}
    ids = []
    for i in range(0x18):
        mid, code = struct.unpack_from("<HH", data, DISPATCH_TABLE - BASE + 4 * i)
        ids.append({"id": f"0x{mid:04x}", "code": f"0x{code:02x}"})

    a7s, a6300 = whole_strings(A7S), whole_strings(A6300)
    diff = {
        "a6000_strings": len(strings),
        "a7s_with_prefix": 0, "a6300_with_prefix": 0,
        "a7s_interior_exact": sum(1 for _, t in strings if interior(t) in a7s),
        "a6300_interior_exact": sum(1 for _, t in strings if interior(t) in a6300),
        "a7s_interior_missing": [interior(t) for _, t in strings if interior(t) not in a7s],
        "a6300_interior_missing": [interior(t) for _, t in strings if interior(t) not in a6300],
    }

    doc = {
        "milestone": "S129",
        "module": "[CAMERA_MAIN_IM]",
        "firmware": "A6000 fw3.21",
        "binary": BIN,
        "base_vaddr": "0x43541000",
        "counts": {"strings": len(strings), "sites": len(rows),
                   "functions": len(funcs), "unreferenced": 0},
        "method": {
            "pic_rule": "regla canónica estricta de analysis/s106_imaging_cap/"
                        "pic_refs_strict_global.json (ldr rX,[pc,#imm] + add rX,pc, "
                        "ver analysis/s106_imaging_cap/pic_xref_methodology.md)",
            "function_attribution": "prólogo Thumb más cercano hacia atrás, corregido a la "
                                    "entrada real cuando la función tiene preámbulo PC-relativo "
                                    "antes del push (0x437b8ed4, 0x437b8fb0, 0x437b9064, "
                                    "0x437b915c, 0x437b91e8, 0x4386bbec)",
        },
        "strings": rows,
        "functions": funcs,
        "dispatch": {
            "function": f"0x{DISPATCH_FUNC:x}",
            "table": f"0x{DISPATCH_TABLE:x}",
            "n_entries": 0x18,
            "lookup": "id de 16 bits en [ctx+0x10] -> código de sección de 8 bits",
            "reverse_default": "0xa00 (0x437b8404 mov.w r3,#0xa00)",
            "entries": ids,
        },
        "support": {
            "logger_private": "0x437b85ac",
            "logger_args": "r0=3 (nivel), r1=0x10, r2=bit de máscara, r3=cadena",
            "mask_predicate": "0x437b848c",
            "printf_generic": "0x43902718",
            "timer_alloc": "0x437b86ac",
            "timer_set": "0x437b84a8",
            "timer_free": "0x437b84f0",
            "osal_snd_msg": "0x43561244",
            "osal_alloc": "0x4356127c",
        },
        "relation_s115": {
            "imager_ctx_getter": "0x436d6118",
            "temperature_wrapper": "0x436d648c",
            "call_sites": ["0x437b877a", "0x437b8780"],
            "vtable_slot": "0x6c",
            "buffer": "float en [sp,#0x34]",
            "scale": "vmul.f32 por 0x42c80000 (100.0f) + 0.5 -> entero (centésimas)",
            "name_candidates": ["0x43c932d4 GetImagerTemperatureAD(unsigned short*)",
                                "0x43c936a3 GetImagerTemperature(float*)",
                                "0x43c93773 GetImagerTemperature(unsigned short*)"],
            "slot_family": {"0x68": "0x436d6478", "0x6c": "0x436d648c",
                            "0x70": "0x436d64c8 (llamado con buffer ushort: "
                                    "ldrh/strh en 0x438c7994)"},
        },
        "relation_s124": {
            "drive_mode_shifts": "+0 PrevDrv, +4 NowDrv, +6 NextDrv, +9 shut (S124)",
            "thermal_reads": ["0x437b87f6 ldrb r3,[r4,#6]", "0x437b87fe ldrb r5,[r4,#4]"],
            "same_struct": "NO VERIFICADO",
        },
        "diff": diff,
        "unverified": [
            "invocación de 0x437b8774: 0 bl, 0 punteros de 32 bits, 0 desplazamientos de 16 bits",
            "correspondencia exacta del slot 0x6c con el nombre GetImagerTemperature(float*)",
            "que el contexto leído en 0x437b8774 sea el mismo struct de S124",
            "significado de los 24 ids del despachador y del código 0x1e0",
            "quién envía los mensajes 0xa20/0xa21/0xac0",
            "fichero fuente del módulo (no hay *Thermal*.cpp en el binario)",
        ],
    }
    out = os.path.join(HERE, "camera_main_im.json")
    json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"{out}: {len(strings)} cadenas, {len(rows)} sitios, {len(funcs)} funciones, "
          f"diff A7S {diff['a7s_interior_exact']}/42 A6300 {diff['a6300_interior_exact']}/42")


if __name__ == "__main__":
    main()
