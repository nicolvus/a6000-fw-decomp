import sys, struct, re
sys.path.insert(0,'/tmp')
from elfhelper import Elf
from capstone import *

path, start, ln = sys.argv[1], int(sys.argv[2],0), int(sys.argv[3],0)
e = Elf(path); d = e.d
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail=False
SEC = [(n,a,o,sz) for n,(a,o,sz) in e.sec.items() if a]
def sec_of(va):
    for n,a,o,sz in SEC:
        if a <= va < a+sz: return n
    return '?'
def rd32(va): return struct.unpack_from('<I', d, va)[0]
def cstr(va):
    if not (0 <= va < len(d)): return None
    j = d.find(b'\0', va, va+200)
    if j < 0: return None
    s = d[va:j]
    if len(s) < 3: return None
    if all(32 <= c < 127 for c in s): return s.decode()
    return None
end = start + ln; pos = start
while pos < end:
    ins = None
    for i in md.disasm(d[pos:min(pos+4,end)], pos):
        if i.address == pos: ins = i
        break
    if ins is None:
        print('%08x  %-8s .hword   0x%04x' % (pos, d[pos:pos+2].hex(), struct.unpack_from('<H',d,pos)[0])); pos += 2; continue
    note = ''
    m = re.match(r'(r\d+|sb|sl|fp|ip), \[pc, #(0x[0-9a-f]+)\]', ins.op_str)
    if ins.mnemonic == 'ldr' and m:
        lit = ((pos + 4) & ~3) + int(m.group(2),16)
        val = rd32(lit)
        s = cstr(val)
        note = '[%08x]=%08x%s' % (lit, val, (' "%s"' % s) if s else '')
    elif ins.mnemonic in ('bl','blx','b','b.w'):
        note = ''
    print('%08x  %-10s %-8s %-30s ; %-10s %s' % (pos, ins.bytes.hex(), ins.mnemonic, ins.op_str, sec_of(pos), note))
    pos += ins.size
