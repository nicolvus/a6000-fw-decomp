"""Correspondencia funcional por ranura de vtable entre C_ImagerCtrl_IMX210 (A6000) y C_ImagerCtrl_IMX235 (A7S).

El rol de cada método sale de las cadenas de depuración que escribe; la equivalencia, del flujo alcanzable normalizado.
No identifica semántica eléctrica de registros (requiere hojas de datos que no están en el repositorio)."""

import difflib
import json
import re
import struct
from pathlib import Path

import fw
import rawfw

OUT = Path(__file__).with_name("imager_vtable_correspondence.json")
VTABLE = {"A6000": 0x43FCC08C, "A7S": 0x43FCE04C}  # palabra del typeinfo; las ranuras siguen
TYPEINFO = {"A6000": 0x43FEA0A4, "A7S": 0x43FEEB20}
SLOTS = 34
ROLES = {5: "SetDFERegData (no soportado)", 6: "PowerOn", 7: "PowerOff", 8: "SetMode", 9: "GetParam/GetModeParam",
         10: "SetExposure", 11: "SetExposureZ", 12: "SetRead", 13: "SetReadZ", 14: "Execute (cambio de modo)",
         15: "Execute(0)", 16: "cálculo de parámetros", 17: "Execute_sleep", 19: "GetTransModeState",
         23: "AsyncInitial", 24: "SyncInitial"}


def slot(lib, model: str, index: int) -> int:
    word = struct.unpack_from("<I", lib.e.data, VTABLE[model] + 4 + 4 * index - rawfw.BASE)[0]
    return word & ~1


def strings(lib, function: int, limit: int = 8) -> list:
    out: list[str] = []
    for item in fw.normalize(lib, function, lib.fend(function)):
        if item[0] == "picref" and item[2] != "PTR" and item[2] not in out:
            out.append(re.sub(r"\s+", " ", item[2])[:150])
    return out[:limit]


def state_dumper() -> dict:
    """S301: volcador del objeto de estado, A6000 0x43858338 frente a A7S 0x437e0974."""
    a, b = rawfw.RawLib("A6000", 0x4000), rawfw.RawLib("A7S", 0x4000)
    na, nb = fw.normalize(a, 0x43858338, a.fend(0x43858338)), fw.normalize(b, 0x437E0974, b.fend(0x437E0974))
    diffs = [(x, y) for x, y in zip(na, nb, strict=False) if x != y]
    return {"len": [len(na), len(nb)], "differing_items": len(diffs),
            "only_got_offsets": all(x[0] == y[0] == "ldrlit" for x, y in diffs)}


def build() -> dict:
    a, b = rawfw.RawLib("A6000", 0x2000), rawfw.RawLib("A7S", 0x2000)
    for model, lib in (("A6000", a), ("A7S", b)):
        assert struct.unpack_from("<I", lib.e.data, VTABLE[model] - rawfw.BASE)[0] == TYPEINFO[model]
    rows = []
    for index in range(SLOTS):
        fa, fb = slot(a, "A6000", index), slot(b, "A7S", index)
        na, nb = fw.normalize(a, fa, a.fend(fa)), fw.normalize(b, fb, b.fend(fb))
        ratio = round(difflib.SequenceMatcher(None, na, nb, autojunk=False).ratio(), 2)
        rows.append({"slot": index, "role": ROLES.get(index), "A6000": hex(fa), "A7S": hex(fb), "len": [len(na), len(nb)],
                     "identical": na == nb, "ratio": ratio, "A6000_strings": strings(a, fa, 4), "A7S_strings": strings(b, fb, 4)})
    return {"classes": {"A6000": "Camera::Imager::IMX210::C_ImagerCtrl_IMX210", "A7S": "Camera::Imager::IMX235::C_ImagerCtrl_IMX235"},
            "slots": rows, "state_dumper": state_dumper(), "identical_slots": [r["slot"] for r in rows if r["identical"]],
            "limits": ("Ranuras emparejadas por índice (misma jerarquía C_ImagerCtrl); los roles proceden de cadenas de "
                       "depuración. Una ranura distinta no implica función eléctrica distinta, ni una idéntica el mismo "
                       "efecto en el sensor.")}


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(data["identical_slots"], len(data["slots"]))
