"""S58-C: escenarios A7S (código real): SetMode(modo) -> SetExposure(shut) -> SetRead(agc) -> Execute; guarda snapshots, tramas P2S y MMIO. Salida: out/a7s_scenarios.json"""
import sys, json, time, struct
sys.path.insert(0, '.')
from a7s_emu import A7S, shadow, R0, NREC
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3
from a7s_p2s import transactions, regs, device_regs
MODES = [0x0b, 0x4c, 0x4d, 0x4e, 0x4f, 0x35]
def scenario(mode, shut=0, svd=0x456, shd=0x123, spl=0x78, agc=0x100, fill=0, **kw):
    msgs = []
    def msg(e):
        u = e.u; msgs.append([u.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]); return 1
    e = A7S(fill=fill, stubfn={0x438f6864: msg}); S = {'init': shadow(e)}; ret = {}; nm = {}
    def records():
        return [list(struct.unpack('<HHH', e.rd(R0 + 6 * k, 6))) for k in range(NREC)]
    ordered = {'init': records()}
    ret['setmode'] = e.setmode(mode); S['setmode'] = shadow(e); nm['setmode'] = len(msgs)
    ordered['setmode'] = records()
    ret['setexp'] = e.setexposure(shd=shd, svd=svd, spl=spl, shut=shut, **kw); S['setexp'] = shadow(e); nm['setexp'] = len(msgs)
    ordered['setexp'] = records()
    ret['setread'] = e.setread(agc=agc); S['setread'] = shadow(e); nm['setread'] = len(msgs)
    ordered['setread'] = records(); ordered['pre_exec'] = records()
    e.writes.clear(); ret['exec'] = e.execute(); S['exec'] = shadow(e); nm['exec'] = len(msgs)
    ordered['exec'] = records()
    tx = transactions(e.writes)
    return dict(mode=mode, shut=shut, args=dict(svd=svd, shd=shd, spl=spl, agc=agc), ret=ret, snaps={k: {'%02x:%02x' % a: v[1] for a, v in s.items()} for k, s in S.items()},
                records=ordered, mmio=e.writes, device_seq=device_regs(tx),
                msgs=msgs, nmsg=nm, tx=[t.hex() for t in tx], seq=regs(tx), stub={hex(a): n for a, n in e.stubbed.items()}, err=getattr(e, 'err', None))
if __name__ == '__main__':
    out = []
    for m in MODES:
        for sh in (0, 1):
            t = time.time(); o = scenario(m, shut=sh); out.append(o)
            print(hex(m), 'shut', sh, 'ret', o['ret'], 'tx', len(o['tx']), 'regs', len(o['seq']), 'msgs', o['nmsg'], 'err', o['err'], round(time.time() - t, 1), 's', flush=True)
    json.dump(out, open('out/a7s_scenarios.json', 'w'))
