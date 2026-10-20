"""S54: barrido capstone (skipdata) de llamadas al escritor/lector bit-band PDOR del FM3 y literales 0x4266823x.
Uso: p4c_scan.py {a6000|a7s|a6300}. Solo lectura de ROM originales."""
import sys, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
ROOT = Path(__file__).resolve().parents[2]
FW = ROOT/'firmware/extracted'
PATH = {'a6000': FW/'fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
        'a7s': FW/'a7s-fw320/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
        'a6300': FW/'a6300-fw201/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin'}
BASE = 0x4200
def load(name):
    d = PATH[name].read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS); md.skipdata = True
    ins = [i for i in md.disasm(d, BASE) if i.mnemonic != '.byte']
    return d, ins
def writers(d):
    """(escritor str r1,[r0,r2] ; lector ldr r0,[r0,r1]) con literal 0x42668000"""
    w = d.find(bytes.fromhex('f74a81507047')) + BASE
    return w, w + 6
if __name__ == '__main__':
    name = sys.argv[1]; d, ins = load(name); w, r = writers(d)
    print(name, 'writer', hex(w), 'reader', hex(r), 'ninst', len(ins))
    vals = {0x230: 'P4C', 0x234: 'P4D', 0x238: 'P4E'}
    for k, i in enumerate(ins):
        if i.mnemonic == 'bl':
            t = int(i.op_str.lstrip('#'), 16)
            if t in (w, r):
                # buscar hacia atrás: registro asignado con inmediato 0x230.. y r1
                win = ins[max(0, k-12):k]
                tags = []
                for c in win:
                    m = re.match(r'(r\d+), #(0x[0-9a-f]+)$', c.op_str)
                    if m and c.mnemonic.startswith(('mov', 'movs', 'movw')):
                        v = int(m.group(2), 16)
                        tags.append(f'{c.address:#x}:{m.group(1)}={vals.get(v, hex(v))}')
                print(f'{i.address:#x} {"W" if t==w else "R"}', ' '.join(tags))

def track(name):
    """Propagación lineal de constantes (aprox.: ignora ramas; r4-r11 se conservan entre bl, r0-r3 no) hasta cada bl al escritor/lector."""
    d, ins = load(name); w, r = writers(d); out = []
    regs = {}; func = None
    for i in ins:
        op, o = i.mnemonic, i.op_str
        if op in ('push', 'push.w') and 'lr' in o:
            regs = {}; func = i.address
        m = re.match(r'(r\d+), #(-?0x[0-9a-f]+|\d+)$', o)
        if m and op.startswith(('mov', 'movs', 'movw')) and not op.startswith('movt'):
            regs[m.group(1)] = int(m.group(2), 0)
        else:
            m = re.match(r'(r\d+), (r\d+)$', o)
            if m and op in ('mov', 'movs', 'mov.w'):
                regs[m.group(1)] = regs.get(m.group(2))
            else:
                m = re.match(r'(r\d+),', o)
                if m and op != 'cmp' and op != 'bl' and not op.startswith(('str', 'push', 'cmp', 'tst', 'b')):
                    regs.pop(m.group(1), None)
        if op == 'bl':
            t = int(o.lstrip('#'), 16)
            if t in (w, r):
                out.append(dict(addr=i.address, kind='W' if t == w else 'R', func=func, r0=regs.get('r0'), r1=regs.get('r1')))
            for x in ('r0', 'r1', 'r2', 'r3'): regs.pop(x, None)
    return out
