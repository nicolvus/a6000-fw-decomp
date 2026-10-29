#!/usr/bin/env python3
"""
E26-R8 — Sony A6000 BootROM UART receiver offline parser.

Parses the BootROM serial receiver protocol reconstructed from static REA of
bootrom.bin (SHA-256: 81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026).
All offsets, register addresses, and packet formats are derived from the
disassembled BootROM code — not assumed from other devices.

This is an OFFLINE analyser only. It does not open, send to, or communicate
with any real hardware. It validates synthetic or captured frame data against
the protocol as implemented in the BootROM binary.

BootROM entry points (all at base 0xffff0000):
  FUN_ffff1062  - BootROM main entry (reset vector)
  FUN_ffff0fa0  - Serial receiver wrapper
  FUN_ffff0876  - Main serial receive loop (772 bytes, Thumb)
  FUN_ffff0634  - Byte-level serial receive (578 bytes, Thumb)
  FUN_ffff05da  - Bit wait / timing (90 bytes, Thumb)
  FUN_ffff0f82  - Read single bit from MMIO 0xf2915010 bit 1
  FUN_ffff0f52  - Timer-based delay (poll 0xf240310c)
  FUN_ffff0f72  - Timer compare
  FUN_ffff0144  - Indirect jump via 0xc0005000
  FUN_ffff0d62  - LED error loop (infinite)

MMIO registers (CXD90014, from sony-oss headers + REA literals):
  0xf2915010  MISC_MODEREG, bit 1 = BOOT_SERIAL_IN (serial data input)
  0xf2910410  GPIO(4,RDATA) — pin direction/data (candidate UART RX pin)
  0xf2403000  Timer base (0xf240310c = timer counter used for bit timing)
  0xc0005000  Jump target storage (type 0xFFFF packet stores address here)
  0xc0010004  UART config table / mode pointer

Packet format (reconstructed from FUN_ffff0876 disassembly):
  - Bit sampling: read 0xf2915010 bit 1, wait for transitions via timer
  - 8 data bits reconstructed LSB-first with XOR checksum accumulation
  - 9th bit = parity/stop, checked via FUN_ffff05da timing
  - Checksum: XOR of data bytes, then CRC8-table lookup (FUN_ffff0c00),
    XOR again with shifted accumulator (FUN_ffff0634 tail)

Packet types (first byte / type field):
  Type 0x0000  : data packet — stores 2-byte value + 2-byte address
  Type 0xFFFF  : jump packet — stores jump target at 0xc000500c, then
                  FUN_ffff0144 loads from 0xc0005000 and branches (BX r0)
  Type 0xFF01  : error 0x3002 — timeout / framing
  Type 0xFF02  : error 0x3003 — parity / bit error
  Type 0xFF03  : error 0x3004 — stop bit error
  Type 0xFF04  : error 0x100c — general protocol error
  Type 0xFF05  : error 0x2004 — packet too large (>0x1000)
  Type 0xFF06  : error 0x2005 — mode/state error
  Type 0xFF07  : error 0x100d — checksum error

Return codes from FUN_ffff0876:
  0            : success (jump address stored, valid packet type 0)
  0x3001 (12289): jump request (type 0xFFFF received)
  0x3002 (12290): timeout (no start bit within 0x3b iterations)
  0x3003 (12291): parity error
  0x3004 (12292): stop bit error
  0x100c (4108): general error
  0x100d (4109): checksum error
  0x2004 (8196): packet too large
  0x2005 (8197): mode error
"""

import struct
import sys
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any

# ── BootROM constants (from REA literals and disassembly) ────────────────────

BOOTROM_BASE = 0xFFFF0000
BOOTROM_SHA256 = "81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026"

# MMIO addresses
MMIO_MISC_MODEREG = 0xF2915010   # bit 1 = BOOT_SERIAL_IN
MMIO_GPIO4_RDATA  = 0xF2910410   # GPIO(4, RDATA) — candidate UART RX pin
MMIO_TIMER_BASE   = 0xF2403000   # timer used for bit timing
MMIO_TIMER_CNTR   = 0xF240310C   # timer counter register

