"""S54: llamadas a las primitivas GPIO de BIONZ en av-cam.bin (gpio_get 0x43b5e2bc, gpio_cfg 0x43b5e22e, gpio_set 0x43b5e29a) con r0/r1 inmediatos."""
import re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
ROOT = Path(__file__).resolve().parents[2]
F = ROOT/'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000
TG = {0x43b5e2bc: 'get', 0x43b5e22e: 'cfg', 0x43b5e29a: 'set'}
def calls():
    d = F.read_bytes(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
    ins = [i for i in md.disasm(d[:0x43fe0000-B], B) if i.mnemonic != '.byte']
    regs = {}; out = []
    for k, i in enumerate(ins):
        op, o = i.mnemonic, i.op_str
        m = re.match(r'(r\d+), #(0x[0-9a-f]+|\d+)$', o)
        if m and op in ('movs', 'mov', 'mov.w', 'movw'): regs[m.group(1)] = int(m.group(2), 0)
        elif op in ('bl', 'b.w', 'blx') and o.startswith('#'):
            t = int(o[1:], 16)
            if t in TG: out.append((i.address, TG[t], regs.get('r0'), regs.get('r1'), regs.get('r2')))
            regs = {}
        elif op in ('push', 'push.w') or op.startswith('b'): regs = {} if op.startswith('b') and op not in ('bic', 'bics', 'bfi', 'bfc') else regs
        else:
            m = re.match(r'(r\d+),', o)
            if m and not op.startswith(('str', 'cmp', 'tst')): regs.pop(m.group(1), None)
    return out
if __name__ == '__main__':
    for a, kind, r0, r1, r2 in calls():
        print(f'{a:#x} {kind} ch={r0} bit={r1} r2={r2}')
