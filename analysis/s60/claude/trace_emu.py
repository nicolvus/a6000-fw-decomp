"""S60-Claude: ejecuta 0x43ada07a/0x43ada0b4 + 0x438f6864 reales (Unicorn) con OSAL sustituido: captura el registro enviado a la cola de trazas 0x8f013a."""
import sys, struct, json
from pathlib import Path
R = Path(__file__).resolve().parents[3]
for p in ('analysis/s58', 'analysis/s57', 'analysis/s55'): sys.path.insert(0, str(R / p))
from unicorn.arm_const import *
from a7s_emu import A7S
POOL, MSG = 0x45800000, 0x45800100
def make(unit_ok=1, alloc_ok=0, send_rc=0):
    sent = []; log = []
    def alloc(s):                       # 0x4355f590(pool,&out,size,flags)
        r0 = s.u.reg_read(UC_ARM_REG_R0); r1 = s.u.reg_read(UC_ARM_REG_R1); r2 = s.u.reg_read(UC_ARM_REG_R2)
        log.append(('alloc', r0, r2))
        if alloc_ok: return 1
        s.u.mem_write(POOL, bytes(0x100)); s.w32(r1, POOL); return 0
    def send(s):                        # 0x4355f4cc(queue,msg)
        q = s.u.reg_read(UC_ARM_REG_R0); m = s.u.reg_read(UC_ARM_REG_R1)
        sent.append((q, s.rd(m, 0x2c))); log.append(('send', q)); return send_rc
    stubs = {0x4355f590: alloc, 0x4355f4cc: send, 0x438f6840: lambda s: unit_ok, 0x438f67f0: lambda s: 0,
             0x438f6834: lambda s: 0, 0x4355f4e8: lambda s: log.append(('force', 0)) or 0, 0x4355f5ac: lambda s: log.append(('free', 0)) or 0}
    e = A7S(ambito=[(0x438f6000, 0x438f7000), (0x43ada000, 0x43adb000)], stubfn=stubs)
    try: e.u.mem_map(0x45800000, 0x10000)
    except Exception: pass
    return e, sent, log
def run(fn, args, **k):
    e, sent, log = make(**k); e.call(fn, *args); return sent, log
if __name__ == '__main__':
    out = {}
    for name, fn in (('0x1000', 0x43ada07a), ('0x1001', 0x43ada0b4)):
        sent, log = run(fn, (0, 0x11223344, 0x55667788, 0x99aabbcc))
        out[name] = dict(sent=[(hex(q), m.hex()) for q, m in sent], log=log)
    sent, log = run(0x438f6864, (1, 0x1234, 0xaaaa5555, 0x0f0f0f0f), unit_ok=0); out['unit_filtered'] = dict(sent=len(sent), log=log)
    sent, log = run(0x438f6864, (1, 0x1234, 1, 2), send_rc=1); out['send_fail'] = dict(sent=len(sent), log=log)
    json.dump(out, open('analysis/s60/claude/trace_emu.json', 'w'), indent=1); print(json.dumps(out)[:1500])
