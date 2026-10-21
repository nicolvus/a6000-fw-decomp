"""S71-2: llamadas a gpio_get/gpio_cfg/gpio_set de BIONZ y el origen de sus argumentos (r0/r1)."""
import collections
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path('analysis/rea-independent/input/av-cam.bin').read_bytes(); base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
P = {'#0x43b5e2bc': 'get', '#0x43b5e22e': 'cfg', '#0x43b5e29a': 'set'}
res = collections.defaultdict(list)
for k, i in enumerate(ins):
    if i.mnemonic == 'bl' and i.op_str in P:
        a0 = a1 = None
        for x in reversed(ins[max(0, k-8):k]):
            m = re.match(r'(r[01]), #(0x[0-9a-f]+|\d+)$', x.op_str)
            if x.mnemonic.startswith(('mov', 'movs', 'movw')) and m:
                if m.group(1) == 'r0' and a0 is None: a0 = int(m.group(2), 0)
                if m.group(1) == 'r1' and a1 is None: a1 = int(m.group(2), 0)
            if x.mnemonic.startswith(('mov', 'ldr')) and re.match(r'r0, ', x.op_str) and a0 is None and not m: a0 = 'var'
            if x.mnemonic.startswith(('mov', 'ldr')) and re.match(r'r1, ', x.op_str) and a1 is None and not m: a1 = 'var'
        res[P[i.op_str]].append((hex(i.address), a0, a1))
for k, v in res.items():
    var = [x for x in v if x[1] == 'var' or x[2] == 'var']
    print(k, len(v), 'con argumento variable:', len(var))
    for x in var[:25]: print('  ', x)
