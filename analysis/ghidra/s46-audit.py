"""Comprueba pruebas de base VD, identidades y límites de las conclusiones S46."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"


def main() -> None:
    findings = json.loads((OUT / "s46-findings.json").read_text())
    blob = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    assert word(0x43E16D2C) == 0
    assert word(0x436C71F8) == findings["vd_base"] == 0xF3120000
    assert findings["vd_destination"] == findings["vd_base"] + 0x220
    assert blob[0x43ACEE66 - 0x43541000:0x43ACEE6A - 0x43541000].hex() == "01607047"
    assert (word(0x43793644) + 0x43792F90) & 0xFFFFFFFF == 0x43E9B548
    assert (word(0x437943C0) + 0x43793EB0) & 0xFFFFFFFF == 0x43E9B548
    assert 0x43E9B548 + 0x1E40 + 0x2C == findings["source_c"] == 0x43E9D3B4
    assert findings["p_equals_c"] == "NO_VERIFICADO"
    assert findings["physical_integration"] == "NO_VERIFICADO"
    assert word(0x43FF8ADC) == 0xCE
    assert word(0x43FF8AE0) == 0x43FF7414
    assert word(0x43FF8AE4) == 1
    assert word(0x43FF7414) == 0x437DAD79
    assert (word(0x437DADA8) + 0x437DAD86) & 0xFFFFFFFF == 0x43F7BBF4
    listing = json.loads((OUT / "s46-c-writer-final-listing.json").read_text())[0]["temporary_listing"]
    for instruction in (
        "437dad7e mov r5,r1", "437dad84 ldr r1,[r3,#0x8]",
        "437dad8e cbz r3,0x437dad9a", "437dad90 movs r3,#0x1",
        "437dad92 strb.w r3,[r5,#0x94]", "437dad96 ldrh r3,[r4,#0x2]",
        "437dad9a strb.w r3,[r5,#0x94]", "437dad9e strb.w r3,[r5,#0x95]",
    ):
        assert instruction in listing
    assert 0x43E9D3B4 + 0x94 == 0x43E9D448
    assert 0x43E9D3B4 + 0x95 == 0x43E9D449
    assert len({int(findings["p_snapshot"], 16), findings["source_c"],
                int(findings["c_scratch"], 16)}) == 3
    print("S46 PASS: literal VD, store, destino +220, construcción partida de C y límites")


if __name__ == "__main__":
    main()