# BootRAM addresses
ADDR_JUMP_TARGET  = 0xC000500C   # type 0xFFFF stores jump address here
ADDR_JUMP_VECTOR  = 0xC0005000   # FUN_ffff0144 loads from here and BX r0
ADDR_UART_CONFIG  = 0xC0010004   # UART config table pointer

# UART config values from FUN_ffff0554 (two paths based on GPIO(4,RDATA) bit 22)
UART_CONFIG_PATH_A = [0x04A0, 0x038D, 0x070A, 0x033E, 0x0001]  # when bit set
UART_CONFIG_PATH_B = [0x0E74, 0x0B18, 0x0F05, 0x0A23, 0x0014]  # when bit clear

# Return codes from FUN_ffff0876
RET_SUCCESS        = 0x0000
RET_JUMP_REQUEST   = 0x3001  # type 0xFFFF — jump to RAM address
RET_TIMEOUT        = 0x3002  # no start bit
RET_PARITY_ERROR   = 0x3003  # parity bit mismatch
RET_STOP_ERROR     = 0x3004  # stop bit error
RET_GENERAL_ERROR  = 0x100C
RET_CHECKSUM_ERROR = 0x100D
RET_PACKET_TOO_LARGE = 0x2004
RET_MODE_ERROR     = 0x2005

# Packet type → return code mapping
TYPE_TO_RET: Dict[int, int] = {
    0xFF01: RET_TIMEOUT,
    0xFF02: RET_PARITY_ERROR,
    0xFF03: RET_STOP_ERROR,
    0xFF04: RET_GENERAL_ERROR,
    0xFF05: RET_PACKET_TOO_LARGE,
    0xFF06: RET_MODE_ERROR,
}

# ── CRC8 table (reconstructed from FUN_ffff0c00 usage in FUN_ffff0634) ───────
# The BootROM uses a table-based CRC8 at FUN_ffff0c00. The polynomial is not
# explicitly visible in the disassembly; the table is built from it. We
# reconstruct a placeholder — the exact polynomial must be verified against
# captured frames before trusting checksum validation.
def _build_crc8_table_placeholder() -> List[int]:
    """Placeholder CRC8 table. NOT verified against bootrom.bin."""
    table = []
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07  # placeholder polynomial — UNVERIFIED
            else:
                crc = crc << 1
            crc &= 0xFF
        table.append(crc)
    return table

CRC8_TABLE = _build_crc8_table_placeholder()

# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class UartFrame:
    """A single decoded UART frame as processed by FUN_ffff0876."""
    type: int
    value: Optional[int] = None      # 2-byte value (type 0)
    address: Optional[int] = None    # 2-byte address (type 0)
    jump_target: Optional[int] = None  # jump target low 16 bits (type 0xFFFF)
    jump_target_hi: Optional[int] = None  # reserved / high part (type 0xFFFF)
    ret_code: int = RET_SUCCESS
    valid_checksum: bool = False
    raw_bytes: List[int] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class ParseResult:
    """Result of parsing a byte stream."""
    frames: List[UartFrame] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_bytes_consumed: int = 0

# ── Parser ───────────────────────────────────────────────────────────────────

def crc8_byte(table: List[int], crc: int, byte: int) -> int:
    """Single-byte CRC8 step using table lookup (as in FUN_ffff0c00)."""
    return table[(crc ^ byte) & 0xFF]

def compute_frame_checksum(data: List[int]) -> int:
    """
    Reconstruct the BootROM checksum algorithm from FUN_ffff0634 tail:
      - XOR-accumulate data bytes (with the 0xFFFF type as seed)
      - CRC8 table lookup on the XOR result
      - XOR again with shifted accumulator
    Exact polynomial of the table is UNVERIFIED — this is a best-effort
    reconstruction from the call pattern, not from table contents.
    """
    acc = 0
    for b in data:
        acc ^= b
        acc &= 0xFF
    # CRC8 table lookup (FUN_ffff0c00)
    crc = crc8_byte(CRC8_TABLE, 0, acc)
    # XOR with shifted accumulator (from disassembly at 0xffff078c-0xffff0794)
    result = crc ^ (acc >> 8)
    return result & 0xFF

