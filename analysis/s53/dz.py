"""Helpers de solo lectura para las ROM Darwin (FM3 Cortex-M3, base 0x4200)."""
import hashlib
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / 'firmware/extracted'
ROMS = {
    'a6000': (FW / 'fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
              '5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4'),
    'a7s': (FW / 'a7s-fw320/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
            '241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf'),
    'a6300': (FW / 'a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
              '6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac'),
}
BASE = 0x4200


def rom(name):
    p, h = ROMS[name]
    d = p.read_bytes()
    if hashlib.sha256(d).hexdigest() != h:
        raise ValueError(f'hash distinto: {name}')
    return d


_md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
_md.detail = True


def dis(d, addr, n=40, stop_ret=False):
    out = []
    off = addr - BASE
    for i in _md.disasm(d[off:off + n * 4], addr):
        out.append(i)
        if len(out) >= n:
            break
        if stop_ret and (i.mnemonic in ('bx',) and 'lr' in i.op_str or
                         (i.mnemonic.startswith('pop') and 'pc' in i.op_str)):
            break
    return out


def show(d, addr, n=40, stop_ret=False):
    for i in dis(d, addr, n, stop_ret):
        extra = ''
        if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
            try:
                imm = i.operands[1].mem.disp
                la = ((i.address + 4) & ~3) + imm
                extra = f"  ; =0x{struct.unpack_from('<I', d, la - BASE)[0]:x}"
            except (IndexError, struct.error):  # literal fuera de la ROM
                extra = ''
        print(f'{i.address:06x}  {i.mnemonic:<8} {i.op_str}{extra}')


def u32(d, a):
    return struct.unpack_from('<I', d, a - BASE)[0]


def literal_refs(d, value):
    """Direcciones de palabras alineadas iguales a value."""
    b = struct.pack('<I', value)
    r, i = [], d.find(b)
    while i >= 0:
        if i % 4 == 0:
            r.append(i + BASE)
        i = d.find(b, i + 1)
    return r


if __name__ == '__main__':
    d = rom(sys.argv[1])
    show(d, int(sys.argv[2], 16), int(sys.argv[3]) if len(sys.argv) > 3 else 40)


def ldr_users(d, lit_addr, lo=None, hi=None):
    """Instrucciones ldr pc-relativas (cualquier alineación de inicio) que cargan lit_addr."""
    lo = lo or max(BASE, lit_addr - 4096)
    hi = hi or lit_addr
    res = set()
    for start in range(lo, hi, 2):
        for i in _md.disasm(d[start - BASE:start - BASE + 4], start):
            if (i.mnemonic.startswith('ldr') and '[pc' in i.op_str
                    and ((i.address + 4) & ~3) + i.operands[1].mem.disp == lit_addr):
                res.add(i.address)
            break
    return sorted(res)
