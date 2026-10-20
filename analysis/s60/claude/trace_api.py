"""S60-Claude: API de trazas A7S (0x438f6864 trace_evt, 0x438f7114 log_printf, 0x439b3918 memcpy ARM) y emisores 0x1000/0x1001."""
import sys, json, struct, hashlib, collections
sys.path.insert(0, 'analysis/s60/claude'); import a7dis
from capstone import *
D, B = a7dis.D, a7dis.BASE
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
T = {0x438f6864: 'trace_evt', 0x438f7114: 'log_printf', 0x439b3918: 'memcpy_arm', 0x43ada07a: 'emit1000', 0x43ada0b4: 'emit1001', 0x43544270: 'm3_fields'}
callers = collections.defaultdict(list)
for off in range(0, len(D) - 4, 2):
    for i in md.disasm(D[off:off+4], B+off, 1):
        if i.mnemonic in ('bl', 'blx', 'b.w'):
            try: t = int(i.op_str.lstrip('#'), 16)
            except ValueError: continue
            if t in T: callers[T[t]].append(B+off)
def lit(v):
    p = struct.pack('<I', v); i = 0; n = 0
    while (i := D.find(p, i)) >= 0: n += 1; i += 1
    return n
out = dict(sha256=hashlib.sha256(D).hexdigest(),
           callers={k: len(v) for k, v in callers.items()},
           emit_callers={k: [hex(a) for a in callers[k]] for k in ('emit1000', 'emit1001', 'm3_fields')},
           trace_evt_in_imager_ctor_region=[hex(a) for a in callers['trace_evt'] if 0x43ada000 <= a < 0x43adb000],
           handle_literals={hex(v): lit(v) for v in (0x8f013a, 0x8f0313, 0x8f0139)},
           execute_vtable_slot=0x43fce088, execute_ptr=hex(struct.unpack_from('<I', D, 0x43fce088 - B)[0]))
json.dump(out, open('analysis/s60/claude/trace_api.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('callers', 'emit_callers', 'handle_literals', 'execute_ptr')}))
