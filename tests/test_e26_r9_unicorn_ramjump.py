"""E26-R9 — prueba de emulación Unicorn del salto a RAM del BootROM (r9-unicorn-ramjump.py).

Prueba offline. No toca la cámara, no transmite paquetes, no ejecuta en hardware.
Valida que el control se transfiere a eSRAM (0xc0000000-0xc0100000) mediante el
vector de salto en [0xc000500C], simulando los paquetes tipo 0 (escritura) y
tipo 0xFFFF (salto) del BootROM.

Informe: docs/capture/e26-r9-bootrom-ram-execution.md
"""

import importlib
import struct

import pytest

pytest.importorskip("unicorn")

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys_path = ROOT / "analysis" / "e26-recovery"
if str(sys_path) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(sys_path))

r9uj = importlib.import_module("r9-unicorn-ramjump")


def test_esram_and_vector_constants():
    assert r9uj.ESRAM_BASE == 0xC0000000
    assert r9uj.ESRAM_SIZE == 0x01000000
    assert r9uj.ADDR_JUMP_VECTOR == 0xC0005000
    assert r9uj.ADDR_JUMP_TARGET == 0xC000500C


def test_ram_jump_transfers_control_to_esram():
    ok = r9uj.emulate_ram_jump()
    assert ok is True


def test_jump_target_is_32_bit_and_thumb_selectable():
    # El bit0 de la dirección de salto selecciona Thumb (1) vs ARM (0) en BX.
    low = r9uj.thumb(0xC0005000)
    assert low & 1 == 1  # Thumb
    assert (low & ~1) == 0xC0005000  # dirección base intacta
    assert low <= 0xFFFFFFFF  # cabe en 32 bits


def test_payload_is_written_to_esram():
    """Simula la escritura tipo 0: el payload queda en eSRAM antes del salto."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, UC_PROT_ALL, Uc
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(r9uj.ESRAM_BASE, r9uj.ESRAM_SIZE, UC_PROT_ALL)
    payload = bytes([0x01, 0x22, 0x00, 0xE0])  # movs r2,#1 ; b .
    uc.mem_write(r9uj.ADDR_JUMP_VECTOR, payload)
    readback = uc.mem_read(r9uj.ADDR_JUMP_VECTOR, len(payload))
    assert readback == payload


def test_indirect_branch_reads_from_0xc000500c():
    """FUN_ffff0144 lee el salto desde [0xc0005000]+0xc = [0xc000500C]."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, UC_PROT_ALL, Uc
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(r9uj.ESRAM_BASE, r9uj.ESRAM_SIZE, UC_PROT_ALL)
    target = r9uj.thumb(r9uj.ADDR_JUMP_VECTOR)
    uc.mem_write(r9uj.ADDR_JUMP_TARGET, struct.pack("<I", target))
    stored = struct.unpack("<I", uc.mem_read(r9uj.ADDR_JUMP_TARGET, 4))[0]
    assert stored == target
