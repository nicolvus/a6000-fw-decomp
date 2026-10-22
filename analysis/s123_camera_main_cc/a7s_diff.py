#!/usr/bin/env python3
"""S123 — diferencial A6000 fw3.21 vs A7S fw3.20 (y A6300 fw2.01) de `[CAMERA_MAIN_CC]`.

Dato clave: en la A6000 fw3.21 las trazas llevan el prefijo literal
`[CAMERA_MAIN_CC]: `; en la A7S fw3.20 y la A6300 fw2.01 **no existe ninguna**
familia de prefijos `[CAMERA_MAIN_*]` (0 ocurrencias), pero **los mismos mensajes**
existen sin el prefijo. Por eso el diferencial se calcula sobre el texto
desprovisto del prefijo.

Uso:  a7s_diff.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[CAMERA_MAIN_CC]"
TAG = "[CAMERA_MAIN_CC]: "


def all_strings(path):
    """[(offset, texto)] de todas las cadenas imprimibles del binario."""
    out = []
    with open(path, "rb") as fh:
        data = fh.read()
    i = 0
    n = len(data)
    prev = False
    start = 0
    while i < n:
        c = data[i]
        cur = 32 <= c < 127
        if cur and not prev:
            start = i
        if not cur and prev:
            out.append((start, data[start:i].decode("latin1")))
        prev = cur
        i += 1
    return out


def main():
    s6 = all_strings(A6000)
    s7 = all_strings(A7S)
    s63 = all_strings(A6300)
    cc6 = [(o, t) for o, t in s6 if t.startswith(PREFIX.decode())]
    set7 = {t for _, t in s7}
    set63 = {t for _, t in s63}
    off7 = {}
    for o, t in s7:
        off7.setdefault(t, o)
    off63 = {}
    for o, t in s63:
        off63.setdefault(t, o)

    rows = []
    for o, t in cc6:
        core = t[len(TAG):] if t.startswith(TAG) else t
        rows.append({"a6000_off": o, "a6000_text": t, "core": core,
                     "a7s_off": off7.get(core), "a6300_off": off63.get(core),
                     "en_a7s": core in set7, "en_a6300": core in set63})
    comunes7 = sum(1 for r in rows if r["en_a7s"])
    comunes63 = sum(1 for r in rows if r["en_a6300"])
    solo6 = [r for r in rows if not r["en_a7s"]]
    out = {
        "a6000": {"n_cadenas_cc": len(cc6)},
        "a7s": {"n_cadenas_cc": 0, "n_cadenas_cc_sin_prefijo": comunes7},
        "a6300": {"n_cadenas_cc": 0, "n_cadenas_cc_sin_prefijo": comunes63},
        "comunes_a7s": comunes7, "comunes_a6300": comunes63,
        "solo_a6000": solo6,
        "tabla": rows,
    }
    json.dump(out, open(os.path.join(HERE, "a7s_diff.json"), "w"),
              indent=1, ensure_ascii=False)
    print(f"A6000 [CAMERA_MAIN_CC]: {len(cc6)} trazas")
    print(f"A7S fw3.20: 0 trazas con prefijo; {comunes7}/{len(cc6)} mensajes "
          f"identicos sin prefijo")
    print(f"A6300 fw2.01: 0 trazas con prefijo; {comunes63}/{len(cc6)} mensajes "
          f"identicos sin prefijo")
    print("solo en A6000:")
    for r in solo6:
        print(f"   a6000_off={r['a6000_off']:#x}  {r['core'][:92]}")


if __name__ == "__main__":
    main()
