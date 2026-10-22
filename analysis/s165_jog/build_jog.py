#!/usr/bin/env python3
"""S165 — genera `analysis/s165_jog/jog.json` a partir de los bytes de las tres fw.

Todo lo que se publica sale de aquí (o está marcado como NO VERIFICADO en el .md).
"""
import hashlib
import json
import os
import re
import struct
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U32, A7S, A6300  # noqa: E402

BIN = "analysis/rea-independent/input/av-cam.bin"

# ---------------------------------------------------------------- trazas [JOG]
# (vaddr, texto) — las 14, extraídas por scan_jog_strings.py
JOG_STRINGS = [
    (0x43c40eb4, "[JOG]JogMain::%s:%d"),
    (0x43c40ef2, "[JOG]ERR. osal_try_valloc_msg. err=0x%x, line=%d"),
    (0x43c40f23, "[JOG]<Send Event> key_code = 0x%x, deg/sec = %d"),
    (0x43c40f53, "[JOG]ERR. osal_snd_msg. err=0x%x, line=%d"),
    (0x43c40f85, "[JOG]ERR. osal_free_timer. err=0x%x, line=%d"),
    (0x43c40fb2, "[JOG]JogFg::%s:%d"),
    (0x43c40fc4, "[JOG]ERR. osal_alloc_timer. err=0x%x, line=%d"),
    (0x43c40ff2, "[JOG]ERR. osal_set_timer. err=0x%x, line=%d"),
    (0x43c410a2, "[JOG]JogTpu::%s:%d"),
    (0x43c410fe, "[JOG]JogVGrip::%s:%d"),
    (0x43c41113, "[JOG]UpdateDataFromVgrip SndErr, line=%d"),
    (0x43c41184, "[JOG]JogKey::%s:%d:0x%x,%d"),
    (0x43c4119f, "[JOG]JogKey::%s:%d,pos:%d->%d"),
    (0x43c411bd, "[JOG]JogKey::%s:%d,Deg=0,Not Send"),
]

# ------------------------------------------------------------- funciones [JOG]
# (inicio, fin, nombre, clase, rol)
FUNCS = [
    (0x435ae5bc, 0x435ae616, "JogMain::Exit", "JogMain", "sale del subsistema: desregistra handlers y temporizadores"),
    (0x435ae6b6, 0x435ae846, "JogMain::Init", "JogMain", "construye hasta 5 JogKey, los liga a un JogDev y llama dev->Start(cb,u32,u32)"),
    (0x435aeb18, 0x435aebd2, "JogMain::SendEvent", "JogMain", "arma el mensaje de 12 B {key_code, deg, err} y lo entrega"),
    (0x435aed30, 0x435aedc6, "JogFg::Exit", "JogFg", "libera el temporizador y el handler de eventos"),
    (0x435aedd0, 0x435aef24, "JogFg::Start", "JogFg", "registra callback + temporizador de sondeo"),
    (0x435af166, 0x435af1fa, "JogTpu::Exit", "JogTpu", "libera el temporizador y el handler de eventos"),
    (0x435af204, 0x435af358, "JogTpu::Start", "JogTpu", "registra callback + temporizador de sondeo"),
    (0x435af582, 0x435af616, "JogVGrip::Exit", "JogVGrip", "libera el temporizador y el handler de eventos"),
    (0x435af620, 0x435af774, "JogVGrip::Start", "JogVGrip", "registra callback + temporizador de sondeo"),
    (0x435af848, 0x435af8b2, "JogVGrip::UpdateDataFromVgrip", "JogVGrip", "recibe 12 B del grip vertical y los reenvía"),
    (0x435af968, 0x435af9ae, "JogKey::SetDev", "JogKey", "liga un JogKey a su JogDev (y fija el índice de key_code)"),
    (0x435af9d0, 0x435afa76, "JogKey::SendKeyEvent", "JogKey", "calcula el delta y emite el evento de rueda"),
]

# --------------------------------------------------------------- RTTI / vtable
RTTI = {
    "JogDev": {"typeinfo": 0x43fdaaf4, "base": None, "vtable": 0x43fbb640,
               "slots": [0x439b4145] * 6},
    "JogFg": {"typeinfo": 0x43fdaafc, "base": 0x43fdaaf4, "vtable": 0x43fbb660,
              "slots": [0x43a4a249, 0x435aedd1, 0x435aed31, 0x43a4a259, 0x43a4a251, 0x43a4a255]},
    "JogTpu": {"typeinfo": 0x43fdab08, "base": 0x43fdaaf4, "vtable": 0x43fbb680,
               "slots": [0x43a4a2c7, 0x435af205, 0x435af165, 0x43a4a273, 0x43a4a2b5, 0x43a4a277]},
    "JogVGrip": {"typeinfo": 0x43fdab14, "base": 0x43fdaaf4, "vtable": 0x43fbb6a0,
                 "slots": [0x43a4a2ef, 0x435af621, 0x435af581, 0x43a4a349, 0x43a4a2f7, 0x43a4a313]},
}

