"""Tests del hito S181 — módulo [FACE]."""
import json

def test_face_counts():
    d=json.load(open('analysis/s181_face/face_strings.json'))
    assert len(d['a6000'])==70
    assert len(d['a7s'])==70
    assert len(d['a6300'])==70
    # textos interiores idénticos
    def core(s):
        t=s
        if t.startswith('[FACE]:'):
            t=t[len('[FACE]:'):].strip()
        elif t.startswith('[FACE]'):
            t=t[len('[FACE]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert a==b==c
    assert len(a)==70