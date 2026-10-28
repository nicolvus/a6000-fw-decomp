"""Reproduce SetExposure y la serialización P2S; emulación offline, no cámara."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s56"))
from p2s_emu import frames
from setexp_emu import SetExp


def trace(shd: int, svd: int, spl: int) -> dict:
    emu = SetExp()
    assert emu.sha == "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
    emu.run(0x0B, 3, shd, svd, spl)
    emu.u.mem_write(emu.O + 0x268, b"\x01")
    emu.call(0x436D7C08, emu.O)
    records = emu.records(0x43FE995C)
    packets, mmio = emu.tx(2, records)
    # El volcado MMIO contiene relleno hasta alineación de palabra.
    decoded = []
    lengths = []
    for packet in packets:
        end = 0
        while end < len(packet) and packet[end] == 0x81:
            end += 2 + packet[end + 1]
        lengths.append(end)
        decoded.extend(frames(packet[:end]))
    assert decoded == records
    values = dict(decoded)
    assert [values[i] for i in range(3, 9)] == [
        svd & 255, (svd >> 8) & 15, shd & 255,
        (shd >> 8) & 63, spl & 255, (spl >> 8) & 15,
    ]
    return {"input": {"shd": shd, "svd": svd, "spl": spl},
            "ids_1_8": [(i, v) for i, v in decoded if 1 <= i <= 8],
            "packet_lengths": lengths, "packets": [p[:n].hex() for p, n in zip(packets, lengths)],
            "mmio_control": mmio}


if __name__ == "__main__":
    print(json.dumps([trace(0x1234, 0xABC, 0x567), trace(1, 472, 0)], indent=2))
