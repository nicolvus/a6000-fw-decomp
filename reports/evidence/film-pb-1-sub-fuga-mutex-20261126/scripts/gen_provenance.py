import sys, collections
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import dec

b = Binary()
print('# Guardas: escritores de [reg,#4] (posibles escritores de [handle+4])')
for lo, hi, label in [(0x6e807c, 0x6ec200, 'TU mp4Ifo_If'),
                      (b.text_va, b.text_va + b.text_sz, '.text completa')]:
    print('== ' + label)
    a, n, cnt = lo, 0, collections.Counter()
    while a < hi:
        i = dec(a)
        if i is None:
            a += 2
            continue
        o = i.op_str.replace(' ', '')
        if i.mnemonic.startswith('str') and (o.endswith(',#4]') or o.endswith(',#0x4]')):
            cnt[i.mnemonic] += 1
            if label.startswith('TU'):
                print('  %08x %-7s %s' % (a, i.mnemonic, i.op_str))
            n += 1
        a += i.size
    print('  total %d  %s' % (n, dict(cnt)))
print()
print('# NOTA: en la TU solo 0x6E80CE (=0) y 0x6E816A (=sem) escriben [mp4Ifo_If+4];')
print('#       el resto de coincidencias son [sp,#4] o el contenedor de 0x6EC0F0.')
