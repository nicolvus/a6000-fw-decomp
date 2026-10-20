"""Decodifica alias bit-band y literales GPIO FM3 (base GPIO 0x4003_3000) y los busca en Darwin.
Uso: python3 -I scripts/fm3_gpio_literals.py darwin_core.bin [base=0x4200]"""
import struct, sys

GPIO = 0x40033000
BANK = {0x000: "PFR", 0x100: "PCR", 0x200: "DDR", 0x300: "PDIR", 0x400: "PDOR", 0x500: "ADE", 0x600: "EPFR"}

def decode_bitband(a):
    """alias 0x42xxxxxx -> (direccion registro 32 bit, bit 0..31)."""
    o = a - 0x42000000
    byte = 0x40000000 + (o >> 5)
    return byte & ~3, (byte & 3) * 8 + ((o >> 2) & 7)

def gpio_name(reg, bit):
    off = reg - GPIO
    k = BANK.get(off & 0xF00)
    if not (0 <= off < 0x1000 and k):
        return None
    n = (off & 0xFF) // 4
    return f"{k}{n:X}[{bit}]" if k != "EPFR" else f"EPFR{n:02X}[{bit}]"

def describe_alias(a):
    reg, bit = decode_bitband(a)
    n = gpio_name(reg, bit)
    return f"{a:#010x} -> {reg:#010x} bit{bit}" + (f" = {n}" if n else "")

def scan(data, base):
    for i in range(0, len(data) - 3, 4):
        v = struct.unpack_from("<I", data, i)[0]
        if GPIO <= v < GPIO + 0x1000:
            yield base + i, v, f"GPIO {v:#x}"
        elif 0x42660000 <= v < 0x42670000:
            yield base + i, v, describe_alias(v)

if __name__ == "__main__":
    base = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x4200
    for a, v, d in scan(open(sys.argv[1], "rb").read(), base):
        print(f"{a:#08x} {d}")
