#!/usr/bin/env python3
"""S322: decodifica la trama A7S que construye 0x43ad9666."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
SCENARIOS = ROOT / "analysis/s58/out/a7s_scenarios.json"
OUT = Path(__file__).with_name("frame_format.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disassemble(blob: bytes, address: int, size: int) -> list[dict[str, str]]:
    raw = blob[address - BASE : address - BASE + size]
    return [
        {
            "address": f"0x{ins.address:08x}",
            "bytes": ins.bytes.hex(),
            "insn": f"{ins.mnemonic} {ins.op_str}".strip(),
        }
        for ins in MD.disasm(raw, address)
    ]


def decode_transaction(raw: bytes) -> list[list[int]]:
    frames: list[list[int]] = []
    offset = 0
    while offset < len(raw):
        if raw[offset] == 0:
            assert offset == len(raw) - 1
            break
        assert raw[offset] == 0x81 and offset + 2 <= len(raw)
        length = raw[offset + 1]
        end = offset + 2 + length
        assert end <= len(raw)
        frames.append(list(raw[offset:end]))
        offset = end
    return frames


def main() -> None:
    blob = A7S.read_bytes()
    scenarios = json.loads(SCENARIOS.read_text())
    summaries = []
    for scenario in scenarios:
        frames = [
            frame
            for transaction in scenario["tx"]
            for frame in decode_transaction(bytes.fromhex(transaction))
        ]
        decoded = [[f[2], f[3], f[4]] for f in frames]
        assert all(len(f) == 5 and f[0:2] == [0x81, 3] for f in frames)
        assert decoded == scenario["device_seq"]
        summaries.append(
            {
                "mode": scenario["mode"],
                "shut": scenario["shut"],
                "transactions": len(scenario["tx"]),
                "registers": len(scenario["device_seq"]),
                "decoded_frames": len(frames),
            }
        )

    total_frames = sum(s["decoded_frames"] for s in summaries)
    data = {
        "milestone": "S322",
        "firmware": {"a7s_sha256": sha256(A7S)},
        "rea": {
            "evidence": "ev_4d11d6e5e67806c9404fb64236de7edaf8b8dcbed1afe35beed8c00119840a2f",
            "result": "0x43ad9666 -> 0x436f2554 y 0x43ad9628; 0x43ad9628 -> 0x43ad9536/0x43ad95a6",
        },
        "formatter": {
            "entry": "0x43ad9666",
            "capacity_check": "0x436f2554",
            "assembler": "0x43ad9628",
            "header_address": "0x43ad9536",
            "data_address": "0x43ad95a6",
            "finalize_length": "0x43ad9374",
            "return_contract": {"success": 0, "rejected": 1, "full": 2},
            "instructions": {
                "wrapper": disassemble(blob, 0x43AD9666, 0x20),
                "assembler": disassemble(blob, 0x43AD9628, 0x3E),
                "header": disassemble(blob, 0x43AD9536, 0x70),
                "data": disassemble(blob, 0x43AD95A6, 0x80),
                "finalize": disassemble(blob, 0x43AD9374, 0x34),
            },
        },
        "byte_aligned_frame": {
            "condition": "obj[0]==0, obj[1]<=8, obj[2]<=8",
            "layout": "81 | 03 | device | address8 | data8",
            "length_value": 3,
            "length_covers": ["device", "address8", "data8"],
            "example": bytes(scenarios[0]["tx"][0], "ascii").decode()[:10],
            "terminator": "00 al final de cada transaccion P2S",
        },
        "existing_emulation": {
            "source": "analysis/s58/out/a7s_scenarios.json",
            "scenarios": len(summaries),
            "summaries": summaries,
            "registers": sum(s["registers"] for s in summaries),
            "decoded_frames": total_frames,
            "one_frame_per_register": True,
        },
        "mode_effect": "seleccion de lista y reintento; misma codificacion",
        "limits": [
            "Analisis estatico y reutilizacion de emulacion previa; no se ejecuto firmware ni camara.",
            "La semantica electrica de P2S y el significado fisico de los registros siguen NO_VERIFICADOS.",
            "El vinculo de modo 2 con silent shutter sigue NO_VERIFICADO; S51 no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"S322: {len(summaries)} escenarios; {total_frames} tramas")


if __name__ == "__main__":
    main()
