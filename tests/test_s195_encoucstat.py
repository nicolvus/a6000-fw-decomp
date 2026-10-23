"""Tests del hito S195 — módulo [ENCOUCSTAT]."""
import json

def test_encoucstat_counts():
    d=json.load(open('analysis/s195_encoucstat/encoucstat_strings.json'))
    assert len(d['a6000'])==49
    assert len(d['a7s'])==54
    assert len(d['a6300'])==68
    def core(s):
        t=s
        if t.startswith('[ENCOUCSTAT]:'):
            t=t[len('[ENCOUCSTAT]:'):].strip()
        elif t.startswith('[ENCOUCSTAT]'):
            t=t[len('[ENCOUCSTAT]'):].strip()
        return t
    a=set(core(s) for s in d['a6000'])
    b=set(core(s) for s in d['a7s'])
    c=set(core(s) for s in d['a6300'])
    assert len(a&b)==49
    assert len(b-a)==5
    assert len(a&c)==47
    assert len(a-c)==2
    assert len(c-a)==21
