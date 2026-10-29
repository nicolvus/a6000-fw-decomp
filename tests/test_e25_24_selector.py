"""E25-24 — selector EFCS/Electronic: estados, parches y emulación (offline)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import emu
from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD
from e25_24.selector import (
    EFCS_MODEL_OFF,
    EFCS_MODEL_ON,
    InvalidSelection,
    Mode,
    Selector,
    State,
    TransitionRejected,
    field_from_mode,
    mode_from_field,
    mode_from_model,
    packet_flag,
    route_for,
)

AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")


def _target(ins) -> int:
    return int(ins.op_str.lstrip("#"), 16)


# --------------------------------------------------------------------------- selector


def test_modelos_de_menu():
    assert mode_from_model(EFCS_MODEL_ON) is Mode.EFCS
    assert mode_from_model(EFCS_MODEL_OFF) is Mode.ELECTRONIC
    with pytest.raises(InvalidSelection):
        mode_from_model(0x2B6)


def test_campo_fisico_no_se_invierte():
    assert mode_from_field(0) is Mode.EFCS
    assert mode_from_field(1) is Mode.ELECTRONIC
    assert field_from_mode(Mode.EFCS) == 0
    assert field_from_mode(Mode.ELECTRONIC) == 1
    with pytest.raises(InvalidSelection):
        mode_from_field(2)


def test_byte_de_paquete_y_ruta():
    assert packet_flag(Mode.EFCS) == 0
    assert packet_flag(Mode.ELECTRONIC) == 1
    assert route_for(Mode.EFCS) == "efcs_original"
    assert route_for(Mode.ELECTRONIC) == "silent_electronico"


def test_estado_inicial_es_efcs():
    s = Selector()
    assert s.mode is Mode.EFCS and s.state is State.EFCS_READY and s.ready


def test_transicion_y_ticket():
    s = Selector()
    s.select(EFCS_MODEL_OFF)
    assert s.mode is Mode.ELECTRONIC and s.state is State.ELECTRONIC_READY
    t = s.begin_capture()
    assert t.mode is Mode.ELECTRONIC and t.packet_flag == 1
    assert t.route == "silent_electronico" and s.state is State.CAPTURE_ACTIVE
    s.end_capture()
    assert s.state is State.ELECTRONIC_READY


def test_no_cambia_durante_captura():
    s = Selector()
    s.begin_capture()
    with pytest.raises(TransitionRejected):
        s.select(EFCS_MODEL_OFF)
    with pytest.raises(TransitionRejected):
        s.begin_capture()
    s.end_capture()


def test_transiciones_repetidas_no_acumulan():
    s = Selector()
    for _ in range(5):
        s.select(EFCS_MODEL_OFF)
        s.select(EFCS_MODEL_ON)
    assert s.mode is Mode.EFCS and s.state is State.EFCS_READY
    assert s.captures == 0
    for _ in range(4):
        t = s.begin_capture()
        assert t.packet_flag == 0
        s.end_capture()
    assert s.captures == 4


def test_valor_invalido_no_cambia_estado():
    s = Selector(mode=Mode.ELECTRONIC)
    with pytest.raises(InvalidSelection):
        s.select(0x1234)
    assert s.mode is Mode.ELECTRONIC and s.state is State.ELECTRONIC_READY


def test_error_y_recuperacion():
    s = Selector(mode=Mode.ELECTRONIC)
    s.fail("darwin sin respuesta")
    assert s.state is State.ERROR and s.last_error
    with pytest.raises(TransitionRejected):
        s.select(EFCS_MODEL_ON)
    with pytest.raises(TransitionRejected):
        s.begin_capture()
    s.recover()
    assert s.state is State.ELECTRONIC_READY and s.mode is Mode.ELECTRONIC


def test_reset_vuelve_a_efcs():
    s = Selector(mode=Mode.ELECTRONIC)
    s.fail("x")
    s.reset()
    assert s.mode is Mode.EFCS and s.state is State.EFCS_READY and not s.last_error


def test_captura_tras_error_no_permitida():
    s = Selector()
    s.fail("init")
    with pytest.raises(TransitionRejected):
        s.begin_capture()
    s.reset()
    assert s.begin_capture().mode is Mode.EFCS


# --------------------------------------------------------------------------- BIONZ patch


@pytest.fixture(scope="module")
def bionz() -> PB.BionzImage:
    if not AV_CAM.is_file():
        pytest.skip("falta av-cam.bin")
    return PB.BionzImage.load(AV_CAM)


@pytest.fixture(scope="module")
def bionz_patched(bionz: PB.BionzImage) -> tuple[bytes, list[dict]]:
    return PB.apply_bytes(bionz.data)


def test_bionz_sha_y_tamano(bionz: PB.BionzImage):
    assert len(bionz.data) == PB.SIZE
    assert bionz.sha256() == PB.SHA256


def test_bionz_bytes_originales(bionz: PB.BionzImage):
    assert bionz.data[PB.BRANCH - PB.BASE:PB.BRANCH - PB.BASE + 4] == PB.BRANCH_OLD
    assert bionz.data[PB.CALL - PB.BASE:PB.CALL - PB.BASE + 4] == PB.CALL_OLD
    assert bionz.data[PB.STORE - PB.BASE:PB.STORE - PB.BASE + 2] == PB.STORE_OLD
    assert all(b == 0 for b in bionz.data[PB.CAVE - PB.BASE:PB.CAVE - PB.BASE + PB.CAVE_LEN])


def test_bionz_diff_solo_en_sitios(bionz: PB.BionzImage, bionz_patched):
    out, diff = bionz_patched
    assert out != bionz.data and diff
    assert all(d["address"] in PB.allowed_addresses() for d in diff)
    assert {d["address"] for d in diff} <= PB.allowed_addresses()


def test_bionz_desensamblado(bionz_patched):
    out, _ = bionz_patched
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    assert bytes(out[PB.BRANCH - PB.BASE:PB.BRANCH - PB.BASE + 4]) == b"\x00\xbf\x00\xbf"
    ins = next(md.disasm(out[PB.CALL - PB.BASE:PB.CALL - PB.BASE + 4], PB.CALL))
    assert ins.mnemonic == "bl" and _target(ins) == PB.CAVE
    assert bytes(out[PB.STORE - PB.BASE:PB.STORE - PB.BASE + 2]) == b"\x00\xbf"
    cave = out[PB.CAVE - PB.BASE:PB.CAVE - PB.BASE + PB.CAVE_LEN]
    text = [(i.mnemonic, i.op_str) for i in md.disasm(cave, PB.CAVE)]
    assert ("ldr.w", "r2, [sb, #0x41c]") in text
    assert ("strb", "r2, [r4, #0xe]") in text
    assert ("b.w", "#0x43841576") in text


def test_bionz_reversion_exacta(bionz: PB.BionzImage, bionz_patched):
    out, _ = bionz_patched
    back = PB.restore_bytes(out)
    assert back == bionz.data
    assert hashlib.sha256(back).hexdigest() == PB.SHA256


def test_bionz_no_toca_cabecera(bionz: PB.BionzImage, bionz_patched):
    out, _ = bionz_patched
    assert out[:0x40] == bionz.data[:0x40]


# --------------------------------------------------------------------------- Darwin patch


@pytest.fixture(scope="module")
def darwin() -> PD.DarwinImage:
    if not DARWIN.is_file():
        pytest.skip("falta darwin_core.bin")
    return PD.DarwinImage.load(DARWIN)


@pytest.fixture(scope="module")
def darwin_patched(darwin: PD.DarwinImage) -> tuple[bytes, list[dict]]:
    return PD.apply_bytes(darwin.data)


def test_darwin_rechaza_tipo0_y_b1a(tmp_path: Path):
    tipo0 = ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin"
    if tipo0.is_file():
        with pytest.raises(PD.ImageError):
            PD.DarwinImage.load(tipo0)


def test_darwin_bytes_originales(darwin: PD.DarwinImage):
    assert darwin.data[PD.COIL_BL - PD.BASE:PD.COIL_BL - PD.BASE + 4] == PD.COIL_OLD
    assert darwin.data[PD.MOTOR_BL - PD.BASE:PD.MOTOR_BL - PD.BASE + 4] == PD.MOTOR_OLD
    assert all(b == 0 for b in darwin.data[PD.CAVE - PD.BASE:PD.CAVE - PD.BASE + 16])
    assert all(b == 0 for b in darwin.data[PD.LITERAL - PD.BASE:PD.LITERAL - PD.BASE + 4])


def test_darwin_diff_y_protegidas(darwin: PD.DarwinImage, darwin_patched):
    out, diff = darwin_patched
    assert diff and all(d["address"] in PD.allowed_addresses() for d in diff)
    before = PD._protected(darwin.data)
    after = PD._protected(out)
    assert before == after


def test_darwin_desensamblado(darwin: PD.DarwinImage, darwin_patched):
    out, _ = darwin_patched
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for site in (PD.COIL_BL, PD.MOTOR_BL):
        ins = next(md.disasm(out[site - PD.BASE:site - PD.BASE + 4], site))
        assert ins.mnemonic == "bl" and _target(ins) == PD.CAVE
    cave = out[PD.CAVE - PD.BASE:PD.CAVE - PD.BASE + PD.CAVE_LEN]
    text = [(i.mnemonic, i.op_str) for i in md.disasm(cave, PD.CAVE)]
    assert ("ldr", "r2, [pc, #0x14]") in text
    assert ("cbz", "r2, #0x4322") in text
    assert ("b.w", "#0x1b080") in text
    assert out[PD.LITERAL - PD.BASE:PD.LITERAL - PD.BASE + 4] == PD.FLAG_ADDR.to_bytes(4, "little")


def test_darwin_funciones_originales_intactas(darwin: PD.DarwinImage, darwin_patched):
    out, _ = darwin_patched
    # La lógica de las compuertas (después del BL) y el lector 0x1b080 no cambian.
    assert out[0x1B080 - PD.BASE:0x1B080 - PD.BASE + 0x16] == darwin.data[0x1B080 - PD.BASE:0x1B080 - PD.BASE + 0x16]
    assert out[0x20C7C - PD.BASE:0x20C90 - PD.BASE] == darwin.data[0x20C7C - PD.BASE:0x20C90 - PD.BASE]
    assert out[0x1FE70 - PD.BASE:0x1FE86 - PD.BASE] == darwin.data[0x1FE70 - PD.BASE:0x1FE86 - PD.BASE]


def test_darwin_reversion_exacta(darwin: PD.DarwinImage, darwin_patched):
    out, _ = darwin_patched
    assert PD.restore_bytes(out) == darwin.data
    assert hashlib.sha256(PD.restore_bytes(out)).hexdigest() == PD.SHA256


# --------------------------------------------------------------------------- emulación


@pytest.mark.parametrize("flag", [0, 1])
def test_emu_darwin_original_ignora_flag(darwin: PD.DarwinImage, flag: int):
    assert emu.run_darwin(darwin.data, 0x20C74, flag) == 3
    assert emu.run_darwin(darwin.data, 0x1FE66, flag) == 4


@pytest.mark.parametrize("flag,coil,motor", [(0, 3, 4), (1, 0, 0)])
def test_emu_darwin_parcheado(darwin_patched, flag: int, coil: int, motor: int):
    out, _ = darwin_patched
    assert emu.run_darwin(out, 0x20C74, flag) == coil
    assert emu.run_darwin(out, 0x1FE66, flag) == motor


@pytest.mark.parametrize("r1,stop", [(1, 0x43841346), (0, 0x43841576)])
@pytest.mark.parametrize("field", [0, 1])
def test_emu_bionz_cave(bionz_patched, r1: int, stop: int, field: int):
    out, _ = bionz_patched
    run = emu.run_bionz_selector(out, r1, field)
    assert run.packet[0] == 0
    assert run.packet[0x0E] == field
    assert run.stopped_at == stop
    assert run.r0 == 0xABCD


def test_emu_bionz_conserva_r3_y_pkt1(bionz: PB.BionzImage, bionz_patched):
    """El cave no debe dejar r3=1: pkt[1] se construye con `adds r3,#0x40`."""
    out, _ = bionz_patched
    orig = emu.run_bionz_pkt1(bionz.data, field=1)
    patched = emu.run_bionz_pkt1(out, field=1)
    assert orig.packet[1] == 0x40 and orig.r3 == 0x40
    assert patched.packet[1] == orig.packet[1]
    assert patched.r3 == orig.r3


def test_matriz_efcs_electronic(bionz_patched, darwin_patched):
    """EFCS: pkt 0 y compuertas 3/4; Electronic: pkt 1 y compuertas 0/0."""
    b, _ = bionz_patched
    d, _ = darwin_patched
    for mode, field, coil, motor in ((Mode.EFCS, 0, 3, 4), (Mode.ELECTRONIC, 1, 0, 0)):
        pkt = emu.run_bionz_selector(b, 1, field).packet
        assert pkt[0x0E] == packet_flag(mode)
        assert emu.run_darwin(d, 0x20C74, pkt[0x0E]) == coil
        assert emu.run_darwin(d, 0x1FE66, pkt[0x0E]) == motor


# --------------------------------------------------------------------------- static chain


def test_cadena_selector_hasta_paquete(darwin: PD.DarwinImage):
    data = darwin.data
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    # El analizador de Darwin copia pkt[0x0e] a S+0x3e.
    load = next(md.disasm(data[0x17FF8 - PD.BASE:0x17FF8 - PD.BASE + 4], 0x17FF8))
    store = next(md.disasm(data[0x17FFC - PD.BASE:0x17FFC - PD.BASE + 4], 0x17FFC))
    assert (load.mnemonic, load.op_str) == ("ldrb.w", "r0, [sp, #0x12]")
    assert (store.mnemonic, store.op_str) == ("strb", "r0, [r4, #0xe]")
    # S = 0x200036d8 (literal de 0x17f98); pkt = S+0x30; flag = S+0x3e.
    literal = int.from_bytes(data[0x1821C - PD.BASE:0x1821C - PD.BASE + 4], "little")
    assert literal == 0x200036D8
    assert literal + 0x3E == PD.FLAG_ADDR


def test_setexposure_y_enganche_c3(bionz: PB.BionzImage):
    data = bionz.data
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    hook = next(md.disasm(data[0x438C82FE - PB.BASE:0x438C82FE - PB.BASE + 4], 0x438C82FE))
    setexposure = next(md.disasm(data[0x438C830C - PB.BASE:0x438C830C - PB.BASE + 4], 0x438C830C))
    assert hook.mnemonic == "bl" and _target(hook) == 0x436D6118
    assert setexposure.mnemonic == "bl" and _target(setexposure) == 0x436D6320


def test_formula_r5_corregida():
    """T047: r5=4203, VTS=4219 -> exposición (VTS-r5)*15,2 us, no r5*15,2."""
    r5, vts, us = 4203, 4219, 15.2
    assert abs((vts - r5) * us - 243.2) < 0.1
    assert abs((vts - r5) * us - 1 / 4000 * 1e6) < 10
    assert r5 * us > 60_000  # la lectura r5*periodo sería absurda
