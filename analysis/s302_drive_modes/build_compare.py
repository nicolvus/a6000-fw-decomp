#!/usr/bin/env python3
"""S302: build the A7S vs A6000 drive-mode / exposure comparison from bytes.

Every claim stores the exact address, 4 raw bytes and the decoded instruction;
verify_compare.py re-decodes them from the firmware blobs.
"""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("compare.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# (etiqueta, firmware, dirección) — instrucciones decisivas del informe
CLAIMS = [
    # A6000: función de comprobación de parámetros
    ("a6000_param_state_accessor", "a6000", 0x438110AE),
    ("a6000_param_block_ptr", "a6000", 0x438110B4),
    ("a6000_param_block_words", "a6000", 0x438110B8),
    ("a6000_param_shut", "a6000", 0x438110BE),
    ("a6000_param_shut_alt", "a6000", 0x438110CA),
    ("a6000_param_vdnum", "a6000", 0x438110CE),
    ("a6000_param_svrnum", "a6000", 0x438110E0),
    ("a6000_param_div", "a6000", 0x438110EC),
    # A7S: misma función
    ("a7s_param_state_accessor", "a7s", 0x4383264C),
    ("a7s_param_block_ptr", "a7s", 0x43832652),
    ("a7s_param_block_words", "a7s", 0x43832656),
    ("a7s_param_shut", "a7s", 0x4383265C),
    ("a7s_param_shut_alt", "a7s", 0x43832666),
    ("a7s_param_vdnum", "a7s", 0x4383266A),
    ("a7s_param_svrnum", "a7s", 0x4383267C),
    ("a7s_param_div", "a7s", 0x4383268C),
    # A6000: accesor de la matriz de registros por columna
    ("a6000_matrix_stride", "a6000", 0x436D657E),
    ("a6000_matrix_row_walk", "a6000", 0x436D6588),
    ("a6000_matrix_payload", "a6000", 0x436D6580),
    # A7S: selector de modo y accesor con mapa modo→columna
    ("a7s_selector_tipo2", "a7s", 0x43826D64),
    ("a7s_selector_sub0", "a7s", 0x43826D68),
    ("a7s_selector_4e", "a7s", 0x43826D7C),
    ("a7s_selector_4f", "a7s", 0x43826DA6),
    ("a7s_selector_0b", "a7s", 0x43826D9E),
    ("a7s_selector_35", "a7s", 0x43826DAA),
    ("a7s_selector_17", "a7s", 0x43826D8C),
    ("a7s_selector_mode5", "a7s", 0x43826DA2),
    ("a7s_matrix_map_lookup", "a7s", 0x436F3930),
    ("a7s_matrix_row_walk", "a7s", 0x436F3942),
    ("a7s_matrix_payload", "a7s", 0x436F393E),
]

MATRICES = {
    "a6000": {"addr": 0x43FE9B74, "rows": 59},
    "a7s": {"addr": 0x43FEE598, "rows": 69},
}
MODE_LIST = {"addr": 0x43FEE370, "count": 34}
MODE_MAP = {"addr": 0x43C9C5B5, "count": 0x52}


def rows(blob, addr, limit):
    """Rows of 20 bytes: 4-byte header + 16-byte payload, zero header terminates."""
    out = []
    for k in range(limit):
        raw = blob[addr - BASE + 20 * k: addr - BASE + 20 * k + 20]
        if int.from_bytes(raw[:4], "little") == 0:
            break
        out.append({"index": k, "header": f"0x{int.from_bytes(raw[:4], 'little'):08x}",
                    "payload_hex": raw[4:].hex()})
    return out


def main():
    a6 = A6.read_bytes()
    a7 = A7.read_bytes()

    def claim(label, fw, addr):
        blob = a6 if fw == "a6000" else a7
        raw = blob[addr - BASE:addr - BASE + 4]
        ins = next(MD.disasm(raw, addr), None)
        return {"label": label, "firmware": fw, "address": f"0x{addr:08x}",
                "bytes_hex": raw.hex(),
                "insn": f"{ins.mnemonic} {ins.op_str}" if ins else None}

    import struct
    data = {
        "milestone": "S302",
        "title": "drive mode y exposición: A7S fw3.20 vs A6000 fw3.21, campo a campo",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a6000": {"sha256": hashlib.sha256(a6).hexdigest()},
            "a7s": {"sha256": hashlib.sha256(a7).hexdigest()},
        },
        "claims": [claim(*c) for c in CLAIMS],
        "exposure_offsets": {
            "a6000": {"guard_ctx": "0xd70", "ldrd_ctx": "0xd60+8", "state_accessor": "0x4378f9b4",
                      "block_ptr": "state+0x24", "block_words": 4,
                      "shut": "ctx+0x1f8", "shut_alt": "ctx+0x1fc",
                      "vdnum": "[state+8]+0xcc", "svrnum": "[state+8]+0x14e",
                      "divide": "0x4355faf0"},
            "a7s": {"guard_ctx": "0xd78", "ldrd_ctx": "0xd70", "state_accessor": "0x437b38ec",
                    "block_ptr": "state+0x24", "block_words": 3,
                    "shut": "ctx+0x200", "shut_alt": "ctx+0x204",
                    "vdnum": "[state+8]+0xd8", "svrnum": "[state+8]+0x15e",
                    "divide": "0x4355de98"},
        },
        "matrices": {},
        "mode_list": {},
        "mode_map": {},
        "selector_a7s": {"entry": "0x43826d58", "tipo2_sub0": "0x4e", "tipo2_sub1": "0x4f",
                         "sub0": "0x0b", "sub1": "0x35", "sub2": "0x17", "mode5": "0x0c"},
        "deltas": {"guard_ctx": 0x8, "shut": 0x8, "shut_alt": 0x8, "vdnum": 0xC, "svrnum": 0x10},
        "scope_limit": "Comparación estática; la semántica de los campos y la equivalencia "
                       "física de los modos no se demuestran aquí.",
    }
    for fw, spec in MATRICES.items():
        blob = a6 if fw == "a6000" else a7
        data["matrices"][fw] = {"addr": f"0x{spec['addr']:08x}", "stride": 20,
                                "header_bytes": 4, "payload_bytes": 16,
                                "rows": rows(blob, spec["addr"], spec["rows"] + 5)}
    blob = a7
    data["mode_list"] = {
        "addr": f"0x{MODE_LIST['addr']:08x}",
        "codes": [struct.unpack("<I", blob[MODE_LIST["addr"] - BASE + 4 * k:
                                            MODE_LIST["addr"] - BASE + 4 * k + 4])[0]
                  for k in range(MODE_LIST["count"])],
    }
    m = blob[MODE_MAP["addr"] - BASE: MODE_MAP["addr"] - BASE + MODE_MAP["count"]]
    data["mode_map"] = {"addr": f"0x{MODE_MAP['addr']:08x}", "count": MODE_MAP["count"], "bytes": m.hex(),
                        "columns_for_modes": {f"0x{k:02x}": m[k] for k in
                                              (0x0B, 0x17, 0x35, 0x46, 0x4C, 0x4D, 0x4E, 0x4F, 0x51)}}
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {OUT}: {len(data['claims'])} claims, "
          f"a6000 rows={len(data['matrices']['a6000']['rows'])}, "
          f"a7s rows={len(data['matrices']['a7s']['rows'])}")


if __name__ == "__main__":
    main()
