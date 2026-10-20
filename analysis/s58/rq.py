"""S56: consulta por lotes a la sesión REA (demonio s56) y resume. uso: rq.py tool arg=valor ... [-- tool2 arg=valor ...]"""
import sys, json, subprocess, tempfile, os
SOCK = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/run/s58.sock'
Q = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/bin/q.py'
def run(calls):
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(calls, f); f.close()
    out = subprocess.run([sys.executable, Q, SOCK, f.name], capture_output=True, text=True).stdout; os.unlink(f.name)
    res = []
    for l in out.splitlines():
        r = json.loads(l); t = r.get('result')
        if isinstance(t, dict) and t.get('content'):
            try: res.append(json.loads(t['content'][0]['text']))
            except Exception: res.append(t['content'][0]['text'])
        else: res.append(r)
    return res
def find(o, k):
    if isinstance(o, dict):
        for kk, v in o.items():
            if kk == k: return v
            r = find(v, k)
            if r is not None: return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, k)
            if r is not None: return r
if __name__ == '__main__':
    calls = []
    for grp in ' '.join(sys.argv[1:]).split(' -- '):
        p = grp.split(); calls.append({'tool': p[0], 'args': {kv.split('=')[0]: kv.split('=', 1)[1] for kv in p[1:]}})
    for c, r in zip(calls, run(calls)):
        print('###', c['args']); n = r.get('normalized_result') if isinstance(r, dict) else None
        print(n if isinstance(n, str) else json.dumps(n if n is not None else r)[:4000])
