import struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from capstone.arm import ARM_OP_MEM, ARM_OP_REG, ARM_OP_IMM

BASE = 0x43541000
A = Path('/tmp/avc/avcam_321.bin').read_bytes()
B = Path('/tmp/avc/avcam_cfw.bin').read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB); MD.detail = True


def rd(d, a, n):
    o = a - BASE
    return d[o:o+n] if 0 <= o < len(d) else b''


def u32(d, a):
    s = rd(d, a, 4)
    return struct.unpack('<I', s)[0] if len(s) == 4 else 0


def cstr(d, a, n=64):
    s = rd(d, a, n).split(b'\0')[0]
    if len(s) >= 4 and all(32 <= c < 127 for c in s):
        return s.decode()
    return None


def anno(d, i):
    """Comentario: literal PC-relativo, destino de salto y cadena resultante."""
    out = []
    a = i.address
    if i.mnemonic.startswith('ldr') and i.operands and i.operands[-1].type == ARM_OP_MEM and i.operands[-1].mem.base == 0 and i.reg_name(i.operands[-1].mem.index) == '':
        # ldr rX, [pc, #imm]
        off = i.operands[-1].mem.disp
        lit = ((a + 4) & ~3) + off
        v = u32(d, lit)
        s = cstr(d, v)
        out.append(f'; lit@{lit:08x}={v:#010x}' + (f' "{s}"' if s else ''))
    if i.mnemonic in ('b', 'bl', 'blx') or i.mnemonic.startswith('b') and i.mnemonic.endswith('.w'):
        if i.operands and i.operands[0].type == ARM_OP_IMM:
            t = i.operands[0].imm
            s = cstr(d, t)
            out.append(f'; ->{t:08x}' + (f' "{s}"' if s else ''))
    if i.mnemonic == 'add' and len(i.operands) >= 3:
        o = i.operands
        if o[-1].type == ARM_OP_REG and o[-1].reg == 15:  # add rX, pc
            out.append('; adr')
    return ('  ' + ' '.join(out)) if out else ''


def show(d, start, end, tag):
    print(f'--- {tag} {start:08x}..{end:08x}')
    for i in MD.disasm(rd(d, start, end - start), start):
        print(f'{i.address:08x}  {i.bytes.hex():<10} {i.mnemonic:<8} {i.op_str}{anno(d, i)}')


def sidebyside(start, end):
    la = {i.address: i for i in MD.disasm(rd(A, start, end - start), start)}
    lb = {i.address: i for i in MD.disasm(rd(B, start, end - start), start)}
    print(f'=== {start:08x}..{end:08x}')
    for a in sorted(set(la) | set(lb)):
        x, y = la.get(a), lb.get(a)
        fx = f'{x.bytes.hex():<10} {x.mnemonic:<8} {x.op_str}{anno(A, x)}' if x else ''
        fy = f'{y.bytes.hex():<10} {y.mnemonic:<8} {y.op_str}{anno(B, y)}' if y else ''
        same = x and y and x.bytes == y.bytes
        print(f'{a:08x}  {"  " if same else "* "}321 {fx:<62} | cfw {fy}')


if __name__ == '__main__':
    a0 = int(sys.argv[1], 16); a1 = int(sys.argv[2], 16)
    sidebyside(a0, a1)
