"""Utilidad S55: desensambla un rango de av-cam.bin (A6000|A7S) resolviendo literales y cadenas (incl. `ldr rX,[pc]; add rX,pc`). uso: fwdis.py A6000 0xINI 0xFIN"""
import sys, struct, re
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from gpio_calls_diff import MODELS, B
def cstr(d, v):
    if 0 <= v - B < len(d) - 80:
        t = d[v - B:v - B + 80].split(b'\0')[0]
        if len(t) >= 3 and all(32 <= c < 127 for c in t): return f' "{t.decode()}"'
    return ''
def dis(model, a, b, out=print):
    d = MODELS[model]['path'].read_bytes(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); lit = {}
    for i in md.disasm(d[a - B:b - B], a):
        s = f'{i.address:#x}  {i.mnemonic} {i.op_str}'
        m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', i.op_str)
        if i.mnemonic.startswith('ldr') and m:
            la = ((i.address + 4) & ~3) + int(m.group(2), 0); v = struct.unpack_from('<I', d, la - B)[0]; lit[m.group(1)] = v
            s += f'   ; ={v:#x}' + cstr(d, v)
        m = re.match(r'(r\d+), pc$', i.op_str)
        if i.mnemonic == 'add' and m and m.group(1) in lit:
            v = (lit[m.group(1)] + i.address + 4) & 0xffffffff; s += f'   ; ->{v:#x}' + cstr(d, v)
        out(s)
if __name__ == '__main__': dis(sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0))
