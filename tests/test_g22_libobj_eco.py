"""G22 (3.59): tras un SET correcto de Silent, `libObj` refresca su contenedor de lectura (`obj+0x54c`, elemento 0) sin esperar la
notificación `0x768f` del núcleo (con el 3.58 el menú volvía siempre a Off). Offline: bytes + flujo emulado con unicorn."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

unicorn = pytest.importorskip("unicorn")
from g22 import patch_libobj_eco as P
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
)

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="libObj.so de Sony ausente")


@needs
def test_solo_cambian_los_sitios_y_la_cola_compartida_queda_intacta():
    old = LIB.read_bytes()
    new = P.apply_bytes(old)
    diff = {i for i, (a, b) in enumerate(zip(old, new)) if a != b}
    assert len(new) == len(old) and diff and diff <= P.allowed_offsets()
    assert new[0x686DF4:0x686DFA] == old[0x686DF4:0x686DFA]  # bl log + b: los usa la ruta de error 0xaa9
    assert P.apply_bytes(new) == new and P.restore_bytes(new) == old


def _run(img: bytes, start: int, r5: int, r0: int) -> list[tuple[int, int, int, int]]:
    """Ejecuta desde `start` con r4 = obj; registra las llamadas (destino, r0, r1, r2) hasta llegar a 0x686e0e."""
    base, obj, cont = 0x680000, 0x100000, 0xC0FFEE
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(base, 0x20000)
    uc.mem_write(base, img[base:base + 0x20000])
    uc.mem_map(obj, 0x1000)
    uc.mem_write(obj + 0x54C, cont.to_bytes(4, "little"))
    calls = []

    def hook(u, addr, size, _):
        if addr in (P.SET_ELEM, P.MARK):
            calls.append((addr, *(u.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))))
            u.reg_write(UC_ARM_REG_R0, 0x5A5A)  # basura: el parche no debe fiarse de r0/r1 tras la llamada
            u.reg_write(UC_ARM_REG_R1, 0x5A5A)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
        elif addr == 0x686E0E:
            u.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.reg_write(UC_ARM_REG_R0, r0)
    uc.reg_write(UC_ARM_REG_R4, obj)
    uc.reg_write(UC_ARM_REG_R5, r5)
    uc.emu_start(start | 1, 0x686E10, count=64)
    return calls


@needs
@pytest.mark.parametrize("valor", [1, 2])
def test_set_correcto_escribe_el_valor_en_el_elemento_0(valor):
    new = P.apply_bytes(LIB.read_bytes())
    calls = _run(new, 0x686DE4, valor, 0)  # cbz r0: envío correcto
    assert calls == [(P.SET_ELEM, 0xC0FFEE, 0, valor), (P.MARK, 0xC0FFEE, 0, calls[1][3])]


@needs
def test_envio_fallido_no_toca_el_contenedor():
    new = P.apply_bytes(LIB.read_bytes())
    assert _run(new, 0x686DE4, 2, 1) == []
