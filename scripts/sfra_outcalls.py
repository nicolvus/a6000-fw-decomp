"""Llamadas BL/B.W directas que salen de la región SFRA hacia código de aplicación (0x43600000-0x43990000).
Uso: python3 -I scripts/sfra_outcalls.py [--json salida.json]
Límite: sin llamadas indirectas (vtable, blx rX, mailbox); BL decodificados sobre datos pueden dar falsos positivos."""
import json
import sys

sys.path.insert(0, "scripts")
from thumb_callers import bl_targets  # noqa: E402

SFRA = (0x439A1000, 0x439B0000)
APP = (0x43600000, 0x43990000)
ANCHORS = {0x43841070: "captura Darwin", 0x438C7800: "ReadExecuteBase", 0x43795A60: "SetMode IMX210",
           0x436D62E4: "SetMode (wrapper)", 0x436FA784: "CAIF opcode 0x10300", 0x436BCEF4: "CAIF canal",
           0x436BA234: "CAIF cable", 0x437DB858: "CAIF eventos", 0x4379B180: "JPEG directo ruta C",
           0x43653D34: "SDF ApiEncodeJpeg"}


def outcalls(d: bytes):
    out: dict[int, list[int]] = {}
    for a, t in bl_targets(d):
        if SFRA[0] <= a < SFRA[1] and APP[0] <= t < APP[1]:
            out.setdefault(t, []).append(a)
    return out


if __name__ == "__main__":
    d = open("analysis/av-cam-analysis-view.elf", "rb").read()
    o = outcalls(d)
    res = {"region": [hex(x) for x in SFRA], "destinos": {hex(t): [hex(a) for a in v] for t, v in sorted(o.items())},
           "anclas_golpeadas": [ANCHORS[t] for t in o if t in ANCHORS]}
    if "--json" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, ensure_ascii=False)
    print(json.dumps({"n_destinos": len(o), "anclas_golpeadas": res["anclas_golpeadas"]}, ensure_ascii=False))
