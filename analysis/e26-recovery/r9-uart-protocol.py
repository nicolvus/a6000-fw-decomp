#!/usr/bin/env python3
"""
E26-R9 — Sony A6000 BootROM UART receiver protocol (offline, corrected).

Reconstructed from static REA of bootrom.bin
(SHA-256: 81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026).

Corrections over R8 (r8-uart-parser.py):
  * CRC polynomial is 0xEDB88320, loaded literally at 0xffff0c04 (ldr r2,[pc,#0x90]),
    NOT the placeholder 0x07 used by R8.
  * The CRC is iterative per-byte (FUN_ffff0c00: 8 iterations, MSB-first,
    shift-right, XOR poly on bit0), not a single table lookup over an XOR of
    all bytes.
  * Checksum accumulator is updated per received byte in FUN_ffff0634:
      acc ^= byte; acc &= 0xFF; tmp = crc8_step(acc); new_acc = tmp ^ (old_acc >> 8)
  * The accumulator initial value observed at 0xffff0a20 is 0xFFFFFFFF
    (str r0,[sp,#0x14] with r0 = -1). Marked NEEDS-CONFIRMATION: the exact
    init and the final comparison (accumulator == received byte vs == 0) could
    not be fully verified offline without a live capture.

Packet format (reconstructed from FUN_ffff0876 / FUN_ffff0634 disassembly):
  7 bytes: [type_hi][type_lo][data_hi][data_lo][addr_hi][addr_lo][checksum]
  Type 0x0000: data -> value, addr -> address.  BootROM does str(value, [address])
               with NO address-range validation.  Sender-controlled RAM write.
  Type 0xFFFF: data -> jump target (low half). Stored at [0xc000500C]; flag at
               [0xc0010008].  FUN_ffff0144 then ldr r1,[0xc0005000];
               ldr r0,[r1,#0xc]; bx r0  -> jump to [0xc000500C].

OFFLINE ONLY.  Does not open, send to, or communicate with any real hardware.
"""

import sys
from dataclasses import dataclass, field

# ── BootROM constants (from REA literals and disassembly) ──────────────────────

BOOTROM_BASE = 0xFFFF0000
BOOTROM_SHA256 = "81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026"

# MMIO addresses (verified literals in bootrom.bin)
MMIO_MISC_MODEREG = 0xF2915010   # bit 1 = BOOT_SERIAL_IN
MMIO_GPIO4_RDATA  = 0xF2910410   # GPIO(4, RDATA) — candidate UART RX pin
MMIO_TIMER_BASE   = 0xF2403000   # timer base
MMIO_TIMER_CNTR   = 0xF240310C   # timer counter used for bit timing

# BootRAM / eSRAM addresses (verified literals; 0xc0000000-0xc0100000 = eSRAM)
ADDR_JUMP_TARGET  = 0xC000500C   # type 0xFFFF stores jump address here
ADDR_JUMP_VECTOR  = 0xC0005000   # FUN_ffff0144 loads from here, +0xc, then BX r0
ADDR_UART_CONFIG  = 0xC0010004   # UART config / mode pointer
ADDR_MODE_FLAG    = 0xC0010008   # mode flag (1 after type 0xFFFF / 0xFFxx)
ADDR_PACKET       = 0xC0010218   # received-packet structure (6 fields)
ADDR_PACKET2      = 0xC0010238   # second packet structure

# eSRAM map (CXD90014 headers + bootrom literals)
ESRAM_BASE = 0xC0000000
ESRAM_SIZE = 0x01000000          # 16 MB (SZ_16M)

# Return codes from FUN_ffff0876
RET_SUCCESS        = 0x0000
RET_JUMP_REQUEST   = 0x3001      # type 0xFFFF — jump to RAM address
RET_TIMEOUT        = 0x3002      # no start bit within 0x3b iterations
RET_PARITY_ERROR   = 0x3003
RET_STOP_ERROR     = 0x3004
RET_GENERAL_ERROR  = 0x100C
RET_CHECKSUM_ERROR = 0x100D
RET_PACKET_TOO_LARGE = 0x2004
RET_MODE_ERROR     = 0x2005

TYPE_TO_RET: dict[int, int] = {
    0xFF01: RET_TIMEOUT,
    0xFF02: RET_PARITY_ERROR,
    0xFF03: RET_STOP_ERROR,
    0xFF04: RET_GENERAL_ERROR,
    0xFF05: RET_PACKET_TOO_LARGE,
    0xFF06: RET_MODE_ERROR,
}

# ── CRC8 reconstruction (FUN_ffff0c00) ─────────────────────────────────────────
# Polynomial 0xEDB88320 loaded literally. 8 iterations, MSB-first (lsr),
# XOR poly when bit0 set.  Input is low byte; result is 32-bit.
CRC_POLY = 0xEDB88320
CRC_INIT_ACC = 0xFFFFFFFF  # observed at 0xffff0a20; NEEDS-CONFIRMATION


