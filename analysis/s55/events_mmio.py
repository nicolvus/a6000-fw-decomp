"""S55-C/D: censo de bloques MMIO por literales y productores de eventos de exposición (códigos de la tabla de trazas CAIF)."""
import sys, re, struct, bisect, json, collections
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from gpio_calls_diff import MODELS, B, disasm
TAB = {'A6000': 0x43fe8138}
CODES = {0x129: 'ExposureReady', 0x12a: 'ExposureEndNotify', 0x12b: 'ExposureEndRes', 0x135: 'ExpBefore', 0x136: 'ExpStartComp', 0x121: 'CaptureRequest', 0x122: 'CaptureStartRes', 0x12d: 'ImageReadStartNotfy', 0x130: 'ImageReadCompNorify', 0x131: 'ReleaseLock', 0x13a: 'S2REQ HI'}
def scan(model):
    d = MODELS[model]['path'].read_bytes(); ins = disasm(d)
    starts = sorted(i.address for i in ins if i.mnemonic == 'push' and 'lr' in i.op_str)
    regs = {}; ev = collections.defaultdict(list); blocks = collections.Counter()
    for x in ins:
        m = re.match(r'(r\d+), #(0x[0-9a-f]+|\d+)$', x.op_str)
        if m and x.mnemonic in ('movs', 'mov', 'mov.w', 'movw'): regs[m.group(1)] = int(m.group(2), 0)
        m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', x.op_str)
        if m and x.mnemonic.startswith('ldr'):
            a = ((x.address + 4) & ~3) + int(m.group(2), 0); v = struct.unpack_from('<I', d, a - B)[0]; regs[m.group(1)] = v
            if 0xf2000000 <= v < 0xf4000000: blocks[v >> 16] += 1
        if x.mnemonic in ('bl', 'b.w') and x.op_str.startswith('#'):
            c = regs.get('r0')
            if c in CODES or (isinstance(c, int) and (c & 0xffff) in CODES and c >> 16 in (0, 1, 2, 3, 4)):
                ev[c & 0xffff].append((x.address, int(x.op_str[1:], 16), starts[bisect.bisect_right(starts, x.address) - 1]))
            regs = {}
    return ev, blocks
if __name__ == '__main__':
    out = {}
    for m in MODELS:
        ev, bl = scan(m)
        out[m] = dict(events={CODES[c]: [(hex(a), hex(t), hex(f)) for a, t, f in v] for c, v in ev.items()}, mmio_blocks={hex(k << 16): n for k, n in bl.most_common()})
        print(m); 
        for c, v in sorted(ev.items()): print(' ', hex(c), CODES[c], [(hex(a), hex(t), hex(f)) for a, t, f in v][:8])
        print('  MMIO', out[m]['mmio_blocks'])
    json.dump(out, open('analysis/s55/events_mmio.json', 'w'), indent=1)
