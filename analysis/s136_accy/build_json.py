#!/usr/bin/env python3
"""S136 — construye `accy.json` (datos estructurados del módulo `[ACCY]`).

Entrada: `accy_raw.json` (cadenas + sitios + función), `accy_diff.json` (diferencial),
`accy_calls.json` (grafo de llamadas).

Uso: .venv/bin/python analysis/s136_accy/build_json.py
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def subblocks(strings):
    """Sub-bloque ([ACCY][NIVEL][SUB]) de cada cadena."""
    out = []
    for s in strings:
        t = s["text"]
        m = re.match(r"\[ACCY\]\[([A-Z]+)\]\[([A-Za-z0-9_]+)\]", t)
        assert m, t
        out.append({"vaddr": s["vaddr"], "level": m.group(1), "sub": m.group(2),
                    "text": t})
    return out


def main():
    raw = json.load(open(os.path.join(HERE, "accy_raw.json")))
    diff = {d["vaddr"]: d for d in json.load(open(os.path.join(HERE, "accy_diff.json")))}
    calls = json.load(open(os.path.join(HERE, "accy_calls.json")))
    strings = raw["strings"]
    sb = subblocks(strings)

    bysub = defaultdict(list)
    for e in sb:
        bysub[e["sub"]].append(e)

    # función -> trazas
    func2str = defaultdict(list)
    for f, lst in raw["by_func"].items():
        for e in lst:
            func2str[f].append(e)

    # sitios por función (ordenados)
    sites_by_func = defaultdict(list)
    for s in strings:
        for site in s["sites"]:
            sites_by_func[site].append(s["vaddr"])

    # sub-bloque -> rango de strings y rango de sitios
    sub_table = []
    for sub, lst in sorted(bysub.items(), key=lambda kv: kv[1][0]["vaddr"]):
        sites = []
        for e in lst:
            for s in strings:
                if s["vaddr"] == e["vaddr"]:
                    sites += s["sites"]
        funcs = set()
        for site in sites:
            for f, l2 in raw["by_func"].items():
                if any(x["site"] == f"0x{site:x}" for x in l2):
                    funcs.add(f)
        sub_table.append({
            "sub": sub,
            "n_strings": len(lst),
            "string_range": [lst[0]["vaddr"], lst[-1]["vaddr"]],
            "n_sites": len(sites),
            "site_range": [f"0x{min(sites):x}", f"0x{max(sites):x}"],
            "n_functions": len(funcs),
            "functions": sorted(funcs, key=lambda x: int(x, 16)),
            "levels": sorted({e["level"] for e in lst}),
        })

    out = {
        "module": "[ACCY]",
        "model": "A6000 fw3.21",
        "binary": "analysis/rea-independent/input/av-cam.bin",
        "vaddr_base": "0x43541000",
        "xref_rule": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
        "counters": {
            "n_strings": raw["n_strings"],
            "n_referenced": raw["n_referenced"],
            "n_sites": raw["n_sites"],
            "n_functions": raw["n_functions"],
            "n_subblocks": len(sub_table),
            "n_classes_rtti": 9,
            "token_in_a7s": 0,
            "token_in_a6300": 0,
        },
        "string_range": raw["range"],
        "code_range": {
            "trace_core": ["0x43562a08", "0x43566f20"],
            "module_helpers": ["0x4356288c", "0x43567060"],
            "api_wrapper": ["0x43a3ab00", "0x43a3b300"],
        },
        "subblocks": sub_table,
        "strings": [{
            "vaddr": s["vaddr"], "text": s["text"], "n_sites": len(s["sites"]),
            "sites": [f"0x{x:x}" for x in s["sites"]],
            "functions": sorted({f for f, l2 in raw["by_func"].items()
                                 for x in l2 if x["str"] == s["vaddr"]},
                                key=lambda x: int(x, 16)),
            "a7s_core_present": diff[s["vaddr"]]["a7s_core"],
            "a6300_core_present": diff[s["vaddr"]]["a6300_core"],
        } for s in strings],
        "functions": [{
            "func": f,
            "n_sites": len(l2),
            "strings": sorted({x["str"] for x in l2}),
            "texts": [x["text"] for x in l2],
            "sites": [x["site"] for x in l2],
        } for f, l2 in sorted(raw["by_func"].items(), key=lambda kv: int(kv[0], 16))],
        "classes_rtti": [
            {"name": "AccyUmDeviceBase", "name_vaddr": "0x43c2536d",
             "typeinfo": "0x43fd7c8c", "kind": "class", "base": None},
            {"name": "AccyUmDeviceWaterHousing", "name_vaddr": "0x43c2546e",
             "typeinfo": "0x43fd7d6c", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmKeyStatusMgr", "name_vaddr": "0x43c25489",
             "typeinfo": "0x43fd7d78", "kind": "class", "base": None},
            {"name": "AccyUmDeviceAvOut", "name_vaddr": "0x43c254ee",
             "typeinfo": "0x43fd7d80", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmDeviceAvr", "name_vaddr": "0x43c2554e",
             "typeinfo": "0x43fd7d8c", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmDeviceHello", "name_vaddr": "0x43c256f9",
             "typeinfo": "0x43fd7d98", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmDeviceJiro", "name_vaddr": "0x43c25afa",
             "typeinfo": "0x43fd7da4", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmDeviceNull", "name_vaddr": "0x43c25b0d",
             "typeinfo": "0x43fd7db0", "kind": "si", "base": "AccyUmDeviceBase"},
            {"name": "AccyUmDeviceRemote", "name_vaddr": "0x43c26340",
             "typeinfo": "0x43fd7dbc", "kind": "si", "base": "AccyUmDeviceBase"},
        ],
        "rtti_vtables": {"__class_type_info": "0x43fd04f8",
                         "__si_class_type_info": "0x43fd03d8"},
        "accessory_types": {
            "by_id": {"0": "AvOut", "1": "JIRO1.5", "4": "HELLO", "5": "LANC-AVR",
                      "other": "UNSUPPORTED(%d)"},
            "by_bitmask": {"0x80": "Remote", "0x40": "WaterHousing"},
            "factory1": "0x435646a4", "factory2": "0x435647c0",
            "device_factories": {
                "HELLO": "0x43565ac8", "AvOut": "0x435655a4",
                "JIRO1.5": "0x43566074", "LANC-AVR": "0x4356573c",
                "Remote": "0x43566484", "WaterHousing": "0x43564bc0"},
        },
        "transport": {
            "uart": {"open": "0x43563bf8", "close": "0x43563de8",
                     "send": "0x43563ef4", "rx": "0x43563a94"},
            "osal": {"try_valloc_msg": "0x435612d0", "snd_msg": "0x4356120c",
                     "free_msg": "0x435612ec", "rcv_msg": "0x43561260"},
            "notify_input": {"func": "0x43565814", "queue_id": "0x030001ee",
                              "msg_layout": "KeyCode@+0x00, ID@+0x04, State@+0x08, INFO@+0x0c"},
            "notify_dial": {"func": "0x435658dc"},
        },
        "remote_keys": {
            "GUIDE_FRAME_OFF": {"key": "0x0a000009", "str": "0x43c26068",
                                 "site": "0x43566bb2"},
            "START_STOP_OFF": {"key": "0x0a00000d", "str": "0x43c260b0",
                               "site": "0x43566be8"},
            "PHOTO_FREEZE_OFF": {"key": "0x0a000008", "str": "0x43c260f7",
                                 "site": "0x43566c24"},
            "PHOTO_REC_OFF": {"key": "0x0a00000c", "str": "0x43c26140",
                              "site": "0x43566c56"},
            "ZOOM_OFF": {"key": "0x0a000011", "str": "0x43c26186",
                         "site": "0x43566c8e"},
        },
        "external_callers": {
            "api_wrapper_block": ["0x43a3ab00", "0x43a3b300"],
            "api_wrapper_entry_points": 28,
            "api_wrapper_call_sites": 57,
            "callers": {
                "0x43562068": ["0x435a00f0 [CLK_CTRL]", "0x43639de2 [SDF]",
                               "0x4366bbfe [SYSV][HS]", "0x4367f7c8 [VDF]",
                               "0x436ab9c0 [VEF]", "0x439ad15e [SFRS]",
                               "0x43541b2a [ADF]"],
                "0x4356288c": ["0x43a3ac04", "0x43a3ac14", "0x43a3ac56",
                               "0x43a3ac60", "0x43a3ac6a", "0x43a3ae38",
                               "0x43a3ae5c", "0x43a3ae80"],
            },
        },
        "differential": {
            "a7s": {"path": "firmware/extracted/a7s-fw320/.../av-cam.bin",
                    "token_ACCY": 0, "full_text_matches": 0, "core_matches": 0,
                    "uart_traces": 0,
                    "rtti_classes_present": ["AccyUmDeviceBase",
                                             "AccyUmDeviceWaterHousing",
                                             "AccyUmKeyStatusMgr",
                                             "AccyUmDeviceAvOut",
                                             "AccyUmDeviceAvr",
                                             "AccyUmDeviceHello",
                                             "AccyUmDeviceJiro",
                                             "AccyUmDeviceNull",
                                             "AccyUmDeviceRemote",
                                             "AccyMiDeviceBase",
                                             "AccyMiDeviceLight"],
                    "rtti_block": "0x43c25a23-0x43c25afc",
                    "api_name_strings": ["accy", "edr", "EnableDummyRecv",
                                         "DisableDummyRecv", "SendCommand",
                                         "MsSleep", "rx/RxResponse",
                                         "rxc/RxCommand", "sq/SetQue",
                                         "GetQue"]},
            "a6300": {"path": "firmware/extracted/a6300-fw201/.../av-cam.bin",
                      "token_ACCY": 0, "full_text_matches": 0, "core_matches": 0,
                      "uart_traces": 0,
                      "rtti_block": "0x43d0c9a4-0x43d0ca7d"},
        },
        "shutter_line": {
            "shutter_mentions": 0,
            "keywords_found": [],
            "closest": "START STOP OFF (0x43c260b0) -> key 0x0a00000d",
            "verdict": "sin relacion directa con el obturador (electronico o mecanico)",
        },
        "source_line_numbers": {
            "note": ("el primer %d de la traza es el numero de linea del fichero fuente; "
                     "se extrae del `movs/movw r3,#N` que se pasa por la pila antes del "
                     "`bl` de impresion. Extraccion heuristica (scan_lines.py)."),
            "FACTORY": {"0x435646d2": 183, "0x435646fc": 191, "0x4356472a": 197,
                        "0x43564758": 203, "0x43564778": 209},
            "UART": {"0x43563c0e": 54, "0x43563cbe": 134, "0x43563cf8": 139,
                     "0x43563d26": 145, "0x43563d5a": 152, "0x43563e00": 164,
                     "0x43563e34": 178, "0x43563e5e": 184, "0x43563f22": 208,
                     "0x43563f3e": 217, "0x43563fa4": 241},
            "BASE": {"0x4356583c": 45, "0x43565860": 60, "0x43565880": 64,
                     "0x435658a8": 68, "0x43565902": 89, "0x43565924": 99,
                     "0x4356594e": 104},
            "REMOTE": {"0x43566b86": 233, "0x43566bb2": 239, "0x43566be8": 246,
                       "0x43566c24": 254, "0x43566c8e": 783, "0x43566cb4": 789},
        },
        "source_files": {
            "verified": [],
            "nota": ("ningun nombre de fichero (.cpp/.c/.h) es referenciado por el codigo "
                     "del modulo: la unica cadena no-[ACCY] referenciada por la region "
                     "0x43562a08-0x43567060 es 'Valloc error!' (0x43c24c9e). "
                     "NO VERIFICADO: los ficheros que implementan el modulo."),
            "names_rtti_only": ["AccyUmDeviceBase", "AccyUmKeyStatusMgr",
                                "AccyUmDeviceWaterHousing", "AccyUmDeviceAvOut",
                                "AccyUmDeviceAvr", "AccyUmDeviceHello",
                                "AccyUmDeviceJiro", "AccyUmDeviceNull",
                                "AccyUmDeviceRemote"],
        },
    }
    json.dump(out, open(os.path.join(HERE, "accy.json"), "w"), indent=1)
    print("sub-bloques:")
    for t in sub_table:
        print(f"  {t['sub']:<9} cadenas={t['n_strings']:>3} sitios={t['n_sites']:>3} "
              f"funciones={t['n_functions']:>3}  {t['string_range'][0]}-{t['string_range'][1]}")
    print("total cadenas", sum(t["n_strings"] for t in sub_table),
          "sitios", sum(t["n_sites"] for t in sub_table))


if __name__ == "__main__":
    main()
