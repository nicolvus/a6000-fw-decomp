"""E26-R12 — Unicorn harness: runs the REAL BootROM from the reset vector and records
which path main (FUN_ffff1062) takes for each MISC_MODEREG / GPIO(4) input.

OFFLINE emulation.  Only peripheral *inputs* are modelled (MODEREG, GPIO4 RDATA, a free-running
timer, a "storage ready" bit); every branch decision is made by the original instructions.
Unmodelled MMIO reads return 0 and are listed in the result.
"""

import hashlib
import struct
from pathlib import Path
from typing import Any

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_UNMAPPED,
    UC_MODE_ARM,
    UC_PROT_ALL,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
)

ROM = Path(__file__).resolve().parents[1] / "camera-dumps/20261020-174955/bootrom.bin"
BASE, ESRAM, ESRAM_SZ = 0xFFFF0000, 0xC0000000, 0x100000
MODEREG, GPIO4_RDATA = 0xF2915010, 0xF2910410
TIMERS = (0xF240300C, 0xF240310C)  # free-running counters polled by FUN_0efc/0f36/0f52

# PCs of the real BootROM that mark decisions (all verified in r12 report §3)
MARKS = {
    0xFFFF0058: "reset: core-id/stack (CPU0 continues)",
    0xFFFF1062: "main FUN_ffff1062",
    0xFFFF1094: "selector read: MODEREG(0xf2915010) bit0",
    0xFFFF10A2: "bit0==0 -> NORMAL boot (FUN_028c / FUN_02c6)",
    0xFFFF113A: "normal boot: FUN_02c6 ok -> FUN_013c (bx 0xc0030000)",
    0xFFFF10DE: "serial branch (MODEREG bit0==1)",
    0xFFFF10F6: "GPIO4 bit22==1 -> FUN_0fa0",
    0xFFFF1102: "GPIO4 bit22==0 -> keep probing",
    0xFFFF0FA0: "FUN_ffff0fa0 (serial wrapper)",
    0xFFFF1160: "FUN_ffff0876 call from main (byte receiver)",
    0xFFFF0876: "FUN_ffff0876 (receiver loop)",
    0xFFFF08B2: "receiver samples MODEREG bit1 (BOOT_SERIAL_IN)",
    0xFFFF013C: "FUN_ffff013c: jump to 0xc0030000",
    0xFFFF0D62: "FUN_ffff0d62 error blink loop (never returns)",
}


def run(moderegs: int, gpio4: int, storage_ready: bool = True, limit: int = 400_000):
    d = ROM.read_bytes()
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(BASE, 0x6000, UC_PROT_ALL)
    uc.mem_write(BASE, d)
    uc.mem_map(ESRAM, ESRAM_SZ, UC_PROT_ALL)
    touched: dict[int, int] = {}
    state: dict[str, Any] = {"timer": 0, "trace": [], "tick": 0}

    def unmapped(u, access, addr, size, value, ud):
        page = addr & ~0xFFF
        u.mem_map(page, 0x1000, UC_PROT_ALL)
        touched[page] = touched.get(page, 0)
        return True

    def on_read(u, access, addr, size, value, ud):
        if addr == MODEREG:
            u.mem_write(addr, struct.pack("<I", moderegs))
        elif addr == GPIO4_RDATA:
            u.mem_write(addr, struct.pack("<I", gpio4))
        elif addr in TIMERS:
            state["timer"] += 0x400
            u.mem_write(addr, struct.pack("<I", state["timer"]))
        elif storage_ready and addr == 0x20410:
            u.mem_write(
                addr, struct.pack("<I", 0x2008)
            )  # polled readiness bits, see report §3.6
        elif addr >= 0xF0000000 or addr < 0x100000:
            touched[addr & ~0xFFF] = touched.get(addr & ~0xFFF, 0) + 1

    def on_code(u, pc, size, ud):
        state["tick"] += 1
        if pc in MARKS and (not state["trace"] or state["trace"][-1][0] != pc):
            state["trace"].append((pc, MARKS[pc], state["tick"]))
        if pc == 0xFFFF0144:
            state["jump_taken"] = struct.unpack("<I", u.mem_read(0xC000500C, 4))[0]
            u.emu_stop()
        if (
            pc == 0xFFFF0114
        ):  # FUN_ffff0114 = busy-wait ms delay (ARM); skipped, not a decision point
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
            return
        if pc == 0xFFFF0D62 and "err" not in state:
            state["err"] = u.reg_read(UC_ARM_REG_R0)
        if pc == 0xFFFF0CB6:  # trace logger: r0=stage, r1=step
            state.setdefault("log", []).append(
                (u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_R1))
            )
        if state["tick"] > limit:
            u.emu_stop()

    uc.hook_add(UC_HOOK_MEM_UNMAPPED, unmapped)
    uc.hook_add(UC_HOOK_MEM_READ, on_read, begin=0, end=0xFFFFFFFF)
    uc.hook_add(UC_HOOK_CODE, on_code, begin=BASE, end=BASE + 0x6000)
    # Cortex-A9-like single core: MPIDR affinity 0; real reset vector
    uc.reg_write(UC_ARM_REG_PC, BASE)
    err = None
    try:
        uc.emu_start(BASE, 0, count=limit * 2)
    except UcError as e:
        err = str(e)
    return {
        "trace": [(hex(p), n, t) for p, n, t in state["trace"]],
        "end_pc": hex(uc.reg_read(UC_ARM_REG_PC)),
        "steps": state["tick"],
        "err_code": state.get("err"),
        "error": err,
        "jump_taken": state.get("jump_taken"),
        "log": state.get("log", [])[:40],
    }


if __name__ == "__main__":
    print("rom sha256", hashlib.sha256(ROM.read_bytes()).hexdigest())
    for m, g in ((0, 0), (1, 0), (1, 1 << 22), (0, 1 << 22), (2, 0), (3, 0)):
        r = run(m, g)
        print(
            f"\n== MODEREG={m:#x} GPIO4={g:#x} -> end {r['end_pc']} steps {r['steps']} err {r['error']}"
        )
        c = r["err_code"]
        if c is not None:
            print(
                f"   error code {c:#06x}: {((c >> 12) - 1)} slow + {c & 0xFFF} fast LED blinks"
            )
        for t in r["trace"]:
            print("  ", *t)
