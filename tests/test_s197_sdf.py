"""Tests del hito S197 — módulo [SDF]."""
import json

def test_sdf_counts():
    d=json.load(open('analysis/s197_sdf/sdf_strings.json'))
    assert len(d['a6000'])==477
    assert len(d['a7s'])==479
    assert len(d['a6300'])==488
    def core(s):
        t=s
        if t.startswith('[SDF]:'):
            t=t[len('[SDF]:'):].strip()
        elif t.startswith('[SDF]'):
            t=t[len('[SDF]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==464
    assert len(a-b)==0
    assert len(b-a)==2
    assert len(a&c)==464
    assert len(a-c)==0
    assert len(c-a)==11
