#!/usr/bin/env python3
"""Línea B (REA, sesión av-cam) vs Línea A (exports Ghidra históricos) y vs LLVM (decodificador independiente) + bytes."""
import json, re, glob, subprocess, collections
BASE = 0x43541000
raw = open('input/av-cam.bin', 'rb').read()
SHA = 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9'
H = {}
for f in sorted(glob.glob('../ghidra/s*.json')):
    try: d = json.load(open(f))
    except Exception: continue
    if not isinstance(d, dict) or SHA not in (d.get('executable_sha256'), d.get('source_sha256')): continue
    for x in d.get('functions') or []:
        if isinstance(x, dict) and x.get('listing') and (x.get('entry') or x.get('address')):
            H.setdefault(int(str(x.get('entry') or x['address']).replace('0x', ''), 16), (f, x))
nz = lambda s: re.sub(r'\s+', '', re.sub(r'0x0+(?=[0-9a-f])', '0x', s.lower()))
def llvm_map(s, e):
    o = subprocess.run(['llvm-objdump', '-D', '--triple=thumbv7-none-eabi', f'--start-address={s-BASE}', f'--stop-address={e-BASE+1}', 'run/av-cam-view.elf'], capture_output=True, text=True).stdout
    return {int(a, 16)+BASE: m.strip().split()[0] for a, m in re.findall(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{4} ?)+\s*\t(.*)$', o, re.M) if m.strip()}
rows = []
for l in __import__('gzip').open('out/exp2d.jsonl.gz','rt'):
    d = json.loads(l); a = d['call']['args']['procedure']; r = d['result']
    if r.get('isError'): rows.append(dict(addr=a, error=True)); continue
    v = r['structuredContent']['raw_result']['value']; ent = int(a, 16)
    ins = [(int(x.split(': ')[0], 16), x.split(': ', 1)[1]) for x in v['assembly']]
    rngs = [(int(g['start'], 16), int(g['end'], 16)) for g in v['procedure']['body']['ranges']]
    hist = H.get(ent); row = dict(addr=a, name=v['procedure']['name'], n_insn=len(ins), bytes_in_body=v['procedure']['body']['total_bytes'], ranges=len(rngs))
    # (1) bytes: el cuerpo REA cae dentro del mapeo y las instrucciones inician dentro del rango
    row['insn_in_ranges'] = all(any(s <= ad <= e for s, e in rngs) for ad, _ in ins)
    # (2) Línea A: listado (dirección+texto normalizado) y extensión
    if hist:
        la = [(int(x.split(' ')[0], 16), nz(x.split(' ', 1)[1])) for x in hist[1]['listing']]
        lb = [(ad, nz(t)) for ad, t in ins]
        row.update(hist_file=hist[0], insn_hist=len(la), addr_seq_equal=[x for x, _ in la] == [x for x, _ in lb], text_equal=la == lb)
        if la != lb: row['first_diff'] = next(((x, y) for x, y in zip(la, lb) if x != y), None)
    # (3) LLVM independiente: mnemónico base en cada dirección de instrucción REA
    lm = {}
    for s, e in rngs: lm.update(llvm_map(s, e))
    mm = lambda t: re.sub(r'(\.w|\.n)$', '', t.split()[0].lower())
    cmp_ = [(ad, mm(t), lm.get(ad)) for ad, t in ins]
    row['llvm_decoded_at_addr'] = sum(1 for _, _, m in cmp_ if m); row['llvm_mnemonic_equal'] = sum(1 for _, a_, m in cmp_ if m and re.sub(r'(\.w|\.n)$', '', m.lower()).rstrip('s') == a_.rstrip('s'))
    rows.append(row)
json.dump(rows, open('out/exp2-comparison.json', 'w'), indent=1)
n = len(rows); h = [r for r in rows if 'text_equal' in r]
print('REA funciones comparadas', n, '| con listado histórico', len(h))
print('listado idéntico (dir+texto):', sum(r['text_equal'] for r in h), '| mismas direcciones:', sum(r['addr_seq_equal'] for r in h))
print('insn en rangos:', sum(r['insn_in_ranges'] for r in rows if 'insn_in_ranges' in r), '/', n)
t = sum(r['n_insn'] for r in rows if 'n_insn' in r); print('LLVM decodifica en dirección:', sum(r['llvm_decoded_at_addr'] for r in rows if 'n_insn' in r), '/', t, '| mnemónico igual:', sum(r['llvm_mnemonic_equal'] for r in rows if 'n_insn' in r))
print('diferentes:', [(r['addr'], r.get('first_diff')) for r in h if not r['text_equal']][:6])
