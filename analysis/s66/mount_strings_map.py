"""S62: mapa de cadenas -> funciones del subsistema MOUNT en av-cam.bin (A6000).

Uso: mount_strings_map.py [A6000|A7S] [--lo 0xADDR] [--hi 0xADDR]
Imprime cada cadena de la región [lo,hi) con las instrucciones que la referencian
(referencia PIC literal + `add pc`) y la función contenedora aproximada.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402
from strrefs import scan, func_of  # noqa: E402

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")


def main():
    model = "A6000"
    lo, hi = 0x43c95000, 0x43c9b000
    args = sys.argv[1:]
    if args and not args[0].startswith("--"):
        model = args.pop(0)
    while args:
        if args[0] == "--lo":
            lo = int(args[1], 0); args = args[2:]
        elif args[0] == "--hi":
            hi = int(args[1], 0); args = args[2:]
        else:
            args = args[1:]
    refs, starts = scan(model)
    d = data(model)
    rows = []
    for m in STR_RE.finditer(d):
        a = B + m.start()
        if not (lo <= a < hi):
            continue
        s = m.group().decode("ascii", "replace")
        hits = refs.get(a, [])
        rows.append((a, s, hits))
    print(f"# {model} [{lo:#x},{hi:#x}): {len(rows)} cadenas")
    for a, s, hits in rows:
        fs = sorted({func_of(starts, h) for h in hits if func_of(starts, h)})
        fstr = ",".join(f"{f:#x}" for f in fs)
        print(f"{a:#x}\t{fstr}\t{s}")
    # funciones de la región, ordenadas, con nº de cadenas referenciadas
    counts = {}
    for a, s, hits in rows:
        for h in hits:
            f = func_of(starts, h)
            if f:
                counts.setdefault(f, []).append(s)
    print("\n# funciones con cadenas MOUNT (nº, dirección)")
    for f in sorted(counts):
        print(f"{len(counts[f]):3d}  {f:#x}")


if __name__ == "__main__":
    main()
