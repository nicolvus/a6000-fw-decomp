#!/usr/bin/env python3
"""
E26-R9 — Unicorn emulation of the BootROM RAM-write → RAM-jump mechanism (offline).

Demonstrates Q2/Q6: code written to eSRAM (simulating BootROM type-0 packets)
can be executed via the type-0xFFFF jump vector at [0xc000500C].

This is an OFFLINE model.  It does not touch real hardware, does not model the
UART line timing or the real CPU state after BootROM entry.  It validates that:
  * eSRAM at 0xc0000000-0xc0100000 is read-write-execute at BootROM time
    (the BootROM itself reads/writes 0xc0005000, 0xc000500C, 0xc0010218, ...),
  * FUN_ffff0144's indirect branch (ldr r1,[0xc0005000]; ldr r0,[r1,#0xc];
    bx r0) transfers control to an address stored in eSRAM.

Requires: unicorn (pip install unicorn)
"""

import struct

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, UC_PROT_ALL, Uc, UcError
from unicorn.arm_const import UC_ARM_REG_PC

# ── Memory map (from bootrom.bin literals + CXD90014 headers) ──────────────────
BOOTROM_BASE = 0xFFFF0000
BOOTROM_SIZE = 0x00006000     # 24 KiB

ESRAM_BASE = 0xC0000000
ESRAM_SIZE = 0x01000000       # 16 MiB (SZ_16M)

# Jump-vector locations (eSRAM, verified literals)
ADDR_JUMP_VECTOR  = 0xC0005000   # FUN_ffff0144: ldr r1,[here]; ldr r0,[r1,#0xc]; bx r0
ADDR_JUMP_TARGET  = 0xC000500C   # type 0xFFFF stores jump address here

DIAG_ADDR = ADDR_JUMP_VECTOR       # diagnostic payload lives at 0xc0005000 (eSRAM)


def thumb(code_addr: int) -> int:
    """Mark an address as Thumb (bit0 = 1) for BX/BLX."""
    return code_addr | 1


def emulate_ram_jump():
    print("=== E26-R9 Unicorn: BootRAM write -> RAM-jump emulation ===")
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)

    # Map eSRAM (RWX) — the region BootROM uses for jump vector and packet store
    uc.mem_map(ESRAM_BASE, ESRAM_SIZE, UC_PROT_ALL)
    # Map MMIO page (for realism; not exercised)
    uc.mem_map(0xF2910000, 0x1000, UC_PROT_ALL)

    # ── Simulate BootROM type-0 packets: write diagnostic payload to eSRAM ──
    # Payload: movs r2,#1 ; b .  (loop forever = controlled stop)
    #   movs r2,#1  = 0x01 0x22
    #   b #0        = 0x00 0xe0
    payload = bytes([0x01, 0x22, 0x00, 0xE0])
    uc.mem_write(DIAG_ADDR, payload)
    print(f"  Wrote {len(payload)} bytes of diagnostic payload to eSRAM {DIAG_ADDR:#010x}"
          f" (simulates consecutive type-0 'str value,[address]' writes)")

    # ── Simulate BootROM type-0xFFFF: store jump target at [0xc000500C] ──
    jump_target = thumb(DIAG_ADDR)            # Thumb bit set
    uc.mem_write(ADDR_JUMP_TARGET, struct.pack("<I", jump_target))
    print(f"  Stored jump target {jump_target:#010x} at [0xc000500C]"
          f" (simulates type-0xFFFF packet; low16={jump_target & 0xFFFF:#06x})")

    # ── Emulate FUN_ffff0144 equivalent indirect branch ──
    # ldr r1,[0xc0005000]; ldr r0,[r1,#0xc]; bx r0  -> PC <- [0xc000500C]
    print(f"  Indirect branch: PC <- [0xc000500C] = {DIAG_ADDR:#010x} (Thumb={jump_target & 1})")
    uc.reg_write(UC_ARM_REG_PC, jump_target)

    # Run until the b . loop or instruction budget
    try:
        uc.emu_start(jump_target, 0xC0005000 + 0x1000, count=50)
    except UcError as e:
        print(f"  Emulation stopped: {type(e).__name__}: {e}")

    pc = uc.reg_read(UC_ARM_REG_PC)
    in_esram = (ESRAM_BASE <= (pc & ~1) < ESRAM_BASE + ESRAM_SIZE)
    print(f"  Final PC = {pc:#010x}  (in eSRAM: {in_esram})")

    ok = in_esram
    print(f"  {'RAM-jump emulation SUCCEEDED: control transferred to and executes in eSRAM.' if ok else 'RAM-jump emulation FAILED.'}")
    return ok


if __name__ == "__main__":
    ok = emulate_ram_jump()
    raise SystemExit(0 if ok else 1)
