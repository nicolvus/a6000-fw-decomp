"""G28: espacio de ProcessIds ampliado en la copia del gestor de `viewUnified2.so` — código real emulado (unicorn) de getElement / initProcessDataElement / setProcessId."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
pytest.importorskip("unicorn")
pytest.importorskip("keystone")
import add_menu_entry as A
import pid_space as S
import pp_descriptors as P
import pp_menu_spec as M
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="viewUnified2.so de Sony ausente")
BASE, FIN = 0x10000000, 0x7F000000
AJ = [P.Ajuste(S.PID_PRIMERO + i, s.clave, tuple(v for _, v in s.opciones), s.evento) for i, s in enumerate(M.SETTINGS.values())]


def _cargar(img: bytes) -> Uc:
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    segs = A._segments(img)
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    uc.mem_map(BASE, (top + 0xFFFF) // 0x1000 * 0x1000)
    for t, o, v, _, fs, _, _, _ in segs:
        if t == 1:
            uc.mem_write(BASE + v, img[o:o + fs])
    _, dyn = A._dynamic(img, segs)
    tags = {t: v for t, v in dyn if t}
    rel = img[A._off(segs, tags[0x11]):][:tags[0x12]]
    for i in range(0, len(rel), 8):
        off, info = struct.unpack_from("<II", rel, i)
        if info & 0xFF == 0x17:
            uc.mem_write(BASE + off, struct.pack("<I", struct.unpack("<I", uc.mem_read(BASE + off, 4))[0] + BASE))
    uc.mem_map(0x20000000, 0x10000)
    uc.mem_map(FIN & ~0xFFF, 0x1000)
    uc.reg_write(UC_ARM_REG_SP, 0x2000F000)
    return uc


def _llamar(uc: Uc, fn: int, *args, hooks=None) -> int:
    for r, a in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2), args):
        uc.reg_write(r, a)
    uc.reg_write(UC_ARM_REG_LR, FIN | 1)
    h = uc.hook_add(UC_HOOK_CODE, hooks, None) if hooks else None
    uc.emu_start(BASE + fn | 1, FIN, count=400)
    if h is not None:
        uc.hook_del(h)
    return uc.reg_read(UC_ARM_REG_R0)


@pytest.fixture(scope="module")
def img():
    if not LIB.is_file():
        pytest.skip("viewUnified2.so de Sony ausente")
    return S.patch(LIB.read_bytes(), AJ)


@needs
def test_set_process_id_e_init_resuelven_los_pids_nuevos_y_conservan_los_antiguos(img):
    orig = LIB.read_bytes()
    d_old = struct.unpack_from("<233I", orig, A._off(A._segments(orig), S.D))
    uc = _cargar(img)
    for fn, args in ((0x25D914, lambda pid: (0x20000100, pid)), (0x25D8EC, lambda pid: (0x20000100, 0x20000200, pid))):
        for pid in (0, 0x12, 0x46, 0xE8, S.PID_PRIMERO, S.PID_PRIMERO + 33, S.PID_MAX):
            uc.mem_write(0x20000100, b"\0" * 16)
            uc.mem_write(0x20000104, struct.pack("<I", 0x20000200))          # vista no nula
            assert _llamar(uc, fn, *args(pid)) == 1, (hex(fn), hex(pid))
            got_pid, got_desc = struct.unpack("<II", bytes(uc.mem_read(0x20000108, 8)))
            assert got_pid == pid
            if pid < S.N_ORIG:
                assert got_desc == BASE + d_old[pid]                          # pids existentes: descriptor original
            elif pid <= S.PID_PRIMERO + 33:
                assert got_desc > BASE and struct.unpack("<I", bytes(uc.mem_read(got_desc + 0x18, 4)))[0] > BASE   # puntero al modelo reubicado
            else:
                assert got_desc == 0
        assert _llamar(uc, fn, *args(S.PID_MAX + 1)) == 0                      # fuera del espacio nuevo: rechazado como antes


@needs
def test_get_element_usa_el_caso_de_normal_para_los_pids_nuevos(img):
    orig = LIB.read_bytes()
    elem = struct.unpack_from("<233I", orig, S.ELEM)
    uc = _cargar(img)
    uc.mem_write(0x20000300, struct.pack("<I", 0x20000400))                  # elemento falso: vtable → slot 2 = «bx lr»
    uc.mem_write(0x20000400, struct.pack("<3I", 0, 0, 0x20000500 | 1))
    uc.mem_write(0x20000500, bytes.fromhex("7047"))
    casos: list[int] = []

    def hook(u, addr, size, _):
        if addr == BASE + 0x188DA4:                                             # factoría: captura el caso y devuelve el elemento falso
            casos.append(u.reg_read(UC_ARM_REG_R1))
            u.reg_write(UC_ARM_REG_R0, 0x20000300)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))

    uc.mem_write(0x20000600, struct.pack("<II", 0, 0x20000200))             # this: [+4] = vista
    for pid in (0x12, 0x46, 0xC4, S.PID_PRIMERO, S.PID_MAX):
        casos.clear()
        r = _llamar(uc, 0x1B4568, 0x20000600, pid, hooks=hook)
        esperado = elem[pid] if pid < S.N_ORIG else elem[0x12]
        assert casos == [esperado] and r == 0x20000300, (hex(pid), casos)
    casos.clear()
    assert _llamar(uc, 0x1B4568, 0x20000600, S.PID_MAX + 1, hooks=hook) == 0 and not casos


@needs
def test_los_pids_de_pp_no_los_usa_ningun_nodo_original():
    import setting_nodes as N
    usados = {v for _, props in N.property_lists(LIB.parent / "CautionConfig.so", ".*") for i, _, v in props if i == 0xE}
    assert not set(M.PIDS) & usados and min(M.PIDS) >= S.PID_PRIMERO and max(M.PIDS) <= S.PID_MAX
