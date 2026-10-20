"""S54: cliente compacto del demonio REA. rq.py tool '{json args}' [tool2 '{args2}' ...] -> imprime solo el contenido útil."""
import sys, json, socket
SOCK = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/run/s54.sock'
calls = [{"tool": sys.argv[i], "args": json.loads(sys.argv[i+1])} for i in range(1, len(sys.argv), 2)]
s = socket.socket(socket.AF_UNIX); s.connect(SOCK)
s.sendall((json.dumps({"calls": calls}) + "\n").encode())
for l in s.makefile("rb"):
    r = json.loads(l)
    if 'call' not in r: continue
    print('###', r['call']['tool'], json.dumps(r['call']['args']))
    res = r.get('result', r)
    for c in res.get('content', []):
        t = c.get('text', '')
        try:
            j = json.loads(t)
        except Exception:
            print(t[:6000]); continue
        for k in ('normalized_result',):
            if k in j:
                v = j[k]
                print(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)[:int(__import__('os').environ.get('RQMAX','9000'))]); break
        else:
            keys = [k for k in j if k not in ('evidence_id', 'subject', 'provider', 'analysis_provenance', 'coverage', 'limitations', 'relationship_coverage', 'locations', 'evidence_links')]
            print(json.dumps({k: j[k] for k in keys})[:6000])
