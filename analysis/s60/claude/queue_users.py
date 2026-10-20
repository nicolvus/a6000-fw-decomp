"""S60-Claude: usuarios del handle de cola 0x8f0313 / pool 0x8f013a y wrappers OSAL (tabla +0x14 del objeto OSAL)."""
import sys, struct, json, re, collections
sys.path.insert(0, 'analysis/s60/claude')
import a7dis
from capstone import *
D, B = a7dis.D, a7dis.BASE
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN); md.detail = False
# 1) wrappers OSAL: patrón ldr.w r?,[r?,#off]; blx — enumera 0x4355e000..0x43561000
wr = {}
for a in range(0x4355e000, 0x43562000, 2):
    ins = list(md.disasm(D[a-B:a-B+0x20], a, 8))
    t = [f"{i.mnemonic} {i.op_str}" for i in ins]
    if len(t) >= 8 and t[0].startswith('push {r3') and 'ldr.w' in t[6] and t[7].startswith('blx') and '#0x14]' in t[5]:
        m = re.search(r'#(0x[0-9a-f]+)\]', t[6]); wr[a] = int(m.group(1), 16)
    elif len(t) >= 8 and t[0].startswith('ldr r3') and t[1].startswith('push {r4'):
        pass
json.dump({hex(k): hex(v) for k, v in wr.items()}, open('analysis/s60/claude/osal_wrappers.json', 'w'), indent=0)
print(len(wr), 'wrappers; offsets distintos', len(set(wr.values())))
off2w = collections.defaultdict(list)
for a, o in wr.items(): off2w[o].append(a)
# 2) para cada ocurrencia del literal 0x8f0313: función contenedora (retroceder al push) y wrappers llamados con r0=queue
def lit_sites(v):
    p = struct.pack('<I', v); i = 0; r = []
    while (i := D.find(p, i)) >= 0: r.append(B+i); i += 1
    return r
res = {}
for q in (0x8f0313,):
    for s in lit_sites(q):
        # busca el ldr pc-relativo que apunta aquí, en ventana previa 0x120
        users = []
        for a in range(max(B, s-0x200), s, 2):
            for i in md.disasm(D[a-B:a-B+4], a, 1):
                if i.mnemonic.startswith('ldr') and 'pc' in i.op_str and '[pc' in i.op_str:
                    m = re.search(r'#(0x[0-9a-f]+)', i.op_str); d = int(m.group(1), 16) if m else 0
                    if ((i.address + 4) & ~3) + d == s: users.append(i.address)
        res[hex(s)] = [hex(u) for u in users]
json.dump(res, open('analysis/s60/claude/queue_literal_users.json', 'w'), indent=0)
print(sum(len(v) for v in res.values()), 'ldr que cargan 0x8f0313')
