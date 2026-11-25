"""DMM command dispatch and missing AVC types in Sony's embedded default map."""

import hashlib
import json
import struct
from pathlib import Path

import pytest
from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_ARM, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "analysis/camera-extract/usr/kmod/dmm.ko"


def test_command_one_allocates_and_command_five_opens():
    with MODULE.open("rb") as stream:
        elf = ELFFile(stream)
        section = elf.get_section_by_name(".rel.rodata")
        symbols = elf.get_section(section["sh_link"])
        targets = {
            rel["r_offset"]: symbols.get_symbol(rel["r_info_sym"]).name
            for rel in section.iter_relocations()
        }
    assert targets[0xFB70] == "dmm_ctrl_AllocUnitNewHdlr"
    assert targets[0xFB80] == "dmm_ctrl_OpenUnitHdlr"
    assert targets[0xFBE0] == "dmm_ctrl_AllocUnitNewHdlr"
    assert targets[0xFBF0] == "dmm_ctrl_OpenUnitHdlr"


@pytest.mark.parametrize("unit", [0x29F, 0x2A0, 0x2A1, 0x2A2, 0x2A3])
def test_native_allocator_rejects_avc_types_absent_from_embedded_map(unit):
    """Exercise the native lookup, without guessing the camera's external map."""
    units = json.loads((ROOT / "analysis/dmm-unit-types.json").read_text())["unit_types"]
    assert hex(unit) not in units
    with MODULE.open("rb") as stream:
        elf = ELFFile(stream)
        code = elf.get_section_by_name(".text").data()
        config = elf.get_section_by_name(".rodata").data()[0x184:0x184 + 63976]
        assert unit not in struct.unpack("<15994I", config)
    vm = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    code_base, memory = 0x20000000, 0x30000000
    vm.mem_map(code_base, 0x10000)
    vm.mem_write(code_base, code)
    vm.mem_map(memory, 0x20000)
    table = b"".join(struct.pack("<II", int(key, 16), memory + 0x10000) for key in units)
    vm.mem_write(memory, table + struct.pack("<II", 0xFFFFFFFF, 0))
    vm.reg_write(UC_ARM_REG_R0, unit)
    vm.reg_write(UC_ARM_REG_R1, 0)
    vm.reg_write(UC_ARM_REG_R2, memory + 0x18000)
    vm.reg_write(UC_ARM_REG_SP, memory + 0x1F000)
    stop = memory + 0x1FF00
    vm.reg_write(UC_ARM_REG_LR, stop)

    def hook(vm, address, size, _):
        if address == code_base + 0x9794:
            vm.reg_write(UC_ARM_REG_R0, memory)
            vm.reg_write(UC_ARM_REG_PC, address + 4)
        elif address == code_base + 0x97A8:
            destination = vm.reg_read(UC_ARM_REG_R0)
            vm.mem_write(destination, bytes(vm.reg_read(UC_ARM_REG_R2)))
            vm.reg_write(UC_ARM_REG_PC, address + 4)
        elif address == stop:
            vm.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(code_base + 0x9770, 0, count=20000)
    assert vm.reg_read(UC_ARM_REG_PC) == stop
    assert vm.reg_read(UC_ARM_REG_R0) == 0xFFFFFFFD
    assert vm.mem_read(memory + 0x18000, 2) == b"\xff\xff"


@pytest.mark.parametrize("snapshot", ["nand-20261020", "nand-20261105"])
def test_archived_external_map_contains_avc_types(snapshot):
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from e25_27.fatimg import Fat16

    image = ROOT / "analysis/camera-dumps" / snapshot / "dev_nflasha2.bin"
    if not image.exists():
        pytest.skip("archived NAND image unavailable")
    config = Fat16.parse(image.read_bytes()).read("DMMCON~1.BIN")
    assert hashlib.sha256(config).hexdigest() == (
        "1f9275747212f2eed7b5aa41ce4af8348c18e2a4b7201a71e5665b195dee8715"
    )
    cursor = config.index(struct.pack("<II", 0x1D3A63, 0))
    units = {}
    while cursor + 8 <= len(config):
        key, _flags = struct.unpack_from("<II", config, cursor)
        cursor += 8
        if key == 0xFFFFFFFF:
            break
        extents = []
        while struct.unpack_from("<I", config, cursor)[0] != 0xFFFFFFFF:
            extents.append(struct.unpack_from("<I", config, cursor)[0])
            cursor += 4
        cursor += 4
        units[key] = extents
    assert len(units) == 625
    assert {key: units[key] for key in range(0x29F, 0x2A4)} == {
        0x29F: [0x39A],
        0x2A0: [0x39B],
        0x2A1: [0x39C],
        0x2A2: [0x39D],
        0x2A3: [0x39E],
    }
    assert units[0x92041] == [0x106]
    assert units[0x92043] == [0x109]
    assert units[0x92044] == [0x108]