def parse_frames(data: bytes) -> ParseResult:
    """
    Parse a raw byte stream into BootROM UART frames.
    
    This is an OFFLINE parser — it does not communicate with hardware.
    It interprets the byte stream as if it were received by FUN_ffff0876,
    applying the packet format reconstructed from the BootROM disassembly.
    
    Frame format (as implemented in BootROM):
      [type_hi][type_lo][value_hi][value_lo][addr_hi][addr_lo][checksum]
      For type 0xFFFF: [0xFF][0xFF][jump_hi][jump_lo][0x00][0x00][checksum]
    
    The parser is heuristic: without the exact bit-timing and parity rules
    verified against live captures, frame boundaries are inferred from
    known type markers and checksum validation.
    """
    result = ParseResult()
    i = 0
    n = len(data)
    
    while i < n:
        # Look for a type marker
        if i + 1 >= n:
            result.errors.append(f"Truncated frame at offset {i}: only {n-i} byte(s) remain")
            break
        
        type_val = (data[i] << 8) | data[i + 1]
        
        if type_val == 0x0000:
            # Data packet: 6 bytes total + checksum = 7 bytes
            if i + 7 > n:
                result.errors.append(f"Truncated type-0 packet at offset {i}")
                break
            value = (data[i + 2] << 8) | data[i + 3]
            address = (data[i + 4] << 8) | data[i + 5]
            checksum = data[i + 6]
            payload = [data[i], data[i + 1], data[i + 2], data[i + 3],
                       data[i + 4], data[i + 5]]
            computed = compute_frame_checksum(payload)
            valid = (computed == checksum)
            frame = UartFrame(
                type=type_val, value=value, address=address,
                valid_checksum=valid, ret_code=RET_SUCCESS if valid else RET_CHECKSUM_ERROR,
                raw_bytes=payload + [checksum],
                error=None if valid else "checksum mismatch"
            )
            result.frames.append(frame)
            i += 7
            
        elif type_val == 0xFFFF:
            # Jump packet: type(2) + jump_target_lo(2) + reserved(2) + checksum(1) = 7 bytes
            # The BootROM stores the jump target at 0xc000500C, then FUN_ffff0144
            # loads from 0xc0005000 and branches (BX r0). The full 32-bit address
            # is reconstructed at runtime from multiple received bytes.
            if i + 7 > n:
                result.errors.append(f"Truncated type-0xFFFF packet at offset {i}")
                break
            jump_target_lo = (data[i + 2] << 8) | data[i + 3]
            reserved = (data[i + 4] << 8) | data[i + 5]
            checksum = data[i + 6]
            payload = [data[i], data[i + 1], data[i + 2], data[i + 3],
                       data[i + 4], data[i + 5]]
            computed = compute_frame_checksum(payload)
            valid = (computed == checksum)
            frame = UartFrame(
                type=type_val, jump_target=jump_target_lo,
                jump_target_hi=reserved,
                valid_checksum=valid,
                ret_code=RET_JUMP_REQUEST if valid else RET_CHECKSUM_ERROR,
                raw_bytes=payload + [checksum],
                error=None if valid else "checksum mismatch"
            )
            result.frames.append(frame)
            i += 7
            
        elif type_val in TYPE_TO_RET:
            # Error response — typically 2 bytes
            result.errors.append(
                f"Error type 0x{type_val:04X} at offset {i}: "
                f"ret=0x{TYPE_TO_RET[type_val]:04X}"
            )
            i += 2
            
        else:
            # Unknown type — skip one byte and try to resync
            result.errors.append(f"Unknown type 0x{type_val:04X} at offset {i}")
            i += 1
    
    result.total_bytes_consumed = i
    return result

# ── Offline capture simulation (synthetic data only) ─────────────────────────

def build_type0_frame(value: int, address: int) -> bytes:
    """Build a synthetic type-0 data frame (does not verify checksum against real HW)."""
    payload = [0x00, 0x00, (value >> 8) & 0xFF, value & 0xFF,
               (address >> 8) & 0xFF, address & 0xFF]
    checksum = compute_frame_checksum(payload)
    return bytes(payload + [checksum])

