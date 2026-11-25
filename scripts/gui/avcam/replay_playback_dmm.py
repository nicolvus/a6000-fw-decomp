"""Controlled replay of AVC work-memory setup with synthetic stream and OS replies.

Usage: replay_playback_dmm.py AV_CAM_BIN ok|short|dmm_error|transport_error
The camera DMM tables and compressed-stream parser are not reproduced.
"""

import hashlib
import json
import struct
import sys
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

base = 0x43541000
blob = Path(sys.argv[1]).read_bytes()
mode = sys.argv[2]
if mode not in {"ok", "short", "dmm_error", "transport_error"}:
    raise ValueError("unsupported reply scenario")
vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
vm.mem_map(base, 0x1000000)
vm.mem_write(base, blob)
mem = 0x10000000
vm.mem_map(mem, 0x10000)


def rd(a):
    return struct.unpack("<I", vm.mem_read(a, 4))[0]


def wr(a, v):
    vm.mem_write(a, struct.pack("<I", v))


regs = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
events: list[dict] = []
# Reconstruct the object graph consumed by the native code.
obj, accessor, backend = mem + 0x100, mem + 0x200, mem + 0x300
wr(obj + 0x10, accessor)
wr(obj + 0xC, mem + 0x500)
wr(accessor + 0xC, backend)
wr(accessor + 0x14, 2)
wr(backend + 0xC, mem + 0x600)
got = (rd(0x43921454) + 0x43921194) & 0xFFFFFFFF
slot = (got + rd(0x43921458)) & 0xFFFFFFFF
wr(slot, mem + 0x700)
stop = mem + 0xF000
vm.reg_write(UC_ARM_REG_SP, mem + 0xE000)
vm.reg_write(UC_ARM_REG_LR, stop | 1)
vm.reg_write(UC_ARM_REG_R0, obj)


def returns(v=0):
    vm.reg_write(UC_ARM_REG_R0, v)
    vm.reg_write(UC_ARM_REG_PC, vm.reg_read(UC_ARM_REG_LR))


def hook(vm, a, size, _):
    if a == stop:
        vm.emu_stop()
        return
    if a in (
        0x4391569C,
        0x43915E20,
        0x4391BD58,
        0x4392117C,
        0x43B3C988,
        0x43B2E39C,
        0x4390C630,
        0x439212EA,
        0x43921230,
        0x43915DB8,
        0x43915E94,
    ):
        events.append({"pc": hex(a), "r0": hex(vm.reg_read(regs[0]))})
    if a == 0x439161FC:
        # Parsed stream chooses decoder type 1. No compressed stream is decoded here.
        wr(rd(vm.reg_read(UC_ARM_REG_SP)), 1)
        wr(vm.reg_read(regs[3]), 1)
        returns()
    elif a in (
        0x4390FE7C,
        0x43B2E968,
        0x43B2E9B4,
        0x43B3D84A,
        0x43B44276,
        0x43B3D604,
        0x43B31260,
        0x43B31268,
    ):
        returns()
    elif a == 0x43915C8C:
        events.append({"decoder_open_reached": True})
        returns()
    elif a == 0x43920D3C:
        returns(mem + 0x800)
    elif a == 0x43A3A9B4:
        returns(vm.reg_read(regs[0]))
    elif a == 0x439C5A04:
        dest = vm.reg_read(regs[0])
        vm.mem_write(dest, bytes([vm.reg_read(regs[1]) & 255]) * vm.reg_read(regs[2]))
        returns(dest)
    elif a == 0x439C5320:
        dest = vm.reg_read(regs[0])
        vm.mem_write(
            dest, bytes(vm.mem_read(vm.reg_read(regs[1]), vm.reg_read(regs[2])))
        )
        returns(dest)
    elif a == 0x435612D0:
        wr(vm.reg_read(regs[1]), mem + 0x1000)
        returns()
    elif a == 0x43561228:
        message = mem + 0x1000
        command = struct.unpack("<H", vm.mem_read(message, 2))[0]
        unit = rd(message + 4)
        events.append({"command": command, "unit": hex(unit), "response": mode})
        status = -1 if mode == "dmm_error" and command == 1 else 0
        size = (
            0x657FF if mode == "short" else (0x1000000 if unit == 0x92041 else 0x800000)
        )
        vm.mem_write(
            message,
            struct.pack(
                "<HhHHH6xII", command | 0x8000, status, 5, 0x1111, 1, 0x82000000, size
            ),
        )
        returns(0xFFFFFFFF if mode == "transport_error" else 0)
    elif a == 0x435612EC:
        returns()


vm.hook_add(UC_HOOK_CODE, hook)
try:
    vm.emu_start(0x4391569D, 0, count=30000)
except Exception as error:
    print(
        json.dumps(
            {
                "error": str(error),
                "pc": hex(vm.reg_read(UC_ARM_REG_PC)),
                "trace": events,
            },
            indent=2,
        )
    )
    raise
assert vm.reg_read(UC_ARM_REG_PC) == stop, hex(vm.reg_read(UC_ARM_REG_PC))
result = vm.reg_read(regs[0])
opened = any(event.get("decoder_open_reached") for event in events)
assert (result, opened) == ((0, True) if mode == "ok" else (0xFFFF0001, False))
print(
    json.dumps(
        {
            "scope": "AVC type 1 setup with synthetic parsed stream, objects and OS/DMM replies",
            "sha256": hashlib.sha256(blob).hexdigest(),
            "mode": mode,
            "result": hex(result),
            "trace": events,
        },
        indent=2,
    )
)
