"""E25-25 — cuevas: regiones, referencias y codificación (offline)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

capstone = pytest.importorskip("capstone")

from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD
from e25_25 import references as R
from e25_26 import patch_c3b as PC

AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
AV_CAM_A7S = ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
EVID25 = ROOT / "analysis/e25-25/evidence.json"


@pytest.fixture(scope="module")
def bionz() -> bytes:
    if not AV_CAM.is_file():
        pytest.skip("falta av-cam.bin")
    return AV_CAM.read_bytes()


@pytest.fixture(scope="module")
def darwin() -> bytes:
    if not DARWIN.is_file():
        pytest.skip("falta darwin_core.bin")
    return DARWIN.read_bytes()


def _target(ins) -> int:
    return int(ins.op_str.lstrip("#"), 16)


# --------------------------------------------------------------------- regiones


def test_region_antigua_no_es_libre(bionz):
    rep = R.region_report(bionz, PB.BASE, 0x435418E4, 0x43541B00)
    assert rep["all_zero"]
    # 0x43541900 tiene una entrada en la GOT (0x44020f00): la zona no es relleno.
    assert any(r["target"] == "0x43541900" for r in rep["literal_references"])


def test_region_nueva_es_cero_y_sin_punteros(bionz):
    rep = R.region_report(bionz, PB.BASE, 0x4354141C, 0x435418D8)
    assert rep["all_zero"]
    assert rep["literal_references"] == []
    assert all(int(r["target"], 16) < 0x43541800 or int(r["target"], 16) >= 0x43541880
               for r in rep["branch_references"])


def test_a7s_comparte_la_misma_estructura(bionz):
    if not AV_CAM_A7S.is_file():
        pytest.skip("falta av-cam-a7s.bin")
    a7s = AV_CAM_A7S.read_bytes()
    assert all(b == 0 for b in a7s[0x41C:0x8D8])
    assert all(b == 0 for b in a7s[0x8E4:0xB00])
    # El objeto de 0x900 también está referenciado por la GOT en la A7S.
    assert a7s.find((0x43541900).to_bytes(4, "little")) >= 0


def test_cuevas_caben_sin_conflictos(bionz):
    rep = R.region_report(bionz, PB.BASE, 0x4354141C, 0x435418D8)
    assert R.cave_overlaps(rep, PB.CAVE, PB.CAVE_LEN, PB.BASE)["literal_conflicts"] == []
    assert R.cave_overlaps(rep, PC.CAVE, PC.CAVE_LEN, PB.BASE)["literal_conflicts"] == []
    assert PB.CAVE + PB.CAVE_LEN <= PC.CAVE
    assert PC.CAVE + PC.CAVE_LEN <= 0x435418D8


def test_darwin_vectores_zero_y_cueva(darwin):
    vec = R.darwin_vectors(darwin)
    assert all(vec[i]["zero"] for i in (70, 71, 72, 73, 76))
    assert not vec[74]["zero"]
    # Cueva 0x4318..0x4326 (vectores 70-73) y literal 0x4330..0x4334 (vector 76).
    assert all(b == 0 for b in darwin[0x4318 - PD.BASE:0x4326 - PD.BASE])
    assert all(b == 0 for b in darwin[0x4330 - PD.BASE:0x4334 - PD.BASE])
    for lo, hi in ((0x4318, 0x4326), (0x4330, 0x4334)):
        rep = R.region_report(darwin, PD.BASE, lo, hi)
        assert rep["literal_references"] == [] and rep["branch_references"] == []


# --------------------------------------------------------------------- bytes


def test_cueva_selector_desensamblada():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    text = [(i.mnemonic, i.op_str) for i in md.disasm(PB.cave_bytes(), PB.CAVE)]
    assert ("ldr.w", "r2, [sb, #0x41c]") in text
    assert ("strb", "r2, [r4, #0xe]") in text
    assert ("b.w", "#0x43841576") in text
    assert text[-1] == ("bx", "lr")


def test_cueva_c3b_desensamblada():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    text = [(i.mnemonic, i.op_str) for i in md.disasm(PC.cave_bytes(), PC.CAVE)]
    assert ("push", "{r1, lr}") in text
    assert ("ldr.w", "r1, [r4, #0x41c]") in text
    assert ("ldrh.w", "r2, [r4, #0x5e0]") in text
    assert ("ldr.w", "r3, [r4, #0x64c]") in text
    assert ("strb.w", "r3, [r4, #0x655]") in text
    assert ("strh.w", "r3, [r4, #0x650]") in text
    assert ("bl", "#0x436d6118") in text
    assert text[-1] == ("pop", "{r1, pc}")


def test_hook_apunta_a_la_cueva():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ins = next(md.disasm(PC.hook_bytes(), PC.HOOK))
    assert ins.mnemonic == "bl" and _target(ins) == PC.CAVE


# --------------------------------------------------------------------- integración


def test_parche_combinado_y_reversion(bionz):
    image = PB.BionzImage.load(AV_CAM)
    selector, d1 = PB.apply_bytes(image.data)
    combined, d2 = PC.apply_bytes(selector)
    assert d1 and d2
    assert all(d["address"] in PB.allowed_addresses() for d in d1)
    assert all(d["address"] in PC.allowed_addresses() for d in d2)
    assert not ({d["address"] for d in d1} & {d["address"] for d in d2})
    assert PC.restore_bytes(combined) == selector
    assert PB.restore_bytes(PC.restore_bytes(combined)) == image.data
    assert PC.sha256(PB.restore_bytes(PC.restore_bytes(combined))) == PB.SHA256


def test_evidencia_e25_25_coherente():
    if not EVID25.is_file():
        pytest.skip("falta analysis/e25-25/evidence.json")
    ev = json.loads(EVID25.read_text())
    assert ev["phase"] == "E25-25" and ev["installable"] is False
    assert ev["bionz"]["old_gap"]["all_zero"] and ev["bionz"]["header_reserved"]["all_zero"]
    assert ev["bionz"]["a7s_same_gap_zero"] and ev["bionz"]["a7s_same_header_zero"]
    assert ev["bionz"]["selector_cave"]["literal_conflicts"] == []
    assert ev["darwin"]["cave_fits_zero_entries"] is True
    assert ev["channel"]["frozen_after_menu_change"] is True


def test_cadena_selector_darwin_por_captura(darwin):
    """GUI/modelo -> campo -> paquete -> S+0x3e -> compuertas Darwin (emulación)."""
    from e25_24 import emu as E24
    from e25_24.selector import EFCS_MODEL_OFF, EFCS_MODEL_ON, Selector
    from e25_25 import channel as C

    dpatched, _ = PD.apply_bytes(darwin)
    for model, flag in ((EFCS_MODEL_ON, 0), (EFCS_MODEL_OFF, 1)):
        sel = Selector()
        sel.select(model)
        ticket = sel.begin_capture()
        assert ticket.packet_flag == flag
        packet = C.build_packet(ticket.packet_flag)
        assert C.CapturePacket(packet).darwin_flag == flag
        coil = E24.run_darwin(dpatched, 0x20C74, flag)
        motor = E24.run_darwin(dpatched, 0x1FE66, flag)
        assert (coil, motor) == ((3, 4) if flag == 0 else (0, 0))
        sel.end_capture()
