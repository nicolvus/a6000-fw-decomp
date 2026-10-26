"""E20: las comprobaciones `[EXL]` de dimensiones pueden rechazar una captura; contra e20_exl.json y los bytes de A6000 (se omite sin firmware)."""
import json
import sys
from pathlib import Path

import pytest
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = Path(__file__).resolve().parents[1] / "analysis/s403_pendientes"
sys.path.insert(0, str(HERE))
import pic

DATA = json.loads((HERE / "e20_exl.json").read_text())


def test_failure_chain_reaches_the_aborting_caller():
    roles = " ".join(v["papel"] for v in DATA.values())
    assert "devuelve 7" in roles and "aborta" in roles and "0x43acc424 devuelve ese código tal cual" in roles
    assert len(DATA) == 21
    assert "2208" in DATA["0x43ad5aa8"]["papel"] and "1242" in DATA["0x43ad5ab8"]["papel"]


@pytest.mark.skipif(not pic.FIRMWARE["a6000"].exists(), reason="requiere el av-cam de A6000")
def test_decisive_instructions_match_firmware_bytes():
    blob, cs = pic.load("a6000"), Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for addr, row in DATA.items():
        a = int(addr, 16)
        i = next(cs.disasm(blob[a - pic.BASE:a - pic.BASE + 4], a))
        assert f"{i.mnemonic} {i.op_str}" == row["instruccion"], addr
