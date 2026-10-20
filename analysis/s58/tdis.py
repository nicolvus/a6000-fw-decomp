"""S58 util: desensamblado Thumb de A6000/A7S con literales. uso: dis.py A6000|A7S 0xINI 0xFIN"""
import sys, struct
from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS, B
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
import re, os, tempfile
def cache(name):
    """Ruta de caché (barrido Capstone ~45 s por modelo); configurable con S58_CACHE."""
    d = os.environ.get('S58_CACHE') or os.path.join(tempfile.gettempdir(), 'a6000_s58_cache'); os.makedirs(d, exist_ok=True); return os.path.join(d, name)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = False
_D: dict[str, bytes] = {}
def data(m):
    if m not in _D: _D[m] = MODELS[m]['path'].read_bytes()
    return _D[m]
def u32(m, a): return struct.unpack_from('<I', data(m), a - B)[0]
def dis(m, a, b, out=print):
    d = data(m)
    for i in md.disasm(d[a - B:b - B], a):
        note = ''
        mm = re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$', i.op_str)
        if i.mnemonic.startswith('ldr') and mm:
            la = ((i.address + 4) & ~3) + int(mm.group(2), 0)
            try: note = ' ; lit=%#x' % u32(m, la)
            except Exception: pass
        out('%x %s %s%s' % (i.address, i.mnemonic, i.op_str, note))
if __name__ == '__main__': dis(sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0))

def ins_list(m):
    """Lista (dirección, mnemónico, operandos) de un barrido Capstone lineal con reanudación (cacheada)."""
    import pickle
    c = cache(f'ins_{m}.pkl')
    if os.path.exists(c): return pickle.load(open(c, 'rb'))
    from strrefs import sweep
    ins = [(i.address, i.mnemonic, i.op_str) for i in sweep(data(m))]; pickle.dump(ins, open(c, 'wb')); return ins
