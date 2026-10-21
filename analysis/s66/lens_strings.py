"""S62:Strings del subsistema de lente en av-cam.bin (A6000/A7S) y el código que los referencia.

Uso: lens_strings.py [A6000|A7S] [--kw k1,k2,...]
- Extrae cadenas ASCII (>=4) del blob con su dirección.
- Filtra por palabras clave del subsistema de lente.
- Para cada cadena, localiza las instrucciones Thumb que la referencian (literal PIC + add pc)
  y la función contenedora aproximada (heurística `push {..,lr}`).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402
from strrefs import scan, func_of  # noqa: E402

DEFAULT_KW = [
    "lens", "mount", "zoom", "focus", "calib", "servo", "aperture", "focal",
    "oss", "ilce", "e-mount", "emount", "bf", "salvador", "explor",
    "e-mount", "wide", "tele", "prime", "macro", "fisheye",
]

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")


def strings(model):
    d = data(model)
    out = []
    for m in STR_RE.finditer(d):
        out.append((B + m.start(), m.group().decode("ascii", "replace")))
    return out


def main():
    model = "A6000"
    kws = list(DEFAULT_KW)
    args = sys.argv[1:]
    if args and not args[0].startswith("--"):
        model = args.pop(0)
    if args and args[0] == "--kw":
        kws = args[1].split(",")
    refs, starts = scan(model)
    kwl = [k.lower() for k in kws]
    rows = []
    for addr, s in strings(model):
        low = s.lower()
        if not any(k in low for k in kwl):
            continue
        hits = refs.get(addr, [])
        rows.append((addr, s, hits))
    print(f"# {model}: {len(rows)} cadenas con coincide de {kws}")
    for addr, s, hits in rows:
        print(f"{addr:#x}  {s!r}")
        for h in hits:
            f = func_of(starts, h)
            print(f"      ref@{h:#x} func~{f:#x}" if f else f"      ref@{h:#x}")


if __name__ == "__main__":
    main()
