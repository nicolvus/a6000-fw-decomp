"""Tests del hito S196 — módulo [VEF]."""
import json

def test_vef_counts():
    d=json.load(open('analysis/s196_vef/vef_strings.json'))
    assert len(d['a6000'])==149
    assert len(d['a7s'])==141
    assert len(d['a6300'])==144
    def core(s):
        t=s
        if t.startswith('[VEF]:'):
            t=t[len('[VEF]:'):].strip()
        elif t.startswith('[VEF]'):
            t=t[len('[VEF]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==140
    assert len(a-b)==8
    assert len(b-a)==0
    assert len(a&c)==140
    assert len(a-c)==8
    assert len(c-a)==3
