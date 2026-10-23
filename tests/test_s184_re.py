"""Tests del hito S184 — módulo [RE]."""
import json

def test_re_counts():
    d=json.load(open('analysis/s184_re/re_strings.json'))
    assert len(d['a6000'])==54
    assert len(d['a7s'])==53
    assert len(d['a6300'])==54
    def core(s):
        t=s
        if t.startswith('[RE]:'):
            t=t[len('[RE]:'):].strip()
        elif t.startswith('[RE]'):
            t=t[len('[RE]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==53
    assert len(a-b)==1
    assert len(b-a)==0
    assert len(a&c)==53
    assert len(a-c)==1
    assert len(c-a)==1