def build_jump_frame(jump_target: int) -> bytes:
    """Build a synthetic type-0xFFFF jump frame."""
    payload = [0xFF, 0xFF, (jump_target >> 8) & 0xFF, jump_target & 0xFF, 0x00, 0x00]
    checksum = compute_frame_checksum(payload)
    return bytes(payload + [checksum])

# ── Verification / self-test ─────────────────────────────────────────────────

def self_test() -> bool:
    """Run unit tests with synthetic data. Does not touch hardware."""
    print("=== E26-R8 UART Parser Self-Test ===")
    
    # Test 1: Build and parse a type-0 frame
    frame_bytes = build_type0_frame(0x1234, 0x5678)
    result = parse_frames(frame_bytes)
    assert len(result.frames) == 1, f"Expected 1 frame, got {len(result.frames)}"
    f = result.frames[0]
    assert f.type == 0x0000
    assert f.value == 0x1234
    assert f.address == 0x5678
    assert f.valid_checksum
    assert f.ret_code == RET_SUCCESS
    print("  [PASS] Type-0 frame build+parse")
    
    # Test 2: Build and parse a jump frame (jump_target is low 16 bits)
    jump_bytes = build_jump_frame(0xC010)
    result = parse_frames(jump_bytes)
    assert len(result.frames) == 1
    f = result.frames[0]
    assert f.type == 0xFFFF
    assert f.jump_target == 0xC010
    assert f.ret_code == RET_JUMP_REQUEST
    print("  [PASS] Jump frame build+parse")
    
    # Test 3: Corrupted checksum should be detected
    bad = bytearray(build_type0_frame(0x0001, 0x0002))
    bad[-1] ^= 0xFF  # flip checksum
    result = parse_frames(bytes(bad))
    assert len(result.frames) == 1
    assert not result.frames[0].valid_checksum
    assert result.frames[0].ret_code == RET_CHECKSUM_ERROR
    print("  [PASS] Checksum corruption detected")
    
    # Test 4: Multiple frames in one stream
    stream = build_type0_frame(0x0001, 0x1000) + build_jump_frame(0xC020)
    result = parse_frames(stream)
    assert len(result.frames) == 2
    assert result.frames[0].value == 0x0001
    assert result.frames[1].jump_target == 0xC020
    print("  [PASS] Multi-frame stream")
    
    # Test 5: Error types
    err_bytes = bytes([0xFF, 0x01])  # type 0xFF01 = timeout
    result = parse_frames(err_bytes)
    assert len(result.errors) == 1
    assert "0xFF01" in result.errors[0]
    print("  [PASS] Error type parsing")
    
    print("  All self-tests passed.")
    return True

# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return 0 if self_test() else 1
    
    if len(sys.argv) < 2:
        print("Usage: r8-uart-parser.py --selftest")
        print("       r8-uart-parser.py <hex_dump_file>")
        print("       r8-uart-parser.py <hex_string>")
        return 1
    
    arg = sys.argv[1]
    
    # Try to read as hex string directly
    try:
        data = bytes.fromhex(arg.replace(" ", "").replace(":", ""))
    except ValueError:
        # Try as file path
        try:
            with open(arg, "rb") as fh:
                data = fh.read()
        except FileNotFoundError:
            print(f"Error: cannot interpret '{arg}' as hex or file")
            return 1
    
    result = parse_frames(data)
    
    print(f"Parsed {len(data)} bytes → {len(result.frames)} frame(s)")
    for idx, f in enumerate(result.frames):
        print(f"\n  Frame {idx}:")
        print(f"    type=0x{f.type:04X}")
        if f.value is not None:
            print(f"    value=0x{f.value:04X} address=0x{f.address:04X}")
        if f.jump_target is not None:
            print(f"    jump_target=0x{f.jump_target:08X}")
        print(f"    ret_code=0x{f.ret_code:04X}")
        print(f"    valid_checksum={f.valid_checksum}")
        print(f"    raw={f.raw_bytes.hex()}")
        if f.error:
            print(f"    error={f.error}")
    
    if result.errors:
        print(f"\n  Errors ({len(result.errors)}):")
        for e in result.errors:
            print(f"    - {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())