"""S60-Claude: accesores 0x43ae84xx del objeto global (0x437876dc) y sus llamadores: dónde se produce/consume el bloque obj+0xd60..0xe60 (A6000)."""
import re, json
from capstone import *
D = open('analysis/rea-independent/input/av-cam.bin', 'rb').read(); B = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
imm = lambda s: int(re.search(r'#(0x[0-9a-f]+|\d+)', s).group(1), 0) if re.search(r'#(0x[0-9a-f]+|\d+)', s) else None
acc = {}
for a in range(0x43ae8400, 0x43ae8a20, 2):
    ins = list(md.disasm(D[a-B:a-B+0x10], a, 5))
    if len(ins) >= 4 and ins[0].mnemonic == 'push' and ins[1].mnemonic == 'bl' and ins[1].op_str == '#0x437876dc' and ins[2].mnemonic.startswith('add') and imm(ins[2].op_str) is not None:
        off = imm(ins[2].op_str)
        if ins[3].mnemonic == 'adds' and imm(ins[3].op_str) is not None: off += imm(ins[3].op_str)
        acc[a] = off
want = {a: o for a, o in acc.items() if 0xd60 <= o <= 0xe60}
callers = {a: [] for a in want}
for off in range(0, len(D) - 4, 2):
    for i in md.disasm(D[off:off+4], B+off, 1):
        if i.mnemonic in ('bl', 'b.w', 'blx') and i.op_str.startswith('#'):
            t = int(i.op_str[1:], 16)
            if t in want: callers[t].append(hex(B+off))
out = {hex(a): dict(off=hex(want[a]), callers=c) for a, c in callers.items()}
json.dump(out, open('analysis/s60/claude/accessor_callers.json', 'w'), indent=1)
if __name__ == '__main__':
    for a, v in out.items(): print(a, v['off'], len(v['callers']), v['callers'][:14])