def crc8_step(byte: int) -> int:
    """One CRC step over a single byte: 8 iterations MSB-first, poly 0xEDB88320."""
    r0 = byte & 0xFF
    for _ in range(8):
        if r0 & 1:
            r0 = (CRC_POLY ^ (r0 >> 1)) & 0xFFFFFFFF
        else:
            r0 = (r0 >> 1) & 0xFFFFFFFF
    return r0


def checksum_update(old_acc: int, byte: int) -> int:
    """One-byte checksum update per FUN_ffff0634 (0xffff077e-0xffff0794).

    acc = (old_acc ^ byte) & 0xFF
    tmp = crc8_step(acc)
    new_acc = tmp ^ (old_acc >> 8)
    """
    old_acc = old_acc & 0xFFFFFFFF
    acc = (old_acc ^ byte) & 0xFF
    tmp = crc8_step(acc)
    new_acc = (tmp ^ (old_acc >> 8)) & 0xFFFFFFFF
    return new_acc


def compute_frame_checksum(data: list[int], init: int = CRC_INIT_ACC) -> int:
    """Iterative checksum over the 6 frame data bytes.

    Coverage: type_hi,type_lo,data_hi,data_lo,addr_hi,addr_lo (the 6 bytes before
    the checksum byte).  NEEDS-CONFIRMATION: whether the checksum byte itself is
    fed into the accumulator and what final value signals success (==0 or ==byte).
    """
    acc = init & 0xFFFFFFFF
    for b in data:
        acc = checksum_update(acc, b)
    return acc & 0xFFFFFFFF


def expected_checksum_byte(type_val: int, value: int, address: int,
                           init: int = CRC_INIT_ACC) -> int:
    """Checksum byte for a 7-byte frame.  Heuristic: the byte that makes the
    post-checksum accumulator equal to the received byte (self-consistency).
    Exact final-comparison rule NEEDS-CONFIRMATION."""
    data = [(type_val >> 8) & 0xFF, type_val & 0xFF,
            (value >> 8) & 0xFF, value & 0xFF,
            (address >> 8) & 0xFF, address & 0xFF]
    acc = compute_frame_checksum(data, init)
    # Heuristic: low byte of accumulator is the transmitted checksum.
    return acc & 0xFF


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class UartFrame:
    type: int
    value: int | None = None          # type 0: 2-byte value
    address: int | None = None        # type 0: 2-byte address
    jump_target: int | None = None    # type 0xFFFF: jump target (low half)
    jump_target_hi: int | None = None # type 0xFFFF: jump target high half (reserved in R8)
    ret_code: int = RET_SUCCESS
    valid_checksum: bool = False
    raw_bytes: list[int] = field(default_factory=list)
    error: str | None = None


@dataclass
class ParseResult:
    frames: list[UartFrame] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_bytes_consumed: int = 0


# ── Parser ─────────────────────────────────────────────────────────────────────

def parse_frames(data: bytes) -> ParseResult:
    """Offline parse of a byte stream into BootROM UART frames.

    Heuristic frame sync on known type markers (0x0000, 0xFFFF, 0xFFxx) with
    checksum validation.  Does not model bit timing / parity (offline only).
    """
    result = ParseResult()
    i = 0
    n = len(data)
    while i < n:
        if i + 1 >= n:
            result.errors.append(f"Truncated frame at offset {i}: {n-i} byte(s) remain")
            break
        type_val = (data[i] << 8) | data[i + 1]

        if type_val == 0x0000:
            if i + 7 > n:
                result.errors.append(f"Truncated type-0 packet at offset {i}")
                break
            value = (data[i + 2] << 8) | data[i + 3]
            address = (data[i + 4] << 8) | data[i + 5]
            checksum = data[i + 6]
            payload = list(data[i:i + 6])
            computed = expected_checksum(type_val, value, address)
            valid = (computed == checksum)
            result.frames.append(UartFrame(
                type=type_val, value=value, address=address,
                valid_checksum=valid,
                ret_code=RET_SUCCESS if valid else RET_CHECKSUM_ERROR,
                raw_bytes=payload + [checksum],
                error=None if valid else "checksum mismatch"))
            i += 7

        elif type_val == 0xFFFF:
            if i + 7 > n:
                result.errors.append(f"Truncated type-0xFFFF packet at offset {i}")
                break
            jump_target_lo = (data[i + 2] << 8) | data[i + 3]
            reserved = (data[i + 4] << 8) | data[i + 5]
            checksum = data[i + 6]
            payload = list(data[i:i + 6])
            computed = expected_checksum(type_val, jump_target_lo, reserved)
            valid = (computed == checksum)
            result.frames.append(UartFrame(
                type=type_val, jump_target=jump_target_lo,
                jump_target_hi=reserved,
                valid_checksum=valid,
                ret_code=RET_JUMP_REQUEST if valid else RET_CHECKSUM_ERROR,
                raw_bytes=payload + [checksum],
                error=None if valid else "checksum mismatch"))
            i += 7

        elif type_val in TYPE_TO_RET:
            result.errors.append(
                f"Error type 0x{type_val:04X} at offset {i}: ret=0x{TYPE_TO_RET[type_val]:04X}")
            i += 2
        else:
            result.errors.append(f"Unknown type 0x{type_val:04X} at offset {i}")
            i += 1
    result.total_bytes_consumed = i
    return result


