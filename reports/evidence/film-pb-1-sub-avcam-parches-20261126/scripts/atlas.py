"""Atlas mínimo de av-cam.bin: inicios de función y llamadores por destino de BL/BLX (T4)."""
import bisect, struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from capstone.arm import ARM_OP_MEM, ARM_OP_IMM

BASE = 0x43541000
KEYS = ('321', 'base', 'pp')
D = {k: Path(f'/tmp/avc/avcam_{k}.bin').read_bytes() for k in KEYS}
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB); MD.detail = True


def u32(d, a):
    o = a - BASE
    return struct.unpack('<I', d[o:o+4])[0] if 0 <= o <= len(d) - 4 else 0


def cstr(d, a, n=96):
    o = a - BASE
    if not (0 <= o < len(d)): return None
    s = d[o:o+n].split(b'\0')[0]
    if len(s) >= 4 and all(32 <= c < 127 for c in s): return s.decode()
    return None


def branch_scan(d):
    """Una pasada: {destino: [origenes]} para BL/BLX/B.W (T4)."""
    idx = {}
    h = memoryview(d).cast('H')
    for i in range(len(d)//2 - 1):
        a, b = h[i], h[i+1]
        if a & 0xF800 == 0xF000 and b & 0x8000:
            kind = b & 0x5000
            if kind not in (0x4000, 0x5000, 0x1000):
                continue
            s = (a >> 10) & 1; j1 = (b >> 13) & 1; j2 = (b >> 11) & 1
            i1 = ~(j1 ^ s) & 1; i2 = ~(j2 ^ s) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((a & 0x3FF) << 12) | ((b & 0x7FF) << 1)
            if s: imm -= 1 << 25
            t = BASE + 2*i + 4 + imm
            if BASE <= t < BASE + len(d):
                idx.setdefault(t & ~1, []).append(BASE + 2*i)
    return idx


IDX = branch_scan(D['321'])
STARTS = sorted(a for a in IDX if IDX[a])


def owner(a):
    i = bisect.bisect_right(STARTS, a) - 1
    return STARTS[i] if i >= 0 else None


def is_bl_target(a):
    return a in IDX


def func(d, start, limit=900):
    o = start - BASE
    out = []
    for i in MD.disasm(d[o:o+limit*4], start):
        out.append(i)
        if i.mnemonic.startswith('pop') and 'pc' in i.op_str: break
        if i.mnemonic == 'bx': break
        if i.mnemonic == 'b' and i.operands and i.operands[0].type == ARM_OP_IMM and not (start <= i.operands[0].imm <= start + limit*4): break
        if len(out) >= limit: break
    return out


def lits(d, ins):
    out = []
    for i in ins:
        if i.mnemonic.startswith('ldr') and i.operands and i.operands[-1].type == ARM_OP_MEM and i.operands[-1].mem.base == 0 and i.reg_name(i.operands[-1].mem.index) == '':
            lit = ((i.address + 4) & ~3) + i.operands[-1].mem.disp
            out.append((i.address, lit, u32(d, lit)))
    return out


def inline_strings(d, start, end):
    """Cadenas ASCII presentes en el rango (para saber a qué subsistema pertenece)."""
    o0, o1 = start - BASE, end - BASE
    blob = d[o0:o1]
    res, cur = [], bytearray()
    for b in blob:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= 6: res.append(cur.decode())
            cur = bytearray()
    if len(cur) >= 6: res.append(cur.decode())
    return res


if __name__ == '__main__':
    print('starts:', len(STARTS))
    for x in sys.argv[1:]:
        a = int(x, 0)
        ow = owner(a)
        print(f'\n### {a:#x}  owner {ow:#x} (+{a-ow:#x})  sitios_bl={len(IDX.get(ow, []))}')
