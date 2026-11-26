import json, re, sys, collections
sys.path.insert(0, '/tmp/avc')
refs = json.load(open('/tmp/avc/strrefs.json'))
pat = re.compile(r'([A-Za-z0-9_]+/[A-Za-z0-9_/]+\.cpp|[A-Za-z0-9_]+\.cpp)')
bywin = collections.defaultdict(collections.Counter)
for ra, t, s in refs:
    m = pat.search(s)
    if m:
        bywin[ra >> 16][m.group(1)] += 1
lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x4354
hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x43E0
for w in range(lo, hi):
    c = bywin.get(w)
    if not c: continue
    top = ', '.join(f'{k}×{v}' for k, v in c.most_common(3))
    print(f'0x{w:04x}0000..0x{w:04x}ffff  {top}')
