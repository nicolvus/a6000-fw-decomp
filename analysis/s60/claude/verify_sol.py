"""S60-Claude: verificación independiente (bytes A6000) de las direcciones principales de Sol."""
import sys, struct, hashlib, json
from capstone import *
BIN = 'analysis/rea-independent/input/av-cam.bin'; B = 0x43541000
D = open(BIN, 'rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
def dis(a, n): return [(i.address, i.mnemonic, i.op_str) for i in md.disasm(D[a-B:a-B+n], a)]
def calls(a, n): return [int(o.lstrip('#'), 16) for _, m, o in dis(a, n) if m in ('bl', 'blx', 'b.w') and o.startswith('#')]
R = {}
R['sha'] = hashlib.sha256(D).hexdigest()
R['recv_0x43806e38_calls_dispatcher'] = hex(0x438069f0) in [hex(c) for c in calls(0x43806e38, 0x30)]
# TBH 0x43806a04: entradas u16 (offset/2 respecto a la dirección de tabla + 4 en Thumb)
tbh = [struct.unpack_from('<H', D, 0x43806a08 - B + 2*k)[0] for k in range(12)]

R['tbh_targets'] = {k: hex(0x43806a08 + 2*tbh[k]) for k in (3, 4, 9, 10)}
R['case4_calls_0x43b00d94'] = 0x43b00d94 in calls(0x43806c24, 0x60)
R['case3_calls_0x43b00fe6'] = 0x43b00fe6 in calls(0x43806bf0, 0x40)
R['case9_calls_0x43b00f62'] = 0x43b00f62 in calls(0x43806cd0, 0x40)
R['emitters_call_0x43806400'] = {hex(e): 0x43806400 in calls(e, 0x80) for e in (0x43b00fe6, 0x43b00f62)}
R['send_literal_0x8003030f'] = struct.pack('<I', 0x8003030f) in D[0x43806400-B:0x43806400-B+0xb0]
R['dispatcher_literal_0x3030f_near_recv'] = struct.pack('<I', 0x3030f) in D[0x43806e00-B:0x43806e90-B]
R['publish_dd4_calls'] = [hex(c) for c in calls(0x43b00dd4, 0x60)]
R['writer_da0_tailcalls'] = [hex(c) for c in calls(0x43b00da0, 0x20)]
json.dump(R, open('analysis/s60/claude/verify_sol.json', 'w'), indent=1); print(json.dumps(R))
