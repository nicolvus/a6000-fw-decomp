"""S60-Claude (A6000): productores del bloque de 24 B obj+0xe20 (= payload+0x20 de Sol) vía accesor 0x43ae8504; comprobación de patrones de bytes."""
import json, re
from capstone import *
D = open('analysis/rea-independent/input/av-cam.bin', 'rb').read(); B = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
def ins(a, n): return [(i.address, i.mnemonic, i.op_str) for i in md.disasm(D[a-B:a-B+n], a)]
def stores(a, n):
    return sorted((int(re.search(r'#(0x[0-9a-f]+|\d+)\]', o).group(1), 0) if re.search(r'#(0x[0-9a-f]+|\d+)\]', o) else 0) for _, m, o in ins(a, n) if m == 'strh')
A = stores(0x437ab516, 0x22)            # productor A: 12 strh uniformes en dos valores
Bp = stores(0x43aecc00, 0x40)           # productor B: 5 pares desde obj8+0x48..0x5f
src_B = sorted(int(re.search(r'#(0x[0-9a-f]+|\d+)\]', o).group(1), 0) for _, m, o in ins(0x43aecc00, 0x40) if m == 'ldrh.w')
out = dict(accessor_e20='0x43ae8504', producer_A_call='0x437ab510', producer_A_dst_offsets=[hex(x) for x in A],
           producer_B_call='0x43aecbfa', producer_B_dst_offsets=[hex(x) for x in Bp], producer_B_src_offsets=[hex(x) for x in src_B],
           producer_B_sixth_pair='0x43aecc50 bl 0x437a5a6c -> strh [r4,#0x14],[r4,#0x16]',
           B_callers=['0x437ac16e', '0x43aecfea', '0x43aed068'], A_caller='0x437ad552')
json.dump(out, open('analysis/s60/claude/e20_producers.json', 'w'), indent=1); print(json.dumps(out))
