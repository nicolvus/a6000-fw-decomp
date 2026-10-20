"""Contrasta cadena, bytes originales, rango de copia y orden del CFG de S47."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
BASE = 0x43541000


def reachable(graph: dict[str, list[str]], start: str, blocked: str = "") -> set[str]:
    seen: set[str] = set()
    pending = [start]
    while pending:
        address = pending.pop()
        if address in seen or address == blocked:
            continue
        seen.add(address)
        pending.extend(graph.get(address, []))
    return seen


def main() -> None:
    findings = json.loads((OUT / "s47-findings.json").read_text())
    blob = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - BASE)[0]

    assert word(0x4401F0C0) == int(findings["saved_request"], 16)
    assert word(0x440204C4) == 0x43789CC1
    assert word(0x4378A4A8) == 0x301D7
    assert word(0x43541014) + 0x1EC == 0x435412A0
    assert word(0x435412A0) == 0
    assert word(0x4393AC84) == 0x46C04778  # BX PC; NOP, seguido de ARM.
    branch = word(0x4393AC88)
    assert branch >> 24 == 0xEA
    displacement = branch & 0xFFFFFF
    if displacement & 0x800000:
        displacement -= 1 << 24
    assert 0x4393AC88 + 8 + displacement * 4 == 0x439C5320
    assert word(0x43FF1B48) == 0x43FF23B0
    assert word(0x43FF29B8) == 0xCE
    assert word(0x43FF29BC) == 0x43789709
    assert word(0x43FF8ADC) == 0xCE
    assert word(word(0x43FF8AE0)) == 0x437DAD79
    assert (word(0x43789798) + 0x4378971A) & 0xFFFFFFFF == 0x4401EEE4
    assert word(0x4378979C) + 0x4401EEE4 == 0x4401F0C0
    assert (word(0x437DA060) + 0x437D9FBE) & 0xFFFFFFFF == 0x43ED461C
    assert (word(0x437DA0C0) + 0x437DA09A) & 0xFFFFFFFF == 0x43ED44DC
    source_root = (word(0x437943EC) + 0x43794096) & 0xFFFFFFFF
    destination_root = (word(0x437943E4) + 0x4379408A) & 0xFFFFFFFF
    assert source_root + 0x1E6C == int(findings["source_c"], 16)
    assert destination_root + 0x1E6C == int(findings["consumed_c"], 16)
    assert findings["copy_size"] == 0x1A4
    for field_offset in (0x94, 0x95):
        assert 0 <= field_offset < findings["copy_size"]
    assert source_root + 0x1E6C + 0x1A4 == 0x43E9D558
    assert destination_root + 0x1E6C + 0x1A4 == 0x43E9B524

    ranges = json.loads((OUT / "s47-chain-listing.json").read_text())
    flow = json.loads((OUT / "s47-order-flow.json").read_text())[0]
    nodes = [node for region in ranges for node in region["nodes"]] + flow["nodes"]
    for node in nodes:
        address = int(node["address"], 16)
        expected = bytes.fromhex(node["bytes"])
        assert blob[address - BASE:address - BASE + len(expected)] == expected
    instructions = {node["address"]: node["instruction"] for node in nodes}
    for site_key, instruction in {
        "4378970e": "mov.w r2,#0x140",
        "4378971e": "blx 0x439c5320",
        "4378975a": "bl 0x437d9f9c",
        "43789f0e": "blx r3",
        "4378a3e6": "bl 0x435612b4",
        "437dad92": "strb.w r3,[r5,#0x94]",
        "437dad9e": "strb.w r3,[r5,#0x95]",
        "43792f9c": "bl 0x437da078",
        "43794096": "bl 0x43ae8faa",
        "4379409e": "bl 0x43ae8eae",
    }.items():
        assert instructions[site_key] == instruction

    graph = {node["address"]: node["successors"] for node in flow["nodes"]}
    assert "43794096" in reachable(graph, flow["entry"])
    assert "43794096" not in reachable(graph, flow["entry"], "43792f9c")
    assert "43792f9c" not in reachable(graph, "4379409a")
    assert findings["callback_before_copy"] is True
    assert findings["original_payload_producer"] == "NO_VERIFICADO"
    assert findings["vd_curtains_relation"] == "NO_VERIFICADO"
    assert findings["milestone_closed"] is False
    print(f"S47 PASS: {len(nodes)} instrucciones, tablas/PIC, copia y dominancia; frontera conservada")


if __name__ == "__main__":
    main()
