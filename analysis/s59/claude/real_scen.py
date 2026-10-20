"""S59-Claude: escenarios A7S con objeto construido por el ctor real 0x436f3fc0 (en vez del objeto sintético de S58). Salida: real_scenarios.json"""
import sys, json
from pathlib import Path
R = Path(__file__).resolve().parents[2]
for p in ('s58', 's57', 's55'): sys.path.insert(0, str(R / p))
from a7s_emu import A7S, shadow, O, AMBITO
from a7s_p2s import device_regs
sys.path.insert(0, str(Path(__file__).parent))
from p2s59 import transactions
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3
CTOR = 0x436f3fc0
AMB = AMBITO + [(0x43ad9000, 0x43ae0000)]
MODES = [0x0b, 0x35, 0x4c, 0x4d, 0x4e, 0x4f]
def scenario(mode, shut=0, svd=0x456, shd=0x123, spl=0x78, agc=0x100, real=True, idx=0):
    msgs = []
    def msg(e):
        u = e.u; msgs.append([u.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]); return 1
    e = A7S(ambito=AMB if real else AMBITO, stubfn={0x438f6864: msg})
    try: e.u.mem_map(0, 0x1000)   # llamada a puntero nulo: el gancho la registra como stub (si no, fallo de captura)
    except Exception: pass
    if real:
        e.u.mem_write(O, bytes(0x500)); e.call(CTOR, O, idx)
    ret = {'setmode': e.setmode(mode), 'setexp': e.setexposure(shd=shd, svd=svd, spl=spl, shut=shut), 'setread': e.setread(agc=agc)}
    e.writes.clear(); 
    try: ret['exec'] = e.execute()
    except RuntimeError as ex: ret['exec'] = 'ERR ' + str(ex)[:80]
    tx = transactions(e.writes, 0xfc088300 if real else 0xf3c00300)
    return dict(mode=mode, shut=shut, real=real, ret=ret, tx=[t.hex() for t in tx], dev=device_regs(tx), msgs=msgs,
                stub={hex(a): n for a, n in e.stubbed.items()}, shadow={'%02x:%04x' % k: v[1] for k, v in shadow(e).items()})
if __name__ == '__main__':
    out = []
    for m in MODES:
        for sh in (0, 1):
            a = scenario(m, sh, real=True); b = scenario(m, sh, real=False)
            same = a['dev'] == b['dev']; sd = sorted(k for k in a['shadow'] if a['shadow'][k] != b['shadow'].get(k))
            print(hex(m), sh, 'writes real/synt', len(a['dev']), len(b['dev']), 'igual', same, 'shadow dif', len(sd), 'msgs', len(a['msgs']), len(b['msgs']), 'stubs', len(a['stub']), len(b['stub']), flush=True)
            out.append(dict(real=a, synth_dev=b['dev'], same_dev=same, shadow_diff=sd))
    json.dump(out, open(Path(__file__).parent / 'real_scenarios.json', 'w'))
