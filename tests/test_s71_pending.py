"""S71: escritor del bloque dd0 (0x437b1048), copia de +0x740/+0x748 y lectores de Backup 0x3e0005."""
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000


def ins(path, addr, n=4):
    d = path.read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[addr - BASE : addr - BASE + n], addr)]


@pytest.mark.skipif(not A6.is_file(), reason="falta av-cam.bin")
def test_constructor_escribe_bloque_dd0():
    assert ins(A6, 0x437B1CA6) == ["strb.w r3, [r4, #0xdd0]"]
    assert ins(A6, 0x437B1CA2) == ["ldrb.w r3, [r8, #0x2eb]"]


@pytest.mark.skipif(not (A6.is_file() and A7.is_file()), reason="faltan av-cam.bin")
def test_copia_en_bloque_en_a6000_y_a7s():
    assert ins(A6, 0x438ACC24) == ["strb.w r1, [r3, #0x740]"]
    assert ins(A6, 0x438ACC20) == ["ldrb.w r1, [r4, #0x133]"]
    assert ins(A7, 0x4389EFC2) == ["strb.w r1, [r3, #0x748]"]
    assert ins(A7, 0x4389EFBE) == ["ldrb.w r1, [r4, #0x13d]"]


@pytest.mark.skipif(not A6.is_file(), reason="falta av-cam.bin")
def test_backup_read_3e0005_tiene_dos_llamadores():
    for a in (0x437DBED4, 0x437DBFF4):
        assert ins(A6, a) and ins(A6, a)[0].startswith("bl")


def test_grafo_de_modulos_contiene_aristas_conocidas():
    import json

    g = json.loads((ROOT / "analysis/s72_graph/module_graph.json").read_text())
    aristas = {(a, b) for a, b, _ in g["aristas"]}
    assert ("CAMERA_MAIN_SYNC", "GOLFSHOT") in aristas
    assert ("ADF", "SYSND") in aristas
    assert not any(b in {"ERR", "INFO", "DEBUG"} for _, b in aristas)


def test_mapa_de_copia_identico_en_a6000_y_a7s():
    import subprocess
    import sys

    out = subprocess.run([sys.executable, str(ROOT / "analysis/s71_pending/copy_map.py")], capture_output=True, text=True, cwd=ROOT, check=True).stdout
    a6, a7 = (ln.split(":", 1)[1] for ln in out.strip().splitlines())
    assert a6 == a7 and "'0x740': '0x133'" in a6 and "'0x748': '0x13d'" in a6