KEYCODE_TABLE = {"addr": 0x43fdab20, "entries": [0x11, 0x12, 0x16, 0x17, 0x14, 0x15]}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def strings_with_prefix(blob, pref):
    pat = pref.encode()
    out, start = [], 0
    while True:
        i = blob.find(pat, start)
        if i < 0:
            break
        j = i
        while j > 0 and 32 <= blob[j - 1] < 127:
            j -= 1
        k = i
        while k < len(blob) and 32 <= blob[k] < 127:
            k += 1
        out.append((j, blob[j:k].decode("ascii", "replace")))
        start = i + 1
    return out


def main():
    pic = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
    sites = {}
    for dest, lst in pic.items():
        for a in lst:
            sites.setdefault(int(dest, 16), []).append(a)

    strs = []
    for addr, text in JOG_STRINGS:
        # comprueba que el texto está realmente en el binario en esa dirección
        off = addr - BASE
        real = B[off:off + len(text)].decode("ascii")
        assert real == text, (hex(addr), real)
        refs = sorted(sites.get(addr, []))
        strs.append({
            "vaddr": hex(addr),
            "file_offset": hex(off),
            "text": text,
            "ref_sites": [hex(x) for x in refs],
            "ref_count": len(refs),
            "functions": sorted({f[2] for f in FUNCS if any(s in range(f[0], f[1]) for s in refs)}),
        })

    # diferencial
    diff = {}
    for name, path in [("A6000_fw321", BIN), ("A7S_fw320", A7S), ("A6300_fw201", A6300)]:
        blob = open(path, "rb").read()
        hits = strings_with_prefix(blob, "[JOG]")
        uniq = sorted({t for _, t in hits})
        classes = sorted({t for t in re.findall(rb"\d+(?:Jog|Illumi|McAssert)[A-Za-z0-9_]*", blob)
                          for t in [t.decode()]})
        diff[name] = {
            "path": path,
            "size": len(blob),
            "sha256": sha256(path),
            "n_jog_token_occurrences": blob.count(b"[JOG]"),
            "n_jog_strings": len(uniq),
            "jog_strings": uniq,
            "rtti_class_names": classes,
            "has_jogkey_text": b"JogKey" in blob,
            "has_send_event_text": b"Send Event" in blob,
        }

    out = {
        "milestone": "S165",
        "subject": "modulo [JOG] — subsistema de rueda/joystick (A6000 fw3.21)",
        "convention": "vaddr = 0x43541000 + file_offset",
        "binary": {"path": BIN, "size": N, "sha256": sha256(BIN)},
        "counters": {
            "n_jog_strings": len(JOG_STRINGS),
            "n_ref_sites_total": sum(s["ref_count"] for s in strs),
            "n_ref_sites_by_rule": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
            "n_functions_with_jog_traces": len(FUNCS),
            "n_dead_strings": sum(1 for s in strs if s["ref_count"] == 0),
            "n_pretty_function_refs": 10,
        },
        "strings": strs,
        "functions": [
            {"start": hex(a), "end": hex(b), "name": n, "class": c, "role": r,
             "jog_sites": []} for a, b, n, c, r in FUNCS
        ],
        "rtti": {k: {kk: (hex(vv) if isinstance(vv, int) else vv) for kk, vv in v.items()}
                 for k, v in RTTI.items()},
        "keycode_table": {"addr": hex(KEYCODE_TABLE["addr"]),
                          "entries": [hex(x) for x in KEYCODE_TABLE["entries"]]},
        "differential": diff,
    }
    # sitios [JOG] por función
    for f in out["functions"]:
        a = int(f["start"], 16)
        b = int(f["end"], 16)
        f["jog_sites"] = sorted(hex(s) for st in strs for s in
                                [int(x, 16) for x in st["ref_sites"]] if a <= s < b)
    json.dump(out, open("analysis/s165_jog/jog.json", "w"), indent=1, ensure_ascii=False)
    print("escrito analysis/s165_jog/jog.json")
    print("cadenas:", len(strs), " sitios:", out["counters"]["n_ref_sites_total"],
          " funciones:", len(FUNCS))


if __name__ == "__main__":
    main()
