"""Tests del hito S200 — módulo [VDF]."""
import json

def test_vdf_counts():
    d=json.load(open('analysis/s200_vdf/vdf_strings.json'))
    assert len(d['a6000'])==243
    assert len(d['a7s'])==162
    assert len(d['a6300'])==162
    def core(s):
        t=s
        if t.startswith('[VDF]:'):
            t=t[len('[VDF]:'):].strip()
        elif t.startswith('[VDF]'):
            t=t[len('[VDF]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==162
    assert len(a-b)==81
    assert len(b-a)==0
    assert len(a&c)==161
    assert len(a-c)==82
    assert len(c-a)==1
