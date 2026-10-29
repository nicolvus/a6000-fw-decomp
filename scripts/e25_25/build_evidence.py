"""E25-25 — evidencia de regiones de cueva y canal de modalidad (offline)."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD

from e25_25 import references as R

AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
AV_CAM_A7S = ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"


def _region(data: bytes, base: int, lo: int, hi: int, label: str) -> dict:
    rep = R.region_report(data, base, lo, hi)
    rep["label"] = label
    return rep


def main() -> None:
    out: dict = {"phase": "E25-25", "status": "offline", "installable": False}
    data = AV_CAM.read_bytes()
    a7s = AV_CAM_A7S.read_bytes()
    darwin = DARWIN.read_bytes()

    out["bionz"] = {
        "sha256": PB.sha256(data),
        "size": len(data),
        "base": hex(PB.BASE),
        "old_gap": _region(data, PB.BASE, 0x435418E4, 0x43541B00, "relleno cabecera/código (E25-24)"),
        "header_reserved": _region(data, PB.BASE, 0x4354141C, 0x435418D8, "reservado de cabecera (E25-25)"),
        "got_object": _region(data, PB.BASE, 0x43541900, 0x43541B00, "objeto cero con entrada GOT"),
        "a7s_same_gap_zero": all(b == 0 for b in a7s[0x8E4:0xB00]),
        "a7s_same_header_zero": all(b == 0 for b in a7s[0x41C:0x8D8]),
        "selector_cave": R.cave_overlaps(
            _region(data, PB.BASE, 0x4354141C, 0x435418D8, "reservado"), PB.CAVE, PB.CAVE_LEN, PB.BASE),
        "loader": {
            "source": "liro.ko tsk_entry (S49): memcpy(hdr[0x14]+0x24, tabla_API, 0x344)",
            "hdr_0x14": hex(struct.unpack_from("<I", data, 0x14)[0]),
            "api_table_dest": "0x435410d8-0x4354141c",
            "implication": "el área 0x141c-0x18d8 queda fuera del memcpy conocido; "
                           "el archivo se lee completo (vfs_read) y el stub ARM de 0x0 se ejecuta, "
                           "por lo que cabecera y texto comparten la misma imagen cargada",
        },
    }

    vec = R.darwin_vectors(darwin)
    out["darwin"] = {
        "sha256": PD.sha256(darwin),
        "size": len(darwin),
        "base": hex(PD.BASE),
        "vectors_70_76": [vec[i] for i in (70, 71, 72, 73, 74, 76)],
        "cave_4318": _region(darwin, PD.BASE, 0x4318, 0x4326, "cueva (vectores 70-73)"),
        "literal_4330": _region(darwin, PD.BASE, 0x4330, 0x4334, "literal S+0x3e (vector 76)"),
        "cave_fits_zero_entries": all(vec[i]["zero"] for i in (70, 71, 72, 73, 76)),
        "literal_refs": [r.as_dict() for r in R.literal_references(darwin, PD.BASE, 0x4318, 0x4334)],
        "branch_refs": [r.as_dict() for r in R.branch_references(darwin, PD.BASE, 0x4318, 0x4334)],
    }

    # Canal de modalidad (modelo, no hardware).
    from e25_25 import channel as C
    ch = C.ModalityChannel()
    ch.select(0)
    efcs = ch.begin_capture()
    ch.end_capture()
    ch.select(1)
    elec = ch.begin_capture()
    ch.select(0)  # cambio durante la captura: no debe afectar al paquete emitido
    out["channel"] = {
        "packet_len": C.PACKET_LEN,
        "modality_offset": hex(C.PACKET_MODALITY),
        "cap_field": hex(C.CAP_FIELD),
        "darwin_s": hex(C.DARWIN_S),
        "darwin_flag": hex(C.DARWIN_S + C.DARWIN_PACKET + C.DARWIN_MODALITY),
        "efcs_packet_flag": efcs.flag,
        "electronic_packet_flag": elec.flag,
        "electronic_darwin_flag": elec.darwin_flag,
        "frozen_after_menu_change": elec.flag == 1,
        "invalid_fallback": C.resolve_flag(b"\xff" * C.PACKET_LEN),
        "s_readers": list(C.S_READERS),
        "s_readers_note": "barrido de desplazamiento 0x3e y literales a 0x200036d8/0x20003716: 0 lectores estáticos",
    }

    dst = ROOT / "analysis/e25-25/evidence.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    old = out["bionz"]["old_gap"]
    new = out["bionz"]["header_reserved"]
    print(f"old gap refs: literal={len(old['literal_references'])} branch={len(old['branch_references'])}")
    print(f"new header refs: literal={len(new['literal_references'])} branch={len(new['branch_references'])}")
    print(f"selector cave fits/conflicts: {out['bionz']['selector_cave']}")
    print(f"darwin 70-76: {[v['value'] for v in out['darwin']['vectors_70_76']]}")
    print(f"written {dst}")


if __name__ == "__main__":
    main()