def expected_checksum(type_val: int, v1: int, v2: int) -> int:
    """Convenience: expected_checksum_byte over the 6-byte payload."""
    return expected_checksum_byte(type_val, v1, v2)


# ── Offline packet builder (synthetic, for validation only) ────────────────────

def build_type0_frame(value: int, address: int) -> bytes:
    """Build a synthetic type-0 data frame (value written to address in RAM)."""
    payload = [0x00, 0x00, (value >> 8) & 0xFF, value & 0xFF,
               (address >> 8) & 0xFF, address & 0xFF]
    chk = expected_checksum_byte(0x0000, value, address)
    return bytes(payload + [chk])


def build_jump_frame(jump_target: int) -> bytes:
    """Build a synthetic type-0xFFFF jump frame."""
    payload = [0xFF, 0xFF, (jump_target >> 8) & 0xFF, jump_target & 0xFF, 0x00, 0x00]
    chk = expected_checksum_byte(0xFFFF, jump_target, 0x0000)
    return bytes(payload + [chk])


# ── Self-test ──────────────────────────────────────────────────────────────────

def self_test() -> bool:
    print("=== E26-R9 UART Protocol Self-Test (corrected CRC 0xEDB88320) ===")
    ok = True

    # T1: type-0 build + parse round-trip
    fb = build_type0_frame(0x1234, 0x5678)
    r = parse_frames(fb)
    if not (len(r.frames) == 1 and r.frames[0].type == 0x0000
            and r.frames[0].value == 0x1234 and r.frames[0].address == 0x5678
            and r.frames[0].valid_checksum and r.frames[0].ret_code == RET_SUCCESS):
        print("  [FAIL] Type-0 round-trip"); ok = False
    else:
        print("  [PASS] Type-0 frame build+parse")

    # T2: jump frame round-trip
    jb = build_jump_frame(0xC010)
    r = parse_frames(jb)
    if not (len(r.frames) == 1 and r.frames[0].type == 0xFFFF
            and r.frames[0].jump_target == 0xC010
            and r.frames[0].ret_code == RET_JUMP_REQUEST):
        print("  [FAIL] Jump frame round-trip"); ok = False
    else:
        print("  [PASS] Jump frame build+parse")

    # T3: checksum corruption detected
    bad = bytearray(build_type0_frame(0x0001, 0x0002))
    bad[-1] ^= 0xFF
    r = parse_frames(bytes(bad))
    if not (len(r.frames) == 1 and not r.frames[0].valid_checksum
            and r.frames[0].ret_code == RET_CHECKSUM_ERROR):
        print("  [FAIL] Checksum corruption detection"); ok = False
    else:
        print("  [PASS] Checksum corruption detected")

    # T4: multi-frame stream
    stream = build_type0_frame(0x0001, 0x1000) + build_jump_frame(0xC020)
    r = parse_frames(stream)
    if not (len(r.frames) == 2 and r.frames[0].value == 0x0001
            and r.frames[1].jump_target == 0xC020):
        print("  [FAIL] Multi-frame stream"); ok = False
    else:
        print("  [PASS] Multi-frame stream")

    # T5: error types
    r = parse_frames(bytes([0xFF, 0x01]))
    if not (len(r.errors) == 1 and "0xFF01" in r.errors[0]):
        print("  [FAIL] Error type parsing"); ok = False
    else:
        print("  [PASS] Error type parsing")

    # T6: truncated packet rejected
    r = parse_frames(bytes([0x00, 0x00, 0x12]))
    if not (len(r.errors) >= 1 and "Truncated" in r.errors[0]):
        print("  [FAIL] Truncated packet rejection"); ok = False
    else:
        print("  [PASS] Truncated packet rejected")

    print(f"  {'All self-tests passed.' if ok else 'SOME TESTS FAILED.'}")
    return ok


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return 0 if self_test() else 1
    if len(sys.argv) < 2:
        print("Usage: r9-uart-protocol.py --selftest")
        print("       r9-uart-protocol.py <hex_string>")
        return 1
    try:
        data = bytes.fromhex(sys.argv[1].replace(" ", "").replace(":", ""))
    except ValueError:
        print(f"Error: cannot interpret '{sys.argv[1]}' as hex")
        return 1
    result = parse_frames(data)
    print(f"Parsed {len(data)} bytes -> {len(result.frames)} frame(s)")
    for idx, f in enumerate(result.frames):
        print(f"\n  Frame {idx}: type=0x{f.type:04X} ret=0x{f.ret_code:04X} "
              f"valid_chk={f.valid_checksum} raw={bytes(f.raw_bytes).hex()}")
        if f.value is not None:
            print(f"    value=0x{f.value:04X} address=0x{f.address:04X}")
        if f.jump_target is not None:
            print(f"    jump_target=0x{f.jump_target:08X} hi=0x{f.jump_target_hi:04X}")
        if f.error:
            print(f"    error={f.error}")
    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"    - {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
